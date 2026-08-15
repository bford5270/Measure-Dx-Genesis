# Critical Review of the Measure Dx Construct

*Source: AHRQ Pub. No. 22-0030, July 2022. Developed by Bradford and Singh (Baylor / MEDVAMC
IQuESt) with MedStar Institute for Quality and Safety.*

## What Measure Dx actually is

Four parts:

1. **Preparing the organization** — psychological safety, leadership engagement, team
   formation (minimum: one clinician who diagnoses, one safety professional),
   stakeholder engagement, dissemination.
2. **Organizational self-assessment** — a readiness checklist and a decision aid for
   choosing among the strategies.
3. **Four case-finding strategies** —
   - **A.** Re-review quality and safety data the organization already collects
   - **B.** Solicit reports from clinicians and staff
   - **C.** Leverage patient-reported data
   - **D.** EHR-enhanced chart review and electronic triggers
4. **Review and analysis** — the Revised Safer Dx Instrument (13 items, 1–7 Likert;
   item 13 is the summary judgment), the Safer Dx Process Breakdown Supplement, the DEER
   taxonomy, modified fishbone, and CFER-DS common formats, plus reviewer training and
   calibration guidance.

Underneath sits the **Safer Dx Framework** — five components of the diagnostic process:
the patient–provider encounter; performance and interpretation of tests; follow-up and
tracking over time; subspecialty and referral factors; patient-related factors.

## Verdict

**The construct is sound and it is the right foundation.** It is the only mature,
publicly available, field-tested resource for operational diagnostic safety measurement,
its central instrument has published interrater reliability, and its evidence base is
real: 11 organizations, 703 cases, 31.8% yield.

Adopt it. But adopt it with clear sight of six places where it does not fit the Fleet
Marine Force as written.

---

## What transfers directly

| Element | Why it transfers |
|---|---|
| **Episode as unit of analysis** | Solves the single biggest defect in current random review |
| **Revised Safer Dx Instrument** | Validated, trainable, produces a defensible binary judgment (item 13 ≥5) |
| **DEER taxonomy** | Maps cleanly onto Role 1 failure modes; the "access/presentation" category is the FMF's dominant factor |
| **Trigger logic (Strategy D)** | The core mechanism; the FMF's data situation is better than assumed |
| **Non-punitive framing** | Necessary, and legally supportable under 10 U.S.C. §1102 |
| **Hierarchy of effectiveness** | Correctly demotes "retrain the corpsman" below system redesign |
| **Start-small guidance** | Prevents the failure mode of trying to instrument all three MEFs at once |

---

## Six gaps for this application

### 1. It is not a measurement system, and says so

> "The strategies outlined in this resource do not prescribe specific metrics, but
> rather provide a foundation for HCOs to implement routine discovery, learning, and
> feedback in their daily operations."

This is the most important line in the guide for your purpose. Measure Dx supplies
**case-finding and adjudication machinery**. It does not supply numerators, denominators,
rates, targets, or trend logic. A request for "safety-specific metrics for peer review"
is not answered by the guide — it is answered by building a metric layer on top of it.
That is [`05-metrics.md`](05-metrics.md).

### 2. It assumes an organization the FMF does not have at the unit level

The readiness checklist presumes a quality department, a risk manager, patient safety
infrastructure, and access to an EHR data warehouse with a person who can query it. The
field test population was "primarily academic medical centers."

An infantry battalion has a medical officer, an IDC, and a handful of corpsmen. It has
none of the above and never will.

**Implication:** this cannot be implemented *at* the battalion. It must be a **shared
service at MEF or division level** — one analytic and review cell, drawing cases from all
subordinate units, feeding findings back down. Battalions participate as case sources and
feedback recipients, not as program operators. This also solves the reviewer-independence
problem in [`01-why-random-review-fails.md`](01-why-random-review-fails.md).

### 3. Strategy C will not work here, and it barely worked there

The 11-site evaluation found organizations reviewed few cases from patient-reported data,
and **none of those cases yielded identified learning opportunities.** In the FMF the
channel is additionally suppressed: a Marine who reports that sick call missed something
is a Marine complaining about medical, with predictable social cost.

