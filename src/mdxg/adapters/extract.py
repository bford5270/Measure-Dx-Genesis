"""Flat-file adapter - the realistic day-one path.

You will almost certainly receive tabular extracts (an M2 export, a CarePoint
report, a Millennium/Discern report saved to CSV or Excel) long before you have
live query access. This adapter maps those columns onto the canonical model
using a YAML mapping file, so switching source systems means editing the mapping
rather than the rules.

    mdxg init-mapping ./mapping.yaml      # write a template
    mdxg run --mapping ./mapping.yaml --data ./extracts

Mapping format:

    encounters:
      file: encounters.csv
      columns:
        fin: ENCNTR_ID           # source column -> canonical name
        mrn: PERSON_MRN
        start: REG_DT_TM
      constants:
        setting: GARRISON        # value applied to every row
      values:                    # per-column value translation
        enc_class:
          "Outpatient": AMB
          "Emergency": EMER
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from ..model import SCHEMAS, Dataset, coerce

TEMPLATE: dict[str, Any] = {
    "encounters": {
        "file": "encounters.csv",
        "columns": {
            "fin": "FIN",
            "mrn": "MRN",
            "start": "ENCOUNTER_START",
            "end": "ENCOUNTER_END",
            "enc_class": "ENCOUNTER_TYPE",
            "role_of_care": "FACILITY_ROLE",
            "facility": "FACILITY",
            "provider_id": "ATTENDING_ID",
            "unit_id": "UIC",
        },
        "constants": {"setting": "GARRISON"},
        "values": {
            "enc_class": {
                "Outpatient": "AMB",
                "Clinic": "AMB",
                "Emergency": "EMER",
                "Inpatient": "IMP",
                "Telehealth": "VIRT",
            }
        },
    },
    "diagnoses": {
        "file": "diagnoses.csv",
        "columns": {
            "fin": "FIN",
            "mrn": "MRN",
            "code": "DIAGNOSIS_CODE",
            "rank": "DIAGNOSIS_RANK",
            "date": "DIAGNOSIS_DT",
        },
        "constants": {"system": "ICD10CM"},
    },
    "orders": {
        "file": "orders.csv",
        "columns": {
            "order_id": "ORDER_ID",
            "fin": "FIN",
            "mrn": "MRN",
            "category": "ORDER_CATEGORY",
            "code": "ORDER_CODE",
            "name": "ORDER_NAME",
            "ordered_dt": "ORDER_DT",
            "status": "ORDER_STATUS",
            "provider_id": "ORDERING_PROVIDER_ID",
        },
    },
    "results": {
        "file": "results.csv",
        "columns": {
            "result_id": "RESULT_ID",
            "order_id": "ORDER_ID",
            "fin": "FIN",
            "mrn": "MRN",
            "code": "RESULT_CODE",
            "name": "RESULT_NAME",
            "value_num": "RESULT_VALUE_NUM",
            "units": "RESULT_UNITS",
            "abnormal_flag": "ABNORMAL_FLAG",
            "resulted_dt": "RESULT_DT",
            "ack_dt": "REVIEWED_DT",
            "ack_provider_id": "REVIEWED_BY_ID",
        },
        "values": {
            "abnormal_flag": {
                "Normal": "N",
                "Abnormal": "A",
                "High": "A",
                "Low": "A",
                "Critical": "AA",
                "Panic": "AA",
            }
        },
    },
    "referrals": {
        "file": "referrals.csv",
        "columns": {
            "referral_id": "REFERRAL_ID",
            "fin": "FIN",
            "mrn": "MRN",
            "specialty": "REFERRED_TO_SPECIALTY",
            "ordered_dt": "REFERRAL_DT",
            "completed_dt": "APPOINTMENT_COMPLETED_DT",
            "status": "REFERRAL_STATUS",
        },
    },
    "dispositions": {
        "file": "dispositions.csv",
        "columns": {
            "mrn": "MRN",
            "kind": "EVENT_TYPE",
            "effective_date": "EVENT_DT",
            "code": "CONDITION_CODE",
            "fin": "FIN",
        },
    },
    "roster": {
        "file": "roster.csv",
        "columns": {
            "mrn": "MRN",
            "birth_date": "DOB",
            "sex": "SEX",
            "unit_id": "UIC",
            "gain_date": "GAIN_DT",
            "loss_date": "LOSS_DT",
        },
    },
    "provider_assignments": {
        "file": "provider_assignments.csv",
        "columns": {
            "provider_id": "PROVIDER_ID",
            "unit_id": "UIC",
            "start_date": "ASSIGNED_DT",
            "end_date": "DETACHED_DT",
        },
    },
    "unit_movements": {
        "file": "unit_movements.csv",
        "columns": {
            "unit_id": "UIC",
            "kind": "MOVEMENT_TYPE",
            "start_date": "START_DT",
            "end_date": "END_DT",
        },
    },
}


def write_template(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# mdxg source mapping.\n"
        "# Left side = canonical column, right side = the column in YOUR extract.\n"
        "# Delete any table you do not have; rules degrade gracefully.\n"
        "# Column names below are illustrative - confirm them against your own\n"
        "# extract. They are not a claim about the MHS GENESIS schema.\n\n"
    )
    p.write_text(header + yaml.safe_dump(TEMPLATE, sort_keys=False))
    return p


def _read(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        return pd.read_excel(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype=str, keep_default_na=True)


def load(
    mapping_path: str | Path, data_dir: str | Path, *, logger=None
) -> Dataset:
    mapping = yaml.safe_load(Path(mapping_path).read_text()) or {}
    root = Path(data_dir)
    tables: dict[str, pd.DataFrame] = {}

    for table, spec in mapping.items():
        if table not in SCHEMAS:
            if logger:
                logger.warning("mapping references unknown table %s - skipped", table)
            continue
        fname = spec.get("file")
        if not fname:
            continue
        path = root / fname
        if not path.exists():
            if logger:
                logger.warning("missing extract for %s: %s", table, path.name)
            continue

        raw = _read(path)
        cols = spec.get("columns", {}) or {}
        out = pd.DataFrame(index=raw.index)

        for canonical, source in cols.items():
            if source in raw.columns:
                out[canonical] = raw[source]
            elif logger:
                logger.warning("%s: source column %r not found", table, source)

        for canonical, value in (spec.get("constants", {}) or {}).items():
            out[canonical] = value

        for canonical, lookup in (spec.get("values", {}) or {}).items():
            if canonical in out.columns:
                out[canonical] = out[canonical].map(lambda v: lookup.get(v, v))

        tables[table] = coerce(table, out)
        if logger:
            logger.info("loaded %s: %d rows", table, len(tables[table]))

    return Dataset(tables=tables)
