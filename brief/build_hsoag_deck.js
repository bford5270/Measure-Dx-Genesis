/**
 * HSOAG Quality Line of Effort — brief deck.
 *
 * Four efforts, one measurement architecture:
 *   EWP  (LOE 1)  — Enterprise-Wide Privileging at I MEF, from the EWP context package
 *   CSC  (LOE 2)  — Crisis Standards of Care / PACE, from the Notion project charter
 *   SIM  (LOE 3)  — role2sim Monte Carlo, from docs/WHITE_PAPER.md
 *   MDX           — Measure Dx application to MHS GENESIS, this repository
 *
 * Build:  node brief/build_hsoag_deck.js
 */

const pptxgen = require("pptxgenjs");
const path = require("path");

// ---------------------------------------------------------------- palette
// Built from the PACE tier progression itself — the deck's visual motif.
const C = {
  ink: "12212B",       // deep petrol, dark ground
  paper: "FFFFFF",
  soft: "F2F5F4",
  primary: "1C5D66",   // deep teal
  sage: "7FA99B",
  accent: "C25E3A",    // burnt orange
  muted: "5A6B72",
  lightInk: "C9D6DB",
};

// PACE tiers — the repeating motif.
const PACE = [
  { k: "P", label: "PRIMARY", color: "2E7D5B" },
  { k: "A", label: "ALTERNATE", color: "B8912F" },
  { k: "C", label: "CONTINGENCY", color: "C25E3A" },
  { k: "E", label: "EMERGENCY", color: "9B2C2C" },
];

const HEAD = "Cambria";
const BODY = "Calibri";
const W = 13.333;
const H = 7.5;

// ---------------------------------------------------------------- content
// Every finding in this deck traces to a project document; see brief/README.md.
const EWP = {
  name: "EWP",
  expansion: "Enterprise-Wide Privileging",
  ask:
    "Advocate the successor instruction to BUMEDNOTE 6000 before its Nov 2026 cancellation, " +
    "and seek enterprise clarification on supervised privileges at operational platforms.",
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "CDR Brian S. Ford, MC, USN";
pres.title = "HSOAG Quality Line of Effort";

// ---------------------------------------------------------------- helpers

/** The four-segment PACE progression bar — the deck's repeating motif. */
function paceBar(slide, x, y, w, h, opts = {}) {
  const seg = w / 4;
  PACE.forEach((t, i) => {
    slide.addShape(pres.ShapeType.rect, {
      x: x + i * seg,
      y,
      w: seg,
      h,
      fill: { color: t.color },
    });
    if (opts.labels) {
      slide.addText(t.label, {
        x: x + i * seg,
        y: y + h + 0.04,
        w: seg,
        h: 0.22,
        fontSize: 8.5,
        fontFace: BODY,
        color: opts.labelColor || C.muted,
        align: "center",
        bold: true,
        charSpacing: 0.6,
        margin: 0,
      });
    }
  });
}

/** Standard light content slide with a title and an eyebrow label. */
function contentSlide(eyebrow, title) {
  const slide = pres.addSlide();
  slide.background = { color: C.paper };
  if (eyebrow) {
    slide.addText(eyebrow.toUpperCase(), {
      x: 0.62, y: 0.42, w: 8, h: 0.26,
      fontSize: 11, fontFace: BODY, color: C.accent,
      bold: true, charSpacing: 1.6, margin: 0,
    });
  }
  slide.addText(title, {
    x: 0.6, y: eyebrow ? 0.7 : 0.5, w: 12.1, h: 0.82,
    fontSize: 30, fontFace: HEAD, color: C.ink, bold: true, margin: 0,
  });
  paceBar(slide, 0.62, eyebrow ? 1.52 : 1.32, 1.5, 0.07);
  return slide;
}

/** A rounded content card with a heading and body lines. */
function card(slide, o) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h,
    fill: { color: o.fill || C.soft },
    rectRadius: 0.06,
    line: { color: o.fill || C.soft, width: 0 },
  });
  if (o.tag) {
    slide.addShape(pres.ShapeType.ellipse, {
      x: o.x + 0.26, y: o.y + 0.26, w: 0.42, h: 0.42,
      fill: { color: o.tagColor || C.primary },
    });
    slide.addText(o.tag, {
      x: o.x + 0.26, y: o.y + 0.26, w: 0.42, h: 0.42,
      fontSize: 13, fontFace: HEAD, color: "FFFFFF",
      bold: true, align: "center", valign: "middle", margin: 0,
    });
  }
  slide.addText(o.head, {
    x: o.x + (o.tag ? 0.82 : 0.3), y: o.y + 0.28, w: o.w - (o.tag ? 1.1 : 0.6), h: 0.4,
    fontSize: o.headSize || 15, fontFace: HEAD, color: o.headColor || C.ink,
    bold: true, valign: "middle", margin: 0,
  });
  if (o.lines && o.lines.length) {
    slide.addText(
      o.lines.map((t, i) => ({
        text: t,
        options: { bullet: true, breakLine: i !== o.lines.length - 1 },
      })),
      {
        x: o.x + 0.3, y: o.y + 0.78, w: o.w - 0.6, h: o.h - 1.05,
        fontSize: o.bodySize || 11.5, fontFace: BODY, color: o.bodyColor || C.muted,
        paraSpaceAfter: 5, margin: 0, valign: "top",
      }
    );
  }
  if (o.body) {
    slide.addText(o.body, {
      x: o.x + 0.3, y: o.y + 0.78, w: o.w - 0.6, h: o.h - 1.05,
      fontSize: o.bodySize || 11.5, fontFace: BODY, color: o.bodyColor || C.muted,
      margin: 0, valign: "top",
    });
  }
}

