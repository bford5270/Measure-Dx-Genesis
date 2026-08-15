# Review Process, Panel, and Instruments

## Where the program lives

**At MEF or division level. Not at the battalion.**

Measure Dx's readiness checklist assumes a quality department, a risk manager, patient
safety infrastructure, and queryable warehouse access with a person who can use it. A
battalion aid station has a medical officer, an IDC, and corpsmen. Attempting to run this
at unit level guarantees two failures: no analytic capability, and no reviewer
independence — the "peer" is a fellow GMO in the same regiment who will be working
alongside the reviewee for two more years.

Pool review above the unit. Cases flow up from all subordinate units; findings flow back
down. **No reviewer adjudicates a case from their own battalion.**

## Panel composition

Measure Dx's stated minimum is one clinician who diagnoses plus one safety professional.
For an operational-forces panel:

| Role | Contribution |
|---|---|
| **Chair** — senior medical officer, MEF/Division Surgeon's staff | Convening authority, feedback delivery, MQA program ownership |
| **2–4 reviewing clinicians** — GMOs, PAs, IDCs, and MTF specialists relevant to the case mix | Adjudication. Rotate to spread the learning; retain a trained core for calibration |
| **CQM / patient safety professional** | Instrument fidelity, DEER coding, CFER-DS alignment, tracking |
| **Analyst** (may be partnered, not organic) | Trigger execution, value sets, denominators, dashboard |
| **IDC or senior HM** | Role 1 reality. Non-optional — the panel will systematically misjudge what was available at the point of contact without one |
| **Ad hoc specialist** | Case-dependent: urology, neurosurgery, orthopedics, behavioral health |

Including a senior corpsman on an adjudication panel will be unfamiliar. It is also the
single highest-value seat at the table, because most triggered cases begin at a sick call
encounter conducted by a corpsman under an IDC's or GMO's supervision, and a panel of
physicians reviewing that encounter without that perspective will reliably score it wrong
in both directions.

## Instruments

### Use the Revised Safer Dx Instrument verbatim

Thirteen items, 1–7 Likert. Items 1–12 walk the diagnostic process; item 13 is the summary
judgment. Do **not** sum the items — the guide is explicit that they exist only to
structure the reviewer's thinking toward item 13.

Adjudication thresholds, per the guide:
- **Item 13 ≥5** → missed opportunity; route to a second reviewer.
- **Item 13 = 4** → second review as capacity allows. Given the stakes here, review all 4s.
- Disagreement between two reviewers → third reviewer or panel discussion.

Every reviewer writes a free-text rationale for item 13. This is not optional; it is the
material from which the system-factor profile and the quarterly vignettes are built.

**Do not rewrite the items into operational language.** The instrument's interrater
reliability is a property of its exact wording, and the guide explicitly cautions against
ad hoc adaptation outside research settings. Rewriting forfeits both the reliability
evidence and any ability to compare findings against the published benchmarks that give
this program its credibility.

### Add an operational context supplement

A separate adjunct instrument — not an edit to the Safer Dx items — capturing what the
civilian instrument has no field for:

**Context of the index encounter**
- Role of care (Role 1 BAS / sick call, Role 2, MTF primary care, MTF ED, purchased care)
- Setting (garrison, field exercise, shipboard, deployed)
- Clinician type and supervision (HM under IDC, IDC, PA, GMO, specialist)
- Diagnostic capability physically available: lab, plain film, ultrasound, i-STAT, none
- Was the limiting factor capability, access, or reasoning? *(single most important field)*

**Access and presentation**
- Interval from symptom onset to first presentation
- Any documented indication of delayed presentation, and stated reason
- Any documented command or duty pressure affecting evaluation, referral, or follow-up

**Continuity**
- Did the episode cross a unit movement, deployment, PCS, or provider turnover?
- Was any relevant prior documentation unavailable to the treating clinician?

**Duty-status outcome**
- Worst duty status attributable: none / light duty / LIMDU / MEB / separation / death
- Estimated duty days lost **beyond** what timely diagnosis would have cost
- Deployability affected: yes / no

