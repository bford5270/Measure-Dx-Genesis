# ACCEPT and CLOSE: templates and measures for primary care practices

This folder supports the article "ACCEPT and CLOSE: A Technology-Enabled Framework
for the 4 C's of Primary Care and a 7-Minute Note" (submitted to FPM, Family Practice
Management). It is the part of this repository written for a community primary care
practice. The rest of the repository is a diagnostic safety design for US Marine Corps
operating forces.

| File | What it holds |
|---|---|
| [`dotphrases.md`](dotphrases.md) | Note templates for the CLOSE lines and the open-loop ledger, ready to paste into an EHR text-macro tool |
| [`measures.md`](measures.md) | The measures that show whether the framework is working, and the 4 trigger queries from this repository that apply in any primary care practice |
| [`LICENSE`](LICENSE) | Creative Commons Attribution 4.0 International (CC BY 4.0) |

## Where to start

1. Paste `.CLOSE` and `.CLOSEOUT` from `dotphrases.md` into your EHR and use them for
   2 weeks.
2. Pull your baseline from the EHR audit-log report (time in notes per appointment,
   time to close the encounter) before changing anything else.
3. Take Table 1 of the article to whoever manages your EHR and ask which items the
   system can supply today.
4. Track the measures in `measures.md` monthly.

Nothing in this folder is clinical advice. The templates show a documentation pattern;
bracketed fields are left for the clinician.

## License and attribution

The contents of this folder are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may copy and adapt them,
including in your own EHR build, with credit:

> ACCEPT and CLOSE note templates, by Brian S. Ford, MD. CC BY 4.0.
> https://github.com/bford5270/Measure-Dx-Genesis/tree/main/accept-close

The license covers this folder only. The views expressed are those of the author and
do not necessarily reflect the official policy or position of the Department of the
Navy, Department of Defense, the Uniformed Services University, or the United States
Government.