function footer(slide, text) {
  slide.addText(text, {
    x: 0.62, y: 6.98, w: 11.5, h: 0.24,
    fontSize: 9, fontFace: BODY, color: C.lightInk, italic: true, margin: 0,
  });
}

// ================================================================ 1. TITLE
{
  const s = pres.addSlide();
  s.background = { color: C.ink };

  s.addText("HSOAG QUALITY LINE OF EFFORT", {
    x: 0.9, y: 1.95, w: 11.5, h: 0.3,
    fontSize: 12.5, fontFace: BODY, color: C.sage,
    bold: true, charSpacing: 2.4, margin: 0,
  });
  s.addText("Measuring quality where\ncapability is not guaranteed", {
    x: 0.9, y: 2.4, w: 11, h: 1.7,
    fontSize: 42, fontFace: HEAD, color: "FFFFFF",
    bold: true, lineSpacing: 46, margin: 0,
  });
  s.addText(
    "Four efforts, one measurement architecture — Enterprise-Wide Privileging, Crisis Standards of Care, Simulation, and Diagnostic Safety",
    {
      x: 0.9, y: 4.25, w: 10.4, h: 0.5,
      fontSize: 14, fontFace: BODY, color: C.lightInk, margin: 0,
    }
  );

  paceBar(s, 0.9, 5.15, 5.0, 0.1, { labels: true, labelColor: C.sage });

  s.addText("CDR Brian S. Ford, MC, USN", {
    x: 0.9, y: 6.15, w: 7, h: 0.3,
    fontSize: 13, fontFace: BODY, color: "FFFFFF", bold: true, margin: 0,
  });
  s.addText("Chief Medical Officer, 1st Medical Battalion", {
    x: 0.9, y: 6.45, w: 7, h: 0.3,
    fontSize: 11.5, fontFace: BODY, color: C.lightInk, margin: 0,
  });
  s.addText("HSOAG · October 2026", {
    x: 9.0, y: 6.15, w: 3.4, h: 0.6,
    fontSize: 11.5, fontFace: BODY, color: C.sage,
    align: "right", valign: "middle", margin: 0,
  });
  s.addNotes(
    "Framing: these are not four separate projects competing for the same attention. " +
    "They are one architecture. Each answers a different question about the same problem — " +
    "how do we know the quality of medical care when the conditions that quality depends on are degrading."
  );
}

