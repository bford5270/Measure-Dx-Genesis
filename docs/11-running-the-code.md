# Running the Code

`mdxg` reads a medical record extract, applies the trigger catalog, and returns a
**FIN-keyed worklist of notes that may benefit from structured review.**

---

## Before you point this at real data

This is a compliance gate, not a checklist to skim. None of it is a code problem
and none of it can be fixed later.

- [ ] The program is chartered in writing as a **medical quality assurance
      activity** under the cognizant CQM authority, so 10 U.S.C. §1102 protection
      attaches ([`07-governance-and-policy.md`](07-governance-and-policy.md))
- [ ] A **data use agreement** covers every extract you will load
- [ ] Privacy Act / HIPAA review of this specific analytic flow is complete
- [ ] The host you run on is **authorized to process PHI** — this is not a laptop
      question, it is an ATO question
- [ ] Output storage is designated, access-controlled, and segregated from
      ordinary command files
- [ ] `MDXG_SALT` is generated, stored under the same protection as the data, and
      will not change between runs
- [ ] The **firewall** between this program and credentialing action is written
      and briefed

**The tool enforces none of this.** It will happily run against anything you feed
it. The gate is yours.

## What it does not do

- It does not write to MHS GENESIS or to any source system. Every code path is
  read-only.
- It does not determine that a missed opportunity occurred. **A trigger firing is
  a question.** Adjudication is a clinician task using the Revised Safer Dx
  Instrument ([`06-review-process.md`](06-review-process.md)).
- It does not evaluate providers. See the firewall.

---

## Install

```bash
pip install -e .          # or: pip install pandas numpy pyyaml requests
```

## Run it right now, with no access to anything

```bash
mdxg demo
```

Synthetic data, no PHI, no network. Generates background noise plus one planted
case per trigger and reports recall against that ground truth, so you can see
what the rules do before deciding whether to trust them.

```
Encounters scanned: 1,168
Trigger firings:    16
Distinct FINs flagged: 12 (1.0% of encounters)

Top of the review worklist (by FIN):
     fin index_date index_dx top_priority  n_triggers   triggers  review_score
F0001153 2024-07-19    R10.2    mandatory           2 T-05; T-10          11.5
F0001160 2024-04-30    B34.9    mandatory           2 T-02; T-10          11.5
F0001162 2024-07-29   R53.83    mandatory           1       T-01          10.0
...
Recall against planted cases:
  OK  T-01: 1/1   OK  T-10: 2/2   OK  T-19: 1/1   ...
```

## Run it against your extract

You will get flat files long before you get live query access. That is the
supported path.

```bash
mdxg init-mapping mapping.yaml     # writes a template
# edit the right-hand column names to match YOUR extract
mdxg run --mapping mapping.yaml --data ./extracts --out ./out --control-arm 40
```

The mapping maps canonical column names onto whatever your source calls them:

```yaml
encounters:
  file: encounters.csv
  columns:
    fin: FIN                    # <- your column name
    mrn: MRN
    start: ENCOUNTER_START
  constants:
    setting: GARRISON
  values:
    enc_class:
      "Outpatient": AMB
      "Emergency": EMER
```

**The column names in the template are illustrative.** They are a plausible shape
for an encounter extract, not a claim about the MHS GENESIS schema. Confirm them
against the extract you actually receive.

Delete any table you do not have. Rules degrade gracefully — a trigger with no
data returns nothing rather than failing, and the run logs what was missing.

### Output

```
out/review/     worklist_by_fin.csv     <- the reviewer's list. CONTAINS FINs. PHI.
                worklist_detail.csv        one row per firing
                control_arm.csv            the random control sample
out/analysis/   worklist_deid.csv       <- pseudonymized
                intervals.csv              symptom-to-diagnosis by dyad
                loop_closure.csv           process rates, no adjudication needed
```

Keep the two directories under different access control. `out/review` is the
working list; `out/analysis` is what leaves the program.

## Build the packet for a case

A reviewer handed a single note cannot score the instrument honestly — items 9,
11 and 12 all require the trajectory.

```bash
mdxg packet --fin F0001153 --mapping mapping.yaml --data ./extracts
```

```
EPISODE PACKET - index FIN F0001153
Window: 2024-01-21 to 2024-10-17

CHRONOLOGY
  2024-07-19  AMB   R1        FIN F0001153  R10.2 <== INDEX
  2024-07-23  EMER  MTF       FIN F0001154  N44.00

DISPOSITIONS
  2024-07-23  SURGERY_EMERGENT  N44.00
```

If the packet is incomplete the command says so. **Defer rather than adjudicate
on a fragment.**

## Calibrate a dyad before trusting it

