# Executive Summary

*Audience: Force Surgeon, MEF Surgeon, Division Surgeon, MARFOR CQM.*

## The finding

Health care quality assurance in the operating forces relies substantially on random
sampling of clinical records. For diagnostic safety, random sampling does not work — not
because it is executed poorly, but because it cannot work arithmetically. A reviewer
sampling 20 charts per quarter from a battalion generating ~4,000 encounters per year has
roughly a **4% chance of encountering a single harmful diagnostic event** even under
generous assumptions about how common those events are (see
[`01-why-random-review-fails.md`](01-why-random-review-fails.md)).

Random review also examines the wrong object. It reviews a *note*. Diagnostic safety is
a property of an *episode* — the sick-call visit for "muscle strain," the second visit
three weeks later, and the femoral neck fracture pinned at the MTF two months after that.
No single-encounter review can see that trajectory. The index note usually looks fine.

## The proposal

Adopt the AHRQ **Measure Dx** construct — case-finding, structured adjudication with the
Revised Safer Dx Instrument, non-punitive feedback — and supply the two things it
deliberately leaves to the adopting organization:

1. **A sampling frame built for this population.** 24 operational-forces-specific
   triggers ([`03-signal-catalog.md`](03-signal-catalog.md)) and a catalog of
   symptom–disease dyads calibrated to what actually kills and disables Marines
   ([`04-spade-dyads.md`](04-spade-dyads.md)) — exertional collapse, testicular torsion
   and testicular cancer, spinal epidural abscess, high-risk stress fracture, PE,
   myocarditis, ectopic pregnancy, missed behavioral health.

2. **A metric layer.** Measure Dx states plainly that it "does not prescribe specific
   metrics." [`05-metrics.md`](05-metrics.md) supplies them, including the two that
   translate to command: **median symptom-to-diagnosis interval** for sentinel
   conditions, and **duty-days lost attributable to confirmed missed opportunities.**

## Why this population is unusually favorable

The FMF holds assets no civilian health system has, and every one of them is a
diagnostic safety instrument:

- **A true denominator.** Unit rosters and DEERS tell you exactly who is at risk. Civilian
  systems cannot compute a miss rate because patients leak to other providers. Marines
  largely do not.
- **Near-universal autopsy on active-duty death** through AFMES, against a civilian
  autopsy rate in the low single digits. Autopsy is the strongest available reference
  standard for missed diagnosis, and here it is close to complete.
- **Guaranteed annual re-contact** through the Periodic Health Assessment. Every Marine
  comes back. Conditions missed at sick call surface on a schedule.
- **Formally adjudicated outcomes** — LIMDU, MEB/PEB, medical separation — each of which
  is a documented finding that a condition is disabling, and therefore a natural
  look-back case.
- **A bounded risk set.** The differential that harms a 21-year-old infantry Marine is
  short and enumerable. The open-ended civilian problem becomes a finite catalog.

## Resource ask

Illustrative, for one Marine division (~10,000 Marines), replacing not adding:

| | Random review (current construct) | Trigger-driven review |
|---|---|---|
| Cases reviewed / year | 1,500 (at a 5% sample) | 200 |
| Review hours / year | 3,000–6,000 | 400–800 (~0.3 FTE) |
| Expected confirmed learning opportunities | single digits | ~60 |

The Measure Dx multi-site evaluation found **31.8%** of triggered cases (224 of 703)
contained a confirmed diagnostic safety improvement opportunity. That is the yield this
design is built to reproduce.

## What it costs to be wrong about the current approach

Nothing is discarded. The recommendation is explicitly **not** to abolish random review:
retain a small random sample as a calibration arm and negative control. It is the only
way to estimate the base rate and prove the triggers are actually lifting yield
(see [`05-metrics.md`](05-metrics.md#the-random-arm-is-the-control-group-keep-it)).

## Protection

The program only functions if it is non-punitive, and it can be. **10 U.S.C. §1102**
protects DoD medical quality assurance records from disclosure and from use in most
adverse personnel actions — a stronger protection than most state peer review statutes.
It attaches only if the program is stood up as a formal MQA activity from the outset.
Design the firewall between systems learning and individual privileging action before
the first case is reviewed, not after ([`07-governance-and-policy.md`](07-governance-and-policy.md)).

## Decision requested

Authorize a **12-month pilot at one division or MEF** with a retrospective look-back run
of Tier 1 triggers against existing MHS GENESIS and MDR data, executed in partnership
with an established analytic organization rather than built organically at the MEF
([`08-data-sources.md`](08-data-sources.md)). Decision gates and phasing in
[`09-implementation-roadmap.md`](09-implementation-roadmap.md).