// ================================================================ 2. PROBLEM
{
  const s = contentSlide("The problem", "Quality is asserted, not measured");

  s.addText(
    "Garrison medicine measures quality against a stable standard. Operational medicine has no stable standard — capability degrades with logistics, evacuation, and personnel. We currently have no shared definition of what good care is at each level of degradation, no way to test a configuration before it deploys, and no systematic way to find what was missed after.",
    {
      x: 0.62, y: 1.85, w: 7.6, h: 1.6,
      fontSize: 14, fontFace: BODY, color: C.muted, lineSpacing: 21, margin: 0,
    }
  );

  const gaps = [
    ["No agreed standard", "JTS CPGs tier recommendations, but nothing links those tiers to operational triggers. Providers improvise the transition."],
    ["No prospective test", "Configuration decisions — team counts, billet substitutions, evacuation posture — are made SME-qualitatively, not quantitatively."],
    ["No retrospective detection", "Peer review samples records at random. In a young, healthy population that finds almost nothing."],
  ];
  gaps.forEach(([h, b], i) => {
    card(s, {
      x: 0.62 + i * 4.03, y: 3.62, w: 3.78, h: 2.05,
      tag: String(i + 1), tagColor: C.primary,
      head: h, headSize: 14.5,
      body: b, bodySize: 11.5,
    });
  });

  s.addText("MEASUREMENT GAP", {
    x: 8.68, y: 1.9, w: 3.84, h: 0.28,
    fontSize: 10, fontFace: BODY, color: C.accent, bold: true, charSpacing: 1.4, margin: 0,
  });
  s.addText("Every quality mechanism we own assumes the standard of care is fixed.", {
    x: 8.68, y: 2.25, w: 3.84, h: 0.95,
    fontSize: 16, fontFace: HEAD, color: C.ink, bold: true, lineSpacing: 22, margin: 0,
  });
  s.addText("In LSCO it is not.", {
    x: 8.68, y: 3.52, w: 3.84, h: 0.34,
    fontSize: 16, fontFace: HEAD, color: C.accent, bold: true, margin: 0,
  });

  footer(s, "Source: CSC PACE one-pager (09 May 2026); Measure Dx analysis, docs/01-why-random-review-fails.md");
  s.addNotes(
    "The three gaps map one-to-one onto the three lines of effort plus Measure Dx. " +
    "This slide is the reason the portfolio is coherent rather than opportunistic."
  );
}

// ================================================================ 3. ARCHITECTURE
{
  const s = contentSlide("How it fits together", "Four efforts, one architecture");

  s.addText(
    "Each effort answers a different question about the same problem. They share one currency — the PACE tier — and one measuring stick — the JTS CPGs.",
    { x: 0.62, y: 1.82, w: 11.9, h: 0.5, fontSize: 13.5, fontFace: BODY, color: C.muted, margin: 0 }
  );

  const flow = [
    { t: "EWP", q: "Who may practice here, and at what scope?", d: "Authorize the provider", color: C.sage, note: "LOE 1" },
    { t: "CSC / PACE", q: "What is good care, right now?", d: "Define the standard", color: C.primary, note: "LOE 2" },
    { t: "Simulation", q: "Where does the configuration break?", d: "Test before deploying", color: C.accent, note: "LOE 3" },
    { t: "Measure Dx", q: "What did we actually miss?", d: "Detect in the record", color: C.ink, note: "Enabling" },
  ];

  const cw = 2.72, gap = 0.42, x0 = 0.62;
  flow.forEach((f, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.55, w: cw, h: 2.75,
      fill: { color: C.soft }, rectRadius: 0.06,
      line: { color: C.soft, width: 0 },
    });
    s.addShape(pres.ShapeType.rect, { x: x + 0.28, y: 2.85, w: 0.5, h: 0.08, fill: { color: f.color } });
    s.addText(f.note.toUpperCase(), {
      x: x + 0.28, y: 3.02, w: cw - 0.56, h: 0.22,
      fontSize: 8.5, fontFace: BODY, color: C.muted, bold: true, charSpacing: 1.2, margin: 0,
    });
    s.addText(f.t, {
      x: x + 0.28, y: 3.26, w: cw - 0.56, h: 0.45,
      fontSize: 19, fontFace: HEAD, color: C.ink, bold: true, margin: 0,
    });
    s.addText(f.q, {
      x: x + 0.28, y: 3.78, w: cw - 0.56, h: 0.8,
      fontSize: 12.5, fontFace: BODY, color: f.color, bold: true, italic: true, margin: 0,
    });
    s.addText(f.d, {
      x: x + 0.28, y: 4.68, w: cw - 0.56, h: 0.45,
      fontSize: 12, fontFace: BODY, color: C.muted, margin: 0,
    });
    if (i < flow.length - 1) {
      s.addText("→", {
        x: x + cw + 0.02, y: 3.6, w: gap - 0.04, h: 0.4,
        fontSize: 17, color: C.lightInk, align: "center", valign: "middle", margin: 0,
      });
    }
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y: 5.6, w: 11.9, h: 0.92,
    fill: { color: C.ink }, rectRadius: 0.05, line: { color: C.ink, width: 0 },
  });
  s.addText(
    [
      { text: "The loop closes.  ", options: { bold: true, color: "FFFFFF" } },
      { text: "What Measure Dx detects in the record becomes the next scenario the simulation tests, and the next trigger the PACE framework names.", options: { color: C.lightInk } },
    ],
    { x: 1.0, y: 5.6, w: 11.1, h: 0.92, fontSize: 13, fontFace: BODY, valign: "middle", margin: 0 }
  );

  s.addNotes(
    "The point of this slide is that removing any one of the four leaves a gap the others cannot cover. " +
    "CSC without simulation is an untested assertion. Simulation without CSC has no outcome to report against. " +
    "Both without Measure Dx never learn from what actually happened."
  );
}

