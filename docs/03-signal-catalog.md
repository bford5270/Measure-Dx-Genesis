# Signal Catalog — Operational Forces Diagnostic Safety Triggers

The sampling frame. Twenty-four triggers, tiered by expected yield and review priority.
Machine-readable definitions in [`../catalog/triggers.yaml`](../catalog/triggers.yaml).

> **All volumes and yields in this document are illustrative planning estimates for a
> 10,000-Marine division generating ~30,000 outpatient encounters per year.** None has
> been measured. Every one must be replaced with observed values from a pilot before the
> catalog is used for resourcing decisions. See [`10-open-questions.md`](10-open-questions.md).

## How to read a trigger

Each trigger specifies: the **signal** (what fires it), the **look-back window** (how far
back the reviewed episode extends), the **data source**, **exclusions** (to suppress
predictable false positives), and a **review priority**.

Two design rules govern the whole catalog:

1. **Sample from the outcome backward.** Every Tier 1–3 trigger fires on a consequential
   downstream event and directs review to the encounters that preceded it. This is what
   makes the index encounter judgeable ([`01-why-random-review-fails.md`](01-why-random-review-fails.md#3-random-review-samples-at-the-wrong-point-in-time)).
2. **A trigger that does not earn its keep gets retired.** Any trigger yielding <10%
   confirmed missed opportunities after 40 adjudicated cases is re-tuned or dropped
   ([`05-metrics.md`](05-metrics.md#trigger-retirement-rule)).

---

## Tier 1 — Sentinel outcomes

Low volume, highest yield, **mandatory 100% review**. If the program does nothing else,
it does these five.

### T-01 · Active-duty death with AFMES autopsy
**Signal:** Any death of an assigned Marine or Sailor. **Look-back:** 12 months of all
encounters.
**Why this is first:** the Armed Forces Medical Examiner System performs autopsy on
essentially all active-duty deaths. Autopsy is the strongest available reference standard
for missed diagnosis, and the DoD has coverage no civilian system approaches. Measure Dx
names autopsy an "underused data source that reveals useful patterns of diagnostic
discrepancies" — here it is not merely underused, it is close to untouched.
**Scope:** all non-battle deaths including natural, undetermined, and suicide. Include
trauma and training deaths where a medical condition may have contributed (exertional
collapse, sickling, cardiac, occult infection).
**Exclusions:** hostile action deaths with no preceding medical encounter of relevance.
**Est. volume:** 3–8/yr per division. **Priority:** mandatory, review within 60 days of
AFMES report.

### T-02 · Unplanned critical care escalation
**Signal:** ICU admission, rapid response, or intubation within 30 days of any Role 1 or
outpatient encounter. **Look-back:** 90 days.
**Exclusions:** planned post-operative ICU; escalation attributable to progression of a
correctly and timely diagnosed condition (captured as a structured field on review, not
as a pre-filter).
**Est. volume:** 10–25/yr. **Priority:** mandatory.

### T-03 · Urgent or priority MEDEVAC preceded by a related encounter
**Signal:** urgent/priority evacuation where the Marine had ≥1 encounter for a related
complaint in the prior 30 days. **Look-back:** 90 days.
**Notes:** evacuation is the operational analog of unplanned admission and is documented
in evacuation systems independent of the EHR, which makes it robust when field
documentation is thin.
**Est. volume:** 5–20/yr, tempo-dependent. **Priority:** mandatory.

### T-04 · Exertional collapse or arrest
**Signal:** cardiac arrest, exertional collapse, exertional heat stroke, or exertional
sickling event during PT, PFT/CFT, hike, or field training. **Look-back:** 180 days.
**Why:** the highest-consequence, most FMF-specific event class. Ask three questions of
the prior record — was there a documented prodrome dismissed as deconditioning; was
sickle cell trait status known and acted upon; was there a cardiac symptom or family
history not pursued.
**Cross-reference:** these events already generate a mishap investigation containing
detailed medical narrative. Pull it. Do not duplicate the collection.
**Est. volume:** 5–15/yr. **Priority:** mandatory.

### T-05 · Emergency surgery within 14 days of an outpatient encounter
**Signal:** emergent operative procedure for a condition plausibly related to a preceding
outpatient complaint. **Look-back:** 90 days.
**Target procedures:** appendectomy with perforation; testicular detorsion or
orchiectomy; fasciotomy for compartment syndrome; debridement for necrotizing soft tissue
infection; laminectomy or drainage for spinal epidural abscess or cauda equina; craniotomy;
operative fixation of a stress fracture; salpingectomy for ectopic pregnancy.
**Est. volume:** 15–40/yr. **Priority:** mandatory.

---

## Tier 2 — Trajectory and escalation

Moderate volume, good yield. Sampled rather than reviewed exhaustively once volume is
known.

### T-06 · Rule of three
**Signal:** ≥3 encounters for the same or a related complaint within 30 days, where the
diagnosis at the third differs from the first, or the third results in referral,
imaging escalation, or admission. **Look-back:** the full complaint episode.
**Why:** the single most productive trajectory signal in an outpatient population and
directly aligned with Safer Dx item 11 — *the final diagnosis was not an evolution of the
care team's initial working diagnosis.*
**Est. volume:** 60–120/yr. **Priority:** high; sample 50% if volume exceeds capacity.

### T-07 · Unplanned hospitalization or ED visit after an outpatient encounter
**Signal:** ED visit or inpatient admission within 14 days of a BAS, sick call, or MTF
primary care encounter for a related complaint. **Look-back:** 60 days.
**Note:** the guide's canonical trigger, and the one whose civilian performance is best
characterized — associated with improvement opportunities in roughly one case in five.
**Exclusions:** scheduled admissions; injury from a new discrete trauma unrelated to the
index complaint.
**Est. volume:** 80–150/yr. **Priority:** high; stratify — admissions before ED visits.

### T-08 · Role-of-care escalation within 72 hours
**Signal:** Role 1 encounter followed by presentation to Role 2/3 or a civilian ED within
72 hours. **Look-back:** 30 days.
**Est. volume:** 40–90/yr. **Priority:** high.

### T-09 · Readmission with a different principal diagnosis
**Signal:** readmission within 30 days where the principal diagnosis differs from the
index admission. **Look-back:** index admission plus 90 days prior.
**Why:** diagnostic instability between admissions is a stronger signal than readmission
alone, which is dominated by disease severity rather than diagnostic error.
**Est. volume:** 5–15/yr. **Priority:** high.

### T-10 · Nonspecific-to-serious diagnostic transition
**Signal:** an index encounter coded to a nonspecific symptom or unspecified-pain code,
followed within the dyad-specific window by a coded target serious condition.
**Look-back:** to the first symptomatic encounter.
**Implementation:** this trigger is the generic engine; the specific pairs and windows
are in [`04-spade-dyads.md`](04-spade-dyads.md) and
[`../catalog/dyads.yaml`](../catalog/dyads.yaml). It is the highest-volume trigger in the
catalog and must be run dyad-by-dyad, not as a single query.
**Est. volume:** 100–250/yr across all dyads. **Priority:** high, dyad-prioritized.

---

## Tier 3 — Disposition and administrative outcomes

Unique to the military. No civilian analog. These triggers convert administrative
adjudications the Marine Corps already performs into diagnostic safety case-finding, at
almost no collection cost — and they are the ones that generate readiness metrics.

### T-11 · New limited duty with a long nonspecific prodrome
**Signal:** LIMDU initiated where the first documented encounter for the qualifying
condition was >90 days prior and coded nonspecifically. **Look-back:** 24 months.
**Metric produced:** symptom-to-diagnosis interval — the program's best continuous
outcome measure ([`05-metrics.md`](05-metrics.md#3-outcome-metrics)).
**Est. volume:** 40–100/yr. **Priority:** medium-high; sample.

### T-12 · Medical board referral
**Signal:** any MEB/PEB referral. **Look-back:** to the first documented symptomatic
encounter for the unfitting condition, up to 36 months.
**Why:** an MEB is a formal, adjudicated, well-documented finding that a condition is
disabling. Every one is a natural look-back case with the outcome already established.
**Est. volume:** 50–120/yr. **Priority:** medium-high; sample, prioritize by interval length.

### T-13 · Condition first identified at PHA or deployment health assessment
**Signal:** a new significant diagnosis arising from PHA, PDHA, or PDHRA where the record
shows prior symptomatic encounters without corresponding workup. **Look-back:** 24 months.
**Why:** the annual PHA is a guaranteed re-contact with 100% of the force — an
ascertainment mechanism with no civilian equivalent. It catches what sick call did not.
**Est. volume:** 20–60/yr. **Priority:** medium.

### T-14 · Early medical attrition
**Signal:** medical separation, EPTS/EPTE determination, or entry-level separation for a
medical condition within 180 days of accession or arrival at the operating forces.
**Look-back:** to accession physical.
**Why:** distinguishes conditions genuinely missed at accession screening from conditions
that were symptomatic and documented and still not pursued. Findings here route to
accession and recruit-training medicine, not to the FMF.
**Est. volume:** 15–50/yr. **Priority:** medium.

### T-15 · Deployment-limiting condition found at pre-deployment screening
**Signal:** a condition identified during pre-deployment health assessment that renders a
Marine non-deployable, with prior symptomatic encounters in the record.
**Look-back:** 18 months.
**Why:** the most direct readiness translation in the catalog. A condition caught at
sick call in month two costs light duty; caught at the deployment gate it costs a
non-deployable slot and a late fill.
**Est. volume:** 20–60/yr. **Priority:** medium.

---

## Tier 4 — Loop-closure failures

Process triggers rather than outcome triggers. Lower yield per case but **actionable
prospectively** — some can be run forward to catch a Marine before harm occurs, which no
other tier can do. Measure Dx singles out this property as the advanced application of
e-triggers.

### T-16 · Abnormal result without documented follow-up
**Signal:** a result on the priority list below with no documented acknowledgment,
notification, follow-up test, or referral within 14 days (30 for lower-acuity results).
**Priority result set for this population:** positive HIV, syphilis, gonorrhea, or
chlamydia testing; hemoglobin <10 g/dL; WBC >15,000 or <2,000; platelets <100,000;
positive TB test; imaging impression containing a recommendation for further evaluation;
positive urine culture; elevated troponin; scrotal ultrasound with a mass; A1c ≥6.5%.
**Exclusions:** documented follow-up at an outside facility; patient refusal;
already under active care for the flagged condition.
**Est. volume:** 100–300/yr. **Priority:** medium; run prospectively and remediate
individually before adjudicating for learning.

### T-17 · Referral ordered and not completed
**Signal:** specialty referral with no completed encounter within 60 days.
**Why this is worse in the FMF than in civilian practice:** referral loops are severed by
field exercises, unit movement, deployment, and PCS. This is a structural defect, not a
patient adherence problem, and separating those two is a specific job for the reviewer.
**Est. volume:** 150–400/yr. **Priority:** medium; sample; prioritize dyad-relevant
referrals (urology, neurosurgery, oncology, cardiology).

### T-18 · Imaging interpretation discrepancy
**Signal:** material discrepancy between preliminary and final read, or an addendum
altering the impression. **Look-back:** the associated episode.
**Note:** disproportionately relevant where imaging is read by teleradiology remote from
the point of care.
**Est. volume:** 20–60/yr. **Priority:** medium.

### T-19 · Test pending at unit movement, deployment, or detachment
**Signal:** an ordered test or referral outstanding at the time the Marine's unit deploys,
the Marine PCSs, or the Marine detaches. **Look-forward:** 90 days for resolution.
**Why this is a military-specific trigger with no civilian analog:** Measure Dx's "tests
pending at discharge" trigger addresses a handoff at a discharge boundary. The FMF has a
harder boundary — the Marine physically leaves, sometimes to a location without
connectivity, and the loop has no owner. This is likely a high-yield trigger and it is
not in any published catalog.
**Est. volume:** unknown; plausibly 50–200/yr, movement-dependent. **Priority:** medium-high.

### T-20 · Result returned after the ordering provider detached
**Signal:** a result returning to an ordering provider who has since PCSd, deployed, or
separated, with no documented reassignment or acknowledgment.
**Why:** the orphaned-result failure. GMO tour lengths guarantee this happens
continuously, and the failure is silent by construction — nobody is watching the inbox.
**Est. volume:** unknown; likely substantial. **Priority:** medium-high. **This trigger
should be run prospectively as a standing safety net, not retrospectively for learning.**

---

## Tier 5 — Solicited and cross-referred

Measure Dx Strategies A, B, and C. Variable yield — but the guide's evaluation found
staff-referred cases produced the *highest* yield of any source, above every e-trigger.
Do not treat this tier as a fallback.

### T-21 · Diagnostic Learning Opportunity report
**Signal:** voluntary submission by any medical provider. Five fields, following the
Cincinnati Children's model: date, patient identifier, initial impression, final
diagnosis, brief course, and an optional "what can we learn."
**Language matters:** "diagnostic learning opportunity," never "diagnostic error."
**Priority:** high — highest observed yield per case in the published evaluation.

### T-22 · Corpsman-initiated concern
**Signal:** a report from an HM or IDC that a diagnosis was missed, delayed, or that a
concern they raised was not acted upon. Routed independently of the provider involved.
**Why this is not in Measure Dx:** the guide contemplates nursing as a reporting source
but not a structurally subordinate, non-privileged clinician who is very often the person
with the most longitudinal contact with the patient. In the FMF the corpsman sees the
Marine at sick call three times before anyone else does. Also solicit **good catches**.
**Priority:** high. Requires explicit non-retaliation protection to function at all.

### T-23 · External inquiry cross-referral
**Signal:** ICE comment, command-directed inquiry, IG complaint, Congressional inquiry, or
claim touching on medical care.
**Note:** this is the realistic FMF version of Strategy C. Expect low volume and low
yield — consistent with the 11-site evaluation, where patient-reported data produced no
confirmed learning opportunities at all. Include for completeness; do not staff it heavily.
**Priority:** low.

### T-24 · Mishap and safety investigation cross-referral
**Signal:** any Naval Safety Command or command safety investigation involving a medical
event — heat casualty, sickling, training death, water event, dive or aviation
physiological episode.
**Why this is the fastest path to a first tranche of findings:** the investigation
already exists, is already thorough, and already contains a detailed medical narrative.
Re-reviewing that existing corpus through a diagnostic safety lens is Strategy A at zero
collection cost.
**Priority:** high. **Recommended as the pilot's opening move** — it produces reviewable
cases in week one without waiting on any data access approval.

---

## Prioritization for a standing program

| Tier | Est. cases/yr | Review posture | Est. confirmed MOD |
|---|---|---|---|
| 1 — Sentinel | 40–110 | 100%, mandatory | 15–40 |
| 2 — Trajectory | 285–625 | Sample to capacity | — |
| 3 — Disposition | 145–390 | Sample, interval-prioritized | — |
| 4 — Loop closure | 320–960 | Prospective remediation; sample for learning | — |
| 5 — Solicited | 20–60 | 100% | 10–25 |

A sustainable steady state for one division is roughly **200 adjudicated cases per year**
— all of Tier 1 and Tier 5, plus a capacity-limited sample of Tiers 2–4 — at 2–4 hours
per review, or about **0.3 FTE** of clinician reviewer time.

At the Measure Dx-observed 31.8% yield, that is **~60 confirmed diagnostic safety events
with improvement opportunities per division per year**, against an expected single-digit
return from 1,500 random reviews consuming ten times the reviewer-hours.
