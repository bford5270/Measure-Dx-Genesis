"""Command line interface.

    mdxg demo                       run end-to-end on synthetic data
    mdxg init-mapping mapping.yaml  write a source mapping template
    mdxg run --mapping m.yaml --data ./extracts --out ./out
    mdxg packet --fin F0001234 --mapping m.yaml --data ./extracts
    mdxg calibrate --dyad D-B01 --mapping m.yaml --data ./extracts
    mdxg metrics --adjudications adj.csv --worklist out/worklist_detail.csv ...

Output separation is deliberate:
    out/review/    contains FINs. This is PHI. Restrict it.
    out/analysis/  pseudonymized and small-cell suppressed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import metrics as M
from . import phi, triggers, worklist
from .adapters import extract
from .catalog import load_catalog
from .episode import build_packet
from .model import Dataset, validate
from .valuesets import calibrate_symptom_set

BANNER = """\
mdxg - diagnostic safety case finding
A trigger firing is a QUESTION, not a finding. Adjudication is a clinician task
using the Revised Safer Dx Instrument. Nothing here writes to the source system.
"""


def _load(args, logger) -> Dataset:
    if getattr(args, "demo", False) or not getattr(args, "mapping", None):
        from .synth import build_demo

        logger.info("using synthetic demo data (no source access)")
        return build_demo()
    return extract.load(args.mapping, args.data, logger=logger)


def _write(df: pd.DataFrame, path: Path, logger) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("wrote %s (%d rows)", path.name, len(df))


def cmd_demo(args) -> int:
    logger = phi.configure_logging()
    print(BANNER)
    from .synth import build_demo

    ds = build_demo()
    cat = load_catalog(args.catalog)

    problems = validate(ds)
    if problems:
        for p in problems:
            logger.warning("validation: %s", p)

    wl = triggers.run(ds, cat, logger=logger)
    detail = worklist.rank_detail(wl)
    by_fin = worklist.by_fin(wl)

    print(f"\nEncounters scanned: {len(ds.encounters):,}")
    print(f"Trigger firings:    {len(detail):,}")
    print(f"Distinct FINs flagged: {len(by_fin):,} "
          f"({100 * len(by_fin) / max(len(ds.encounters), 1):.1f}% of encounters)\n")

    if not detail.empty:
        print("Firings by trigger:")
        counts = detail.groupby(["trigger_id", "trigger_name"]).size()
        for (tid, name), n in counts.items():
            print(f"  {tid}  {n:5d}  {name[:52]}")

    print("\nTop of the review worklist (by FIN):")
    cols = ["fin", "index_date", "index_dx", "top_priority", "n_triggers", "triggers", "review_score"]
    if not by_fin.empty:
        show = by_fin[cols].head(12).copy()
        show["index_date"] = pd.to_datetime(show["index_date"]).dt.date
        print(show.to_string(index=False))

    planted = getattr(ds, "planted", {})
    if planted:
        print("\nRecall against planted cases:")
        flagged = set(detail["fin"])
        for tid, fins in sorted(planted.items()):
            hit = sum(1 for f in fins if f in flagged)
            mark = "OK " if hit == len(fins) else "MISS"
            print(f"  {mark} {tid}: {hit}/{len(fins)}")

    iv = M.interval_summary(ds, cat)
    iv = iv[iv["n"] > 0]
    if not iv.empty:
        print("\nSymptom-to-diagnosis interval (synthetic):")
        print(iv.to_string(index=False))

    lc = M.loop_closure_rates(ds)
    if not lc.empty:
        print("\nLoop closure:")
        print(lc.to_string(index=False))

    if args.out:
        out = Path(args.out)
        _write(detail, out / "review" / "worklist_detail.csv", logger)
        _write(by_fin, out / "review" / "worklist_by_fin.csv", logger)
    return 0


def cmd_init_mapping(args) -> int:
    p = extract.write_template(args.path)
    print(f"wrote mapping template: {p}")
    print("Edit the right-hand column names to match your extract, then:")
    print(f"  mdxg run --mapping {p} --data ./extracts --out ./out")
    return 0


def cmd_run(args) -> int:
    logger = phi.configure_logging()
    cat = load_catalog(args.catalog)
    ds = _load(args, logger)

    problems = validate(ds)
    for p in problems:
        logger.warning("validation: %s", p)
    if any("required table missing" in p for p in problems):
        logger.error("cannot proceed without encounters and diagnoses")
        return 2

    only = args.triggers.split(",") if args.triggers else None
    wl = triggers.run(ds, cat, only=only, logger=logger)
    if args.sample:
        wl = worklist.apply_sampling(wl, cat)
        for tid, n in (wl.attrs.get("sampling") or {}).items():
            logger.info("sampling dropped %d rows from %s", n, tid)

    detail = worklist.rank_detail(wl)
    by_fin = worklist.by_fin(wl)
    out = Path(args.out)

    _write(detail, out / "review" / "worklist_detail.csv", logger)
    _write(by_fin, out / "review" / "worklist_by_fin.csv", logger)

    if args.control_arm:
        ctrl = worklist.random_control_arm(
            ds.encounters, n=args.control_arm, exclude_fins=set(detail["fin"])
        )
        _write(ctrl, out / "review" / "control_arm.csv", logger)

    # Analysis-side artifacts are pseudonymized.
    try:
        salt = phi.get_salt(args.salt)
        _write(phi.deidentify(detail, salt), out / "analysis" / "worklist_deid.csv", logger)
    except phi.MissingSaltError as exc:
        logger.warning("skipping de-identified output: %s", exc)

    _write(M.interval_summary(ds, cat), out / "analysis" / "intervals.csv", logger)
    _write(M.loop_closure_rates(ds), out / "analysis" / "loop_closure.csv", logger)

    print(f"\n{len(by_fin)} FINs flagged for review from {len(ds.encounters)} encounters.")
    print(f"Review worklist: {out / 'review' / 'worklist_by_fin.csv'}")
    print("out/review contains FINs and is PHI. Restrict access accordingly.")
    return 0


def cmd_packet(args) -> int:
    logger = phi.configure_logging()
    ds = _load(args, logger)
    packet = build_packet(ds, args.fin, look_back_days=args.look_back)
    text = packet.to_text()
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        logger.info("wrote packet to %s", p.name)
    else:
        print(text)
    if not packet.complete:
        print("\nWARNING: packet incomplete - defer rather than adjudicate on a fragment.")
    return 0


def cmd_calibrate(args) -> int:
    logger = phi.configure_logging()
    cat = load_catalog(args.catalog)
    ds = _load(args, logger)
    dyad = cat.dyads.get(args.dyad)
    if dyad is None:
        logger.error("unknown dyad %s", args.dyad)
        return 2
    table = calibrate_symptom_set(
        ds.get("diagnoses"), dyad.target_set,
        window_days=dyad.window_days, min_support=args.min_support,
    )
    print(f"\nObserved symptom categories preceding {dyad.target} ({dyad.id}), "
          f"window {dyad.window_days}d:\n")
    print(table.to_string(index=False) if not table.empty else "  no support found")
    print("\nUse this to replace symptom_codes_anchor in catalog/dyads.yaml.")
    if args.out:
        _write(table, Path(args.out), logger)
    return 0


def cmd_metrics(args) -> int:
    logger = phi.configure_logging()
    cat = load_catalog(args.catalog)
    ds = _load(args, logger)
    adj = pd.read_csv(args.adjudications) if args.adjudications else pd.DataFrame()
    wl = pd.read_csv(args.worklist) if args.worklist else pd.DataFrame()
    out = Path(args.out)

    _write(M.coverage(wl, adj), out / "analysis" / "coverage.csv", logger)
    y = M.mod_yield(adj, wl)
    _write(y, out / "analysis" / "mod_yield.csv", logger)
    _write(M.retirement_check(y), out / "analysis" / "retirement.csv", logger)
    _write(M.ppv_lift(adj, wl), out / "analysis" / "ppv_lift.csv", logger)
    _write(M.detection_density(adj, ds), out / "analysis" / "detection_density.csv", logger)
    _write(M.harm_and_duty_profile(adj), out / "analysis" / "harm_profile.csv", logger)
    _write(M.interval_summary(ds, cat), out / "analysis" / "intervals.csv", logger)

    if not y.empty:
        print("\nYield by trigger:")
        print(y.to_string(index=False))
    lift = M.ppv_lift(adj, wl)
    if lift.empty:
        print("\nNo PPV lift computed: no RANDOM_CONTROL rows in the adjudications.")
        print("The control arm is what makes the lift claim defensible. See docs/05-metrics.md.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mdxg", description="Diagnostic safety case finding")
    p.add_argument("--catalog", default=None, help="catalog directory (default: repo catalog/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="run end-to-end on synthetic data")
    d.add_argument("--out", default=None)
    d.set_defaults(func=cmd_demo)

    im = sub.add_parser("init-mapping", help="write a source mapping template")
    im.add_argument("path")
    im.set_defaults(func=cmd_init_mapping)

    r = sub.add_parser("run", help="run triggers and write the worklist")
    r.add_argument("--mapping")
    r.add_argument("--data", default=".")
    r.add_argument("--out", default="./out")
    r.add_argument("--triggers", help="comma-separated trigger ids, e.g. T-06,T-07")
    r.add_argument("--sample", action="store_true", help="apply catalog sample rates")
    r.add_argument("--control-arm", type=int, default=0, help="draw N random control charts")
    r.add_argument("--salt", default=None, help="override MDXG_SALT")
    r.add_argument("--demo", action="store_true")
    r.set_defaults(func=cmd_run)

    k = sub.add_parser("packet", help="assemble an episode packet for one FIN")
    k.add_argument("--fin", required=True)
    k.add_argument("--mapping")
    k.add_argument("--data", default=".")
    k.add_argument("--look-back", type=int, default=180)
    k.add_argument("--out")
    k.add_argument("--demo", action="store_true")
    k.set_defaults(func=cmd_packet)

    c = sub.add_parser("calibrate", help="derive a symptom value set from observed data")
    c.add_argument("--dyad", required=True)
    c.add_argument("--mapping")
    c.add_argument("--data", default=".")
    c.add_argument("--min-support", type=int, default=5)
    c.add_argument("--out")
    c.add_argument("--demo", action="store_true")
    c.set_defaults(func=cmd_calibrate)

    m = sub.add_parser("metrics", help="compute metrics from adjudications")
    m.add_argument("--adjudications", required=True)
    m.add_argument("--worklist")
    m.add_argument("--mapping")
    m.add_argument("--data", default=".")
    m.add_argument("--out", default="./out")
    m.add_argument("--demo", action="store_true")
    m.set_defaults(func=cmd_metrics)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
