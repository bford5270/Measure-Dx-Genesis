# ACCEPT and CLOSE: note templates (dot-phrase library)

Version 1.1, November 2026. Companion to the article "ACCEPT and CLOSE: A
Technology-Enabled Framework for the 4 C's of Primary Care and a 7-Minute Note"
(submitted to FPM).

These are documentation patterns, not clinical advice. Paste them into your EHR's
text-macro tool (Epic SmartPhrases, Oracle Health auto-text, or the equivalent) and
adapt the pick lists to your practice. Bracketed fields are left blank on purpose.

Field conventions: `[___]` free text or date; `{a / b / c}` pick list, keep one.

## How the 2 checklists fit together

ACCEPT names 6 goals to weigh going into the visit: **A**genda setting,
**C**hief complaint or acute care, **C**hronic disease management,
**E**vidence-based prevention, **P**erson-centered assessment, and
**T**ransition and coordination.

CLOSE names up to 5 lines that end each problem in the assessment and plan:

| Line | What it records |
|---|---|
| **C** Clinical reasoning | The impression, and what was considered and excluded |
| **L** Loop owner | Who holds each pending result, referral, or callback |
| **O** Orders and options | What was ordered, the options considered, and what the patient decided; for a declined test or treatment, the risks of declining that were explained |
| **S** Safety-net | The specific warning signs and time frame for returning sooner |
| **E** Endpoint | When the problem is revisited: the result reviewed, acted on, and communicated to the patient (not merely arrived), with the failsafe if that does not happen |

A stable problem with nothing pending may need only the first line.

The design rule that joins the 2 checklists (no orphan loops) is that nothing leaves the
visit pending without an owner, a due date or trigger, and a failsafe the practice controls and will actually run. A patient can
own an action (returning a kit, having blood drawn); the failsafe belongs to the
practice. Document only the failsafes your systems or staff carry out.

---

## 1. `.CLOSE` : per-problem footer

```
A/P [problem] [optional tag, ACCEPT goal: {A agenda / C acute / C chronic / E prevention / P person-centered / T transition}]
C  [impression]; considered and excluded: [___]
L  {clinician / patient / specialist / lab / nurse pool / care team} owns [pending result / referral / titration / callback]
O  [orders]; options considered: [option 1 / option 2]; patient {agrees / declines / defers}{; risks of declining explained: [___]}
S  return sooner if [named warning signs] within [time frame]
E  closes when [result] is reviewed, acted on, and communicated {by [date] / when resulted}; failsafe: [task / reminder / outreach] if no result by [date], and [task] if a result is not communicated within [days] of arriving
```

## 2. `.CLOSE1` : stable problem, nothing pending

```
A/P [problem] [ACCEPT: {C chronic / E prevention / P person-centered}]
C  [status against goal; what was reviewed]; no change; nothing pending
```

## 3. `.CLOSEOUT` : visit-level open-loop ledger

One block at the end of the note. It gathers every L and E line into one list written
in plain language for 3 readers: the patient, the care team, and the next clinician.

```
OPEN-LOOP LEDGER
Addressed today: [___]
Not addressed today (on next agenda, not counted toward decision making): [___] -> [booked visit / date]

Item | Owner | Due date or trigger | Failsafe
[___] | {clinician / patient / specialist / lab / nurse pool} | [date / when resulted]; communicate within [days] | [task / reminder / outreach]
[___] | {___} | [___] | [___]

Results pending at signing: {none / [___]} -> tracked by {results inbox / nurse pool / [___]}
Next contact: {office / telehealth / portal / phone} on [date] {or result-triggered}
```

Keep the "Results pending at signing" line even when the answer is none, so that the next
reader can see the question was asked.

## 4. Weighted variants

The 5 lines stay the same, but the lines that need the most detail change with the type
of visit. The ACCEPT tag on each problem is optional and only records which goal the problem came from.

### `.CLOSEACUTE` : acute problem (most detail in S and E)

```
A/P [acute problem] [ACCEPT: C acute]
C  working diagnosis: [___]; red flags considered and excluded: [___]
L  pending: {none / [test], owner {clinician / lab}}
O  [treatment]; options considered: [___]; patient {agrees / declines}
S  return sooner if [named warning signs] within [time frame]; not improving by [time frame]: [contact route]
E  recheck {as needed / [date]} via {portal / phone / office}; failsafe: [___]
```

### `.CLOSECHRONIC` : chronic condition (most detail in C and L)

```
A/P [condition] [ACCEPT: C chronic]
C  {at goal / not at goal}; [measure] = [value]; reason for change: [___]
L  [next lab / titration check], owner {clinician / lab / patient}, by [date]
O  [start / continue / adjust ___]; options considered: [___]; patient {agrees / declines}
S  contact if [named symptom]
E  follow-up {[interval] / [date]} booked before leaving; failsafe if lab not done by [date]: [___]
```

### Other visit types

- Adult preventive visits: put most detail in O (screening chosen from named options)
  and L (result tracked to closure). The endpoint is usually result-triggered. A positive screening
  result opens a new loop (for example, a diagnostic referral) with its own owner.
- Well-child visits: put most detail in E (next immunization or milestone) and S
  (warning signs for the parent). The owner of the next-due loop is often the parent; the failsafe is
  still the practice's.
- Adolescent visits: put most detail in L (a confidential follow-up channel) and O
  (a confidential shared decision). Record the consent basis in O.

## Coding notes

- A problem deferred to another visit belongs on the ledger but does not count as
  addressed for medical decision making.
- Name the options in O. "Options discussed" alone does not show what was weighed.
- When the level is selected by time, write the actual total for that date and what
  it was spent on. Do not paste a generic time statement.
- Confirm against current CPT, your payers, and a certified coder.
