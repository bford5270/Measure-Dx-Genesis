# Governance, Legal Protection, and Policy Fit

> **Verify before briefing.** Citations below are by instruction number and subject.
> Network restrictions during drafting prevented retrieval of current full text for
> several of these. Confirm current versions, paragraph-level requirements, and the
> operative peer review sampling requirement with the cognizant CQM office before any of
> this is represented as authoritative. See [`10-open-questions.md`](10-open-questions.md).

## The protection that makes this possible

**10 U.S.C. § 1102 — Confidentiality of medical quality assurance records.**

This is the single most important legal fact for the program. §1102 protects DoD medical
quality assurance records from disclosure and constrains their use, including in most
adverse personnel and administrative actions. It is a stronger and more uniform protection
than most state peer review privileges.

Three consequences that must shape the design from day one:

1. **The protection attaches to a properly constituted MQA activity — not to good
   intentions.** Measure Dx makes the general version of this point: confidentiality and
   privilege protections "will likely only apply if specific requirements are followed,"
   including how the activity is chartered, how it is conducted, and where records are
   stored. Charter the program formally, in writing, as an MQA activity under the
   cognizant CQM authority, **before the first case is reviewed.**

2. **Records must be segregated.** MQA records held in ordinary command files, shared
   drives, or personal email are records the program may not be able to protect. Establish
   the storage location and access control at charter, not after the first request for
   the file arrives.

3. **Non-punitive framing is legally supportable, not merely aspirational.** The program
   can honestly tell clinicians and corpsmen that findings are protected — which is the
   precondition for the voluntary reporting channels (T-21, T-22) that the published
   evaluation found to be the highest-yield source of all.

Get the cognizant judge advocate and the CQM office involved at the charter stage. This is
a one-meeting task at the beginning and an unrecoverable problem later.

## The firewall

The program's credibility rests entirely on a boundary that must be written down and
briefed before the first case:

| | Diagnostic safety review (this program) | Credentialing / privileging action |
|---|---|---|
| Purpose | System learning | Individual competence determination |
| Default output | Aggregate, de-identified | Individual, attributed |
| Instrument | Revised Safer Dx | Existing QA investigation standards |
| Individual feedback | Facilitated, private, non-punitive, not in an evaluation | Formal, documented, reportable |
| Entry to the other track | **Only** via existing standard-of-care review criteria, applied independently | — |

**A finding of a missed opportunity is not a finding of substandard care.** These are
different determinations with different standards, and the Safer Dx Instrument does not
measure the second one. A missed opportunity may reflect a Role 1 capability limit, a
severed referral loop, an orphaned result, or a Marine who waited three weeks to come to
sick call — with no clinician performance issue anywhere in it. The instrument was built
to detect episodes worth learning from, not to adjudicate individual competence, and it
will produce wrong answers if used for the second purpose.

Cases meeting the *existing* threshold for standard-of-care review route to the *existing*
QA pathway, evaluated independently by that pathway's criteria and by people other than
the diagnostic safety panel. That routing must be written into the charter, briefed to
every reviewer, and briefed to every unit whose cases are reviewed.

If clinicians come to believe this program is a credentialing instrument in disguise, T-21
and T-22 volume goes to zero within a quarter, and it will not recover.

## Policy landscape

Where this sits in the existing structure. Confirm current versions.

| Authority | Subject | Relevance |
|---|---|---|
| **10 U.S.C. §1102** | MQA record confidentiality | The enabling protection |
| **DoDI 6025.13** | Medical quality assurance and clinical quality management in the MHS | Top-level QA framework |
| **DHA clinical quality management framework (2019)** | Credentialing/privileging, patient safety, risk management | The framework the services are directed to align to |
| **MCO 6320.4-series / OPNAVINST 6320.7-series** | Health services quality assurance for the operating forces | The order this program operates under; contains the current peer review requirement |
| **BUMEDINST 6010.13-series** | Navy Medicine QA program | MTF-side QA, credentials, peer review |
| **Joint Patient Safety Reporting (JPSR)** | DoD event reporting | Strategy B substrate; interoperate, do not duplicate |
| **AHRQ CFER-DS** | Common Formats for Event Reporting – Diagnostic Safety | Data standard for cross-unit aggregation |
| **Privacy Act / HIPAA** | PHI handling | Governs the data flows in [`08-data-sources.md`](08-data-sources.md) |

### Relationship to OPPE and non-privileged competency assessment

Privileged providers are subject to ongoing and focused professional practice evaluation;
non-privileged providers in the operating forces — IDCs, corpsmen — are subject to periodic
competency assessment by the privileging authority. Both requirements persist and this
program does not replace either.

Measure Dx itself lists "ongoing or focused professional practice evaluation, when
diagnosis-focused" as a legitimate Strategy A data source, so the flow **into** the
program is contemplated. The flow **out** is where the danger sits. Recommended posture:

- **Aggregate, de-identified diagnostic safety findings inform OPPE at the program level**
  — the unit's system-factor profile, the loop-closure rates, the interval measures.
- **Individual attributed findings do not flow to OPPE from this program.** They reach a
  clinician only through the facilitated feedback channel.
- **The only path to an individual competence determination is the existing QA pathway,
  entered on its own criteria.**

This distinction will be questioned by anyone who reads "peer review" and expects
individual accountability. The answer is empirical rather than philosophical: programs
that fuse learning and accountability channels stop receiving reports, and a program that
receives no reports finds nothing. The accountability channel already exists, already
works, and is not being weakened.

## The policy window

GAO has recently and repeatedly examined clinical quality management in DoD operational
settings — including field hospitals, aircraft carriers, and comparable environments —
and has recommended that the military departments finalize updated policies for provider
reviews and evaluations in those settings, noting that as of early 2026 the Army and Air
Force had not issued updated policies while the Navy had issued several.

Two implications:

1. Operational-setting clinical quality management is under active external scrutiny.
   A concrete, measured, defensible program in the Fleet Marine Force is well-timed.
2. Because Navy policy in this area is actively moving, **verify the current requirement
   before designing around it.** The specific random-sampling requirement this program is
   intended to displace may already have changed.

## Charter checklist

Before case one:

- [ ] Written charter as a formal MQA activity under the cognizant CQM authority
- [ ] Judge advocate review of §1102 applicability and record-handling requirements
- [ ] Designated protected storage location with documented access control
- [ ] Written firewall policy, briefed to reviewers and to participating units
- [ ] Written routing criteria for sentinel events and standard-of-care concerns
- [ ] Data use agreements for every source in [`08-data-sources.md`](08-data-sources.md)
- [ ] Privacy Act / HIPAA review of the analytic data flow
- [ ] Non-retaliation protection for corpsman-initiated reports (T-22), in writing
- [ ] Confirmation of the current peer review requirement and what may be reallocated
- [ ] Command messaging plan — this cannot be introduced as a medical-internal initiative
      if "delay in presentation" is going to be measured honestly
