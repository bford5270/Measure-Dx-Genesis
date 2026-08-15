# Measure Dx — Genesis

Adapting AHRQ's **Measure Dx** construct into a signal-driven diagnostic safety and peer
review program for **U.S. Marine Corps operational forces**, using MHS GENESIS and
adjacent DoD data.

**Problem.** Health care quality assurance in the operating forces leans on random
sampling of clinical records. In a young, healthy, high-denominator population, random
review has a near-zero probability of finding the events that actually harm Marines and
cost readiness. It measures documentation, not diagnosis.

**Proposal.** Keep peer review. Change how cases are *selected*. Replace most random
sampling with a catalog of **operational-forces-specific electronic triggers and
symptom–disease dyads** that concentrate review capacity on episodes with a materially
elevated probability of a missed diagnostic opportunity — and build the metric layer
that Measure Dx deliberately does not supply.

---

## Start here

| Document | What it covers |
|---|---|
| [`docs/00-executive-summary.md`](docs/00-executive-summary.md) | Two-page version for a Force Surgeon / MEF brief |
| [`docs/01-why-random-review-fails.md`](docs/01-why-random-review-fails.md) | The arithmetic of random sampling, and why the unit of analysis is wrong |
| [`docs/02-measure-dx-construct-review.md`](docs/02-measure-dx-construct-review.md) | Critical review of Measure Dx: what transfers to the FMF, what does not |
| [`docs/03-signal-catalog.md`](docs/03-signal-catalog.md) | **Core deliverable.** 24 triggers with logic, data source, exclusions, expected yield |
| [`docs/04-spade-dyads.md`](docs/04-spade-dyads.md) | Symptom–disease pairs calibrated to the USMC risk set |
| [`docs/05-metrics.md`](docs/05-metrics.md) | The metric layer: process, yield, outcome, system-factor Pareto |
| [`docs/06-review-process.md`](docs/06-review-process.md) | Review panel, instruments, calibration, feedback |
| [`docs/07-governance-and-policy.md`](docs/07-governance-and-policy.md) | 10 U.S.C. §1102, CQM framework, OPPE firewall |
| [`docs/08-data-sources.md`](docs/08-data-sources.md) | Where the data actually live and who to partner with |
| [`docs/09-implementation-roadmap.md`](docs/09-implementation-roadmap.md) | Phased pilot, resourcing, decision gates |
| [`docs/10-open-questions.md`](docs/10-open-questions.md) | What must be verified before this is briefable as fact |
| [`docs/11-running-the-code.md`](docs/11-running-the-code.md) | **The tool** — install, run, calibrate, and the compliance gate |

Machine-readable specs for an analyst:

- [`catalog/triggers.yaml`](catalog/triggers.yaml) — trigger definitions
- [`catalog/dyads.yaml`](catalog/dyads.yaml) — symptom–disease pairs with look-forward windows

---

## The tool

`mdxg` reads a medical record extract and returns a **FIN-keyed worklist of notes
that may benefit from review**. 15 of the 24 catalog triggers are implemented; the
rest are solicited report streams rather than queries.

```bash
pip install -e .
mdxg demo        # runs on synthetic data — no PHI, no network, no access needed
```

```
Encounters scanned: 1,168
Trigger firings:    16
Distinct FINs flagged: 12 (1.0% of encounters)

     fin index_date index_dx top_priority  n_triggers   triggers  review_score
F0001153 2024-07-19    R10.2    mandatory           2 T-05; T-10          11.5
F0001160 2024-04-30    B34.9    mandatory           2 T-02; T-10          11.5
F0001162 2024-07-29   R53.83    mandatory           1       T-01          10.0
```

Against your own extract:

```bash
mdxg init-mapping mapping.yaml                    # map your columns
mdxg run --mapping mapping.yaml --data ./extracts --out ./out --control-arm 40
mdxg packet --fin F0001153 --mapping mapping.yaml --data ./extracts
mdxg calibrate --dyad D-B01 --mapping mapping.yaml --data ./extracts
mdxg metrics --adjudications adj.csv --worklist out/review/worklist_detail.csv
```

**A trigger firing is a question, not a finding.** Adjudication is a clinician
task using the Revised Safer Dx Instrument. Nothing in the package writes to any
source system, and nothing in it determines that care was substandard.

Read [`docs/11-running-the-code.md`](docs/11-running-the-code.md) before pointing
it at real data — the compliance gate there is not optional and is not a code
problem.

---

## The one-sentence argument

The Fleet Marine Force has something no civilian health system has — a **closed,
enumerated population with a true denominator, guaranteed annual re-contact, and
near-universal autopsy on death** — which makes diagnostic safety measurement *more*
tractable here than in the academic medical centers where Measure Dx was field-tested,
if the sampling frame is built from signals instead of a random number generator.

## Status

Design document. No trigger in this repository has been run against live data. Expected
volumes and yields are explicitly labeled illustrative and must be replaced with
measured values from a pilot before any of it is briefed as fact. See
[`docs/10-open-questions.md`](docs/10-open-questions.md).

## Source

AHRQ Publication No. 22-0030, *Measure Dx: A Resource To Identify, Analyze, and Learn
From Diagnostic Safety Events* (July 2022), Bradford A, Singh H, et al.
