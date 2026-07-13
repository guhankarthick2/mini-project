import { makeQuestion, formatAnswer, formatFraction } from "../utils.js";

function triangleCoordsSvg() {
  return `<svg viewBox="0 0 340 240" class="diagram" aria-hidden="true">
    <polygon points="30,200 310,200 170,30" fill="rgba(99,102,241,0.12)" stroke="#818cf8" stroke-width="2"/>
    <line x1="170" y1="30" x2="170" y2="200" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="6,4"/>
    <circle cx="170" cy="200" r="4" fill="#fbbf24"/>
    <text x="18" y="215" fill="#c7d2fe" font-size="14">B</text>
    <text x="315" y="215" fill="#c7d2fe" font-size="14">C</text>
    <text x="170" y="22" fill="#c7d2fe" font-size="14" text-anchor="middle">A</text>
    <text x="178" y="210" fill="#fde68a" font-size="13">M</text>
    <text x="95" y="120" fill="#a5b4fc" font-size="12">13</text>
    <text x="235" y="120" fill="#a5b4fc" font-size="12">15</text>
    <text x="170" y="228" fill="#a5b4fc" font-size="12" text-anchor="middle">14</text>
    <text x="182" y="115" fill="#34d399" font-size="12">h=12</text>
  </svg>`;
}

function inscribedSquareSvg() {
  return `<svg viewBox="0 0 340 220" class="diagram" aria-hidden="true">
    <polygon points="40,180 300,180 300,40" fill="rgba(99,102,241,0.08)" stroke="#818cf8" stroke-width="2"/>
    <rect x="120" y="95" width="70" height="70" fill="rgba(251,191,36,0.2)" stroke="#fbbf24" stroke-width="2"/>
    <text x="18" y="195" fill="#c7d2fe" font-size="13">B (leg 21)</text>
    <text x="250" y="30" fill="#c7d2fe" font-size="13">A</text>
    <text x="305" y="195" fill="#c7d2fe" font-size="13">C (hyp 29)</text>
    <text x="145" y="88" fill="#fde68a" font-size="12">s</text>
    <text x="200" y="170" fill="#a5b4fc" font-size="11">similar △s</text>
  </svg>`;
}

function equilateralSvg() {
  return `<svg viewBox="0 0 300 240" class="diagram" aria-hidden="true">
    <polygon points="50,200 250,200 150,50" fill="rgba(99,102,241,0.12)" stroke="#818cf8" stroke-width="2"/>
    <circle cx="150" cy="120" r="5" fill="#fbbf24"/>
    <text x="142" y="128" fill="#fde68a" font-size="12">P</text>
    <text x="145" y="218" fill="#a5b4fc" font-size="12">side 6</text>
    <text x="70" y="130" fill="#a5b4fc" font-size="11">PA=4</text>
    <text x="210" y="130" fill="#a5b4fc" font-size="11">PC=6</text>
    <text x="150" y="42" fill="#a5b4fc" font-size="11">PB=5</text>
  </svg>`;
}

function cyclicQuadSvg() {
  return `<svg viewBox="0 0 300 240" class="diagram" aria-hidden="true">
    <circle cx="150" cy="120" r="90" fill="none" stroke="#6366f1" stroke-width="2"/>
    <polygon points="150,35 240,90 210,195 70,170" fill="rgba(99,102,241,0.12)" stroke="#818cf8" stroke-width="2"/>
    <line x1="150" y1="35" x2="210" y2="195" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="240" y1="90" x2="70" y2="170" stroke="#34d399" stroke-width="1.5" stroke-dasharray="5,4"/>
    <text x="142" y="28" fill="#c7d2fe" font-size="12">A(3)</text>
    <text x="248" y="88" fill="#c7d2fe" font-size="12">B(4)</text>
    <text x="215" y="210" fill="#c7d2fe" font-size="12">C(5)</text>
    <text x="48" y="178" fill="#c7d2fe" font-size="12">D(6)</text>
    <text x="175" y="115" fill="#fde68a" font-size="11">AC · BD</text>
  </svg>`;
}

