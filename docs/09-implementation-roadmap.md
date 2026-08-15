# Implementation Roadmap

Scoped to **one division or MEF**, 24 months, with decision gates. Measure Dx's own
guidance is to begin with a single strategy in a limited capacity and expand as the
capability matures — that guidance is followed here.

---

## Phase 0 — Charter and stand-up (months 1–3)

**No data access required.**

- Written charter as a formal MQA activity; judge advocate review of §1102 applicability
  and record handling ([`07-governance-and-policy.md`](07-governance-and-policy.md))
- Firewall policy written and briefed
- Panel formed, including an IDC or senior HM
- Reviewers read the Safer Dx Instrument source publication
- 10–20 pilot adjudications from existing mishap investigations (T-24) — training cases,
  no findings counted
- κ established on the pilot set; recalibrate until ≥0.60
- Local exemplar set drafted (5–8 cases with written rationale)
- Analytic partner identified and engaged; trigger specifications delivered
- Command messaging plan briefed to participating unit commanders

**Gate 0 → 1:** κ ≥0.60 on ≥15 dual-reviewed pilot cases. **If the panel cannot agree, the
program cannot produce defensible findings — stop and fix it here.** This is the gate most
programs skip and the one that determines whether anything downstream is credible.

## Phase 1 — Sentinel and solicited (months 4–9)

**Minimal data access. Highest yield per unit of effort.**

Triggers live: **T-01** (death/autopsy), **T-04** (exertional collapse), **T-21** (DLO
reports), **T-22** (corpsman reports), **T-24** (mishap cross-referral). Add **T-03**
(MEDEVAC) if evacuation records are obtainable.

- DLO reporting form deployed — five fields, "diagnostic learning opportunity" language
- Corpsman channel opened with written non-retaliation protection
- Retrospective AFMES look-back on the prior 24 months of deaths
- First quarterly report: process metrics, source mix, system-factor Pareto, de-identified
  vignettes
- Random control arm begins in parallel — 25–40 charts/quarter, same instrument, same panel

**Gate 1 → 2:** ≥30 adjudicated cases; measured MOD yield published by source; feedback
closure ≥90%; the random arm has produced a base-rate estimate. **Decision:** does measured
trigger yield justify building the analytic pipeline?

## Phase 2 — Trajectory triggers and the first dyads (months 10–15)

**Requires the analytic partnership to be producing.**

Triggers live: add **T-06** (rule of three), **T-07** (unplanned hospitalization),
**T-05** (emergency surgery), **T-02** (critical care escalation).

Dyads live — the five highest-value only:
femoral neck stress fracture · testicular torsion and testicular cancer · spinal epidural
abscess · PE and myocarditis · the behavioral health dyad.

- Symptom-side value sets built **from observed local data**, not from a textbook
  ([`04-spade-dyads.md`](04-spade-dyads.md#implementation-notes-for-the-analyst))
- First **symptom-to-diagnosis interval** baselines published per dyad
- Loop-closure triggers (T-16, T-17) begin as a **prospective safety net** — remediate
  individually first, adjudicate for learning later
- First trigger retirements executed and published
- Review volume approaching the 200 cases/yr steady state

**Gate 2 → 3:** trigger PPV lift over the random arm is demonstrated with a confidence
interval; ≥1 system-level change implemented and tracked to closure; interval baselines
established for ≥3 dyads.

## Phase 3 — Disposition triggers and the readiness metric (months 16–24)

**The phase that makes the program permanent.**

Triggers live: add **T-11** (LIMDU), **T-12** (MEB), **T-15** (pre-deployment),
**T-19**/**T-20** (movement and detachment loop failures), remaining dyads.

- **Duty-days-lost** estimates produced and reported
- Full annual report: intervals, harm distribution, deployability impact, catalog changes
- CFER-DS-aligned data structure validated for cross-MEF aggregation
- Recommendation on the standing peer review requirement — what proportion of review
  capacity should remain random, based on 18 months of measured comparative yield

**Gate 3 → sustainment:** the program can state, with data, the diagnostic safety event
rate per 1,000 Marines per year and the duty-days attributable to it. At that point it is
briefable to the line in the line's own terms, and it stops being a medical-internal
activity.

---

## Resourcing

| | Phase 0–1 | Phase 2–3 / steady state |
|---|---|---|
| Clinician reviewer time | ~0.1 FTE | ~0.3 FTE (200 cases × 2–4 h) |
| CQM / safety professional | ~0.2 FTE | ~0.4 FTE |
| Analyst | partnered | partnered + ~0.2 FTE local |
| Panel members | 4–6 people, ~4 h/month each | same |

Against 3,000–6,000 reviewer-hours consumed by a 5% random sample of a division's
encounters, this is a **net reduction** in review burden with roughly a twenty-fold
increase in confirmed findings ([`01-why-random-review-fails.md`](01-why-random-review-fails.md#1-the-arithmetic)).

That framing matters for the resourcing conversation: this is a reallocation, not a
new bill.

## The four ways this fails

**It becomes punitive.** One case that reappears in a FITREP ends T-21 and T-22
permanently. The firewall is not a formality; it is the program's survival condition.

**It waits for perfect data.** Phase 1 requires almost no data access and produces real
findings. Programs that sequence the analytic pipeline first spend eighteen months on data
use agreements, produce nothing, and are cancelled before the first case is reviewed.

**It counts instead of fixing.** Confirmed events are an input, not an output. If the
annual report contains no implemented system changes tracked to closure, the program is a
measurement exercise and will be correctly identified as one.

**It gets killed by its own early numbers.** Confirmed event counts will rise for 18–24
months because detection is improving. Frame that in the *first* brief, pair every count
with its trigger coverage rate, and lead with the interval measures
([`05-metrics.md`](05-metrics.md#the-counting-trap-stated-plainly)). A program that
reports rising error counts without that framing hands its opponents an accurate-sounding
argument that things got worse after it started.
