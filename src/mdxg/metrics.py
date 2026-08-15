"""Metrics from docs/05-metrics.md.

Adjudication-dependent metrics (yield, PPV lift, harm) require an adjudications
table the review panel fills in:

    fin, arm, reviewer_id, review_date, safer_dx_item13, missed_opportunity,
    ncc_merp, duty_days_lost, deployability_affected, primary_factor

`arm` is TRIGGERED or RANDOM_CONTROL. Without the control arm there is no PPV
lift, which is the program's central claim.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .catalog import Catalog, DyadSpec
from .model import Dataset
from .valuesets import NONSPECIFIC, ValueSet

MOD_THRESHOLD = 5  # Revised Safer Dx item 13 >= 5 indicates a missed opportunity
RETIREMENT_MIN_CASES = 40
RETIREMENT_YIELD = 0.10


# --------------------------------------------------------------------------
# interval measures - computable with no adjudication at all
# --------------------------------------------------------------------------


def symptom_to_diagnosis_interval(
    ds: Dataset, dyad: DyadSpec, *, use_nonspecific_fallback: bool = True
) -> pd.DataFrame:
    """Days from first related symptomatic encounter to the target diagnosis.

    The best single measure the program produces: continuous, insensitive to
    review intensity, and comparable across units in a way an error count is not.
    """
    dx = ds.get("diagnoses").dropna(subset=["mrn", "code", "date"])
    if dx.empty or not dyad.target_codes:
        return pd.DataFrame(columns=["mrn", "symptom_date", "target_date", "interval_days"])

    target = dyad.target_set
    symptom = dyad.symptom_set
    sym_set: ValueSet = symptom if symptom else (NONSPECIFIC if use_nonspecific_fallback else ValueSet(()))
    if not sym_set:
        return pd.DataFrame(columns=["mrn", "symptom_date", "target_date", "interval_days"])

    hits = dx[target.mask(dx["code"])]
    if hits.empty:
        return pd.DataFrame(columns=["mrn", "symptom_date", "target_date", "interval_days"])
    first_target = hits.groupby("mrn", as_index=False)["date"].min().rename(
        columns={"date": "target_date"}
    )

    sym = dx[sym_set.mask(dx["code"]) & ~target.mask(dx["code"])]
    if sym.empty:
        return pd.DataFrame(columns=["mrn", "symptom_date", "target_date", "interval_days"])

    merged = sym.merge(first_target, on="mrn", how="inner")
    delta = (merged["target_date"] - merged["date"]).dt.days
    merged = merged[(delta > 0) & (delta <= dyad.window_days)]
    if merged.empty:
        return pd.DataFrame(columns=["mrn", "symptom_date", "target_date", "interval_days"])

    out = (
        merged.groupby(["mrn", "target_date"], as_index=False)["date"]
        .min()
        .rename(columns={"date": "symptom_date"})
    )
    out["interval_days"] = (out["target_date"] - out["symptom_date"]).dt.days
    return out[["mrn", "symptom_date", "target_date", "interval_days"]].reset_index(drop=True)


def interval_summary(ds: Dataset, cat: Catalog, *, dyads=None) -> pd.DataFrame:
    """Median and IQR interval per dyad. Report this, not a mean."""
    dyads = dyads if dyads is not None else list(cat.dyads.values())
    rows = []
    for d in dyads:
        iv = symptom_to_diagnosis_interval(ds, d)
        if iv.empty:
            rows.append(
                {"dyad": d.id, "target": d.target, "n": 0, "median_days": None,
                 "p25": None, "p75": None, "window_days": d.window_days}
            )
            continue
        s = iv["interval_days"]
        rows.append(
            {
                "dyad": d.id,
                "target": d.target,
                "n": int(len(s)),
                "median_days": float(s.median()),
                "p25": float(s.quantile(0.25)),
                "p75": float(s.quantile(0.75)),
                "window_days": d.window_days,
            }
        )
    return pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------
# loop closure - pure process rates, no adjudication, available monthly
# --------------------------------------------------------------------------


def loop_closure_rates(
    ds: Dataset, *, as_of: pd.Timestamp | None = None, result_days: int = 14, referral_days: int = 60
) -> pd.DataFrame:
    as_of = as_of or pd.Timestamp.today().normalize()
    rows = []

    res = ds.get("results")
    if not res.empty:
        abn = res[res["abnormal_flag"].isin(["A", "AA"])].dropna(subset=["resulted_dt"])
        mature = abn[(as_of - abn["resulted_dt"]).dt.days >= result_days]
        unacked = mature[mature["ack_dt"].isna()]
        rows.append(
            {
                "measure": "abnormal_result_unacknowledged",
                "numerator": int(len(unacked)),
                "denominator": int(len(mature)),
                "rate_per_1000": _per_1000(len(unacked), len(mature)),
                "threshold_days": result_days,
            }
        )

    ref = ds.get("referrals")
    if not ref.empty:
        mature = ref[(as_of - ref["ordered_dt"]).dt.days >= referral_days]
        mature = mature[mature["status"].astype("object") != "CANCELLED"]
        incomplete = mature[mature["completed_dt"].isna()]
        rows.append(
            {
                "measure": "referral_not_completed",
                "numerator": int(len(incomplete)),
                "denominator": int(len(mature)),
                "rate_per_1000": _per_1000(len(incomplete), len(mature)),
                "threshold_days": referral_days,
            }
        )

    return pd.DataFrame(rows)


def _per_1000(num: int, den: int) -> float | None:
    return round(1000.0 * num / den, 1) if den else None


# --------------------------------------------------------------------------
# adjudication-dependent
# --------------------------------------------------------------------------


@dataclass
class Proportion:
    numerator: int
    denominator: int

    @property
    def value(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None

    def wilson(self, z: float = 1.96) -> tuple[float, float] | None:
        """Wilson score interval - correct at the small denominators this
        program will actually have, unlike the normal approximation."""
        n = self.denominator
        if not n:
            return None
        p = self.numerator / n
        d = 1 + z**2 / n
        centre = (p + z**2 / (2 * n)) / d
        half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
        return (max(0.0, centre - half), min(1.0, centre + half))


def _mod_flag(adj: pd.DataFrame) -> pd.Series:
    if "missed_opportunity" in adj.columns and adj["missed_opportunity"].notna().any():
        return adj["missed_opportunity"].astype("boolean").fillna(False)
    return (
        pd.to_numeric(adj.get("safer_dx_item13"), errors="coerce") >= MOD_THRESHOLD
    ).fillna(False)


def mod_yield(adjudications: pd.DataFrame, worklist: pd.DataFrame) -> pd.DataFrame:
    """Confirmed missed opportunities per adjudicated case, by trigger.

    Reference: 31.8% (224/703) across 11 organizations in the Measure Dx
    evaluation.
    """
    if adjudications.empty:
        return pd.DataFrame(columns=["trigger_id", "adjudicated", "confirmed", "yield", "ci_low", "ci_high"])

    adj = adjudications.copy()
    adj["_mod"] = _mod_flag(adj)

    link = worklist[["fin", "trigger_id"]].drop_duplicates() if not worklist.empty else pd.DataFrame(columns=["fin", "trigger_id"])
    merged = adj.merge(link, on="fin", how="left")
    merged["trigger_id"] = merged["trigger_id"].fillna(
        merged.get("arm", pd.Series("UNKNOWN", index=merged.index))
    )

    rows = []
    for tid, g in merged.groupby("trigger_id", sort=False):
        p = Proportion(int(g["_mod"].sum()), int(len(g)))
        ci = p.wilson()
        rows.append(
            {
                "trigger_id": tid,
                "adjudicated": p.denominator,
                "confirmed": p.numerator,
                "yield": round(p.value, 4) if p.value is not None else None,
                "ci_low": round(ci[0], 4) if ci else None,
                "ci_high": round(ci[1], 4) if ci else None,
            }
        )
    return pd.DataFrame(rows).sort_values("yield", ascending=False).reset_index(drop=True)


def ppv_lift(adjudications: pd.DataFrame, worklist: pd.DataFrame) -> pd.DataFrame:
    """Trigger yield divided by the random control arm yield.

    The central claim of the program. Without a control arm this returns nothing,
    deliberately: there is no defensible lift figure without a base rate.
    """
    if adjudications.empty or "arm" not in adjudications.columns:
        return pd.DataFrame(columns=["trigger_id", "yield", "control_yield", "lift"])

    control = adjudications[adjudications["arm"] == "RANDOM_CONTROL"]
    if control.empty:
        return pd.DataFrame(columns=["trigger_id", "yield", "control_yield", "lift"])

    base = Proportion(int(_mod_flag(control).sum()), int(len(control)))
    base_val = base.value
    triggered = adjudications[adjudications["arm"] != "RANDOM_CONTROL"]
    y = mod_yield(triggered, worklist)
    if y.empty:
        return pd.DataFrame(columns=["trigger_id", "yield", "control_yield", "lift"])

    y = y.copy()
    y["control_yield"] = round(base_val, 4) if base_val is not None else None
    y["control_n"] = base.denominator
    y["lift"] = y["yield"] / base_val if base_val else np.nan
    y["lift"] = y["lift"].round(1)
    return y[["trigger_id", "adjudicated", "yield", "ci_low", "ci_high", "control_yield", "control_n", "lift"]]


def retirement_check(yield_table: pd.DataFrame) -> pd.DataFrame:
    """Apply the retirement rule from docs/05-metrics.md."""
    if yield_table.empty:
        return yield_table
    out = yield_table.copy()
    out["decision"] = [
        "retain"
        if (n < RETIREMENT_MIN_CASES)
        else ("retire_or_retune" if (y is not None and y < RETIREMENT_YIELD) else "retain")
        for n, y in zip(out["adjudicated"], out["yield"])
    ]
    out["decision_basis"] = [
        f"insufficient cases (n={n} < {RETIREMENT_MIN_CASES})"
        if n < RETIREMENT_MIN_CASES
        else f"yield {y:.1%} vs {RETIREMENT_YIELD:.0%} threshold"
        for n, y in zip(out["adjudicated"], out["yield"].fillna(0))
    ]
    return out


def detection_density(
    adjudications: pd.DataFrame, ds: Dataset, *, period_years: float = 1.0
) -> pd.DataFrame:
    """Confirmed events per 10,000 encounters and per 1,000 Marines per year.

    The true-denominator measure. This is the one a civilian health system
    cannot compute.
    """
    if adjudications.empty:
        return pd.DataFrame()
    confirmed = int(_mod_flag(adjudications).sum())
    n_enc = int(len(ds.get("encounters")))
    roster = ds.get("roster")
    n_pop = int(roster["mrn"].nunique()) if not roster.empty else int(
        ds.get("encounters")["mrn"].nunique()
    )
    return pd.DataFrame(
        [
            {
                "confirmed_events": confirmed,
                "encounters": n_enc,
                "population": n_pop,
                "period_years": period_years,
                "per_10k_encounters": round(10000 * confirmed / n_enc, 2) if n_enc else None,
                "per_1k_marines_year": (
                    round(1000 * confirmed / (n_pop * period_years), 2) if n_pop else None
                ),
                "denominator_source": "roster" if not roster.empty else "encounters (roster absent)",
            }
        ]
    )


def harm_and_duty_profile(adjudications: pd.DataFrame) -> pd.DataFrame:
    """Harm distribution and the readiness translation."""
    if adjudications.empty:
        return pd.DataFrame()
    adj = adjudications.copy()
    adj["_mod"] = _mod_flag(adj)
    conf = adj[adj["_mod"]]
    if conf.empty:
        return pd.DataFrame()

    rows = []
    if "ncc_merp" in conf.columns:
        for cat, g in conf.groupby("ncc_merp", sort=True):
            rows.append({"dimension": "ncc_merp", "value": cat, "n": int(len(g))})
    if "duty_days_lost" in conf.columns:
        days = pd.to_numeric(conf["duty_days_lost"], errors="coerce")
        rows.append({"dimension": "duty_days_lost", "value": "total", "n": int(days.sum(skipna=True))})
        rows.append(
            {"dimension": "duty_days_lost", "value": "median_per_event",
             "n": float(days.median(skipna=True)) if days.notna().any() else None}
        )
    if "deployability_affected" in conf.columns:
        n = int(conf["deployability_affected"].astype("boolean").fillna(False).sum())
        rows.append({"dimension": "deployability", "value": "affected", "n": n})
    if "primary_factor" in conf.columns:
        for f, g in conf.groupby("primary_factor", sort=False):
            rows.append({"dimension": "primary_factor", "value": f, "n": int(len(g))})
    return pd.DataFrame(rows)


def coverage(worklist: pd.DataFrame, adjudications: pd.DataFrame) -> pd.DataFrame:
    """Trigger coverage - fired versus adjudicated, per trigger.

    Every count reported to leadership must be paired with this. A rising
    confirmed-event count next to a rising coverage rate is a detection story,
    not a deterioration story.
    """
    if worklist.empty:
        return pd.DataFrame(columns=["trigger_id", "fired", "adjudicated", "coverage"])
    fired = worklist.groupby("trigger_id")["fin"].nunique().rename("fired")
    if adjudications.empty:
        out = fired.reset_index()
        out["adjudicated"] = 0
        out["coverage"] = 0.0
        return out
    link = worklist[["fin", "trigger_id"]].drop_duplicates()
    done = adjudications.merge(link, on="fin", how="inner")
    adjud = done.groupby("trigger_id")["fin"].nunique().rename("adjudicated")
    out = pd.concat([fired, adjud], axis=1).fillna(0).reset_index()
    out["coverage"] = (out["adjudicated"] / out["fired"]).round(3)
    return out
