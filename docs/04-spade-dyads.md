# Symptom–Disease Dyads for the USMC Risk Set

The operational engine behind trigger **T-10**. Machine-readable in
[`../catalog/dyads.yaml`](../catalog/dyads.yaml).

## Method

Adapted from the SPADE approach (Symptom-Disease Pair Analysis of Diagnostic Error). For
each dyad, define a **symptom presentation** (the way the condition first shows up, and
the benign label it typically receives), a **target disease**, and a **look-forward
window**. The trigger fires when an encounter carrying the symptom label is followed
within the window by an encounter carrying the target disease code. Review then extends
back to the first symptomatic encounter.

The window is the clinically defensible outer bound within which the earlier visit
should be considered part of the same diagnostic episode. Too short and real misses are
excluded; too long and the trigger fills with coincidental co-occurrence.

## Why this is tractable here and not in civilian practice

The civilian SPADE problem is open-ended because the population is unbounded in age and
comorbidity. The Fleet Marine Force is not. The population is young, screened at
accession, physically stressed in specific and predictable ways, and overwhelmingly free
of chronic disease. **The differential that actually kills or permanently disables a
21-year-old Marine is short enough to enumerate on two pages.** That is the entire reason
this design is feasible.

It also means the false-positive burden is lower: a 55-year-old with chest pain and eleven
comorbidities generates noise, a 21-year-old with chest pain does not.

---

## Tier A — Catastrophic or organ-threatening; hours to days

| Symptom presentation (typical benign label) | Target | Window | Note |
|---|---|---|---|
| Abdominal, groin, or flank pain; "epididymitis"; "hernia" | **Testicular torsion** (N44.00–N44.04) | 7 d | Salvage is time-dependent in hours. Any torsion with a preceding related visit is a mandatory review. |
| Abdominal pain (R10.-); "gastroenteritis"; "constipation" | **Appendicitis with perforation** (K35.2–K35.3) | 14 d | Perforation is the harm marker; simple appendicitis is not automatically a miss. |
| Back pain (M54.5-); "muscle strain"; "sciatica" | **Spinal epidural abscess** (G06.1), **cauda equina**, **vertebral osteomyelitis** (M46.2-) | 30 d | The classic outpatient catastrophe. Look for the documented red flags in Safer Dx item 4 — fever, IVDU, progressive deficit, bladder change. |
| Extremity pain after exertion; "shin splints"; "cramp" | **Nontraumatic compartment syndrome** (M79.A1-/M79.A2-) | 3 d | Chronic exertional compartment syndrome is common in this population; acute is the miss. |
| Cellulitis or abscess; "spider bite"; "boil" | **Necrotizing soft tissue infection** (M72.6) | 7 d | Pain out of proportion is the pivot. |
| Headache (R51.-); "dehydration"; "tension headache" | **SAH** (I60.-), **meningitis** (G00–G03), **cerebral venous thrombosis** (I67.6) | 14 d | |
| Neck pain after combatives, MVA, or parachute ops | **Cervical artery dissection** → **stroke** (I63.-, I65.-, I77.71) | 30 d | Specific to the training exposure profile; not on any civilian dyad list. |
| Dizziness (R42); "vertigo"; "dehydration" | **Posterior circulation stroke** (I63.-) | 30 d | The canonical published SPADE dyad. Low absolute incidence at this age but high harm. |
| Chest pain (R07.-); "costochondritis"; "anxiety" | **Myocarditis** (I40.-, I51.4), **PE** (I26.-), **ACS** (I21.-), **spontaneous pneumothorax** (J93.1-) | 30 d | Myocarditis is the age-appropriate one and is regularly labeled anxiety. |
| Dyspnea (R06.0-); "deconditioning"; "asthma" | **PE** (I26.-), **myocarditis** | 30 d | |
| Leg pain or swelling after injury, casting, or long transport | **DVT/PE** (I82.4-, I26.-) | 30 d | Strategic airlift and immobilization are unrecognized risk exposures in this population. |
| Pelvic or abdominal pain, female Marine | **Ectopic pregnancy** (O00.-), **ovarian torsion** (N83.5-), **tubo-ovarian abscess** (N70.-) | 14 d | Verify that a pregnancy test was documented — a single high-value process check. |
| Viral syndrome; "gastroenteritis"; "flu" | **Sepsis** (A41.-), **meningococcemia** (A39.-), **DKA** (E10.1-) | 7 d | The Rory Staunton case in the Measure Dx guide is exactly this dyad. |