// ================================================================ 4. EWP
{
  const s = contentSlide("Line of effort 1", "Enterprise-Wide Privileging");

  s.addText(
    "Privileges are now MHS privileges — portable across the enterprise without a re-privileging action, held to the top of the provider's training rather than to the gaining facility's scope. The gaining command no longer adjudicates competence; it authorizes practice. For I MEF that means inheriting privileged providers on a five-business-day clock and catching the exceptions before arrival, not after.",
    { x: 0.62, y: 1.85, w: 7.55, h: 1.28, fontSize: 12.5, fontFace: BODY, color: C.muted, lineSpacing: 18, margin: 0 }
  );

  // The clock — the operative constraint for an operational command.
  const clock = [
    ["1 calendar day", "Clinician notifies the PA of orders"],
    ["24 hours", "MSP office reviews the credentials record"],
    ["5 business days", "Authorization complete — and before arrival"],
    ["Monthly, NLT 16th", "Data call to the Network lead"],
  ];
  s.addText("THE CLOCK", {
    x: 0.62, y: 3.3, w: 7.55, h: 0.24,
    fontSize: 10, fontFace: BODY, color: C.accent, bold: true, charSpacing: 1.4, margin: 0,
  });
  clock.forEach(([when, what], i) => {
    const y = 3.62 + i * 0.46;
    s.addShape(pres.ShapeType.ellipse, { x: 0.62, y: y + 0.08, w: 0.13, h: 0.13, fill: { color: C.sage } });
    s.addText(when, {
      x: 0.92, y, w: 1.92, h: 0.3,
      fontSize: 11.5, fontFace: BODY, color: C.ink, bold: true, margin: 0,
    });
    s.addText(what, {
      x: 2.92, y, w: 5.25, h: 0.3,
      fontSize: 11.5, fontFace: BODY, color: C.muted, margin: 0,
    });
  });

  card(s, {
    x: 8.42, y: 1.85, w: 4.1, h: 2.28,
    head: "Two hard stops", headSize: 14, headColor: C.accent,
    lines: [
      "Privileges expiring within 90 days — stop EWP, revert to legacy privileging",
      "Supervised privileges bound for an operational assignment — operational platforms cannot host them",
    ],
    bodySize: 10.5, fill: "FDF3EE",
  });

  card(s, {
    x: 8.42, y: 4.28, w: 4.1, h: 2.24,
    head: "I MEF posture", headSize: 14, headColor: C.primary,
    lines: [
      "PA is the I MEF Surgeon, delegated from the Medical Officer of the Marine Corps",
      "MEC is quarterly — not a fast path",
      "No local bylaws modifying the DHA baseline",
      "Reserve Component in scope since 27 May 2026",
    ],
    bodySize: 10.5, fill: C.soft,
  });

  // The two forms — what actually moves at a transfer.
  const forms = [
    ["DHA Form 456", "Authorization to practice + attestation, signed before arrival. No clinician practices without it; its signature date is the metrics completion marker.", C.primary],
    ["DHA Form 455", "The Performance Assessment Report. Clinical supervisor completes it on PCS or TDY over two weeks. Supersedes all MILDEP and CCQAS PARs — scaffold it, never author it.", C.accent],
  ];
  forms.forEach(([h, b, col], i) => {
    card(s, {
      x: 0.62 + i * 3.94, y: 5.38, w: 3.64, h: 1.48,
      head: h, headSize: 13, headColor: col, body: b, bodySize: 9.5, fill: C.soft,
    });
  });

  footer(s, "Source: DHA-PM 6025.13 Vol 8 (21 Oct 2025); BUMEDNOTE 6000 (25 Nov 2025); DHA Form 455 PAR fact sheet. All C&P content is MQA information under 10 U.S.C. §1102 and CUI.");
  s.addNotes(
    "The two hard stops are where transfers actually go wrong. Expiring-within-90-days is the most common way a case gets processed down the wrong track. " +
    "Supervised privileges at an operational platform drives more I MEF adjudication than anything else in the policy — and it is the same substitution question the simulation quantifies. " +
    "Note also that privilege duration is 3 years with NPDB Continuous Query enrollment and 2 years without, which is what sets the 90-day clock."
  );
}

