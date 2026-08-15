"""End-to-end and rule-level tests against synthetic data with known ground truth."""

from __future__ import annotations

import pandas as pd
import pytest

from mdxg import metrics as M
from mdxg import phi, triggers, worklist
from mdxg.catalog import load_catalog
from mdxg.episode import build_packet
from mdxg.model import Dataset, coerce, validate
from mdxg.synth import SyntheticBuilder, build_demo
from mdxg.valuesets import ValueSet, calibrate_symptom_set, is_nonspecific, normalize


@pytest.fixture(scope="module")
def cat():
    return load_catalog()


@pytest.fixture(scope="module")
def demo():
    return build_demo()


# --------------------------------------------------------------------------
# catalog
# --------------------------------------------------------------------------


def test_catalog_loads_full_specification(cat):
    assert len(cat.triggers) == 24
    assert len(cat.dyads) == 24
    assert cat.trigger("T-01").priority == "mandatory"
    assert cat.dyads["D-A01"].window_days == 7


def test_every_implemented_rule_has_a_catalog_entry(cat):
    missing = [tid for tid in triggers.RULES if tid not in cat.triggers]
    assert not missing, f"rules with no catalog spec: {missing}"


def test_catalog_triggers_are_implemented_or_declared_manual(cat):
    unaccounted = [
        tid
        for tid in cat.triggers
        if tid not in triggers.RULES and tid not in triggers.MANUAL_TRIGGERS
    ]
    assert not unaccounted, f"triggers neither implemented nor declared manual: {unaccounted}"


# --------------------------------------------------------------------------
# value sets
# --------------------------------------------------------------------------


def test_normalize_strips_decimal_and_case():
    assert normalize("n44.00") == "N4400"
    assert normalize(" m54.50 ") == "M5450"
    assert normalize(None) is None


def test_valueset_is_prefix_matched():
    vs = ValueSet(["R10", "N44.00"])
    assert vs.matches("R10.31")
    assert vs.matches("N44.00")
    assert not vs.matches("N44.03")
    assert not vs.matches("K35.20")


def test_nonspecific_recognizes_symptom_codes_not_diagnoses():
    assert is_nonspecific("R10.9")
    assert is_nonspecific("M54.50")
    assert not is_nonspecific("K35.20")
    assert not is_nonspecific("C62.90")


def test_valueset_mask_handles_nulls():
    vs = ValueSet(["R10"])
    s = pd.Series(["R10.9", None, "K35.20"])
    assert list(vs.mask(s)) == [True, False, False]


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------


def test_coerce_adds_missing_columns_and_types():
    df = coerce("encounters", pd.DataFrame({"fin": ["F1"], "mrn": ["M1"], "start": ["2024-01-01"]}))
    assert "role_of_care" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["start"])


def test_validate_flags_duplicate_fins():
    ds = Dataset(
        tables={
            "encounters": coerce(
                "encounters",
                pd.DataFrame({"fin": ["F1", "F1"], "mrn": ["M1", "M1"], "start": ["2024-01-01"] * 2}),
            ),
            "diagnoses": coerce("diagnoses", pd.DataFrame({"fin": ["F1"], "code": ["R10.9"]})),
        }
    )
    assert any("duplicate fin" in p for p in validate(ds))


def test_validate_flags_orphan_diagnoses():
    ds = Dataset(
        tables={
            "encounters": coerce(
                "encounters", pd.DataFrame({"fin": ["F1"], "mrn": ["M1"], "start": ["2024-01-01"]})
            ),
            "diagnoses": coerce("diagnoses", pd.DataFrame({"fin": ["F9"], "code": ["R10.9"]})),
        }
    )
    assert any("unknown fin" in p for p in validate(ds))


# --------------------------------------------------------------------------
# triggers: ground truth recall
# --------------------------------------------------------------------------


def test_all_planted_cases_are_recovered(demo, cat):
    wl = triggers.run(demo, cat)
    flagged = set(wl["fin"])
    misses = {
        tid: [f for f in fins if f not in flagged]
        for tid, fins in demo.planted.items()
    }
    misses = {k: v for k, v in misses.items() if v}
    assert not misses, f"planted cases not recovered: {misses}"