The symptom side of every dyad ships uncalibrated. Until you fix that, `T-10`
falls back to a generic nonspecific-code definition and stamps
`[symptom set NOT locally calibrated]` into the reason string so the reviewer
knows.

```bash
mdxg calibrate --dyad D-B01 --mapping mapping.yaml --data ./extracts
```

```
Observed symptom categories preceding Femoral neck stress fracture (D-B01), window 90d:
category  patients  share  background  lift
     M79        34   0.61      0.2733  2.24
     M25        21   0.38      0.1904  1.98
```

This looks back from every confirmed case and reports what *actually* preceded
it, ranked by lift over background. Put the winners into
`symptom_codes_anchor` in `catalog/dyads.yaml`. This is the single highest-value
tuning step in the whole pipeline — an uncalibrated symptom set silently
under-fires.

## Compute metrics after a review round

The panel fills in an adjudications file:

| column | values |
|---|---|
| `fin` | the reviewed encounter |
| `arm` | `TRIGGERED` or `RANDOM_CONTROL` |
| `safer_dx_item13` | 1–7 |
| `missed_opportunity` | true/false (overrides item 13 if present) |
| `ncc_merp` | A–I |
| `duty_days_lost` | integer, beyond what timely diagnosis would have cost |
| `deployability_affected` | true/false |
| `primary_factor` | DEER category |

```bash
mdxg metrics --adjudications adj.csv --worklist out/review/worklist_detail.csv \
             --mapping mapping.yaml --data ./extracts --out ./out
```

Produces yield by trigger with Wilson confidence intervals, PPV lift against the
control arm, the retirement decision per trigger, detection density against the
roster denominator, and the harm and duty-status profile.

**Without `RANDOM_CONTROL` rows, PPV lift returns nothing** — deliberately. There
is no defensible lift figure without a base rate, and the tool will not invent
one ([`05-metrics.md`](05-metrics.md#the-random-arm-is-the-control-group-keep-it)).

---

## What is implemented

15 of the 24 catalog triggers are computable from record data:

| | |
|---|---|
| **Implemented** | T-01, T-02, T-03, T-05, T-06, T-07, T-08, T-09, T-10, T-11, T-12, T-16, T-17, T-19, T-20 |
| **Manual / solicited** | T-04, T-13, T-14, T-15, T-18, T-21, T-22, T-23, T-24 |

The manual set is not a gap. T-21 (diagnostic learning opportunity reports),
T-22 (corpsman-initiated), and T-24 (mishap cross-referral) are the ones the
published evaluation found highest-yield of all, and they are report streams, not
queries. Ingest them as a CSV with the same columns and concatenate onto the
worklist.

`tests/test_pipeline.py` (44 tests) covers rule recall against planted ground
truth, window boundary conditions on both sides, suppression logic, PHI handling,
and the metric math including the Wilson interval against the published
224/703 = 31.8% figure.

```bash
pytest -q
```

## The FHIR adapter

`mdxg.adapters.fhir` implements a read-only FHIR R4 client mapping
Encounter → encounters, Condition → diagnoses, Observation → results,
ServiceRequest → orders and referrals, using the standard R4 resource and search
parameter names and the Millennium identifier-type convention for pulling the FIN
off an Encounter.

**It has been exercised against synthetic bundles only and is unverified against
MHS GENESIS.** Before it touches a live endpoint you need an authorized client
registration, the correct base URL and tenant, scopes for those resources, and
written authority to extract PHI for a QA purpose.

It also pulls patient-by-patient, because that is what a normal non-bulk FHIR
authorization grants. For anything at division scale you want Bulk Data export or
a warehouse extract, not this — see [`08-data-sources.md`](08-data-sources.md).

---

## Known limits

**Relatedness is coarse.** Linking a follow-on encounter to an index encounter
uses the 3-character ICD-10 category. It will miss related presentations coded
across categories (`R10.9` abdominal pain → `N44.00` torsion is caught by the
dyad rules, not by the generic relatedness test). Dyads carry the
symptom-to-disease relationships; the relatedness test only groups repeat
presentations of the same complaint.

**Coding drives everything.** A sick call note carrying no diagnosis code is
invisible to most rules. Measure your coding completeness at Role 1 before
interpreting a low fire rate as good news.

**Field documentation is incomplete and the incompleteness is not random.** It is
biased toward exactly the operational conditions you most want to understand.
Phase 1 is garrison-only for this reason.

**Estimated volumes in the catalog are illustrative and unmeasured.** The
`est_volume_per_year` values are planning figures. Replace them with what the
tool actually reports on your data before using them for resourcing.

**`review_score` is a triage aid, not a probability.** It sorts the worklist. It
is not a measure and must not be reported as one.
