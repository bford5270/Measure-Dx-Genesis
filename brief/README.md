# HSOAG Quality Line of Effort — brief deck

`HSOAG_Quality_LOE.pptx` — 10 slides covering the quality line of effort as one
architecture rather than four projects.

| Slide | Content | Source |
|---|---|---|
| 1 | Title | — |
| 2 | The problem — quality is asserted, not measured | CSC one-pager; Measure Dx `docs/01` |
| 3 | Four efforts, one architecture | integrating argument |
| 4 | **EWP (LOE 1)** | **content pending** |
| 5 | CSC — the PACE × JTS CPG framework | CSC PACE one-pager v2 (09 May 2026) |
| 6 | CSC — path to HSOAG Oct 2026 | CSC project charter v0.2 |
| 7 | Simulation (LOE 3) — role2sim | `role2sim` docs/WHITE_PAPER.md rev. 3 |
| 8 | Measure Dx | this repository; AHRQ Pub. 22-0030 |
| 9 | What makes this one program | integrating argument |
| 10 | Decisions requested | all four |

Speaker notes are on every slide.

## Rebuild

```bash
npm install pptxgenjs        # once
node brief/build_hsoag_deck.js
```

## Filling in EWP

Everything EWP-specific is in the `EWP` object at the top of
`build_hsoag_deck.js`. Set `pending: false`, fill in `expansion` and the four
slots on slide 4, and update the EWP ask on slide 10. No other slide changes.

## Caveats carried into the deck

- Simulation figures are pre-SME-face-validity; several parameters remain
  provisional. Slide 7 says so, and the speaker note says it louder.
- The Measure Dx 31.8% is the published AHRQ multi-site result, not a local
  projection. Local yield is unmeasured.
- CSC timeline assumes the *Military Medicine* submission holds. The publication
  -timing decision on slide 6 is the live risk.
