# The Metric Layer

Measure Dx states that it "does not prescribe specific metrics." This document supplies
them. It is the part of the design that answers the original question — *how do I obtain
safety-specific metrics for peer review usage* — and it is the part that has no source
document behind it.

## Design constraints

1. **Every rate must have a real denominator.** The FMF can compute true population rates
   because it knows exactly who is at risk. Use that. Never report "percent of reviewed
   cases" as a safety measure — it varies with review volume and is uninterpretable.
2. **Nothing that identifies an individual provider leaves the program.** See
   [`07-governance-and-policy.md`](07-governance-and-policy.md).
3. **At least one top-line metric must be legible to a line commander.** Clinical quality
   metrics do not survive contact with a division brief. Readiness metrics do.
4. **Metrics must distinguish "we looked harder" from "care got better."** A rising count
   of confirmed events during the first two years is a sign of success, not failure, and
   the metric set has to make that unambiguous or the program will be killed by its own
   early results.

---

## 1. Program process metrics

Do the machinery metrics first. They are the only ones that mean anything in year one,
and they are the ones that tell you whether the program is real.

| Metric | Definition | Target |
|---|---|---|
| **Trigger coverage** | Triggered cases adjudicated ÷ triggered cases fired, by tier | ≥95% Tier 1; ≥40% Tiers 2–4 |
| **Review timeliness** | Median days from trigger fire to completed adjudication | ≤45 d |
| **Sentinel timeliness** | Days from AFMES report / sentinel event to adjudication | ≤60 d, 100% |
| **Dual-review rate** | Cases independently scored by ≥2 reviewers | ≥10%, plus all item-13 scores of 4–5 |
| **Reviewer agreement** | Cohen's κ on item 13 (dichotomized ≥5) across the dual-reviewed sample | ≥0.60, recalibrate below |
| **Feedback closure** | Confirmed events with documented feedback delivered ÷ confirmed events | ≥90% within 45 d |
| **Action closure** | System recommendations with a documented disposition at 180 d | ≥80% |

The dual-review and κ metrics are not bureaucratic garnish. The Measure Dx guide is
explicit that findings from two or more reviewers must be compared after training and
periodically thereafter, and that persistent disagreement requires retraining. Without a
published κ, every finding this program produces is contestable.

## 2. Yield and efficiency metrics

These justify the program's existence and drive the trigger catalog.

| Metric | Definition | Reference |
|---|---|---|
| **MOD yield** | Confirmed missed opportunities (Safer Dx item 13 ≥5) ÷ cases adjudicated, **reported per trigger** | 31.8% across 703 cases in the 11-site Measure Dx evaluation |
| **Trigger PPV lift** | MOD yield of trigger *t* ÷ MOD yield of the random arm | Report with CI; this is the core argument |
| **Reviewer-hours per confirmed event** | Total review hours ÷ confirmed events | Random review baseline ≈ 500–1,500 h; target <15 h |
| **Detection density** | Confirmed events per 10,000 encounters, **and** per 1,000 Marines per year | New measure; establish local baseline |
| **Source mix** | Share of confirmed events by strategy (A/B/C/D) | The published evaluation found staff reports the single highest-yield source |

### Trigger retirement rule

Any trigger with a MOD yield **<10% after 40 adjudicated cases** is re-tuned once. If it
fails again, retire it and reallocate the capacity. Publish the retirement in the
program's quarterly report — a catalog that never loses a trigger is a catalog nobody is
measuring.

### The random arm is the control group. Keep it.

Retain a small random sample — 25–40 charts per quarter per division is enough — reviewed
with the identical instrument by the identical panel, blinded to selection method where
practical.

It serves three purposes and none of them are compliance:

1. It estimates the **base rate**, which is the denominator of every PPV-lift claim.
2. It is the only defense against the objection that triggers merely re-find events that
   were already known.
3. It detects **entire failure classes the catalog is blind to** — the misses that never
   escalate, never generate a board, and never come back. A trigger catalog can only find
   what it was built to look for. The random arm is the program's check on its own
   blind spots.

Report it as a control arm, not as the residue of the old program.

## 3. Outcome metrics

### The two that go on the command brief

**Median symptom-to-diagnosis interval, sentinel dyads.** Days from the first documented
encounter with a related symptom to the date the target diagnosis was established.
Reported per dyad, as a median with IQR.