That last block is what produces the readiness metric in
[`05-metrics.md`](05-metrics.md#the-two-that-go-on-the-command-brief). It is an estimate
and is labeled as one on every report.

### Then classify contributing factors

For confirmed events only: DEER taxonomy plus the Safer Dx Process Breakdown Supplement,
and NCC MERP severity. Record in CFER-DS-aligned fields from the beginning — retrofitting
common formats onto two years of accumulated free text is a project nobody completes.

## Reviewer training and calibration

Per the guide's Appendix F process, plus what an operational panel additionally needs:

1. **Read the source.** Singh, Khanna, Spitzmueller, Meyer. *Recommendations for using the
   Revised Safer Dx Instrument to help measure and improve diagnostic safety.* Diagnosis
   2019;6(4):315–23. Open access. Non-negotiable prerequisite.
2. **Pilot 10–20 cases** before any finding counts. Refine ambiguous language in the
   *local instructions* — never in the instrument.
3. **Establish κ** on the dual-reviewed sample. Below 0.60, stop and rebuild the shared
   mental model before adjudicating further.
4. **Build a local exemplar set.** Five to eight adjudicated cases with written rationales,
   used to onboard every new reviewer. Given GMO tour lengths, the panel turns over
   continuously and the exemplar set is the only thing that carries calibration across
   the turnover. **This is the highest-leverage durable artifact the program creates.**
5. **Recalibrate quarterly** against the exemplar set.

**Judge on the information available at the time.** Hindsight bias is the principal threat
to validity and it is worse in this population, because the outcome is often dramatic
and the index encounter is often a two-line sick call note. Reviewers must be trained
explicitly and repeatedly on this. The related discipline: a case escalating because a
correctly and timely diagnosed condition progressed is **not** a missed opportunity — the
instrument has a dedicated field for exactly this and reviewers must use it.

## Feedback

Two channels, kept strictly separate.

**System feedback — default, aggregate, wide.** Quarterly de-identified vignettes and the
system-factor Pareto to unit surgeons, IDCs, and corpsmen. This is where nearly all the
value is. The Measure Dx hierarchy of effectiveness is unambiguous that redesign,
forcing functions, and automation outperform education and retraining — so lead with what
was *changed*, not with what was found.

**Individual feedback — selective, private, non-punitive.** Following the Geisinger model
referenced in the guide's Appendix I: delivered in person by a trained facilitator, framed
as learning, never written into an evaluation. A clinician who learns that a case they
were involved in went to peer review and reappeared in their FITREP will end voluntary
reporting across the command permanently, and it will not come back during that
commander's tour.

The firewall between this program and credentialing action is described in
[`07-governance-and-policy.md`](07-governance-and-policy.md). Design it before the first
case, not after the first uncomfortable one.

## Case flow

```
Trigger fires (Tier 1–4)  ·  Report submitted (Tier 5)
                    │
                    ▼
        Analyst assembles episode packet
    (all encounters in look-back window, results,
     imaging, referrals, evacuation and disposition record)
                    │
                    ▼
        Reviewer 1 — Revised Safer Dx (13 items)
                    │
        ┌───────────┴───────────┐
   item 13 ≤3                item 13 ≥4
   close, log                     │
                                  ▼
                    Reviewer 2 — independent scoring
                                  │
                    ┌─────────────┴─────────────┐
                 agree                      disagree
                    │                           │
                    ▼                           ▼
      DEER + Breakdown Supplement      Panel adjudication
      + operational supplement
      + NCC MERP + duty-status
                    │
                    ▼
        System recommendation ─────────► action tracking to closure
        Individual feedback (if indicated, facilitated)
                    │
                    ▼
        Quarterly aggregation ─────────► metrics, Pareto, vignettes
```

Two hard rules on this flow:

**Anything meeting sentinel-event or standard-of-care criteria routes immediately to the
existing QA and risk pathway in parallel.** This program is additive. It never becomes
the reason a reportable event was not reported, and the panel needs a written trigger for
that hand-off before it starts work.

**The packet, not the note, is the unit of review.** If the analyst cannot assemble the
full episode, the case is deferred rather than adjudicated on a fragment — adjudicating
partial packets is how a program starts generating findings it cannot defend.
