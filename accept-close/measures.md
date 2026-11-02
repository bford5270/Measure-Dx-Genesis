# Measures that show whether ACCEPT and CLOSE is working

Track each measure monthly as a run chart, before and after each change. A fall in note
time accompanied by a rise in the balancing measures suggests that the work has moved to
someone else rather than been removed.

| Type | Measure | Source |
|---|---|---|
| Target | Median clinician time in notes per visit (7 minutes or less); 75th percentile (11 minutes or less); median time to close the encounter (same day) | EHR audit-log report (for example, time in notes per appointment) |
| Process | Share of notes signed the same day; share of ledger items with an owner, a due date or trigger, and a failsafe; share of problems with complete CLOSE lines | EHR report; monthly sample of 10 notes per clinician |
| Outcome | Abnormal results with documented patient notification; referrals with a completed appointment; trigger hits for results without follow-up and referrals not completed | Results and referral reports; trigger queries (below) |
| Balancing | Total EHR time per visit; EHR time outside scheduled hours; inbox time; EHR and task time for medical assistants and nurses | EHR audit-log report |
| Cost | Staff hours; build hours; scribe licenses; visits per week | Practice management records |

The 7-minute target comes from 2 audit-log studies of ambulatory clinicians
(Pearlman et al, JAMA Netw Open 2025; Harvey et al, JMIR Med Inform 2026). Both were
multispecialty, so a primary care practice should set its own baseline first.

## Trigger queries that transfer to any primary care practice

The trigger catalog in [`../catalog/triggers.yaml`](../catalog/triggers.yaml) was
written for US Marine Corps operating forces. These entries apply in any practice and
make outcome measures for the CLOSE lines:

| Trigger | What it finds | CLOSE line it tests | Coded in `mdxg` |
|---|---|---|---|
| T-07 | Emergency visit or hospitalization soon after an office visit for a related complaint | S (safety-net) | Yes |
| T-16 | Abnormal result without documented follow-up | L and E | Yes |
| T-17 | Referral ordered and not completed | L and E | Yes |
| T-06 | Third visit within 30 days for the same or a related complaint that ends in a different diagnosis, a referral, imaging, or admission | C (clinical reasoning) | Yes |

The code reads flat-file extracts from military record systems, needs adapting for other EHRs, and has been run only on synthetic data. Before
pointing it at real records, read [`../docs/11-running-the-code.md`](../docs/11-running-the-code.md).
A trigger hit identifies a chart for clinician review; it does not by itself show that an
error occurred.
