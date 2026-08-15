"""Worklist assembly.

The primary output: **one row per FIN**, listing every trigger that fired on that
note, ranked so a reviewer works the list top-down.

A FIN on this list is a note worth a second look. It is not an allegation, and
the column headers are written so nobody can read it as one.
"""

from __future__ import annotations

import pandas as pd

PRIORITY_RANK = {
    "mandatory": 0,
    "high": 1,
    "medium_high": 2,
    "medium": 3,
    "low": 4,
}

BY_FIN_COLUMNS = [
    "fin",
    "mrn",
    "index_date",
    "index_dx",
    "index_role",
    "index_setting",
    "top_priority",
    "n_triggers",
    "triggers",
    "review_score",
    "earliest_event_date",
    "min_days_to_event",
    "event_kinds",
    "reasons",
]


def _prio_rank(series: pd.Series) -> pd.Series:
    return series.astype("object").map(lambda p: PRIORITY_RANK.get(str(p), 5)).fillna(5)


def rank_detail(worklist: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate firings and sort by review priority."""
    if worklist.empty:
        return worklist
    df = worklist.copy()
    df["_prio"] = _prio_rank(df["priority"])
    df = (
        df.sort_values(["_prio", "days_index_to_event"], ascending=[True, True])
        .drop_duplicates(subset=["fin", "trigger_id", "event_fin"], keep="first")
        .reset_index(drop=True)
    )
    return df.drop(columns=["_prio"])


def by_fin(worklist: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per FIN - the reviewer's actual worklist.

    `review_score` is a triage aid, not a probability. It rewards multiple
    independent triggers firing on the same note and weights by the priority of
    the strongest one. Sort by it; do not report it as a measure.
    """
    if worklist.empty:
        return pd.DataFrame({c: pd.Series(dtype="object") for c in BY_FIN_COLUMNS})

    df = rank_detail(worklist)
    df["_prio"] = _prio_rank(df["priority"])

    grouped = []
    for fin, g in df.groupby("fin", sort=False):
        g = g.sort_values("_prio")
        top = g.iloc[0]
        n = int(g["trigger_id"].nunique())
        best_prio = int(g["_prio"].min())
        score = round((5 - best_prio) * 2 + (n - 1) * 1.5, 2)
        grouped.append(
            {
                "fin": fin,
                "mrn": top["mrn"],
                "index_date": top["index_date"],
                "index_dx": top["index_dx"],
                "index_role": top["index_role"],
                "index_setting": top["index_setting"],
                "top_priority": top["priority"],
                "n_triggers": n,
                "triggers": "; ".join(sorted(set(g["trigger_id"]))),
                "review_score": score,
                "earliest_event_date": g["event_date"].min(),
                "min_days_to_event": (
                    int(g["days_index_to_event"].min())
                    if g["days_index_to_event"].notna().any()
                    else None
                ),
                "event_kinds": "; ".join(sorted(set(g["event_kind"].dropna().astype(str)))),
                "reasons": " | ".join(g["reason"].dropna().astype(str).tolist()[:4]),
            }
        )

    out = pd.DataFrame(grouped)
    out = out.sort_values(
        ["review_score", "min_days_to_event"], ascending=[False, True]
    ).reset_index(drop=True)
    return out[BY_FIN_COLUMNS]


def apply_sampling(
    worklist: pd.DataFrame, catalog, *, seed: int = 20260815
) -> pd.DataFrame:
    """Apply per-trigger sample_rate from the catalog.

    Sampling is recorded, never silent: the number dropped per trigger is
    returned in `.attrs['sampling']` so it can be reported. A worklist that
    silently truncates reads as full coverage when it is not.
    """
    if worklist.empty:
        return worklist
    kept, dropped = [], {}
    for tid, g in worklist.groupby("trigger_id", sort=False):
        spec = catalog.triggers.get(tid)
        rate = getattr(spec, "sample_rate", None) if spec else None
        if not rate or rate >= 1:
            kept.append(g)
            continue
        take = g.sample(frac=float(rate), random_state=seed)
        dropped[tid] = int(len(g) - len(take))
        kept.append(take)
    out = pd.concat(kept, ignore_index=True) if kept else worklist
    out.attrs["sampling"] = dropped
    return out


def random_control_arm(
    encounters: pd.DataFrame, *, n: int, seed: int = 20260815, exclude_fins=()
) -> pd.DataFrame:
    """Draw the random control arm.

    Reviewed with the same instrument by the same panel. This is what makes the
    trigger PPV-lift claim defensible - see docs/05-metrics.md.
    """
    pool = encounters[~encounters["fin"].isin(set(exclude_fins))]
    if pool.empty:
        return pd.DataFrame(columns=["fin", "mrn", "index_date", "arm"])
    take = pool.sample(n=min(n, len(pool)), random_state=seed)
    return pd.DataFrame(
        {
            "fin": take["fin"].values,
            "mrn": take["mrn"].values,
            "index_date": take["start"].values,
            "arm": "RANDOM_CONTROL",
        }
    ).reset_index(drop=True)