**Do not lead with Strategy C.** Instead, capture the patient-side signal indirectly and
systematically through the **delay-in-presentation** finding on every reviewed case — a
structured field, scored on every episode, aggregated to the unit. That produces the
information Strategy C is meant to produce, without requiring Marines to file complaints.

Retain a light version of Strategy C by cross-referring existing channels: ICE comments,
command-directed inquiries, IG and Congressional inquiries touching medical care.

### 4. Strategy B needs command air cover, not just a form

Measure Dx recommends either adding a diagnostic category to the general event reporting
system or standing up a dedicated "diagnostic learning opportunity" channel. In DoD the
general system is JPSR. Reporting volume from operational units is negligible, and a
category added to a system nobody uses produces nothing.

**Implication:** build the dedicated channel (Cincinnati Children's model — a five-field
form, "diagnostic learning opportunity" language, transparent use), and pair it with
explicit, repeated command messaging. Then add the FMF-specific variant the guide does
not contemplate: **a corpsman-initiated report.** The person who most often knows a
diagnosis was missed is the HM who saw the Marine three times. Give them a channel that
does not route through the provider whose case it is.

### 5. The harm taxonomy has no duty-status dimension

Measure Dx uses the NCC MERP severity categories — no harm, temporary harm, permanent
harm, death. Correct, and insufficient here. In the operating forces the outcome that
matters to the commander and to the Marine is **fitness for duty**: days on light or
limited duty, deployability status, LIMDU, board, separation.

**Implication:** extend the outcome capture with a duty-status axis
([`05-metrics.md`](05-metrics.md#3-outcome-metrics)). A missed diagnosis that costs a
Marine 90 duty days and a deployment is a serious event even if it caused no permanent
physical harm. This extension is also what makes the program legible to line leadership.

### 6. It warns against adapting the instrument — heed that

> "Teams are cautioned against ad hoc adaptations of this or any other review tools.
> In general, adaptation of existing tools is not recommended outside of research
> settings."

The temptation to rewrite the 13 items in operational language will be strong. Resist it.
The instrument's interrater reliability is a property of its exact wording, and rewriting
it forfeits the ability to compare findings against published benchmarks.

**Use the 13 items verbatim. Add a separate operational context supplement** capturing
role of care, organic capability at the point of contact, evacuation constraints,
tempo/field conditions, and the duty-status outcome — as an adjunct instrument, not an
edit ([`06-review-process.md`](06-review-process.md)).

---

## What the FMF has that Measure Dx does not anticipate

The guide is written for organizations that cannot see their own denominator. Its authors
work around loss to follow-up, fragmented records, and absent autopsy. Those constraints
are substantially relaxed here, and the design should exploit that rather than inherit
workarounds built for a harder problem.

| Asset | Civilian equivalent | Consequence |
|---|---|---|
| Unit roster / DEERS denominator | None — patients leak between systems | **True rates**, not proportions of reviewed cases |
| AFMES autopsy on active-duty deaths | Autopsy rate in low single digits | The strongest reference standard for missed diagnosis, at near-complete coverage |
| Annual Periodic Health Assessment | None — no guaranteed re-contact | Scheduled ascertainment of conditions missed at sick call |
| LIMDU / MEB / PEB adjudication | Disability claims, delayed and external | Formally adjudicated outcomes usable as look-back anchors |
| Purchased care claims in MDR | Fragmented, often invisible | Downstream civilian care remains visible to the analysis |
| Bounded risk set (young, screened, occupationally stressed) | Open-ended | A **finite dyad catalog** is achievable ([`04-spade-dyads.md`](04-spade-dyads.md)) |
| Mishap investigations (heat, sickling, training deaths) | None | An existing, already-investigated case stream for Strategy A at zero collection cost |

The last row deserves emphasis. Every exertional heat stroke and every exertional sickling
event in the Marine Corps already generates a safety investigation containing detailed
medical care narrative. Re-reviewing that existing corpus through a diagnostic safety lens
is Strategy A applied to a military data stream, requires no new collection, and is
probably the single fastest way to produce a first tranche of findings.

---

## Bottom line

Measure Dx gives you the machinery and withholds the metrics. The machinery transfers.
The metrics have to be built, the sampling frame has to be rewritten for this population,
and the program has to live at MEF or division level rather than at the battalion.
