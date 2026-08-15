# Why Random Peer Review Cannot Find Diagnostic Error

Three independent failures. Each alone would be disqualifying. Fixing execution — more
reviewers, more charts, better forms — addresses none of them.

---

## 1. The arithmetic

Let `p` be the probability that a randomly drawn encounter belongs to an episode
containing a harmful missed diagnostic opportunity. Detection probability across `n`
sampled charts is `1 − (1 − p)^n`.

The true value of `p` in an operational-forces population is not published. The table
brackets it. A range of 0.1%–0.5% is generous for *harmful* misses in a young, healthy,
screened population.

| Charts reviewed | p = 0.1% | p = 0.2% | p = 0.5% |
|---|---|---|---|
| 20 (one quarter) | 2.0% | 3.9% | 9.5% |
| 80 (one year) | 7.7% | 14.8% | 33.0% |
| 160 (one two-year tour) | 14.8% | 27.3% | 55.1% |

Read the middle column. A provider performing conscientious random peer review at 20
charts per quarter has a **73% chance of completing an entire tour without ever sampling
a single harmful diagnostic event.** The expected number of such events they will
encounter across two years is 0.32.

This is not a program that is underperforming. It is a program whose expected yield is
approximately zero by construction, and which therefore returns "no findings" quarter
after quarter — a result that is then read as reassurance.

Scaling up does not rescue it. Reviewing 5% of a division's ~30,000 annual encounters
means 1,500 chart reviews. At the Measure Dx-documented 2–4 hours per structured review,
that is **3,000–6,000 reviewer-hours** to surface an expected 3 events.

## 2. The unit of analysis is wrong

Random review samples **encounters**. Diagnostic safety is a property of **episodes**.

> A Marine presents to sick call with anterior thigh pain after a hike. Exam is
> unremarkable. Assessment: muscle strain. Rest, ibuprofen, light duty 72 hours.
> He returns twice over five weeks, is treated the same way, and is eventually
> diagnosed with a displaced femoral neck stress fracture requiring surgical fixation
> and a medical board.

Pull that first note at random and review it. It is a defensible note. History taken,
exam documented, plan appropriate to the working diagnosis, follow-up given. A reviewer
scoring it in isolation passes it, correctly, on the information available.

The missed opportunity is not *in* the note. It is in the relationship between the note
and what came after. Measure Dx is explicit that the object of review is "all the care a
patient received over a given period of time for a specific health problem" — spanning
encounters, settings, and roles of care.

## 3. Random review samples at the wrong point in time

This is the subtlest failure and the one that explains why triggers work.

Effective detection is not `p`. It is `p × P(reviewer recognizes the miss | sampled)`.
A reviewer who lands on the index encounter is looking at an episode whose outcome has
not happened yet. They have no trajectory, no downstream diagnosis, no hindsight anchor.
That second term is small.

**Triggers invert the sampling direction.** They sample *from the outcome backward*: the
emergency surgery, the MEDEVAC, the autopsy, the medical board. By the time the case
reaches a reviewer, the trajectory is complete and the index encounter is legible. The
reviewer is asked the answerable question — *given how this ended, was there an earlier
opportunity?* — rather than the unanswerable one.

The two published sites cited in the Measure Dx guide reviewed trigger-identified records
and found improvement opportunities in **34%** (Regions Hospital, 184 cases) and **19%**
(UC San Diego, 346 cases). The 11-site Measure Dx evaluation found **31.8%** (224 of 703).

Against a random-review yield of roughly 0.2%, that is a **100- to 150-fold improvement
in the return on a reviewer-hour.**

---

## Two failure modes specific to the operating forces

**Reviewer independence collapses in small units.** A battalion has one medical officer
and an IDC. The "peer" reviewing the GMO is frequently the GMO from the adjacent
battalion, of similar rank, in the same regiment, with whom they will work for two more
years and who may write or influence their evaluation. Structural independence requires
that review be pooled above the unit — at minimum at division or MEF level.

**Provider-centric review misattributes system failure.** Peer review is built around
privileging: it asks whether *this provider* met the standard. But diagnostic safety in
an operational setting is dominated by factors no provider controls — no imaging past
plain film at Role 1, referral queues to the supporting MTF, results returning after the
ordering provider has detached, unit movement severing follow-up, and above all
**delay in presentation**, because Marines are culturally penalized for going to sick
call.

That last factor is the most important thing this program can measure. The Diagnostic
Error Evaluation and Research taxonomy opens with exactly this category —
*1a. Failure/delay in presentation.* Counting it converts a cultural problem that is
currently invisible into a number that belongs to the commander, not the corpsman.

---

## The recommendation is not "stop doing random review"

Retain a small random sample. It is the **control arm**. Without it there is no estimate
of the base rate, and therefore no way to demonstrate that triggers are lifting yield
rather than merely re-labeling cases that would have been caught anyway. It costs little
and it is what makes the program defensible when someone asks whether it is working.

Reallocate the *remainder* of review capacity to triggers. See
[`05-metrics.md`](05-metrics.md#the-random-arm-is-the-control-group-keep-it).
