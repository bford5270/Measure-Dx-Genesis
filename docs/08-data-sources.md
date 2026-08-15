# Data Sources and Access

The realistic assessment: **data access, not analytic difficulty, is the binding
constraint on this program.** The triggers are not hard to write. Getting authorized,
repeatable, linked access to the data they run against is the whole problem, and a design
that ignores this produces a beautiful catalog that never executes.

## The core recommendation

**Do not attempt to build analytic capability organically at the MEF.**

A MEF surgeon's staff will not obtain direct MHS GENESIS warehouse access, will not
maintain validated value sets, and will not sustain a linked longitudinal extract across
GENESIS, purchased care claims, personnel data, and mortality data. Every attempt to do
this locally stalls at the data use agreement.

Partner instead with an organization that already holds linked longitudinal data on
service members and already performs this class of epidemiology — the Armed Forces Health
Surveillance Division is the natural fit, and Navy Medicine clinical informatics or a
supporting NMRTC analytics cell are the secondary options. Bring them a defined trigger
specification and a defined question. That is a tractable ask. "Give us warehouse access"
is not.

**Keep locally only what must be local:** the reporting channels (T-21, T-22), the review
panel, the feedback loop, and the case tracking. Those need no special data access and can
start immediately.

## Source inventory

| Source | Holds | Feeds | Access reality |
|---|---|---|---|
| **MHS GENESIS** | Garrison encounters, orders, results, referrals, notes | Most triggers | Local read access is routine; *analytic extract* access is not |
| **CarePoint / Health Services Data Warehouse** | DHA reporting layer over GENESIS | Tiers 2, 4 | Via DHA; the realistic route to structured GENESIS data |
| **M2 (MHS Management Analysis and Reporting Tool)** | Direct and purchased care claims, encounters | Tiers 2, 3 | Account-based; widely used; **the most obtainable starting point** |
| **MDR / MART** | Enterprise repository, longitudinal | Dyads, intervals | Via analytic partner |
| **DMSS (Defense Medical Surveillance System)** | Longitudinal health + personnel + deployment, service-member-specific | Dyads, denominators, exposure restriction | Via AFHSD; **the best single fit for the dyad work** |
| **AFMES** | Autopsy and mortality | T-01 | Formal request; the highest-value source in the catalog |
| **JPSR** | Patient safety reports | T-21 cross-reference | Existing program access |
| **Naval Safety Command (RMI)** | Mishap investigations — heat, sickling, training deaths | T-24 | Existing safety channel; **needs no medical data agreement** |
| **Evacuation systems (e.g., TRAC2ES)** | Patient movement | T-03 | Via operational medical channels |
| **DEERS / MCTFS** | Roster, demographics, unit assignment | **Denominators**, T-19, T-20 | Personnel channels |
| **e-Profile / LIMDU / MEB systems** | Duty limitation and board adjudication | T-11, T-12, duty outcomes | Navy Medicine / PEB channels |
| **PHA / DOEHRS / deployment health assessments** | Annual and deployment screening | T-13, T-15 | Occupational health channels |

## Two structural gaps to plan around

### Field and deployed documentation is incomplete

Role 1 care in the field is documented variably — paper SF 600s, DD 1380 casualty cards,
and EHR coverage that is uneven afloat and in theater. Any trigger depending on structured
field encounter data will under-fire, and — worse — will under-fire *non-randomly*, biased
toward exactly the operational conditions the program most wants to understand.

**Plan accordingly:**
- **Phase 1 is garrison-only.** GENESIS capture is substantially complete there and the
  triggers will behave.
- For field and deployed episodes, use **outcome-anchored triggers that do not require the
  index encounter to be structured** — T-01 (death/autopsy), T-03 (MEDEVAC), T-04
  (exertional collapse), T-24 (mishap investigation). These fire on the downstream event,
  which is documented regardless, and the reviewer reconstructs the index encounter from
  whatever exists, including paper.
- **Report the documentation gap as a finding.** "The record was insufficient to determine
  what was done" is itself a system factor, it maps to DEER 2b/3b, and quantifying it is
  a legitimate and useful output. Do not treat undocumented episodes as clean.

### Purchased care lag

Marines receive substantial care from civilian facilities under TRICARE. Those encounters
appear in claims data, not in GENESIS, and they arrive with a lag of months. Trigger runs
that depend on purchased care must either accept the lag or accept incompleteness.

**Plan accordingly:** run Tier 2 and Tier 3 triggers on a rolling 90-day-lagged window,
and accept that near-real-time triggers are limited to sources with immediate capture —
which is most of Tier 1 and all of Tier 5.

## The denominator

The single asset most worth protecting. Unit rosters linked to encounter data give a true
population denominator — the thing civilian diagnostic safety research cannot obtain
because patients disappear into other systems.

Get the roster linkage right at the outset. Every rate in
[`05-metrics.md`](05-metrics.md) depends on it, and it is what allows the Marine Corps to
report a *rate* of diagnostic harm rather than a proportion of reviewed charts. No academic
medical center in the Measure Dx cohort could do that.

## Sequencing that does not wait on access

An honest reading of the access timeline says the analytic pipeline is a 6–12 month
proposition. The program does not have to wait for it.

| Start now — no new data access | Requires access |
|---|---|
| T-24 mishap investigation re-review | All Tier 2 triggers |
| T-21 diagnostic learning opportunity reports | All Tier 3 triggers |
| T-22 corpsman-initiated reports | Dyad analysis |
| T-01 via existing mortality notification | Loop-closure triggers |
| Panel formation, training, κ calibration | Interval and rate metrics |
| Exemplar case set development | Duty-days-lost estimates |
| Charter, firewall, legal review | |

**T-24 is the opening move.** Every exertional heat stroke, sickling event, and training
death already generated a thorough investigation containing detailed medical narrative.
That corpus exists, is already collected, requires no medical data use agreement, and can
be re-reviewed through a diagnostic safety lens starting the week the panel is trained.
It will produce real findings — and a trained, calibrated panel with a working exemplar
set — before the first data use agreement is signed.