## Tier B — Function- and career-threatening; weeks to months

| Symptom presentation (typical benign label) | Target | Window | Note |
|---|---|---|---|
| Hip, groin, or thigh pain; "muscle strain"; "hip flexor" | **Femoral neck / high-risk stress fracture** (M84.3- family) | 90 d | The highest-volume preventable disability in the infantry. Displacement is the harm marker and is frequently preventable. |
| Scrotal complaint; "epididymitis"; "varicocele" | **Testicular cancer** (C62.-) | 180 d | Peak incidence is exactly this age and sex. A treated-and-not-resolved epididymitis without ultrasound is the signature failure. |
| Joint pain or effusion; "sprain"; "overuse" | **Septic arthritis** (M00.-), **inflammatory arthropathy** (M05–M08, M45) | 60 d | |
| Fatigue (R53.8-); "overtraining"; "poor sleep hygiene" | **Leukemia / lymphoma** (C81–C96), **hypothyroidism** (E03.-), **T1DM** (E10.-), **anemia** (D50–D64) | 180 d | Long window by design; the metric of interest is the interval, not the binary. |
| Skin lesion; "mole"; "wart" | **Melanoma** (C43.-) | 365 d | Occupational UV exposure is extreme and rarely counted as an exposure. |
| Exertional collapse or heat illness (T67.-) | **Exertional sickling** (D57.3 + rhabdomyolysis M62.82), **occult cardiac disease** | Immediate | Feeds T-04. The look-back question is whether a prodrome was documented and dismissed. |
| "Adjustment disorder"; "stress"; "malingering" | **Suicide attempt** (T14.91), **psychiatric admission**, **missed TBI** (S06.-), **substance use disorder** (F10–F19) | 90 d | The most under-instrumented dyad in military medicine and probably the highest-harm one. |
| Post-blast or post-concussive somatic complaint | **TBI under-recognition** (S06.-) | 90 d | Under-recognition rather than misdiagnosis; the review question is whether screening was performed at all. |
| Dysmenorrhea; "normal periods" | **Endometriosis** (N80.-) | 365 d | Diagnostic delay here is measured in years across all populations; the interval is the metric. |
| Fever after deployment or travel | **Malaria** (B50–B54), **dengue** (A90–A91), **leptospirosis** (A27.-), **Q fever** (A78) | 30 d | Restrict to Marines with documented deployment or travel exposure; otherwise the trigger is all noise. |
| Joint or neurologic complaint after diving or flight | **Decompression sickness** (T70.3-), **AGE** (T70.-) | 7 d | Restrict to dive- and flight-qualified populations. |

---

## Implementation notes for the analyst

**Codes shown are representative anchors, not validated value sets.** Each dyad needs a
value set built and validated against the local data before use — including the symptom
side, which is the harder half. Nonspecific symptom coding in MHS GENESIS varies by
provider and by role of care, and a value set that misses how corpsmen and GMOs actually
code will silently under-fire.

**Build the symptom side from observed data, not from a textbook.** Pull the actual
distribution of index codes preceding confirmed cases of each target condition for the
last three years, and let that define the symptom value set. This is the difference
between a trigger that fires and one that does not.

**Restrict by exposure where the dyad demands it.** The deployment-fever and dive dyads
are useless without an exposure denominator and will generate pure noise if run against
the whole population.

**Run the highest-value dyads first.** For an initial pilot: femoral neck stress fracture,
testicular torsion and testicular cancer, spinal epidural abscess, PE/myocarditis, and
the behavioral health dyad. These five cover the largest share of preventable harm and
preventable duty-day loss in this population, and each has an unambiguous target code.

**Expect the interval, not the count, to be the useful output.** For Tier B especially,
most cases will not be adjudicated as missed opportunities. The **median
symptom-to-diagnosis interval** across all cases in a dyad is a stable, sensitive,
trendable measure that does not require adjudicating every case — and it is the metric
that moves when the program works ([`05-metrics.md`](05-metrics.md)).