// ================================================================ 5. CSC — the framework
{
  const s = contentSlide("Line of effort 2", "Crisis Standards of Care — a PACE framework");

  s.addText(
    "The USMC lacks a shared mental model for stepwise degradation of care standards during contested operations. JTS CPGs already tier recommendations. PACE supplies the decision framework that links those tiers to operational triggers — so every transition is planned, briefed, and recognized, not improvised.",
    { x: 0.62, y: 1.82, w: 11.9, h: 0.72, fontSize: 12.5, fontFace: BODY, color: C.muted, lineSpacing: 18, margin: 0 }
  );

  const rows = [
    [
      { text: "PACE LEVEL", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "JTS CPG TIER", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "CLINICAL POSTURE", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "TRANSITION TRIGGER", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
      { text: "ETHICAL FRAME", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
    ],
    [
      { text: "PRIMARY", options: { bold: true, color: PACE[0].color } },
      "Preferred (Best)",
      "Full Role 2 capability; component blood therapy, dual surgical teams, complete AMAL",
      "Class VIII resupply < 24 h; evacuation within doctrinal timelines",
      { text: "Prudence", options: { italic: true } },
    ],
    [
      { text: "ALTERNATE", options: { bold: true, color: PACE[1].color } },
      "Acceptable (Better)",
      "Degraded but capable; known substitutions within CPG",
      "Resupply 24–72 h; evacuation delayed but functional; key billets gapped",
      { text: "Prudence + Justice", options: { italic: true } },
    ],
    [
      { text: "CONTINGENCY", options: { bold: true, color: PACE[2].color } },
      "Minimum standard",
      "Capability gaps present; triage shifts to reverse triage protocols",
      "Resupply > 72 h or interdicted; evacuation non-functional; MASCAL",
      { text: "Justice + Courage", options: { italic: true } },
    ],
    [
      { text: "EMERGENCY", options: { bold: true, color: PACE[3].color } },
      "Below minimum",
      "Survivability focus for the unit; reverse triage to sustain the force",
      "Supply chain severed; no movement possible; comms degraded or lost",
      { text: "Courage + Temperance", options: { italic: true } },
    ],
  ];

  s.addTable(rows, {
    x: 0.62, y: 2.72, w: 11.9,
    colW: [1.55, 1.55, 3.35, 3.5, 1.95],
    rowH: [0.34, 0.72, 0.72, 0.72, 0.72],
    fontSize: 10, fontFace: BODY, color: C.muted,
    border: { type: "solid", color: "E2E8E7", pt: 1 },
    valign: "middle",
    margin: [4, 7, 4, 7],
    fill: { color: "FFFFFF" },
  });

  footer(s, "Source: CSC PACE one-pager v2 (09 May 2026). Co-authors: Dan Hanfling, MD and John L. Hick, MD — the architects of the civilian CSC field.");
  s.addNotes(
    "This table is the manuscript's centerpiece and the white paper's foundation. " +
    "The key move is that it requires no new doctrine — PACE and the JTS CPGs both already exist. " +
    "The virtue-ethics column is what makes the moral burden institutional rather than individual."
  );
}

// ================================================================ 6. CSC — status and path
{
  const s = contentSlide("Line of effort 2 · status", "Path to HSOAG, October 2026");

  const done = [
    "Three-imperative thesis (operational / moral / ethical)",
    "Co-authors secured — Hanfling and Hick",
    "PACE → JTS CPG → virtue-ethics mapping complete",
    "Rev 3 outline complete; ~30–35 references staged",
    "Worked vignette drafted; one-pager in circulation",
    "MAVEN / MedCOP institutional hook identified",
  ];
  card(s, {
    x: 0.62, y: 1.95, w: 5.75, h: 2.95,
    head: "Confirmed", headSize: 16, headColor: C.primary,
    lines: done, bodySize: 11.5, fill: C.soft,
  });

  const milestones = [
    ["Late Jun 2026", "Military Medicine Perspective submitted"],
    ["Aug 2026", "White paper draft v1"],
    ["Sep 2026", "Internal review — TMO, BUMED, JTS"],
    ["Oct 2026", "White paper delivered to HSOAG"],
  ];
  s.addText("MILESTONES", {
    x: 6.78, y: 2.23, w: 5.74, h: 0.24,
    fontSize: 10, fontFace: BODY, color: C.accent, bold: true, charSpacing: 1.4, margin: 0,
  });
  milestones.forEach(([when, what], i) => {
    const y = 2.62 + i * 0.58;
    s.addShape(pres.ShapeType.ellipse, {
      x: 6.78, y: y + 0.09, w: 0.14, h: 0.14,
      fill: { color: i === milestones.length - 1 ? C.accent : C.sage },
    });
    s.addText(when, {
      x: 7.08, y, w: 1.5, h: 0.32,
      fontSize: 11, fontFace: BODY, color: C.ink, bold: true, margin: 0,
    });
    s.addText(what, {
      x: 8.6, y, w: 3.92, h: 0.32,
      fontSize: 11, fontFace: BODY, color: C.muted, margin: 0,
    });
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y: 5.18, w: 11.9, h: 1.35,
    fill: { color: "FDF3EE" }, rectRadius: 0.05, line: { color: C.accent, width: 1 },
  });
  s.addText(
    [
      { text: "Critical path risk.  ", options: { bold: true, color: C.accent } },
      { text: "Military Medicine review-to-publication for Perspectives typically runs 4–8 months. Submission by late June is required for “in press” status by the October HSOAG.  ", options: { color: C.muted } },
      { text: "Decision needed: does “accepted / in press” suffice for TMO, or is full publication required?", options: { bold: true, color: C.ink } },
    ],
    { x: 1.0, y: 5.18, w: 11.1, h: 1.35, fontSize: 12.5, fontFace: BODY, valign: "middle", lineSpacing: 18, margin: 0 }
  );

  footer(s, "Recipient: DC I&L via The Medical Officer of the Marine Corps. CSC adoption is a logistics and resource-allocation policy decision.");
  s.addNotes("The ask on this slide is the publication-timing decision. It is the only thing on the critical path that someone else controls.");
}

// ================================================================ 7. SIMULATION
{
  const s = contentSlide("Line of effort 3", "Testing the configuration before it deploys");

  s.addText(
    "A glass-box discrete-event Monte Carlo of an integrated USMC Role 2 (STP → FRSS → Holding) under stochastic casualty flow and resource conditions. Outputs graded PACE tier distributions across a factorial sweep of configurations — the same PACE construct the CSC framework defines.",
    { x: 0.62, y: 1.82, w: 6.5, h: 1.15, fontSize: 12.5, fontFace: BODY, color: C.muted, lineSpacing: 18, margin: 0 }
  );

  const findings = [
    ["Crisis is the expected state", "Not the exception — the numerically expected operating state of a Role 2 in LSCO."],
    ["The top lever is a re-slate, not a buy", "Holding-OIC → intensivist re-slate: −1.80 DOW per scenario (9.7% of LSCO baseline), edging out +50% MEDEVAC slots."],
    ["The constraint is downstream of surgery", "Evacuation and holding critical care bind — not surgical capacity."],
  ];
  findings.forEach(([h, b], i) => {
    card(s, {
      x: 0.62, y: 3.12 + i * 1.18, w: 6.5, h: 1.05,
      head: h, headSize: 13, body: b, bodySize: 10.5, fill: C.soft,
    });
  });

  s.addImage({
    path: path.join(__dirname, "assets", "wp_fig1_tier_by_archetype.png"),
    x: 7.42, y: 2.05, w: 5.1, h: 2.83,
  });
  s.addText("PACE tier distribution by scenario archetype — role2-sim", {
    x: 7.42, y: 4.95, w: 5.1, h: 0.26,
    fontSize: 9.5, fontFace: BODY, color: C.muted, italic: true, align: "center", margin: 0,
  });

  card(s, {
    x: 7.42, y: 5.42, w: 5.1, h: 1.1,
    head: "Status", headSize: 13, headColor: C.accent,
    body: "Engine, PACE monitor, scenario library and analysis layers built and tested. Phase 8 calibration in progress; not yet SME face-validity reviewed.",
    bodySize: 10.5, fill: C.soft,
  });

  footer(s, "Source: role2sim docs/WHITE_PAPER.md rev. 3 (13 Jul 2026), post Phase-R1 corrections. Provisional parameters tracked in docs/OPEN_PROVISIONAL_PARAMS.md.");
  s.addNotes(
    "Be careful to state the limitation out loud: several parameters remain provisional and the model has not passed SME face validity. " +
    "The robust unconditional claim is the third one — the binding constraint is downstream of surgery. " +
    "The MEDEVAC-versus-intensivist ordering flips depending on transit mortality of un-operated evacuees, which is the single most decision-relevant open SME question."
  );
}

// ================================================================ 8. MEASURE DX
{
  const s = contentSlide("Enabling effort", "Finding what the record already knows");

  s.addText(
    "AHRQ's diagnostic safety construct, adapted to the operational forces and applied to MHS GENESIS. Replaces random chart sampling with triggers that sample backward from an outcome — the surgery, the MEDEVAC, the medical board — so the index note becomes judgeable.",
    { x: 0.62, y: 1.82, w: 7.4, h: 1.0, fontSize: 12.5, fontFace: BODY, color: C.muted, lineSpacing: 18, margin: 0 }
  );

  const stats = [
    ["0.2%", "Yield of random\nchart review", C.muted],
    ["31.8%", "Yield of triggered\nreview (AHRQ, 11 sites)", C.accent],
    ["24", "Operational triggers\nspecified", C.primary],
  ];
  stats.forEach(([n, l, col], i) => {
    const x = 0.62 + i * 2.55;
    s.addText(n, {
      x, y: 2.98, w: 2.5, h: 0.85,
      fontSize: 44, fontFace: HEAD, color: col, bold: true, margin: 0,
    });
    s.addText(l, {
      x, y: 3.86, w: 2.42, h: 0.66,
      fontSize: 10.5, fontFace: BODY, color: C.muted, margin: 0,
    });
  });

  s.addText(
    "A reviewer sampling 20 charts a quarter has a 73% chance of finishing an entire tour without ever encountering a harmful diagnostic event. That is not a program performing poorly — it is a program whose expected yield is near zero by construction.",
    { x: 0.62, y: 4.72, w: 7.4, h: 1.1, fontSize: 12, fontFace: BODY, color: C.ink, italic: true, lineSpacing: 18, margin: 0 }
  );

  card(s, {
    x: 8.35, y: 1.95, w: 4.17, h: 2.4,
    head: "Unique to the FMF", headSize: 14, headColor: C.primary,
    lines: [
      "A true denominator — unit rosters and DEERS",
      "Near-universal autopsy on active-duty death",
      "Guaranteed annual re-contact at PHA",
      "LIMDU / MEB as adjudicated outcomes",
    ],
    bodySize: 10.5, fill: C.soft,
  });
  card(s, {
    x: 8.35, y: 4.5, w: 4.17, h: 2.02,
    head: "Built and running", headSize: 14, headColor: C.accent,
    body: "Working tool reads a GENESIS extract and returns a FIN-keyed worklist of notes warranting review. 15 of 24 triggers implemented; 44 tests; runs today on synthetic data with no PHI.",
    bodySize: 10.5, fill: C.soft,
  });

  footer(s, "Source: AHRQ Pub. 22-0030; Bradford et al., J Gen Intern Med 2025;40(4):782–9. Repository: Measure-Dx-Genesis.");
  s.addNotes(
    "The 31.8% figure is the published multi-site result, not a projection. " +
    "Emphasize that this is the only one of the four efforts that already has running code against real data structures."
  );
}

// ================================================================ 9. INTERLOCK
{
  const s = pres.addSlide();
  s.background = { color: C.ink };

  s.addText("WHAT MAKES THIS ONE PROGRAM", {
    x: 0.62, y: 0.72, w: 8, h: 0.28,
    fontSize: 11, fontFace: BODY, color: C.sage, bold: true, charSpacing: 1.6, margin: 0,
  });
  s.addText("One currency, one measuring stick", {
    x: 0.62, y: 1.02, w: 11.9, h: 0.7,
    fontSize: 32, fontFace: HEAD, color: "FFFFFF", bold: true, margin: 0,
  });

  const links = [
    ["10 U.S.C. §1102 is the common legal substrate", "EWP already handles all credentialing content as protected medical quality assurance information. Measure Dx requires the same charter to function non-punitively. One protection, one handling channel — not four separate conversations with the judge advocate."],
    ["Scope of utilization is the PACE problem in credentialing language", "EWP privileges a provider to the top of their training, then states plainly that they may exercise only the privileges their current location supports. That gap between credential and capability is exactly what the PACE tiers describe as it widens."],
    ["The PACE tier is the shared unit of account", "CSC defines the tiers and their triggers; the simulation reports its outcomes as tier distributions. Both speak one language to a commander, and both surface in MedCOP via MAVEN."],
    ["Peer review is where all four already meet", "EWP needs SMART performance metrics for FPPE and OPPE. Measure Dx produces exactly that class of measure, with a true denominator. The recurring EWP product is already “forms to track peer review” — this supplies the content."],
  ];
  links.forEach(([h, b], i) => {
    const y = 1.98 + i * 1.28;
    s.addShape(pres.ShapeType.rect, { x: 0.62, y: y + 0.05, w: 0.07, h: 1.0, fill: { color: PACE[i].color } });
    s.addText(h, {
      x: 0.98, y, w: 11.5, h: 0.38,
      fontSize: 16, fontFace: HEAD, color: "FFFFFF", bold: true, margin: 0,
    });
    s.addText(b, {
      x: 0.98, y: y + 0.4, w: 11.4, h: 0.76,
      fontSize: 11.5, fontFace: BODY, color: C.lightInk, lineSpacing: 16, margin: 0,
    });
  });

  s.addNotes(
    "This is the slide to land if you only get one. Two of these four links were not visible until the lines of effort were put side by side. " +
    "The 1102 point is the practical one — charter Measure Dx as an MQA activity under the same authority EWP already operates under, and the protection question is answered once. " +
    "The scope-of-utilization point is the conceptual one: EWP and CSC are describing the same gap between what a provider is credentialed to do and what the location can actually support. " +
    "Closing thought if asked: take any one away and the others lose a function — an untested standard, an outcome with no definition, or a prediction never checked against what happened."
  );
}

// ================================================================ 10. ASKS
{
  const s = contentSlide("Decisions requested", "What we need from HSOAG");

  const asks = [
    ["EWP", EWP.ask, C.sage],
    ["CSC", "Confirm whether “accepted / in press” satisfies the citation requirement, and identify the I&L action officer to staff the white paper.", C.primary],
    ["Simulation", "Sponsor an SME face-validity review panel. The model cannot be cited in a decision until it has one.", C.accent],
    ["Measure Dx", "Authorize a 12-month pilot at one division, and name the analytic partner for the data extract.", C.ink],
  ];
  asks.forEach(([who, what, col], i) => {
    const y = 1.95 + i * 1.12;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.62, y, w: 11.9, h: 0.98,
      fill: { color: C.soft }, rectRadius: 0.05, line: { color: C.soft, width: 0 },
    });
    s.addShape(pres.ShapeType.rect, { x: 0.62, y, w: 0.09, h: 0.98, fill: { color: col } });
    s.addText(who, {
      x: 1.0, y, w: 2.2, h: 0.98,
      fontSize: 16, fontFace: HEAD, color: C.ink, bold: true, valign: "middle", margin: 0,
    });
    s.addText(what, {
      x: 3.25, y, w: 9.0, h: 0.98,
      fontSize: 12.5, fontFace: BODY, color: C.muted, valign: "middle", margin: 0,
    });
  });

  s.addText(
    "Common thread: none of these asks is a resourcing request. Each is a decision, an endorsement, or an authority — the things HSOAG is positioned to give and we cannot generate ourselves.",
    { x: 0.62, y: 6.5, w: 11.9, h: 0.42, fontSize: 12.5, fontFace: BODY, color: C.ink, bold: true, margin: 0 }
  );

  s.addNotes("Close on the common thread. It reframes the brief from four project updates into one governance request.");
}

// ---------------------------------------------------------------- write
const out = path.join(__dirname, "HSOAG_Quality_LOE.pptx");
pres.writeFile({ fileName: out }).then(() => console.log(`Wrote ${out}`));