def test_worklist_is_keyed_on_the_index_encounter_not_the_event(demo, cat):
    """The FIN on a row must be the note to review, not the downstream event."""
    wl = triggers.t05_emergency_surgery(demo, cat)
    assert not wl.empty
    row = wl.iloc[0]
    assert row["fin"] != row["event_fin"]
    assert row["index_date"] < row["event_date"]


def test_specificity_is_not_catastrophic(demo, cat):
    """Background noise must not flag a large share of encounters."""
    wl = triggers.run(demo, cat)
    rate = worklist.by_fin(wl).shape[0] / len(demo.encounters)
    assert rate < 0.05, f"{rate:.1%} of encounters flagged - triggers are too loose"


def test_rule_of_three_requires_three_visits_in_window():
    b = SyntheticBuilder()
    b._roster("M1")
    b.encounter("M1", 0, "R10.9")
    b.encounter("M1", 5, "R10.31")  # only two visits
    ds = b.build()
    assert triggers.t06_rule_of_three(ds, load_catalog()).empty


def test_rule_of_three_ignores_visits_outside_window():
    b = SyntheticBuilder()
    b._roster("M1")
    b.encounter("M1", 0, "R10.9")
    b.encounter("M1", 5, "R10.31")
    b.encounter("M1", 400, "R10.32", enc_class="EMER")  # far outside 30d
    ds = b.build()
    assert triggers.t06_rule_of_three(ds, load_catalog()).empty


def test_dyad_respects_the_look_forward_window():
    """Torsion 60 days after groin pain is outside the 7-day window."""
    b = SyntheticBuilder()
    b._roster("M1")
    b.encounter("M1", 0, "R10.2")
    b.encounter("M1", 60, "N44.00", enc_class="EMER")
    ds = b.build()
    cat = load_catalog()
    out = triggers.t10_dyad_transitions(ds, cat, dyads=[cat.dyads["D-A01"]])
    assert out.empty


def test_dyad_fires_inside_the_window():
    b = SyntheticBuilder()
    b._roster("M1")
    b.encounter("M1", 0, "R10.2")
    b.encounter("M1", 4, "N44.00", enc_class="EMER")
    ds = b.build()
    cat = load_catalog()
    out = triggers.t10_dyad_transitions(ds, cat, dyads=[cat.dyads["D-A01"]])
    assert len(out) == 1
    assert out.iloc[0]["days_index_to_event"] == 4


def test_uncalibrated_dyad_is_marked_in_the_reason(demo, cat):
    out = triggers.t10_dyad_transitions(demo, cat, dyads=[cat.dyads["D-B01"]])
    assert not out.empty
    # D-B01 supplies no symptom_codes_anchor, so the reviewer must be told.
    assert "NOT locally calibrated" in out.iloc[0]["reason"]


def test_acknowledged_result_does_not_fire():
    b = SyntheticBuilder()
    b.plant_unacked_result(day=100)
    ds = b.build()
    ds.tables["results"].loc[0, "ack_dt"] = ds.tables["results"].loc[0, "resulted_dt"]
    out = triggers.t16_unacknowledged_result(ds, load_catalog(), as_of=pd.Timestamp("2025-06-01"))
    assert out.empty


def test_result_within_window_is_not_yet_overdue():
    b = SyntheticBuilder()
    b.plant_unacked_result(day=100)
    ds = b.build()
    resulted = ds.tables["results"].loc[0, "resulted_dt"]
    out = triggers.t16_unacknowledged_result(
        ds, load_catalog(), as_of=resulted + pd.Timedelta(days=3)
    )
    assert out.empty


