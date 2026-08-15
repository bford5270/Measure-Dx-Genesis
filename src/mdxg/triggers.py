"""Trigger rules.

Each rule returns worklist rows. **The `fin` on a row is the index encounter -
the note that might benefit from review** - not the downstream event that fired
the trigger. The downstream event is carried in `event_fin` / `event_date` so the
reviewer can see how the episode ended.

That direction is the whole point: triggers sample backward from an outcome so
the index note becomes judgeable. See docs/01-why-random-review-fails.md.

A rule firing is a question, never a finding. Nothing here asserts that a missed
opportunity occurred; that determination is made by a clinician using the Revised
Safer Dx Instrument.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import pandas as pd

from .catalog import Catalog, DyadSpec
from .model import Dataset
from .valuesets import NONSPECIFIC, ValueSet, category3

WORKLIST_COLUMNS = [
    "trigger_id",
    "trigger_name",
    "priority",
    "fin",
    "mrn",
    "index_date",
    "index_dx",
    "index_role",
    "index_setting",
    "event_kind",
    "event_fin",
    "event_date",
    "event_dx",
    "days_index_to_event",
    "look_back_start",
    "reason",
    "evidence",
]

OUTPATIENT_CLASSES = ("AMB", "VIRT")
ACUTE_CLASSES = ("IMP", "EMER")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def principal_dx(diagnoses: pd.DataFrame) -> pd.DataFrame:
    """One row per fin: the principal diagnosis (or the first recorded)."""
    if diagnoses.empty:
        return pd.DataFrame(columns=["fin", "dx_code"])
    dx = diagnoses.dropna(subset=["fin", "code"]).copy()
    if dx.empty:
        return pd.DataFrame(columns=["fin", "dx_code"])
    dx["_rank"] = (dx["rank"].astype("object") != "PRINCIPAL").astype(int)
    dx = dx.sort_values(["fin", "_rank"])
    first = dx.groupby("fin", as_index=False).first()
    return first[["fin", "code"]].rename(columns={"code": "dx_code"})


def encounters_with_dx(ds: Dataset) -> pd.DataFrame:
    enc = ds.get("encounters").copy()
    pdx = principal_dx(ds.get("diagnoses"))
    enc = enc.merge(pdx, on="fin", how="left")
    enc["dx_cat3"] = enc["dx_code"].map(category3)
    return enc


def _empty_worklist() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in WORKLIST_COLUMNS})


def _rows(records: list[dict]) -> pd.DataFrame:
    if not records:
        return _empty_worklist()
    df = pd.DataFrame(records)
    for col in WORKLIST_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[WORKLIST_COLUMNS]


def _ev(**kwargs) -> str:
    """Compact evidence blob. Never put free text or names in here."""
    clean = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in kwargs.items()}
    return json.dumps(clean, default=str, separators=(",", ":"))


def _lookback(
    enc: pd.DataFrame,
    events: pd.DataFrame,
    *,
    days: int,
    event_date_col: str,
    index_classes: tuple[str, ...] | None = None,
    require_related: bool = False,
    min_days: int = 0,
) -> pd.DataFrame:
    """Join encounters to downstream events on mrn within a look-back window.

    Returns one row per (index encounter, event) pair.
    """
    if enc.empty or events.empty:
        return pd.DataFrame()

    left = enc
    if index_classes:
        left = left[left["enc_class"].isin(index_classes)]
    if left.empty:
        return pd.DataFrame()

    merged = left.merge(events, on="mrn", how="inner", suffixes=("", "_ev"))
    if merged.empty:
        return pd.DataFrame()

    delta = (merged[event_date_col] - merged["start"]).dt.days
    merged = merged.assign(_delta=delta)
    merged = merged[(merged["_delta"] >= min_days) & (merged["_delta"] <= days)]

    if require_related and not merged.empty and "event_dx" in merged.columns:
        ev_cat = merged["event_dx"].map(category3)
        # Keep the pair when the categories agree, or when the event carries no
        # diagnosis to compare against (do not silently drop unclassified events).
        merged = merged[(merged["dx_cat3"] == ev_cat) | ev_cat.isna()]

    return merged


def _dispositions(ds: Dataset, kind: str) -> pd.DataFrame:
    d = ds.get("dispositions")
    if d.empty:
        return pd.DataFrame(columns=["mrn", "event_date", "event_fin", "event_dx"])
    sel = d[d["kind"] == kind].dropna(subset=["mrn", "effective_date"])
    return pd.DataFrame(
        {
            "mrn": sel["mrn"],
            "event_date": sel["effective_date"],
            "event_fin": sel["fin"],
            "event_dx": sel["code"],
        }
    ).reset_index(drop=True)


def _emit(
    pairs: pd.DataFrame,
    *,
    tid: str,
    name: str,
    priority: str,
    event_kind: str,
    days: int,
    reason: Callable[[pd.Series], str],
) -> pd.DataFrame:
    records = []
    for _, r in pairs.iterrows():
        records.append(
            {
                "trigger_id": tid,
                "trigger_name": name,
                "priority": priority,
                "fin": r["fin"],
                "mrn": r["mrn"],
                "index_date": r["start"],
                "index_dx": r.get("dx_code"),
                "index_role": r.get("role_of_care"),
                "index_setting": r.get("setting"),
                "event_kind": event_kind,
                "event_fin": r.get("event_fin"),
                "event_date": r.get("event_date"),
                "event_dx": r.get("event_dx"),
                "days_index_to_event": int(r["_delta"]),
                "look_back_start": r["event_date"] - pd.Timedelta(days=days),
                "reason": reason(r),
                "evidence": _ev(window_days=days),
            }
        )
    return _rows(records)


# --------------------------------------------------------------------------
# Tier 1 - sentinel outcomes
# --------------------------------------------------------------------------


def t01_death_lookback(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-01")
    days = spec.look_back or 365
    pairs = _lookback(
        encounters_with_dx(ds), _dispositions(ds, "DEATH"), days=days, event_date_col="event_date"
    )
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-01",
        name=spec.name,
        priority=spec.priority,
        event_kind="DEATH",
        days=days,
        reason=lambda r: (
            f"Encounter {int(r['_delta'])} days before death; "
            f"index impression {r.get('dx_code') or 'not coded'}"
        ),
    )


def t02_icu_escalation(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-02")
    days = spec.look_back or 90
    pairs = _lookback(
        encounters_with_dx(ds),
        _dispositions(ds, "ICU"),
        days=days,
        event_date_col="event_date",
        index_classes=OUTPATIENT_CLASSES,
    )
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-02",
        name=spec.name,
        priority=spec.priority,
        event_kind="ICU",
        days=days,
        reason=lambda r: f"Outpatient encounter {int(r['_delta'])} days before unplanned critical care escalation",
    )


def t03_medevac(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-03")
    days = spec.look_back or 90
    pairs = _lookback(
        encounters_with_dx(ds),
        _dispositions(ds, "MEDEVAC"),
        days=days,
        event_date_col="event_date",
        require_related=True,
    )
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-03",
        name=spec.name,
        priority=spec.priority,
        event_kind="MEDEVAC",
        days=days,
        reason=lambda r: f"Related encounter {int(r['_delta'])} days before urgent/priority evacuation",
    )


def t05_emergency_surgery(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-05")
    days = spec.look_back or 90
    pairs = _lookback(
        encounters_with_dx(ds),
        _dispositions(ds, "SURGERY_EMERGENT"),
        days=days,
        event_date_col="event_date",
        index_classes=OUTPATIENT_CLASSES,
    )
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-05",
        name=spec.name,
        priority=spec.priority,
        event_kind="SURGERY_EMERGENT",
        days=days,
        reason=lambda r: f"Outpatient encounter {int(r['_delta'])} days before emergent operative procedure",
    )


# --------------------------------------------------------------------------
# Tier 2 - trajectory and escalation
# --------------------------------------------------------------------------


def t06_rule_of_three(ds: Dataset, cat: Catalog, *, window: int = 30) -> pd.DataFrame:
    """Three or more encounters for the same complaint category within `window`,
    where the third carries a different diagnosis or escalates."""
    spec = cat.trigger("T-06")
    enc = encounters_with_dx(ds)
    enc = enc.dropna(subset=["dx_cat3"]).sort_values(["mrn", "start"])
    if enc.empty:
        return _empty_worklist()

    records = []
    for (mrn, cat3), grp in enc.groupby(["mrn", "dx_cat3"], sort=False):
        if len(grp) < 3:
            continue
        grp = grp.sort_values("start").reset_index(drop=True)
        for i in range(len(grp) - 2):
            first, third = grp.iloc[i], grp.iloc[i + 2]
            span = (third["start"] - first["start"]).days
            if span > window:
                continue
            escalated = (
                third["enc_class"] in ACUTE_CLASSES
                or third["dx_code"] != first["dx_code"]
            )
            if not escalated:
                continue
            for j in (i, i + 1):
                r = grp.iloc[j]
                records.append(
                    {
                        "trigger_id": "T-06",
                        "trigger_name": spec.name,
                        "priority": spec.priority,
                        "fin": r["fin"],
                        "mrn": mrn,
                        "index_date": r["start"],
                        "index_dx": r["dx_code"],
                        "index_role": r["role_of_care"],
                        "index_setting": r["setting"],
                        "event_kind": "THIRD_VISIT",
                        "event_fin": third["fin"],
                        "event_date": third["start"],
                        "event_dx": third["dx_code"],
                        "days_index_to_event": int((third["start"] - r["start"]).days),
                        "look_back_start": first["start"],
                        "reason": (
                            f"Visit {j - i + 1} of >=3 for category {cat3} in {span} days; "
                            f"third visit "
                            + (
                                "escalated to acute care"
                                if third["enc_class"] in ACUTE_CLASSES
                                else f"changed diagnosis to {third['dx_code']}"
                            )
                        ),
                        "evidence": _ev(category=cat3, span_days=span, visits=len(grp)),
                    }
                )
            break  # one firing per patient-category is enough for a worklist
    return _rows(records)


def t07_unplanned_acute(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-07")
    days = 14
    enc = encounters_with_dx(ds)
    acute = enc[enc["enc_class"].isin(ACUTE_CLASSES)]
    if acute.empty:
        return _empty_worklist()
    events = pd.DataFrame(
        {
            "mrn": acute["mrn"],
            "event_date": acute["start"],
            "event_fin": acute["fin"],
            "event_dx": acute["dx_code"],
            "event_class": acute["enc_class"],
        }
    )
    pairs = _lookback(
        enc,
        events,
        days=days,
        event_date_col="event_date",
        index_classes=OUTPATIENT_CLASSES,
        require_related=True,
        min_days=0,
    )
    if pairs.empty:
        return _empty_worklist()
    pairs = pairs[pairs["fin"] != pairs["event_fin"]]
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-07",
        name=spec.name,
        priority=spec.priority,
        event_kind="UNPLANNED_ACUTE",
        days=days,
        reason=lambda r: (
            f"Outpatient encounter {int(r['_delta'])} days before "
            f"{'admission' if r.get('event_class') == 'IMP' else 'ED visit'} for a related complaint"
        ),
    )


def t08_role_escalation(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-08")
    days = 3
    enc = encounters_with_dx(ds)
    higher = enc[
        enc["role_of_care"].isin(["R2", "R3", "MTF", "PURCHASED"])
        | enc["enc_class"].isin(ACUTE_CLASSES)
    ]
    role1 = enc[enc["role_of_care"] == "R1"]
    if higher.empty or role1.empty:
        return _empty_worklist()
    events = pd.DataFrame(
        {
            "mrn": higher["mrn"],
            "event_date": higher["start"],
            "event_fin": higher["fin"],
            "event_dx": higher["dx_code"],
        }
    )
    pairs = _lookback(role1, events, days=days, event_date_col="event_date")
    if pairs.empty:
        return _empty_worklist()
    pairs = pairs[pairs["fin"] != pairs["event_fin"]]
    if pairs.empty:
        return _empty_worklist()
    return _emit(
        pairs,
        tid="T-08",
        name=spec.name,
        priority=spec.priority,
        event_kind="ROLE_ESCALATION",
        days=days,
        reason=lambda r: f"Role 1 encounter escalated to a higher role of care within {int(r['_delta'])} days",
    )


def t09_readmission_diff_dx(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    spec = cat.trigger("T-09")
    days = 30
    enc = encounters_with_dx(ds)
    imp = enc[enc["enc_class"] == "IMP"].sort_values(["mrn", "start"])
    if len(imp) < 2:
        return _empty_worklist()
    records = []
    for mrn, grp in imp.groupby("mrn", sort=False):
        grp = grp.sort_values("start").reset_index(drop=True)
        for i in range(len(grp) - 1):
            a, b = grp.iloc[i], grp.iloc[i + 1]
            gap_from = a["end"] if pd.notna(a["end"]) else a["start"]
            delta = (b["start"] - gap_from).days
            if not (0 <= delta <= days):
                continue
            if category3(a["dx_code"]) == category3(b["dx_code"]):
                continue
            records.append(
                {
                    "trigger_id": "T-09",
                    "trigger_name": spec.name,
                    "priority": spec.priority,
                    "fin": a["fin"],
                    "mrn": mrn,
                    "index_date": a["start"],
                    "index_dx": a["dx_code"],
                    "index_role": a["role_of_care"],
                    "index_setting": a["setting"],
                    "event_kind": "READMIT_DIFF_DX",
                    "event_fin": b["fin"],
                    "event_date": b["start"],
                    "event_dx": b["dx_code"],
                    "days_index_to_event": int((b["start"] - a["start"]).days),
                    "look_back_start": a["start"],
                    "reason": (
                        f"Readmitted {delta} days later with a different principal diagnosis "
                        f"({a['dx_code']} -> {b['dx_code']})"
                    ),
                    "evidence": _ev(gap_days=delta),
                }
            )
    return _rows(records)


def t10_dyad_transitions(
    ds: Dataset, cat: Catalog, *, dyads: list[DyadSpec] | None = None
) -> pd.DataFrame:
    """Nonspecific symptom followed by a target serious condition.

    Run dyad by dyad, never as one query. If a dyad supplies no symptom anchors,
    fall back to the generic nonspecific-code definition and say so in the reason
    string, so the reviewer knows the symptom side was not calibrated.
    """
    spec = cat.trigger("T-10")
    dyads = dyads if dyads is not None else list(cat.dyads.values())
    enc = encounters_with_dx(ds)
    dx = ds.get("diagnoses").dropna(subset=["fin", "code", "date"])
    if enc.empty or dx.empty:
        return _empty_worklist()

    enc_by_fin = enc.set_index("fin")
    records = []

    for dyad in dyads:
        if dyad.window_days <= 0 or not dyad.target_codes:
            continue
        target = dyad.target_set
        symptom = dyad.symptom_set
        calibrated = bool(symptom)

        hits = dx[target.mask(dx["code"])]
        if hits.empty:
            continue
        first_hit = (
            hits.sort_values("date").groupby("mrn", as_index=False).first()
        )

        for _, hit in first_hit.iterrows():
            mrn, tdate = hit["mrn"], hit["date"]
            prior = enc[(enc["mrn"] == mrn) & (enc["start"] < tdate)]
            if prior.empty:
                continue
            delta = (tdate - prior["start"]).dt.days
            prior = prior[delta <= dyad.window_days]
            if prior.empty:
                continue

            codes = prior["dx_code"]
            mask = symptom.mask(codes) if calibrated else NONSPECIFIC.mask(codes)
            mask = mask & ~target.mask(codes.fillna(""))
            cand = prior[mask]
            if cand.empty:
                continue

            index_row = cand.sort_values("start").iloc[0]
            interval = int((tdate - index_row["start"]).days)
            records.append(
                {
                    "trigger_id": "T-10",
                    "trigger_name": f"{spec.name} [{dyad.id}]",
                    "priority": "mandatory" if dyad.review_rule == "mandatory" else spec.priority,
                    "fin": index_row["fin"],
                    "mrn": mrn,
                    "index_date": index_row["start"],
                    "index_dx": index_row["dx_code"],
                    "index_role": index_row["role_of_care"],
                    "index_setting": index_row["setting"],
                    "event_kind": f"DYAD:{dyad.id}",
                    "event_fin": hit["fin"],
                    "event_date": tdate,
                    "event_dx": hit["code"],
                    "days_index_to_event": interval,
                    "look_back_start": index_row["start"],
                    "reason": (
                        f"{dyad.symptom_presentation or 'Nonspecific presentation'} "
                        f"({index_row['dx_code']}) followed {interval} days later by "
                        f"{dyad.target} ({hit['code']})"
                        + ("" if calibrated else " [symptom set NOT locally calibrated]")
                    ),
                    "evidence": _ev(
                        dyad=dyad.id,
                        window_days=dyad.window_days,
                        interval_days=interval,
                        calibrated=calibrated,
                        prior_visits=int(len(cand)),
                    ),
                }
            )
    _ = enc_by_fin  # retained for packet assembly callers
    return _rows(records)


# --------------------------------------------------------------------------
# Tier 3 - disposition anchors
# --------------------------------------------------------------------------


def _disposition_prodrome(
    ds: Dataset,
    cat: Catalog,
    *,
    tid: str,
    kind: str,
    min_prodrome_days: int,
    require_nonspecific: bool,
) -> pd.DataFrame:
    spec = cat.trigger(tid)
    days = spec.look_back or 730
    enc = encounters_with_dx(ds)
    events = _dispositions(ds, kind)
    if enc.empty or events.empty:
        return _empty_worklist()

    records = []
    for _, ev in events.iterrows():
        mrn, edate = ev["mrn"], ev["event_date"]
        prior = enc[(enc["mrn"] == mrn) & (enc["start"] < edate)]
        if prior.empty:
            continue
        prior = prior[(edate - prior["start"]).dt.days <= days]
        if prior.empty:
            continue

        cond = ValueSet([ev["event_dx"]]) if pd.notna(ev.get("event_dx")) else None
        if cond:
            same = prior[
                cond.mask(prior["dx_code"].fillna(""))
                | (prior["dx_cat3"] == category3(ev["event_dx"]))
            ]
            candidates = same if not same.empty else prior
        else:
            candidates = prior

        if require_nonspecific:
            ns = candidates[NONSPECIFIC.mask(candidates["dx_code"].fillna(""))]
            candidates = ns if not ns.empty else candidates

        first = candidates.sort_values("start").iloc[0]
        prodrome = int((edate - first["start"]).days)
        if prodrome < min_prodrome_days:
            continue

        records.append(
            {
                "trigger_id": tid,
                "trigger_name": spec.name,
                "priority": spec.priority,
                "fin": first["fin"],
                "mrn": mrn,
                "index_date": first["start"],
                "index_dx": first["dx_code"],
                "index_role": first["role_of_care"],
                "index_setting": first["setting"],
                "event_kind": kind,
                "event_fin": ev.get("event_fin"),
                "event_date": edate,
                "event_dx": ev.get("event_dx"),
                "days_index_to_event": prodrome,
                "look_back_start": edate - pd.Timedelta(days=days),
                "reason": (
                    f"First documented related encounter {prodrome} days before {kind}"
                    f"; index impression {first['dx_code'] or 'not coded'}"
                ),
                "evidence": _ev(prodrome_days=prodrome, kind=kind),
            }
        )
    return _rows(records)


def t11_limdu_prodrome(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    return _disposition_prodrome(
        ds, cat, tid="T-11", kind="LIMDU", min_prodrome_days=90, require_nonspecific=True
    )


def t12_meb_lookback(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    return _disposition_prodrome(
        ds, cat, tid="T-12", kind="MEB", min_prodrome_days=0, require_nonspecific=False
    )


# --------------------------------------------------------------------------
# Tier 4 - loop closure
# --------------------------------------------------------------------------


def t16_unacknowledged_result(
    ds: Dataset, cat: Catalog, *, as_of: pd.Timestamp | None = None
) -> pd.DataFrame:
    """Abnormal result with no acknowledgment and no downstream action."""
    spec = cat.trigger("T-16")
    days = int(spec.look_fwd_days or 14)
    res = ds.get("results")
    if res.empty:
        return _empty_worklist()
    as_of = as_of or pd.Timestamp.today().normalize()

    abn = res[res["abnormal_flag"].isin(["A", "AA"])].dropna(subset=["resulted_dt"])
    if abn.empty:
        return _empty_worklist()

    # Unacknowledged past the window, and matured enough to judge.
    overdue = abn[
        abn["ack_dt"].isna() & ((as_of - abn["resulted_dt"]).dt.days >= days)
    ].copy()
    if overdue.empty:
        return _empty_worklist()

    # Suppress when a follow-up order or referral was placed inside the window.
    orders = ds.get("orders")
    if not orders.empty:
        follow = orders.dropna(subset=["mrn", "ordered_dt"])[["mrn", "ordered_dt"]]
        merged = overdue.merge(follow, on="mrn", how="left")
        d = (merged["ordered_dt"] - merged["resulted_dt"]).dt.days
        acted = merged[(d > 0) & (d <= days)]["result_id"].unique()
        overdue = overdue[~overdue["result_id"].isin(acted)]
    if overdue.empty:
        return _empty_worklist()

    enc = encounters_with_dx(ds)[["fin", "start", "role_of_care", "setting", "dx_code"]]
    joined = overdue.merge(enc, on="fin", how="left")

    records = []
    for _, r in joined.iterrows():
        age = int((as_of - r["resulted_dt"]).days)
        records.append(
            {
                "trigger_id": "T-16",
                "trigger_name": spec.name,
                "priority": spec.priority,
                "fin": r["fin"],
                "mrn": r["mrn"],
                "index_date": r.get("start"),
                "index_dx": r.get("dx_code"),
                "index_role": r.get("role_of_care"),
                "index_setting": r.get("setting"),
                "event_kind": "RESULT_UNACKNOWLEDGED",
                "event_fin": r["fin"],
                "event_date": r["resulted_dt"],
                "event_dx": r.get("code"),
                "days_index_to_event": age,
                "look_back_start": r.get("start"),
                "reason": (
                    f"{'Critical' if r['abnormal_flag'] == 'AA' else 'Abnormal'} result "
                    f"unacknowledged with no follow-up order for {age} days"
                ),
                "evidence": _ev(
                    result_code=r.get("code"),
                    flag=r.get("abnormal_flag"),
                    days_open=age,
                    threshold=days,
                ),
            }
        )
    return _rows(records)


def t17_open_referral(
    ds: Dataset, cat: Catalog, *, as_of: pd.Timestamp | None = None
) -> pd.DataFrame:
    spec = cat.trigger("T-17")
    days = int(spec.look_fwd_days or 60)
    ref = ds.get("referrals")
    if ref.empty:
        return _empty_worklist()
    as_of = as_of or pd.Timestamp.today().normalize()

    open_ref = ref[
        ref["completed_dt"].isna()
        & (ref["status"].astype("object") != "CANCELLED")
        & ((as_of - ref["ordered_dt"]).dt.days >= days)
    ].copy()
    if open_ref.empty:
        return _empty_worklist()

    enc = encounters_with_dx(ds)[["fin", "start", "role_of_care", "setting", "dx_code"]]
    joined = open_ref.merge(enc, on="fin", how="left")

    records = []
    for _, r in joined.iterrows():
        age = int((as_of - r["ordered_dt"]).days)
        records.append(
            {
                "trigger_id": "T-17",
                "trigger_name": spec.name,
                "priority": spec.priority,
                "fin": r["fin"],
                "mrn": r["mrn"],
                "index_date": r.get("start"),
                "index_dx": r.get("dx_code"),
                "index_role": r.get("role_of_care"),
                "index_setting": r.get("setting"),
                "event_kind": "REFERRAL_OPEN",
                "event_fin": r["fin"],
                "event_date": r["ordered_dt"],
                "event_dx": r.get("dx_code"),
                "days_index_to_event": age,
                "look_back_start": r.get("start"),
                "reason": (
                    f"{r.get('specialty') or 'Specialty'} referral open {age} days "
                    f"with no completed encounter"
                ),
                "evidence": _ev(specialty=r.get("specialty"), days_open=age, threshold=days),
            }
        )
    return _rows(records)


def t19_pending_at_movement(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    """Order or referral still open when the Marine's unit moved.

    No civilian analog and no published base rate. Measure the fire rate before
    trusting it.
    """
    spec = cat.trigger("T-19")
    orders, moves, enc = ds.get("orders"), ds.get("unit_movements"), ds.get("encounters")
    if orders.empty or moves.empty or enc.empty:
        return _empty_worklist()

    unit = enc.dropna(subset=["mrn", "unit_id"])[["mrn", "unit_id"]].drop_duplicates("mrn")
    o = orders[orders["status"].astype("object") == "ORDERED"].dropna(subset=["ordered_dt"])
    if o.empty:
        return _empty_worklist()
    o = o.merge(unit, on="mrn", how="inner")
    if o.empty:
        return _empty_worklist()

    m = moves.dropna(subset=["unit_id", "start_date"])
    joined = o.merge(m, on="unit_id", how="inner", suffixes=("", "_mv"))
    joined = joined[joined["ordered_dt"] < joined["start_date"]]
    if joined.empty:
        return _empty_worklist()

    encd = encounters_with_dx(ds)[["fin", "start", "role_of_care", "setting", "dx_code"]]
    joined = joined.merge(encd, on="fin", how="left")

    records = []
    for _, r in joined.iterrows():
        lead = int((r["start_date"] - r["ordered_dt"]).days)
        records.append(
            {
                "trigger_id": "T-19",
                "trigger_name": spec.name,
                "priority": spec.priority,
                "fin": r["fin"],
                "mrn": r["mrn"],
                "index_date": r.get("start"),
                "index_dx": r.get("dx_code"),
                "index_role": r.get("role_of_care"),
                "index_setting": r.get("setting"),
                "event_kind": f"MOVEMENT:{r['kind']}",
                "event_fin": r["fin"],
                "event_date": r["start_date"],
                "event_dx": None,
                "days_index_to_event": lead,
                "look_back_start": r["ordered_dt"],
                "reason": (
                    f"{r.get('category') or 'Order'} placed {lead} days before unit "
                    f"{str(r['kind']).lower()} and still open at movement"
                ),
                "evidence": _ev(
                    order_category=r.get("category"),
                    movement=r.get("kind"),
                    lead_days=lead,
                ),
            }
        )
    return _rows(records)


def t20_orphan_result(ds: Dataset, cat: Catalog) -> pd.DataFrame:
    """Result returned after the ordering provider's assignment ended."""
    spec = cat.trigger("T-20")
    res, orders, assign = ds.get("results"), ds.get("orders"), ds.get("provider_assignments")
    if res.empty or orders.empty or assign.empty:
        return _empty_worklist()

    o = orders[["order_id", "provider_id", "category"]].dropna(subset=["order_id"])
    joined = res.merge(o, on="order_id", how="inner", suffixes=("", "_ord"))
    prov = joined["provider_id_ord"] if "provider_id_ord" in joined.columns else joined["provider_id"]
    joined = joined.assign(order_provider=prov)

    a = assign.dropna(subset=["provider_id", "end_date"])[["provider_id", "end_date"]]
    a = a.groupby("provider_id", as_index=False)["end_date"].max()
    joined = joined.merge(
        a, left_on="order_provider", right_on="provider_id", how="inner", suffixes=("", "_a")
    )
    joined = joined[joined["resulted_dt"] > joined["end_date"]]
    joined = joined[joined["ack_dt"].isna()]
    if joined.empty:
        return _empty_worklist()

    encd = encounters_with_dx(ds)[["fin", "start", "role_of_care", "setting", "dx_code"]]
    joined = joined.merge(encd, on="fin", how="left")

    records = []
    for _, r in joined.iterrows():
        gap = int((r["resulted_dt"] - r["end_date"]).days)
        records.append(
            {
                "trigger_id": "T-20",
                "trigger_name": spec.name,
                "priority": spec.priority,
                "fin": r["fin"],
                "mrn": r["mrn"],
                "index_date": r.get("start"),
                "index_dx": r.get("dx_code"),
                "index_role": r.get("role_of_care"),
                "index_setting": r.get("setting"),
                "event_kind": "ORPHANED_RESULT",
                "event_fin": r["fin"],
                "event_date": r["resulted_dt"],
                "event_dx": r.get("code"),
                "days_index_to_event": gap,
                "look_back_start": r.get("start"),
                "reason": (
                    f"Result returned {gap} days after the ordering provider's assignment "
                    f"ended, with no acknowledgment"
                ),
                "evidence": _ev(days_after_detachment=gap, flag=r.get("abnormal_flag")),
            }
        )
    return _rows(records)


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