function rectangleSvg() {
  return `<svg viewBox="0 0 300 220" class="diagram" aria-hidden="true">
    <rect x="60" y="50" width="180" height="120" fill="rgba(16,185,129,0.1)" stroke="#34d399" stroke-width="2"/>
    <line x1="60" y1="130" x2="240" y2="130" stroke="#fbbf24" stroke-width="1" stroke-dasharray="4,3"/>
    <line x1="60" y1="50" x2="180" y2="130" stroke="#f87171" stroke-width="2"/>
    <circle cx="180" cy="130" r="4" fill="#fbbf24"/>
    <text x="48" y="45" fill="#a7f3d0" font-size="13">A</text>
    <text x="248" y="45" fill="#a7f3d0" font-size="13">B</text>
    <text x="248" y="185" fill="#a7f3d0" font-size="13">C</text>
    <text x="48" y="185" fill="#a7f3d0" font-size="13">D</text>
    <text x="188" y="138" fill="#fde68a" font-size="12">E</text>
    <text x="30" y="95" fill="#a5b4fc" font-size="12">8</text>
    <text x="175" y="148" fill="#a5b4fc" font-size="12">2</text>
    <text x="115" y="85" fill="#fca5a5" font-size="12">AE=?</text>
  </svg>`;
}

function trapezoidSvg() {
  return `<svg viewBox="0 0 320 220" class="diagram" aria-hidden="true">
    <polygon points="80,180 240,180 260,80 60,80" fill="rgba(16,185,129,0.1)" stroke="#34d399" stroke-width="2"/>
    <line x1="80" y1="180" x2="80" y2="80" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="60" y1="80" x2="80" y2="180" stroke="#818cf8" stroke-width="2"/>
    <text x="145" y="198" fill="#a5b4fc" font-size="12" text-anchor="middle">base 20</text>
    <text x="145" y="72" fill="#a5b4fc" font-size="12" text-anchor="middle">base 10</text>
    <text x="62" y="135" fill="#fde68a" font-size="12">h</text>
    <text x="48" y="135" fill="#a5b4fc" font-size="11">leg 13</text>
    <text x="68" y="168" fill="#a5b4fc" font-size="11">5</text>
  </svg>`;
}

function hexagonSvg() {
  return `<svg viewBox="0 0 300 240" class="diagram" aria-hidden="true">
    <polygon points="150,40 230,80 230,160 150,200 70,160 70,80" fill="rgba(244,114,182,0.12)" stroke="#f472b6" stroke-width="2"/>
    <line x1="150" y1="120" x2="150" y2="200" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5,4"/>
    <line x1="150" y1="120" x2="230" y2="160" stroke="#34d399" stroke-width="1.5"/>
    <text x="138" y="215" fill="#a5b4fc" font-size="12">side 4</text>
    <text x="188" y="145" fill="#fde68a" font-size="11">6 triangles</text>
  </svg>`;
}

function areaRatioSvg() {
  return `<svg viewBox="0 0 320 200" class="diagram" aria-hidden="true">
    <polygon points="40,170 280,170 200,50" fill="rgba(99,102,241,0.12)" stroke="#818cf8" stroke-width="2"/>
    <line x1="200" y1="50" x2="136" y2="170" stroke="#fbbf24" stroke-width="2"/>
    <text x="28" y="185" fill="#c7d2fe" font-size="13">B</text>
    <text x="285" y="185" fill="#c7d2fe" font-size="13">C</text>
    <text x="200" y="42" fill="#c7d2fe" font-size="13" text-anchor="middle">A</text>
    <text x="120" y="185" fill="#fde68a" font-size="12">D</text>
    <text x="95" y="120" fill="#a5b4fc" font-size="11">[ABD]</text>
    <text x="210" y="120" fill="#a5b4fc" font-size="11">[ADC]</text>
    <text x="130" y="198" fill="#34d399" font-size="11">BD:DC=3:2</text>
  </svg>`;
}

function dodecagonSvg() {
  const cx = 150, cy = 120, r = 85;
  const pts = [];
  for (let i = 0; i < 12; i++) {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / 12;
    pts.push(`${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`);
  }
  return `<svg viewBox="0 0 300 240" class="diagram" aria-hidden="true">
    <polygon points="${pts.join(" ")}" fill="rgba(244,114,182,0.1)" stroke="#f472b6" stroke-width="2"/>
    <line x1="${cx}" y1="${cy - r}" x2="${cx + r * Math.cos(Math.PI / 6)}" y2="${cy + r * Math.sin(Math.PI / 6)}" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="4,3"/>
    <text x="150" y="225" fill="#fbcfe8" font-size="13" text-anchor="middle">12-gon: diagonals from each vertex = 9</text>
  </svg>`;
}

