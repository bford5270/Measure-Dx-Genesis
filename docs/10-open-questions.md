# Open Questions and Verification Requirements

What in this repository is grounded, what is estimated, and what must be confirmed before
any of it is briefed as fact.

## Grounded in source

Verified against the Measure Dx guide (AHRQ Pub. No. 22-0030, July 2022) and the
peer-reviewed evaluation:

- The four strategies, the four-part structure, the Safer Dx Framework's five components
- The Revised Safer Dx Instrument — 13 items, 1–7 scale, item 13 as the summary judgment,
  no summing, ≥5 as the threshold for a second review
- The DEER taxonomy structure and the Safer Dx Process Breakdown Supplement contents
- The guide's statement that it "does not prescribe specific metrics"
- The guide's caution against ad hoc adaptation of review tools
- **31.8% yield (224 of 703 cases) across 11 organizations** — Bradford A, Tran A, Ali KJ,
  et al. *Evaluation of Measure Dx, a Resource to Accelerate Diagnostic Safety Learning and
  Improvement.* J Gen Intern Med. 2025;40(4):782–9. Retrieved via PubMed.
  [DOI](https://doi.org/10.1007/s11606-024-09132-8)
- Patient-reported data (Strategy C) yielded few reviewed cases and no confirmed learning
  opportunities in that evaluation
- The two published trigger-review sites: 34% of 184 cases (Regions Hospital) and 19% of
  346 cases (UC San Diego); 2–4 hours per review including feedback
- Measure Dx concept paper — Bradford A, Shofer M, Singh H. *Measure Dx: Implementing
  pathways to discover and learn from diagnostic errors.* Int J Qual Health Care.
  2022;34(3). Retrieved via PubMed. [DOI](https://doi.org/10.1093/intqhc/mzac068)

Sourced from PubMed; both DOIs above are the primary references for the yield figures used
throughout this repository.

## Estimated — must be replaced with measured values

**Every volume and yield figure in [`03-signal-catalog.md`](03-signal-catalog.md) is an
illustrative planning estimate.** None has been run against data. They are internally
consistent and derived from a stated model (10,000 Marines, ~30,000 encounters/year), and
they are adequate for scoping a pilot. They are not adequate for a resourcing decision and
must not be presented as observed.

Also estimated:

- The base rate `p` used in the random-sampling arithmetic. The 0.1–0.5% bracket is a
  reasoned range for *harmful* missed diagnoses in a young, screened population, not a
  measured value. The conclusion is robust across the whole bracket — but the arithmetic
  should be re-run with a locally measured `p` from the random control arm as soon as one
  exists.
- The 200 cases/year steady state and the ~0.3 FTE derived from it.
- All dyad look-forward windows. Clinically reasoned, not empirically optimized. They
  should be tuned against observed data once the dyads run.
- ICD-10 codes in the dyad catalog are **representative anchors, not validated value
  sets.** Several were confirmed against the current code set during drafting; the
  symptom-side sets in particular must be built from observed local coding patterns.

## Must be verified before briefing

Network egress restrictions during drafting blocked retrieval of full text from `ahrq.gov`,
`marines.mil`, `med.navy.mil`, and `gao.gov`. The following are cited by number and
subject from search results and general knowledge, and **must be confirmed against current
full text**:

| Item | What to confirm | Who |
|---|---|---|
| **MCO 6320.4-series** | Current version; the **actual** peer review sampling requirement — how many records, selected how, how often, by whom. The premise that current practice is random sampling is drawn from the user's own description and general practice, not from verified text. | MEF/Division CQM |
| **10 U.S.C. §1102** | Exact scope of protection; what a "properly constituted MQA activity" requires; record storage and access requirements | Judge advocate |
| **DoDI 6025.13** | Current version; operational-setting applicability | CQM office |
| **DHA CQM framework** | Current guidance and how the Navy has implemented it for operating forces | CQM office |
| **BUMEDINST 6010.13-series** | Current version; MTF-side interface | Navy Medicine |
| **GAO-25-106445 / GAO-26-107979** | Findings and recommendations on operational-setting clinical quality management, and current DoD response status | Direct read |
| **JPSR** | Whether a diagnostic safety category exists or can be added; current reporting volume from FMF units | Patient safety |
| **AFMES** | Actual autopsy coverage rate for active-duty deaths, and the request process for QA purposes | AFMES |

The AFMES verification matters most. **The claim that autopsy coverage of active-duty
deaths approaches universal is the strongest single argument in this design.** Confirm the
actual rate and the actual process for obtaining reports for a quality assurance purpose
before it goes on a slide.

## Genuinely unknown

Questions this design raises and cannot answer:

1. **What is the actual diagnostic safety event rate in the FMF?** Nobody knows. No one has
   measured it with a real denominator. This program would produce the first credible
   estimate — which is a research contribution, not just a QA improvement, and is worth
   framing that way when seeking support.

2. **How much of the harm is delay in presentation rather than clinical performance?** The
   working hypothesis in [`05-metrics.md`](05-metrics.md#4-system-factor-profile) is that
   it is the dominant factor. If true, the highest-yield intervention is a command
   conversation about sick call culture, not a clinical one. If false, that materially
   changes the program's emphasis. This is the most important empirical question here and
   it is answerable within one year.

3. **Do the loop-closure triggers (T-19, T-20) fire at the volume expected?** Test-pending-
   at-movement and result-after-detachment have no civilian analog and no published base
   rate. They may be the highest-yield triggers in the catalog or they may be noise.

4. **Will the corpsman channel (T-22) function?** It depends entirely on whether
   non-retaliation protection is believed. There is no way to know in advance.

5. **What is field documentation completeness, and how biased is it?** This determines how
   much of the program can extend beyond garrison. It is measurable early and should be
   measured early, because a non-random documentation gap biased toward field and deployed
   conditions is a threat to every conclusion the program draws about operational care.

## Repository status

Design document. No trigger has been executed. No case has been reviewed. Nothing here has
been staffed through any CQM authority.