def test_followup_order_suppresses_the_result_trigger():
    b = SyntheticBuilder()
    b.plant_unacked_result(day=100)
    ds = b.build()
    resulted = ds.tables["results"].loc[0, "resulted_dt"]
    ds.tables["orders"] = coerce(
        "orders",
        pd.concat(
            [
                ds.tables["orders"],
                pd.DataFrame(
                    [
                        {
                            "order_id": "O2", "fin": "F0000001", "mrn": "M900008",
                            "category": "LAB", "code": "x", "name": "repeat",
                            "ordered_dt": resulted + pd.Timedelta(days=2),
                            "status": "ORDERED", "provider_id": "P1",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        ),
    )
    out = triggers.t16_unacknowledged_result(ds, load_catalog(), as_of=pd.Timestamp("2025-06-01"))
    assert out.empty


def test_completed_referral_does_not_fire():
    b = SyntheticBuilder()
    b.plant_open_referral(day=100)
    ds = b.build()
    ds.tables["referrals"].loc[0, "completed_dt"] = ds.tables["referrals"].loc[0, "ordered_dt"] + pd.Timedelta(days=20)
    out = triggers.t17_open_referral(ds, load_catalog(), as_of=pd.Timestamp("2025-06-01"))
    assert out.empty


def test_rules_survive_completely_empty_input(cat):
    ds = Dataset(tables={})
    out = triggers.run(ds, cat)
    assert out.empty
    assert list(out.columns) == triggers.WORKLIST_COLUMNS


# --------------------------------------------------------------------------
# worklist
# --------------------------------------------------------------------------


def test_by_fin_collapses_to_one_row_per_fin(demo, cat):
    wl = triggers.run(demo, cat)
    bf = worklist.by_fin(wl)
    assert bf["fin"].is_unique
    assert bf["review_score"].is_monotonic_decreasing


def test_multi_trigger_fin_outranks_single_trigger_fin(demo, cat):
    bf = worklist.by_fin(triggers.run(demo, cat))
    multi = bf[bf["n_triggers"] > 1]
    assert not multi.empty
    # Among equal top priority, more triggers must score higher.
    for prio, g in bf.groupby("top_priority"):
        if g["n_triggers"].nunique() > 1:
            assert g.sort_values("n_triggers")["review_score"].is_monotonic_increasing


def test_control_arm_excludes_triggered_fins(demo, cat):
    wl = triggers.run(demo, cat)
    ctrl = worklist.random_control_arm(demo.encounters, n=30, exclude_fins=set(wl["fin"]))
    assert len(ctrl) == 30
    assert not set(ctrl["fin"]) & set(wl["fin"])


def test_sampling_records_what_it_dropped(demo, cat):
    wl = triggers.run(demo, cat)
    sampled = worklist.apply_sampling(wl, cat)
    assert "sampling" in sampled.attrs


# --------------------------------------------------------------------------
# episode packets
# --------------------------------------------------------------------------


def test_packet_contains_the_full_episode(demo, cat):
    wl = triggers.run(demo, cat)
    fin = wl.iloc[0]["fin"]
    packet = build_packet(demo, fin, look_back_days=180)
    assert packet.complete
    assert fin in set(packet.encounters["fin"])
    assert len(packet.encounters) >= 1
    text = packet.to_text()
    assert "<== INDEX" in text
    assert "Revised Safer Dx Instrument" in text


def test_packet_rejects_unknown_fin(demo):
    with pytest.raises(KeyError):
        build_packet(demo, "NOPE")


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------


def test_interval_summary_reports_medians(demo, cat):
    iv = M.interval_summary(demo, cat)
    hit = iv[iv["dyad"] == "D-A01"].iloc[0]
    assert hit["n"] == 1
    assert hit["median_days"] == 4.0


def test_wilson_interval_brackets_the_point_estimate():
    p = M.Proportion(224, 703)  # the published Measure Dx figure
    lo, hi = p.wilson()
    assert lo < p.value < hi
    assert round(p.value, 3) == 0.319


def test_wilson_handles_zero_denominator():
    assert M.Proportion(0, 0).wilson() is None
    assert M.Proportion(0, 0).value is None


def _adjudications(demo, cat):
    wl = triggers.run(demo, cat)
    rows = [
        {"fin": f, "arm": "TRIGGERED", "safer_dx_item13": 6 if i % 3 == 0 else 2,
         "ncc_merp": "E", "duty_days_lost": 14, "deployability_affected": i % 3 == 0,
         "primary_factor": "delay_in_presentation"}
        for i, f in enumerate(wl["fin"].unique())
    ]
    ctrl = worklist.random_control_arm(demo.encounters, n=40, exclude_fins=set(wl["fin"]))
    rows += [
        {"fin": f, "arm": "RANDOM_CONTROL", "safer_dx_item13": 1,
         "ncc_merp": "A", "duty_days_lost": 0, "deployability_affected": False,
         "primary_factor": None}
        for f in ctrl["fin"]
    ]
    return pd.DataFrame(rows), wl


def test_mod_yield_uses_the_item13_threshold(demo, cat):
    adj, wl = _adjudications(demo, cat)
    y = M.mod_yield(adj[adj["arm"] == "TRIGGERED"], wl)
    assert not y.empty
    assert (y["yield"] <= 1).all()
    assert (y["confirmed"] <= y["adjudicated"]).all()


def test_ppv_lift_requires_a_control_arm(demo, cat):
    adj, wl = _adjudications(demo, cat)
    assert M.ppv_lift(adj[adj["arm"] == "TRIGGERED"], wl).empty
    assert not M.ppv_lift(adj, wl).empty


def test_retirement_rule_needs_forty_cases():
    y = pd.DataFrame(
        [
            {"trigger_id": "T-A", "adjudicated": 10, "confirmed": 0, "yield": 0.0},
            {"trigger_id": "T-B", "adjudicated": 50, "confirmed": 1, "yield": 0.02},
            {"trigger_id": "T-C", "adjudicated": 50, "confirmed": 20, "yield": 0.40},
        ]
    )
    out = M.retirement_check(y).set_index("trigger_id")["decision"]
    assert out["T-A"] == "retain"  # too few cases to judge
    assert out["T-B"] == "retire_or_retune"
    assert out["T-C"] == "retain"


def test_detection_density_prefers_the_roster_denominator(demo, cat):
    adj, _ = _adjudications(demo, cat)
    d = M.detection_density(adj, demo).iloc[0]
    assert d["denominator_source"] == "roster"
    assert d["per_1k_marines_year"] is not None


def test_coverage_pairs_fired_with_adjudicated(demo, cat):
    adj, wl = _adjudications(demo, cat)
    cov = M.coverage(wl, adj)
    assert set(cov.columns) >= {"trigger_id", "fired", "adjudicated", "coverage"}
    assert (cov["coverage"] <= 1.0).all()


def test_loop_closure_needs_no_adjudication(demo):
    lc = M.loop_closure_rates(demo)
    assert set(lc["measure"]) == {"abnormal_result_unacknowledged", "referral_not_completed"}


# --------------------------------------------------------------------------
# PHI
# --------------------------------------------------------------------------


def test_pseudonyms_are_stable_and_salt_dependent():
    a = phi.pseudonymize(["M0001"], b"salt-one-that-is-long")
    b = phi.pseudonymize(["M0001"], b"salt-one-that-is-long")
    c = phi.pseudonymize(["M0001"], b"a-different-long-salt")
    assert a[0] == b[0]
    assert a[0] != c[0]
    assert "M0001" not in str(a[0])


def test_deidentify_removes_identifiers_and_free_text(demo, cat):
    wl = triggers.run(demo, cat)
    out = phi.deidentify(wl, b"a-sufficiently-long-salt")
    assert not set(out["fin"]) & set(wl["fin"])
    assert "value_text" not in out.columns


def test_missing_salt_is_an_error_not_a_default(monkeypatch):
    monkeypatch.delenv("MDXG_SALT", raising=False)
    with pytest.raises(phi.MissingSaltError):
        phi.get_salt()
    with pytest.raises(phi.MissingSaltError):
        phi.get_salt("short")


def test_small_cell_suppression():
    df = pd.DataFrame({"group": ["a", "b"], "n": [5, 40]})
    out = phi.suppress_small_cells(df, ["n"])
    assert out.loc[0, "n"] == "<11"
    assert out.loc[1, "n"] == 40


def test_log_filter_blocks_identifier_like_strings(caplog):
    logger = phi.configure_logging()
    handler = logger.handlers[0]
    rec = pd.NA  # placeholder to keep linters quiet
    import logging

    record = logging.LogRecord("mdxg", logging.INFO, __file__, 1, "patient 123456789 flagged", None, None)
    for f in handler.filters:
        f.filter(record)
    assert "123456789" not in record.getMessage()
    assert rec is pd.NA


# --------------------------------------------------------------------------
# calibration
# --------------------------------------------------------------------------


def test_calibration_surfaces_the_planted_symptom_category(cat):
    b = SyntheticBuilder()
    b.background(n_marines=60)
    for i in range(12):
        mrn = f"C{i:04d}"
        b._roster(mrn)
        b.encounter(mrn, 100, "M79.605")
        b.encounter(mrn, 150, "M84.359A")
    ds = b.build()
    table = calibrate_symptom_set(
        ds.get("diagnoses"), cat.dyads["D-B01"].target_set, window_days=90, min_support=3
    )
    assert not table.empty
    assert "M79" in set(table["category"])