This is the best single measure the program produces. It is continuous rather than
binary, it does not require adjudicating every case, it is not distorted by changes in
review intensity, it moves when care improves, and it is directly interpretable. It is
also comparable across units in a way that "number of errors found" never will be —
a unit that reviews more will always appear worse on a count and will not on an interval.

**Duty-days lost attributable to confirmed missed opportunities.** For each confirmed
event, the reviewer estimates duty days lost beyond what timely diagnosis would have
cost. Aggregate per 1,000 Marines per year.

This is the translation layer. A Force Surgeon can brief "diagnostic safety" to a division
commander for exactly as long as it takes the commander to ask what it costs him. This
number answers that, in his units. It is an estimate and must be labeled as one — but a
labeled estimate that reaches the decision-maker beats a precise measure that does not.

### Supporting outcome measures

| Metric | Definition |
|---|---|
| **Harm-weighted event rate** | Confirmed events at NCC MERP category E or above, per 1,000 Marines/yr |
| **Duty-status harm distribution** | Confirmed events by worst duty outcome: none / light duty / LIMDU / MEB / separation / death |
| **Deployability impact** | Confirmed events resulting in a non-deployable determination |
| **Loop-closure failure rate** | T-16/T-17/T-19/T-20 firings per 1,000 orders — a pure process rate needing no adjudication, available monthly |

The loop-closure rate deserves emphasis: it is the only outcome family here that can be
measured **continuously and prospectively without any chart review at all.** It should be
standing on a dashboard from month one while the adjudication machinery is still being
built.

## 4. System-factor profile

Not a scorecard — a Pareto. For every confirmed event, classify contributing factors
using the DEER taxonomy and the Safer Dx Process Breakdown Supplement, then report the
aggregate distribution quarterly.

Expected FMF-specific categories, mapped to DEER:

| Factor | DEER | Why it matters here |
|---|---|---|
| **Delay in presentation** | 1a | The dominant FMF factor. Marines are culturally penalized for going to sick call. |
| Organic capability gap at Role 1 | 4a/4b | No imaging past plain film, minimal lab |
| Referral loop failure | 6b/6d | Severed by movement, deployment, PCS |
| Result loop failure | 4k | Orphaned results after provider detachment |
| Handoff / turnover | 7d | GMO and corpsman tour cycling |
| Information not available in the record | 2b/3b | Field encounters documented on paper or not at all |
| Clinical reasoning | 5a–5e | The only cognitive category — expect it to be a minority |

**Report the split between system and cognitive factors explicitly.** If the profile comes
back dominated by clinical reasoning, that is far more likely to mean the reviewers are
untrained than that the providers are bad — the published literature consistently finds
most diagnostic safety events carry both, with system factors prominent. Treat a
reasoning-dominant profile as a signal to recalibrate the panel.

**"Delay in presentation" is the finding to watch.** If it turns out to be the leading
contributing factor across a division — which is plausible — then the highest-yield
intervention this program can produce is not a clinical one. It is a conversation with
battalion commanders about sick call access and the informal cost a Marine pays for using
it. That is a finding no random chart review would ever surface, and it belongs to the
line, not to medical.

---

## The counting trap, stated plainly

**Confirmed event counts will rise for the first 18–24 months.** That is the program
working. Detection is improving faster than care is.

Build this into the reporting format from the first brief — pair every count with its
trigger coverage rate, and lead the outcome section with the interval measures, which are
insensitive to review intensity. A program that reports a rising error count without that
framing invites its own cancellation, and the people who cancel it will be able to say,
accurately, that things got worse after it started.

## Reporting cadence

| | Content | Audience |
|---|---|---|
| **Monthly** | Loop-closure rates, trigger fire volumes, coverage, backlog | Program cell |
| **Quarterly** | Yield by trigger, system-factor Pareto, confirmed events with de-identified case vignettes, action closure | MEF/Division Surgeon, CQM committee |
| **Annually** | Interval measures, duty-days lost, harm distribution, trigger catalog changes with retirements | Force Surgeon, HQMC Health Services, command |

De-identified aligned to AHRQ **CFER-DS** common formats from the start. It costs almost
nothing at the outset and it is the only thing that will let findings aggregate across
MEFs — and eventually let the Marine Corps say something about diagnostic safety in
operational forces that no one else can say, because no one else has the denominator.