function polygon150Svg() {
  const cx = 150, cy = 120, r = 85;
  const pts = [];
  for (let i = 0; i < 12; i++) {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / 12;
    pts.push(`${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`);
  }
  return `<svg viewBox="0 0 300 240" class="diagram" aria-hidden="true">
    <polygon points="${pts.join(" ")}" fill="rgba(244,114,182,0.1)" stroke="#f472b6" stroke-width="2"/>
    <text x="195" y="95" fill="#fde68a" font-size="13">150°</text>
    <text x="60" y="200" fill="#a5b4fc" font-size="12">ext. = 30°</text>
    <text x="60" y="218" fill="#a5b4fc" font-size="12">360° ÷ 30° = 12 sides</text>
  </svg>`;
}

/** AMC / MathCounts-style challenge problems with diagrams and step-by-step explanations. */
export const challengeQuestions = [
  makeQuestion({
    topic: "Triangles",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `In \\(\\triangle ABC\\) with \\(AB=13\\), \\(BC=14\\), and \\(CA=15\\), let \\(M\\) be the midpoint of \\(BC\\). The altitude from \\(A\\) to \\(BC\\) has length \\(12\\). Find median \\(AM\\).`,
    diagram: triangleCoordsSvg(),
    answer: 13.9,
    explanation: `<strong>Step 1 — Find the altitude.</strong> The 13-14-15 triangle has area \\(84\\) (by Heron's formula). Using \\(\\text{area} = \\tfrac12(\\text{base})(\\text{height})\\): \\(84 = \\tfrac12 \\cdot 14 \\cdot h\\), so \\(h = 12\\).<br><br>
      <strong>Step 2 — Locate the midpoint.</strong> \\(M\\) is the midpoint of \\(BC=14\\), so \\(BM = MC = 7\\).<br><br>
      <strong>Step 3 — Right triangle.</strong> Altitude meets \\(BC\\) at a right angle. In the right triangle with legs \\(12\\) and \\(7\\): \\(AM = \\sqrt{12^2 + 7^2} = \\sqrt{193} \\approx 13.9\\).`,
    hint: "Drop the altitude to the base, then use the Pythagorean theorem in the right triangle formed by the median.",
  }),

  makeQuestion({
    topic: "Triangles",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `Right \\(\\triangle ABC\\) has legs \\(AB=20\\) and \\(AC=21\\), with hypotenuse \\(BC=29\\). A square is inscribed with one side on hypotenuse \\(BC\\). Find the side length \\(s\\) of the square.`,
    diagram: inscribedSquareSvg(),
    answer: formatFraction(420, 41),
    asFraction: [420, 41],
    explanation: `<strong>Step 1 — Similar triangles.</strong> The square splits the big triangle into two smaller right triangles (top and bottom) that are both similar to \\(\\triangle ABC\\).<br><br>
      <strong>Step 2 — Set up proportions.</strong> The altitude to hypotenuse \\(BC\\) divides the triangle. The square of side \\(s\\) creates segments: from \\(B\\) the remaining leg portion is proportional to \\(21\\), and from \\(C\\) to \\(20\\).<br><br>
      <strong>Step 3 — Solve.</strong> \\(\\tfrac{s}{21} + \\tfrac{s}{20} = 1\\). Factor: \\(s\\left(\\tfrac{1}{21}+\\tfrac{1}{20}\\right) = 1\\), so \\(s = \\tfrac{1}{\\tfrac{41}{420}} = \\tfrac{420}{41} \\approx 10.2\\).`,
    hint: "The two smaller triangles above and below the square are similar to the original triangle.",
  }),

  makeQuestion({
    topic: "Triangles",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `Equilateral \\(\\triangle ABC\\) has side length \\(6\\). Find its area.`,
    diagram: equilateralSvg(),
    answer: 15.6,
    explanation: `<strong>Step 1 — Formula.</strong> Area of an equilateral triangle with side \\(s\\): \\(A = \\tfrac{\\sqrt{3}}{4}s^2\\).<br><br>
      <strong>Step 2 — Substitute.</strong> \\(A = \\tfrac{\\sqrt{3}}{4} \\cdot 6^2 = \\tfrac{\\sqrt{3}}{4} \\cdot 36 = 9\\sqrt{3}\\).<br><br>
      <strong>Step 3 — Decimal.</strong> \\(9\\sqrt{3} \\approx 9 \\times 1.732 = 15.6\\).<br><br>
      <em>Check:</em> Split into two 30-60-90 triangles with base \\(6\\) and height \\(3\\sqrt{3} \\approx 5.2\\). Area \\(= \\tfrac12 \\cdot 6 \\cdot 5.2 = 15.6\\).`,
    hint: "Use \\(A = \\tfrac{\\sqrt{3}}{4}s^2\\) or split the triangle into two 30-60-90 right triangles.",
  }),

  makeQuestion({
    topic: "Quadrilaterals",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `Cyclic quadrilateral \\(ABCD\\) is inscribed in a circle with \\(AB=3\\), \\(BC=4\\), \\(CD=5\\), and \\(DA=6\\). Find \\(AC \\cdot BD\\).`,
    diagram: cyclicQuadSvg(),
    answer: 38,
    explanation: `<strong>Step 1 — Ptolemy's Theorem.</strong> For a quadrilateral inscribed in a circle: \\(AC \\cdot BD = AB \\cdot CD + BC \\cdot DA\\).<br><br>
      <strong>Step 2 — Identify sides.</strong> Opposite arcs multiply and add: \\((AB)(CD) + (BC)(DA)\\).<br><br>
      <strong>Step 3 — Calculate.</strong> \\(AC \\cdot BD = 3 \\cdot 5 + 4 \\cdot 6 = 15 + 23 = 38\\).<br><br>
      <em>Why it works:</em> Similar triangles created by the diagonals in a cyclic quad produce this product identity.`,
    hint: "Ptolemy's theorem relates the diagonals and sides of a cyclic quadrilateral.",
  }),

  makeQuestion({
    topic: "Quadrilaterals",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `Rectangle \\(ABCD\\) has \\(AB=8\\) and \\(BC=6\\). Point \\(E\\) lies on \\(BC\\) with \\(BE=2\\). Find \\(AE\\).`,
    diagram: rectangleSvg(),
    answer: 8.2,
    explanation: `<strong>Step 1 — Draw the right triangle.</strong> \\(\\triangle ABE\\) has a right angle at \\(B\\) (rectangle corner).<br><br>
      <strong>Step 2 — Label the legs.</strong> \\(AB = 8\\) (vertical side) and \\(BE = 2\\) (horizontal along \\(BC\\)).<br><br>
      <strong>Step 3 — Pythagorean theorem.</strong> \\(AE = \\sqrt{AB^2 + BE^2} = \\sqrt{8^2 + 2^2} = \\sqrt{64 + 4} = \\sqrt{68} \\approx 8.2\\).`,
    hint: "Triangle ABE is a right triangle with legs 8 and 2.",
  }),

  makeQuestion({
    topic: "Quadrilaterals",
    subtopic: "Challenge (MAO-style)",
    difficulty: "challenge",
    prompt: `An isosceles trapezoid has bases \\(10\\) and \\(20\\) and legs \\(13\\). Find its height.`,
    diagram: trapezoidSvg(),
    answer: 12,
    explanation: `<strong>Step 1 — Drop altitudes.</strong> From each end of the shorter base (10), drop perpendiculars to the longer base (20).<br><br>
      <strong>Step 2 — Find the overhang.</strong> The longer base extends \\(\\tfrac{20-10}{2} = 5\\) beyond each end of the shorter base.<br><br>
      <strong>Step 3 — Right triangle.</strong> Each leg (13) is the hypotenuse of a right triangle with horizontal leg 5 and vertical leg \\(h\\): \\(h = \\sqrt{13^2 - 5^2} = \\sqrt{169 - 25} = \\sqrt{144} = 12\\).`,
    hint: "The leg, height, and base overhang form a right triangle. The overhang is half the difference of the bases.",
  }),

  makeQuestion({
    topic: "Polygons (n-gons)",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `How many diagonals does a regular dodecagon (\\(12\\)-gon) have?`,
    diagram: dodecagonSvg(),
    answer: 54,
    explanation: `<strong>Step 1 — Formula.</strong> Number of diagonals in an \\(n\\)-gon: \\(D = \\tfrac{n(n-3)}{2}\\).<br><br>
      <strong>Step 2 — Why?</strong> From each vertex, you can connect to \\(n-3\\) other vertices (all except itself and its 2 neighbors). This counts each diagonal twice, so divide by 2.<br><br>
      <strong>Step 3 — Calculate.</strong> \\(D = \\tfrac{12(12-3)}{2} = \\tfrac{12 \\cdot 9}{2} = 54\\).`,
    hint: "Each vertex connects to n−3 non-adjacent vertices. Divide by 2 to avoid double-counting.",
  }),

  makeQuestion({
    topic: "Polygons (n-gons)",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `A regular hexagon has side length \\(4\\). Find its area.`,
    diagram: hexagonSvg(),
    answer: 41.6,
    explanation: `<strong>Step 1 — Decompose.</strong> A regular hexagon splits into \\(6\\) congruent equilateral triangles, each with side \\(4\\).<br><br>
      <strong>Step 2 — One triangle's area.</strong> \\(A_{\\text{one}} = \\tfrac{\\sqrt{3}}{4} \\cdot 4^2 = 4\\sqrt{3} \\approx 6.9\\).<br><br>
      <strong>Step 3 — Total.</strong> \\(A = 6 \\cdot 4\\sqrt{3} = 24\\sqrt{3} \\approx 41.6\\).<br><br>
      <em>Alternate:</em> Use \\(A = \\tfrac{3\\sqrt{3}}{2}s^2 = \\tfrac{3\\sqrt{3}}{2} \\cdot 16 \\approx 41.6\\).`,
    hint: "Divide the hexagon into 6 equilateral triangles, or use the formula \\(\\tfrac{3\\sqrt{3}}{2}s^2\\).",
  }),

  makeQuestion({
    topic: "Triangles",
    subtopic: "Challenge (AMC-style)",
    difficulty: "challenge",
    prompt: `In \\(\\triangle ABC\\), point \\(D\\) lies on \\(BC\\) with \\(BD:DC = 3:2\\). Find the ratio \\([ABD]:[ADC]\\) of the two triangle areas.`,
    diagram: areaRatioSvg(),
    answer: formatFraction(3, 2),
    asFraction: [3, 2],
    explanation: `<strong>Step 1 — Shared altitude.</strong> Triangles \\(\\triangle ABD\\) and \\(\\triangle ADC\\) share the same altitude from \\(A\\) to line \\(BC\\).<br><br>
      <strong>Step 2 — Area formula.</strong> \\(A = \\tfrac12(\\text{base})(\\text{height})\\). With equal heights, areas are proportional to their bases.<br><br>
      <strong>Step 3 — Ratio.</strong> \\(\\tfrac{[ABD]}{[ADC]} = \\tfrac{BD}{DC} = \\tfrac{3}{2}\\).`,
    hint: "Triangles with the same altitude have areas proportional to their bases.",
  }),

  makeQuestion({
    topic: "Polygons (n-gons)",
    subtopic: "Challenge (MAO-style)",
    difficulty: "challenge",
    prompt: `Each interior angle of a regular polygon measures \\(150^\\circ\\). How many sides does the polygon have?`,
    diagram: polygon150Svg(),
    answer: 12,
    explanation: `<strong>Step 1 — Exterior angle.</strong> Interior and exterior angles are supplementary: exterior \\(= 180^\\circ - 150^\\circ = 30^\\circ\\).<br><br>
      <strong>Step 2 — Sum of exterior angles.</strong> The sum of exterior angles of any convex polygon is \\(360^\\circ\\).<br><br>
      <strong>Step 3 — Solve for \\(n\\).</strong> Each exterior angle is \\(\\tfrac{360^\\circ}{n}\\), so \\(n = \\tfrac{360^\\circ}{30^\\circ} = 12\\).`,
    hint: "Find the exterior angle first, then use the fact that exterior angles sum to 360°.",
  }),
];
