"""Canonical data model.

Every source adapter normalizes into these tables. Trigger rules and metrics are
written against this model only, so the same rules run against an M2 extract, a
CarePoint report, or a FHIR pull without modification.

Identifier convention follows Millennium usage:
    fin  - encounter identifier (the "FIN" on the note); the unit of the worklist
    mrn  - person identifier

Nothing in this package writes back to the source system.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# --------------------------------------------------------------------------
# Table schemas: column -> pandas dtype hint used for coercion and validation.
# "datetime" columns are coerced with pd.to_datetime.
# --------------------------------------------------------------------------

SCHEMAS: dict[str, dict[str, str]] = {
    "encounters": {
        "fin": "string",
        "mrn": "string",
        "start": "datetime",
        "end": "datetime",
        "enc_class": "string",  # AMB | EMER | IMP | VIRT
        "role_of_care": "string",  # R1 | R2 | R3 | MTF | PURCHASED
        "setting": "string",  # GARRISON | FIELD | SHIP | DEPLOYED
        "facility": "string",
        "provider_id": "string",
        "unit_id": "string",
        "disposition": "string",
    },
    "diagnoses": {
        "fin": "string",
        "mrn": "string",
        "code": "string",
        "system": "string",  # ICD10CM
        "rank": "string",  # PRINCIPAL | SECONDARY
        "date": "datetime",
    },
    "orders": {
        "order_id": "string",
        "fin": "string",
        "mrn": "string",
        "category": "string",  # LAB | IMG | REFERRAL | PROC
        "code": "string",
        "name": "string",
        "specialty": "string",
        "ordered_dt": "datetime",
        "status": "string",  # ORDERED | COMPLETED | CANCELLED
        "provider_id": "string",
    },
    "results": {
        "result_id": "string",
        "order_id": "string",
        "fin": "string",
        "mrn": "string",
        "code": "string",
        "name": "string",
        "value_num": "float",
        "value_text": "string",
        "units": "string",
        "abnormal_flag": "string",  # N | A | AA (critical)
        "resulted_dt": "datetime",
        "ack_dt": "datetime",
        "ack_provider_id": "string",
    },
    "referrals": {
        "referral_id": "string",
        "fin": "string",
        "mrn": "string",
        "specialty": "string",
        "ordered_dt": "datetime",
        "completed_dt": "datetime",
        "status": "string",
    },
    "dispositions": {
        "mrn": "string",
        "kind": "string",  # see DISPOSITION_KINDS
        "effective_date": "datetime",
        "code": "string",
        "detail": "string",
        "fin": "string",  # optional linkage to the encounter that recorded it
    },
    "roster": {
        "mrn": "string",
        "birth_date": "datetime",
        "sex": "string",
        "unit_id": "string",
        "gain_date": "datetime",
        "loss_date": "datetime",
    },
    "provider_assignments": {
        "provider_id": "string",
        "unit_id": "string",
        "start_date": "datetime",
        "end_date": "datetime",
    },
    "unit_movements": {
        "unit_id": "string",
        "kind": "string",  # DEPLOYMENT | FIELD_EX
        "start_date": "datetime",
        "end_date": "datetime",
    },
}

DISPOSITION_KINDS = {
    "DEATH",
    "ICU",
    "SURGERY_EMERGENT",
    "MEDEVAC",
    "LIMDU",
    "MEB",
    "PEB",
    "SEPARATION",
    "NONDEPLOYABLE",
    "EXERTIONAL_COLLAPSE",
}

# Columns that may contain PHI and must never be written to logs or to
# de-identified aggregate output. See phi.py.
PHI_COLUMNS = {
    "mrn",
    "fin",
    "birth_date",
    "value_text",
    "detail",
    "name",
    "provider_id",
    "ack_provider_id",
}


@dataclass
class Dataset:
    """A validated set of canonical tables."""

    tables: dict[str, pd.DataFrame] = field(default_factory=dict)

    def __getattr__(self, name: str) -> pd.DataFrame:
        # Only reached when normal attribute lookup fails, so `tables` is safe.
        try:
            return self.tables[name]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(
                f"table {name!r} not loaded; present: {sorted(self.tables)}"
            ) from exc

    def has(self, name: str) -> bool:
        return name in self.tables and not self.tables[name].empty

    def get(self, name: str) -> pd.DataFrame:
        """Return the table, or a correctly-shaped empty frame if absent."""
        if name in self.tables:
            return self.tables[name]
        return empty_table(name)

    def summary(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"table": k, "rows": len(v)} for k, v in sorted(self.tables.items())]
        )


def empty_table(name: str) -> pd.DataFrame:
    """An empty frame carrying the declared columns for `name`."""
    schema = SCHEMAS[name]
    return pd.DataFrame({c: pd.Series(dtype=_pandas_dtype(t)) for c, t in schema.items()})


def _pandas_dtype(hint: str) -> str:
    return {
        "string": "object",
        "float": "float64",
        "datetime": "datetime64[ns]",
    }[hint]


def coerce(name: str, df: pd.DataFrame, *, strict: bool = False) -> pd.DataFrame:
    """Coerce `df` to the declared schema for `name`.

    Missing optional columns are added as null. Unknown columns are preserved
    (they are frequently useful for review packets) unless `strict`.
    """
    if name not in SCHEMAS:
        raise KeyError(f"unknown table {name!r}")
    schema = SCHEMAS[name]
    out = df.copy()

    for col, hint in schema.items():
        if col not in out.columns:
            out[col] = pd.Series([pd.NA] * len(out), index=out.index)
        if hint == "datetime":
            out[col] = pd.to_datetime(out[col], errors="coerce")
        elif hint == "float":
            out[col] = pd.to_numeric(out[col], errors="coerce")
        else:
            out[col] = out[col].astype("object").where(out[col].notna(), None)

    if strict:
        out = out[list(schema)]
    else:
        extra = [c for c in out.columns if c not in schema]
        out = out[list(schema) + extra]
    return out.reset_index(drop=True)


REQUIRED_TABLES = ("encounters", "diagnoses")


def validate(ds: Dataset) -> list[str]:
    """Return a list of human-readable problems. Empty list means usable."""
    problems: list[str] = []

    for name in REQUIRED_TABLES:
        if not ds.has(name):
            problems.append(f"required table missing or empty: {name}")

    if ds.has("encounters"):
        enc = ds.encounters
        if enc["fin"].isna().any():
            problems.append("encounters: null fin present (fin is the worklist key)")
        dupes = int(enc["fin"].duplicated().sum())
        if dupes:
            problems.append(f"encounters: {dupes} duplicate fin values")
        if enc["start"].isna().any():
            problems.append("encounters: null start present")

    if ds.has("diagnoses") and ds.has("encounters"):
        known = set(ds.encounters["fin"].dropna())
        orphan = int((~ds.diagnoses["fin"].isin(known)).sum())
        if orphan:
            problems.append(f"diagnoses: {orphan} rows reference an unknown fin")

    if ds.has("dispositions"):
        bad = sorted(set(ds.dispositions["kind"].dropna()) - DISPOSITION_KINDS)
        if bad:
            problems.append(f"dispositions: unrecognized kind values {bad}")

    return problems
