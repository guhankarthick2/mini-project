import {
  randInt,
  pick,
  pythagoreanTriple,
  formatFraction,
  makeQuestion,
} from "../utils.js";

function triangleSvg(labels = {}) {
  const { A = "A", B = "B", C = "C", extras = "" } = labels;
  return `<svg viewBox="0 0 320 220" class="diagram" aria-hidden="true">
    <polygon points="40,180 280,180 160,40" fill="rgba(99,102,241,0.12)" stroke="#818cf8" stroke-width="2"/>
    <text x="28" y="195" fill="#c7d2fe" font-size="14">${B}</text>
    <text x="285" y="195" fill="#c7d2fe" font-size="14">${C}</text>
    <text x="160" y="28" fill="#c7d2fe" font-size="14" text-anchor="middle">${A}</text>
    ${extras}
  </svg>`;
}

export const triangleGenerators = {
  supplementary_angles: () => {
    const a = randInt(35, 75);
    const b = randInt(40, 85);
    const c = 180 - a - b;
    const variant = pick(["triangle", "linear", "exterior"]);
    if (variant === "linear") {
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Supplementary Angles",
        prompt: `Points \\(D\\), \\(E\\), and \\(F\\) are collinear with \\(E\\) between \\(D\\) and \\(F\\). Ray \\(EG\\) forms angles \\(\\angle DEG = ${a}^\\circ\\) and \\(\\angle GEF = ${b}^\\circ\\). Find \\(m\\angle DEG + m\\angle GEF\\).`,
        answer: 180,
        explanation: `Angles on a straight line are supplementary, so \\(m\\angle DEG + m\\angle GEF = 180^\\circ\\). Here \\(${a}^\\circ + ${b}^\\circ = ${a + b}^\\circ\\), and since the rays form a straight angle at \\(E\\), the two adjacent angles must sum to \\(180^\\circ\\).`,
      });
    }
    if (variant === "exterior") {
      const interior = randInt(28, 62);
      const exterior = 180 - interior;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Supplementary Angles",
        prompt: `In \\(\\triangle ABC\\), side \\(BC\\) is extended past \\(C\\) to point \\(D\\). If \\(m\\angle ACB = ${interior}^\\circ\\), find the exterior angle \\(m\\angle ACD\\).`,
        diagram: triangleSvg({
          extras: `<line x1="280" y1="180" x2="310" y2="180" stroke="#fbbf24" stroke-width="2"/><text x="300" y="170" fill="#fde68a" font-size="13">D</text>`,
        }),
        answer: exterior,
        explanation: `An exterior angle and its adjacent interior angle are supplementary: \\(m\\angle ACD + m\\angle ACB = 180^\\circ\\). So \\(m\\angle ACD = 180^\\circ - ${interior}^\\circ = ${exterior}^\\circ\\).`,
      });
    }
    return makeQuestion({
      topic: "Triangles",
      subtopic: "Supplementary Angles",
      prompt: `In \\(\\triangle ABC\\), \\(m\\angle A = ${a}^\\circ\\) and \\(m\\angle B = ${b}^\\circ\\). Find \\(m\\angle C\\).`,
      diagram: triangleSvg(),
      answer: c,
      explanation: `The interior angles of a triangle sum to \\(180^\\circ\\): \\(m\\angle C = 180^\\circ - ${a}^\\circ - ${b}^\\circ = ${c}^\\circ\\).`,
    });
  },

  pythagorean_theorem: () => {
    const scale = pick([1, 2, 3, 4, 5]);
    const [a, b, c] = pythagoreanTriple(scale);
    const ask = pick(["leg", "hypotenuse", "altitude"]);
    if (ask === "hypotenuse") {
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Pythagorean Theorem",
        prompt: `A right triangle has legs of lengths \\(${a}\\) and \\(${b}\\). Find the hypotenuse.`,
        answer: c,
        explanation: `By the Pythagorean theorem: \\(c = \\sqrt{${a}^2 + ${b}^2} = \\sqrt{${a * a} + ${b * b}} = \\sqrt{${c * c}} = ${c}\\).`,
      });
    }
    if (ask === "leg") {
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Pythagorean Theorem",
        prompt: `A right triangle has hypotenuse \\(${c}\\) and one leg \\(${a}\\). Find the other leg.`,
        answer: b,
        explanation: `\\(b = \\sqrt{c^2 - a^2} = \\sqrt{${c}^2 - ${a}^2} = \\sqrt{${c * c - a * a}} = ${b}\\).`,
      });
    }
    const num = a * b;
    const frac = [num, c];
    const decimal = num / c;
    return makeQuestion({
      topic: "Triangles",
      subtopic: "Pythagorean Theorem",
      difficulty: "challenge",
      prompt: `In a right triangle with legs \\(${a}\\) and \\(${b}\\) and hypotenuse \\(${c}\\), an altitude is drawn from the right angle to the hypotenuse. Find the length of that altitude.`,
      answer: Number.isInteger(decimal) ? decimal : decimal,
      asFraction: Number.isInteger(decimal) ? null : frac,
      explanation: `Area gives \\(\\tfrac12 ab = \\tfrac12 ch\\), so \\(h = \\dfrac{ab}{c} = \\dfrac{${a}\\cdot${b}}{${c}} = ${formatFraction(...frac)}${Number.isInteger(decimal) ? "" : ` \\approx ${(Math.round(decimal * 10) / 10).toFixed(1)}`}\\).`,
    });
  },

  congruence_similarity: () => {
    const k = pick([2, 3, 4]);
    const small = randInt(6, 14);
    const large = small * k;
    const variant = pick(["ratio", "area", "perimeter"]);
    if (variant === "area") {
      const areaSmall = randInt(12, 48);
      const areaLarge = areaSmall * k * k;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Congruence & Similarity",
        difficulty: "challenge",
        prompt: `Two similar triangles have a side-length ratio of \\(${k}:1\\) (larger to smaller). If the smaller triangle has area \\(${areaSmall}\\), find the area of the larger triangle.`,
        answer: areaLarge,
        explanation: `For similar figures, areas scale by the square of the linear ratio: \\(A_{\\text{large}} = ${k}^2 \\cdot ${areaSmall} = ${k * k} \\cdot ${areaSmall} = ${areaLarge}\\).`,
      });
    }
    if (variant === "perimeter") {
      const pSmall = small * 3;
      const pLarge = pSmall * k;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Congruence & Similarity",
        prompt: `Two similar triangles have perimeters \\(${pSmall}\\) and \\(?\\). The ratio of corresponding sides (larger : smaller) is \\(${k}:1\\). Find the larger perimeter.`,
        answer: pLarge,
        explanation: `Perimeters of similar triangles scale linearly with side ratio: \\(P_{\\text{large}} = ${k} \\cdot ${pSmall} = ${pLarge}\\).`,
      });
    }
    const bc = small + randInt(2, 6);
    const ef = bc * k;
    return makeQuestion({
      topic: "Triangles",
      subtopic: "Congruence & Similarity",
      prompt: `In similar triangles \\(\\triangle ABC \\sim \\triangle DEF\\), \\(AB = ${small}\\) corresponds to \\(DE = ${large}\\). If \\(BC = ${bc}\\), find \\(EF\\).`,
      answer: ef,
      explanation: `Corresponding sides are proportional: \\(\\dfrac{AB}{DE} = \\dfrac{BC}{EF}\\). Ratio is \\(1:${k}\\), so \\(EF = ${k} \\cdot ${bc} = ${ef}\\).`,
    });
  },

  triangle_centers: () => {
    const center = pick(["centroid", "incenter", "circumcenter", "orthocenter"]);
    if (center === "centroid") {
      const median = pick([12, 15, 18, 21, 24, 27, 30]);
      const ag = (median * 2) / 3;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Centroid",
        prompt: `In \\(\\triangle ABC\\), median \\(\\overline{AM}\\) has length \\(${median}\\), where \\(M\\) is the midpoint of \\(BC\\). The centroid \\(G\\) divides \\(AM\\) so that \\(AG:GM = 2:1\\). Find \\(AG\\).`,
        answer: ag,
        asFraction: Number.isInteger(ag) ? null : [median * 2, 3],
        explanation: `The centroid splits each median in a \\(2:1\\) ratio from vertex to midpoint. So \\(AG = \\tfrac{2}{3}\\cdot AM = \\tfrac{2}{3}\\cdot ${median} = ${formatFraction(median * 2, 3)}\\).`,
      });
    }
    if (center === "incenter") {
      const a = pick([40, 50, 60, 70, 80]);
      const half = a / 2;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Incenter",
        prompt: `In \\(\\triangle ABC\\), \\(m\\angle A = ${a}^\\circ\\). The incenter \\(I\\) lies on the angle bisector of \\(\\angle A\\). What is \\(m\\angle BAI\\)?`,
        answer: half,
        explanation: `The incenter lies on all angle bisectors. Thus \\(m\\angle BAI = \\tfrac12 m\\angle A = \\tfrac{${a}^\\circ}{2} = ${half}^\\circ\\).`,
      });
    }
    if (center === "circumcenter") {
      const r = randInt(5, 13);
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Circumcenter",
        prompt: `Point \\(O\\) is the circumcenter of \\(\\triangle ABC\\) and \\(OA = ${r}\\). Find \\(OB\\).`,
        answer: r,
        explanation: `The circumcenter is equidistant from all vertices, so \\(OA = OB = OC = ${r}\\).`,
      });
    }
    const acuteA = randInt(50, 70);
    return makeQuestion({
      topic: "Triangles",
      subtopic: "Orthocenter",
      prompt: `In an acute triangle, altitudes from \\(A\\) and \\(B\\) meet at \\(H\\) (the orthocenter). If \\(m\\angle A = ${acuteA}^\\circ\\), find \\(m\\angle BHC\\).`,
      answer: 180 - acuteA,
      explanation: `In the orthocentric configuration, \\(\\angle BHC\\) and \\(\\angle A\\) are supplementary in an acute triangle: \\(m\\angle BHC = 180^\\circ - ${acuteA}^\\circ = ${180 - acuteA}^\\circ\\).`,
    });
  },

  triangle_area: () => {
    const method = pick(["base_height", "heron", "sas", "sector"]);
    if (method === "sector") {
      const r = randInt(4, 12);
      const angle = pick([90, 120, 180]);
      const area = (angle / 360) * Math.PI * r * r;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Sector Area",
        difficulty: "challenge",
        prompt: `A circle has radius \\(${r}\\). A sector bounded by a central angle of \\(${angle}^\\circ\\) is cut out. Find the area of the sector (round to one decimal place).`,
        answer: area,
        explanation: `Sector area \\(A = \\tfrac{\\theta}{360^\\circ}\\pi r^2 = \\tfrac{${angle}}{360}\\pi(${r})^2 \\approx ${(Math.round(area * 10) / 10).toFixed(1)}\\).`,
      });
    }
    if (method === "base_height") {
      const b = randInt(10, 24);
      const h = randInt(6, 18);
      const area = (b * h) / 2;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Area (Base × Height)",
        prompt: `A triangle has base \\(${b}\\) and corresponding height \\(${h}\\). Find its area.`,
        answer: area,
        explanation: `\\(A = \\tfrac12 bh = \\tfrac12 \\cdot ${b} \\cdot ${h} = ${area}\\).`,
      });
    }
    if (method === "heron") {
      const scale = pick([1, 2]);
      const [x, y, z] = pythagoreanTriple(scale);
      const area = (x * y) / 2;
      return makeQuestion({
        topic: "Triangles",
        subtopic: "Area (Heron's Formula)",
        difficulty: "challenge",
        prompt: `A triangle has side lengths \\(${x}\\), \\(${y}\\), and \\(${z}\\). Find its area.`,
        answer: area,
        explanation: `This is a ${x}-${y}-${z} right triangle, so \\(A = \\tfrac12 \\cdot ${x} \\cdot ${y} = ${area}\\). (Heron's formula gives the same result.)`,
      });
    }
    const a = randInt(8, 15);
    const b = randInt(10, 18);
    const angle = 30;
    const area = (0.5 * a * b) / 2;
    return makeQuestion({
      topic: "Triangles",
      subtopic: "Area (SAS / Trigonometry)",
      difficulty: "challenge",
      prompt: `In \\(\\triangle ABC\\), \\(AB = ${a}\\), \\(AC = ${b}\\), and \\(m\\angle A = ${angle}^\\circ\\). Find the area.`,
      answer: area % 1 === 0 ? area : area,
      asFraction: area % 1 !== 0 ? [a * b, 4] : null,
      explanation: `\\(A = \\tfrac12 ab\\sin C = \\tfrac12 \\cdot ${a} \\cdot ${b} \\cdot \\sin 30^\\circ = \\tfrac12 \\cdot ${a * b} \\cdot \\tfrac12 = ${formatFraction(a * b, 4)}\\).`,
    });
  },
};