RULES: dict[str, Callable[[Dataset, Catalog], pd.DataFrame]] = {
    "T-01": t01_death_lookback,
    "T-02": t02_icu_escalation,
    "T-03": t03_medevac,
    "T-05": t05_emergency_surgery,
    "T-06": t06_rule_of_three,
    "T-07": t07_unplanned_acute,
    "T-08": t08_role_escalation,
    "T-09": t09_readmission_diff_dx,
    "T-10": t10_dyad_transitions,
    "T-11": t11_limdu_prodrome,
    "T-12": t12_meb_lookback,
    "T-16": t16_unacknowledged_result,
    "T-17": t17_open_referral,
    "T-19": t19_pending_at_movement,
    "T-20": t20_orphan_result,
}

# Tier 5 triggers (T-21..T-24) are solicited or cross-referred reports, not
# computed. Ingest them as a CSV and concatenate onto the worklist.
MANUAL_TRIGGERS = ("T-04", "T-13", "T-14", "T-15", "T-18", "T-21", "T-22", "T-23", "T-24")


def run(
    ds: Dataset,
    cat: Catalog,
    *,
    only: list[str] | None = None,
    logger=None,
) -> pd.DataFrame:
    """Run the rule set and return a combined FIN-keyed worklist."""
    selected = only or list(RULES)
    frames = []
    for tid in selected:
        rule = RULES.get(tid)
        if rule is None:
            if logger:
                logger.warning("no implementation for %s (manual or unimplemented)", tid)
            continue
        try:
            out = rule(ds, cat)
        except Exception as exc:  # keep one bad rule from killing the run
            if logger:
                logger.error("rule %s failed: %s", tid, type(exc).__name__)
            continue
        if not out.empty:
            frames.append(out)
        if logger:
            logger.info("%s fired %d rows", tid, len(out))

    if not frames:
        return _empty_worklist()
    return pd.concat(frames, ignore_index=True)
