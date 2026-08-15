"""PHI handling.

Three jobs:

1. Pseudonymize identifiers with a keyed HMAC so cases can be tracked across
   runs without carrying MRNs into analysis artifacts.
2. Refuse to let PHI-designated columns reach the logs.
3. Enforce small-cell suppression on aggregate output.

The worklist a reviewer works from necessarily contains the real FIN - that is
the point of it. Everything else this package emits is pseudonymized. Keep the
two output classes in separate directories with separate access control; see
docs/11-running-the-code.md.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
from collections.abc import Iterable

import pandas as pd

from .model import PHI_COLUMNS

DEFAULT_MIN_CELL = 11  # HHS/CMS-style small-cell suppression threshold


class MissingSaltError(RuntimeError):
    pass


def get_salt(explicit: str | None = None) -> bytes:
    """Resolve the pseudonymization key.

    Read from the MDXG_SALT environment variable so it is never committed. The
    same salt must be reused across runs for identifiers to remain linkable, and
    must be stored with the same protection as the data itself.
    """
    salt = explicit or os.environ.get("MDXG_SALT")
    if not salt:
        raise MissingSaltError(
            "set MDXG_SALT to a long random secret (and store it under the same "
            "access control as the data). Generate one with: "
            "python -c \"import secrets;print(secrets.token_hex(32))\""
        )
    if len(salt) < 16:
        raise MissingSaltError("MDXG_SALT must be at least 16 characters")
    return salt.encode("utf-8")


def pseudonymize(values: Iterable, salt: bytes, *, length: int = 12) -> pd.Series:
    """Keyed one-way pseudonym. Stable across runs for a fixed salt."""
    ser = pd.Series(list(values), dtype="object")

    def _one(v):
        if v is None or (isinstance(v, float) and pd.isna(v)) or pd.isna(v):
            return None
        digest = hmac.new(salt, str(v).strip().encode("utf-8"), hashlib.sha256)
        return digest.hexdigest()[:length]

    return ser.map(_one)


def deidentify(
    df: pd.DataFrame,
    salt: bytes,
    *,
    keep: Iterable[str] = (),
    drop_free_text: bool = True,
) -> pd.DataFrame:
    """Return a copy safe for aggregate analysis artifacts.

    Identifier columns are replaced with pseudonyms; free-text columns are
    dropped outright rather than scrubbed, because reliable scrubbing of
    clinical free text is not a solved problem and should not be pretended.
    """
    keep = set(keep)
    out = df.copy()

    for col in ("mrn", "fin", "provider_id", "ack_provider_id", "order_id", "result_id"):
        if col in out.columns and col not in keep:
            out[col] = pseudonymize(out[col], salt)

    if drop_free_text:
        for col in ("value_text", "detail", "narrative", "note_text", "reason_text"):
            if col in out.columns and col not in keep:
                out = out.drop(columns=[col])

    if "birth_date" in out.columns and "birth_date" not in keep:
        # Age in years at a fixed reference is adequate for this population and
        # removes a direct identifier.
        out = out.drop(columns=["birth_date"])

    return out


def suppress_small_cells(
    df: pd.DataFrame,
    count_columns: Iterable[str],
    *,
    minimum: int = DEFAULT_MIN_CELL,
    marker: str = "<11",
) -> pd.DataFrame:
    """Blank counts below `minimum` in aggregate output."""
    out = df.copy()
    for col in count_columns:
        if col not in out.columns:
            continue
        out[col] = out[col].map(
            lambda v: marker if pd.notna(v) and 0 < float(v) < minimum else v
        )
    return out


# --------------------------------------------------------------------------
# Logging guard
# --------------------------------------------------------------------------

_MRN_LIKE = re.compile(r"\b\d{6,12}\b")


class PHILogFilter(logging.Filter):
    """Blocks log records that appear to carry PHI.

    This is a backstop, not a license. Do not log record-level data.
    """

    def __init__(self, extra_terms: Iterable[str] = ()):
        super().__init__()
        self.terms = {t.lower() for t in (*PHI_COLUMNS, *extra_terms)}

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = str(record.getMessage())
        except Exception:  # pragma: no cover - defensive
            return False
        if _MRN_LIKE.search(msg):
            record.msg = "[suppressed: log line matched an identifier pattern]"
            record.args = ()
        return True


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("mdxg")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        handler.addFilter(PHILogFilter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger
