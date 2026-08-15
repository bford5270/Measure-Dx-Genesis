"""ICD-10 value set matching.

Codes in catalog/dyads.yaml are representative anchors, not validated value
sets. Matching is therefore prefix-based: an anchor of ``R10`` matches
``R10.31``, and an anchor of ``N44.00`` matches only itself.

The symptom side of every dyad must be calibrated against observed local coding
before the results mean anything. ``calibrate_symptom_set`` does that empirically
- see docs/04-spade-dyads.md#implementation-notes-for-the-analyst.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def normalize(code: str | None) -> str | None:
    """Uppercase, strip the decimal and surrounding whitespace."""
    if code is None or (isinstance(code, float) and pd.isna(code)):
        return None
    try:
        if pd.isna(code):
            return None
    except (TypeError, ValueError):
        pass
    return str(code).strip().upper().replace(".", "").replace(" ", "")


class ValueSet:
    """A prefix-matched set of ICD-10 codes."""

    def __init__(self, anchors: Iterable[str], name: str = ""):
        self.name = name
        self.anchors = tuple(
            sorted({a for a in (normalize(c) for c in anchors) if a})
        )

    def __repr__(self) -> str:  # pragma: no cover - display only
        return f"ValueSet({self.name!r}, {len(self.anchors)} anchors)"

    def __bool__(self) -> bool:
        return bool(self.anchors)

    def matches(self, code: str | None) -> bool:
        c = normalize(code)
        if not c:
            return False
        return any(c.startswith(a) for a in self.anchors)

    def mask(self, codes: pd.Series) -> pd.Series:
        """Vectorized membership test over a Series of codes."""
        if not self.anchors:
            return pd.Series(False, index=codes.index)
        norm = codes.map(normalize)
        out = pd.Series(False, index=codes.index)
        for anchor in self.anchors:
            out |= norm.fillna("").str.startswith(anchor)
        return out & norm.notna()


# Codes that mean "we do not yet know what this is". The left-hand side of the
# nonspecific-to-serious transition (trigger T-10) and the marker of a
# nonspecific prodrome (T-11).
NONSPECIFIC_ANCHORS = (
    # R00-R99 symptoms, signs and abnormal findings, not elsewhere classified
    "R",
    # Unspecified-site musculoskeletal pain and soft tissue disorders
    "M545", "M549", "M79", "M255", "M626",
    # Malaise, fatigue, viral syndrome NOS
    "B349",
    # Encounter for examination without complaint
    "Z00",
)

NONSPECIFIC = ValueSet(NONSPECIFIC_ANCHORS, name="nonspecific")


def is_nonspecific(code: str | None) -> bool:
    return NONSPECIFIC.matches(code)


def category3(code: str | None) -> str | None:
    """The 3-character ICD-10 category, used as a coarse relatedness test."""
    c = normalize(code)
    return c[:3] if c and len(c) >= 3 else c


def chapter(code: str | None) -> str | None:
    """The ICD-10 chapter letter."""
    c = normalize(code)
    return c[0] if c else None


def related(code_a: str | None, code_b: str | None, *, strategy: str = "category3") -> bool:
    """Coarse 'same clinical problem' test for linking encounters.

    ``category3`` is deliberately conservative: it links R10.9 to R10.31 but not
    to K35.20. Dyad-based linking (see triggers.dyad_transitions) is what carries
    the symptom-to-disease relationships; this function only groups repeat
    presentations of the same complaint.
    """
    if strategy == "category3":
        a, b = category3(code_a), category3(code_b)
    elif strategy == "chapter":
        a, b = chapter(code_a), chapter(code_b)
    elif strategy == "exact":
        a, b = normalize(code_a), normalize(code_b)
    else:
        raise ValueError(f"unknown relatedness strategy {strategy!r}")
    return bool(a) and a == b


def calibrate_symptom_set(
    diagnoses: pd.DataFrame,
    target: ValueSet,
    *,
    window_days: int,
    min_support: int = 5,
    top_n: int = 40,
) -> pd.DataFrame:
    """Derive a symptom value set from observed data.

    For every patient reaching `target`, look back `window_days` and count the
    3-character categories that actually preceded it. This is how the symptom
    side of a dyad should be built - from how corpsmen and GMOs code in practice,
    not from a textbook.

    Returns categories ranked by patient support, with a lift estimate against
    the background rate of the same category in the full diagnosis corpus.
    """
    dx = diagnoses.dropna(subset=["mrn", "code", "date"]).copy()
    if dx.empty:
        return pd.DataFrame(columns=["category", "patients", "share", "background", "lift"])

    dx["date"] = pd.to_datetime(dx["date"], errors="coerce")
    dx = dx.dropna(subset=["date"])
    dx["cat3"] = dx["code"].map(category3)

    hits = dx[target.mask(dx["code"])]
    if hits.empty:
        return pd.DataFrame(columns=["category", "patients", "share", "background", "lift"])

    first_hit = hits.groupby("mrn", as_index=False)["date"].min()
    first_hit = first_hit.rename(columns={"date": "target_date"})

    merged = dx.merge(first_hit, on="mrn", how="inner")
    delta = (merged["target_date"] - merged["date"]).dt.days
    window = merged[(delta > 0) & (delta <= window_days)]
    window = window[~target.mask(window["code"])]

    if window.empty:
        return pd.DataFrame(columns=["category", "patients", "share", "background", "lift"])

    n_patients = int(first_hit["mrn"].nunique())
    counts = (
        window.groupby("cat3")["mrn"]
        .nunique()
        .reset_index(name="patients")
        .query("patients >= @min_support")
    )
    counts["share"] = counts["patients"] / n_patients

    total_patients = int(dx["mrn"].nunique())
    background = (
        dx.groupby("cat3")["mrn"].nunique().reset_index(name="bg_patients")
    )
    background["background"] = background["bg_patients"] / max(total_patients, 1)

    out = counts.merge(background[["cat3", "background"]], on="cat3", how="left")
    out["lift"] = out["share"] / out["background"].replace(0, pd.NA)
    out = out.rename(columns={"cat3": "category"})
    return (
        out[["category", "patients", "share", "background", "lift"]]
        .sort_values(["lift", "patients"], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
