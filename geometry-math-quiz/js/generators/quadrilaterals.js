import { randInt, pick, makeQuestion, rhombusDiagonalPairs } from "../utils.js";

function quadSvg(extras = "") {
  return `<svg viewBox="0 0 320 200" class="diagram" aria-hidden="true">
    <polygon points="60,160 260,160 280,60 40,60" fill="rgba(16,185,129,0.12)" stroke="#34d399" stroke-width="2"/>
    <text x="48" y="55" fill="#a7f3d0" font-size="13">A</text>
    <text x="268" y="55" fill="#a7f3d0" font-size="13">B</text>
    <text x="288" y="165" fill="#a7f3d0" font-size="13">C</text>
    <text x="42" y="175" fill="#a7f3d0" font-size="13">D</text>
    ${extras}
  </svg>`;
}

export const quadrilateralGenerators = {
  angle_sum: () => {
    const a = randInt(70, 110);
    const b = randInt(80, 120);
    const c = randInt(60, 100);
    const d = 360 - a - b - c;
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Angle Sum Property",
      prompt: `In convex quadrilateral \\(ABCD\\), \\(m\\angle A = ${a}^\\circ\\), \\(m\\angle B = ${b}^\\circ\\), and \\(m\\angle C = ${c}^\\circ\\). Find \\(m\\angle D\\).`,
      diagram: quadSvg(),
      answer: d,
      explanation: `Interior angles of any quadrilateral sum to \\(360^\\circ\\): \\(m\\angle D = 360^\\circ - ${a}^\\circ - ${b}^\\circ - ${c}^\\circ = ${d}^\\circ\\).`,
    });
  },

  general_properties: () => {
    const n = randInt(5, 12);
    const variant = pick(["vertices", "diagonals_count", "sides"]);
    if (variant === "vertices") {
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "General Properties",
        prompt: `A polygon has \\(${n}\\) sides. How many vertices does it have?`,
        answer: n,
        explanation: `In any simple polygon, the number of vertices equals the number of sides. So there are \\(${n}\\) vertices.`,
      });
    }
    if (variant === "diagonals_count") {
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "General Properties",
        prompt: `How many diagonals does a convex quadrilateral have?`,
        answer: 2,
        explanation: `A quadrilateral has \\(\\tfrac{n(n-3)}{2} = \\tfrac{4\\cdot1}{2} = 2\\) diagonals.`,
      });
    }
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "General Properties",
      prompt: `How many sides does a quadrilateral have?`,
      answer: 4,
      explanation: `The prefix "quad-" means four. A quadrilateral is a 4-sided polygon.`,
    });
  },

  parallelograms: () => {
    const side = randInt(7, 18);
    const angle = randInt(55, 125);
    const opp = 180 - angle;
    const variant = pick(["opposite_side", "opposite_angle", "diagonal_bisect"]);
    if (variant === "opposite_side") {
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Parallelograms",
        prompt: `In parallelogram \\(ABCD\\), \\(AB = ${side}\\). Find \\(CD\\).`,
        answer: side,
        explanation: `Opposite sides of a parallelogram are congruent, so \\(CD = AB = ${side}\\).`,
      });
    }
    if (variant === "opposite_angle") {
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Parallelograms",
        prompt: `In parallelogram \\(ABCD\\), \\(m\\angle A = ${angle}^\\circ\\). Find \\(m\\angle C\\).`,
        answer: angle,
        explanation: `Opposite angles in a parallelogram are congruent, so \\(m\\angle C = ${angle}^\\circ\\). (Consecutive angles are supplementary: \\(m\\angle B = ${opp}^\\circ\\).)`,
      });
    }
    const half = randInt(4, 11);
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Parallelograms",
      prompt: `Diagonals of parallelogram \\(ABCD\\) intersect at \\(E\\). If \\(AE = ${half}\\), find \\(EC\\).`,
      answer: half,
      explanation: `Diagonals of a parallelogram bisect each other, so \\(AE = EC = ${half}\\).`,
    });
  },

  special_parallelograms: () => {
    const kind = pick(["rectangle", "rhombus", "square"]);
    if (kind === "rectangle") {
      const d = randInt(10, 26);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Rectangles",
        prompt: `Rectangle \\(ABCD\\) has diagonal \\(AC = ${d}\\). Find \\(BD\\).`,
        answer: d,
        explanation: `Rectangle diagonals are congruent, so \\(BD = AC = ${d}\\).`,
      });
    }
    if (kind === "rhombus") {
      const [d1, d2] = pick(rhombusDiagonalPairs());
      const side = Math.sqrt((d1 / 2) ** 2 + (d2 / 2) ** 2);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Rhombuses",
        difficulty: "challenge",
        prompt: `A rhombus has diagonals of lengths \\(${d1}\\) and \\(${d2}\\). Find the side length.`,
        answer: side,
        explanation: `Rhombus diagonals are perpendicular bisectors. Each side is the hypotenuse of a right triangle with legs \\(${d1 / 2}\\) and \\(${d2 / 2}\\): \\(s = \\sqrt{(${d1 / 2})^2 + (${d2 / 2})^2} = ${side}\\).`,
      });
    }
    const s = pick([6, 8, 10, 12, 14]);
    const diag = s * Math.SQRT2;
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Squares",
      prompt: `Square \\(ABCD\\) has side length \\(${s}\\). Find the length of diagonal \\(AC\\) (round to one decimal place).`,
      answer: diag,
      explanation: `A square is a rhombus with right angles. Diagonal \\(AC = s\\sqrt2 = ${s}\\sqrt2 \\approx ${(Math.round(diag * 10) / 10).toFixed(1)}\\).`,
    });
  },

  trapezoids: () => {
    const b1 = randInt(8, 16);
    const b2 = randInt(12, 22);
    const h = randInt(5, 12);
    const area = ((b1 + b2) * h) / 2;
    const variant = pick(["area", "isosceles", "median"]);
    if (variant === "median") {
      const sum = b1 + b2;
      const median = sum / 2;
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Trapezoids",
        prompt: `A trapezoid has bases \\(${b1}\\) and \\(${b2}\\). Find the length of its median (midsegment).`,
        answer: median,
        asFraction: sum % 2 !== 0 ? [sum, 2] : null,
        explanation: `The median of a trapezoid equals the average of the bases: \\(m = \\tfrac{${b1}+${b2}}{2} = ${sum % 2 === 0 ? median : `${sum}/2`}\\).`,
      });
    }
    if (variant === "isosceles") {
      const leg = randInt(8, 15);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Isosceles Trapezoids",
        prompt: `In isosceles trapezoid \\(ABCD\\) with \\(AB \\parallel CD\\), non-parallel sides \\(AD = ${leg}\\). Find \\(BC\\).`,
        answer: leg,
        explanation: `An isosceles trapezoid has congruent legs, so \\(BC = AD = ${leg}\\).`,
      });
    }
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Trapezoids",
      prompt: `A trapezoid has parallel bases \\(${b1}\\) and \\(${b2}\\) with height \\(${h}\\). Find its area.`,
      answer: area,
      explanation: `\\(A = \\tfrac{h(b_1+b_2)}{2} = \\tfrac{${h}(${b1}+${b2})}{2} = ${area}\\).`,
    });
  },

  kites: () => {
    const d1 = randInt(12, 24);
    const d2 = randInt(8, 18);
    const area = (d1 * d2) / 2;
    const variant = pick(["area", "symmetry"]);
    if (variant === "symmetry") {
      const seg = randInt(4, 10);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Kites",
        prompt: `In kite \\(ABCD\\) with \\(AB = AD\\) and \\(CB = CD\\), diagonal \\(AC\\) is the axis of symmetry. If \\(AB = ${seg}\\), find \\(AD\\).`,
        answer: seg,
        explanation: `A kite has two pairs of adjacent congruent sides. Since \\(AB = AD\\), \\(AD = ${seg}\\).`,
      });
    }
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Kites",
      prompt: `A kite has perpendicular diagonals of lengths \\(${d1}\\) and \\(${d2}\\). Find its area.`,
      answer: area,
      explanation: `For a kite (or any quadrilateral with perpendicular diagonals): \\(A = \\tfrac{d_1 d_2}{2} = \\tfrac{${d1}\\cdot${d2}}{2} = ${area}\\).`,
    });
  },

  quad_area: () => {
    const kind = pick(["parallelogram", "rhombus_diag", "trapezoid", "kite", "sector"]);
    if (kind === "sector") {
      const r = randInt(4, 10);
      const angle = pick([72, 90, 120, 180]);
      const area = (angle / 360) * Math.PI * r * r;
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Sector Area",
        difficulty: "challenge",
        prompt: `In a circle of radius \\(${r}\\), a sector with central angle \\(${angle}^\\circ\\) is shaded. Find the area of the sector (round to one decimal place).`,
        answer: area,
        explanation: `\\(A_{\\text{sector}} = \\tfrac{\\theta}{360^\\circ}\\pi r^2 = \\tfrac{${angle}}{360}\\pi(${r})^2 \\approx ${(Math.round(area * 10) / 10).toFixed(1)}\\).`,
      });
    }
    if (kind === "parallelogram") {
      const b = randInt(9, 20);
      const h = randInt(5, 14);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Area Calculations",
        prompt: `A parallelogram has base \\(${b}\\) and height \\(${h}\\). Find its area.`,
        answer: b * h,
        explanation: `\\(A = bh = ${b}\\cdot${h} = ${b * h}\\).`,
      });
    }
    if (kind === "rhombus_diag") {
      const d1 = randInt(10, 22);
      const d2 = randInt(8, 16);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Area Calculations",
        prompt: `A rhombus has diagonals \\(${d1}\\) and \\(${d2}\\). Find its area.`,
        answer: (d1 * d2) / 2,
        explanation: `\\(A = \\tfrac12 d_1 d_2 = \\tfrac{${d1}\\cdot${d2}}{2} = ${(d1 * d2) / 2}\\).`,
      });
    }
    if (kind === "trapezoid") {
      const b1 = randInt(7, 14);
      const b2 = randInt(15, 24);
      const h = randInt(6, 11);
      return makeQuestion({
        topic: "Quadrilaterals",
        subtopic: "Area Calculations",
        prompt: `Find the area of a trapezoid with bases \\(${b1}\\) and \\(${b2}\\) and height \\(${h}\\).`,
        answer: ((b1 + b2) * h) / 2,
        explanation: `\\(A = \\tfrac{h(b_1+b_2)}{2} = \\tfrac{${h}(${b1}+${b2})}{2} = ${((b1 + b2) * h) / 2}\\).`,
      });
    }
    const d1 = randInt(14, 26);
    const d2 = randInt(6, 12);
    return makeQuestion({
      topic: "Quadrilaterals",
      subtopic: "Area Calculations",
      prompt: `A kite has diagonals \\(${d1}\\) and \\(${d2}\\). Find its area.`,
      answer: (d1 * d2) / 2,
      explanation: `\\(A = \\tfrac12 d_1 d_2 = ${(d1 * d2) / 2}\\).`,
    });
  },
};
