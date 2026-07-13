import { randInt, pick, makeQuestion, NICE_POLYGON_N } from "../utils.js";

function polygonSvg(n = 6) {
  const cx = 160;
  const cy = 110;
  const r = 80;
  const pts = [];
  for (let i = 0; i < n; i++) {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / n;
    pts.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
  }
  return `<svg viewBox="0 0 320 220" class="diagram" aria-hidden="true">
    <polygon points="${pts.join(" ")}" fill="rgba(244,114,182,0.12)" stroke="#f472b6" stroke-width="2"/>
    <text x="160" y="205" fill="#fbcfe8" font-size="13" text-anchor="middle">${n}-gon</text>
  </svg>`;
}

export const polygonGenerators = {
  terminology: () => {
    const n = pick(NICE_POLYGON_N.filter((x) => x >= 5 && x <= 12));
    const variant = pick(["regular_angle", "convex_diagonal", "sides_vertices"]);
    if (variant === "regular_angle") {
      const angle = ((n - 2) * 180) / n;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Regular vs Irregular",
        prompt: `Each interior angle of a regular \\(${n}\\)-gon measures how many degrees?`,
        diagram: polygonSvg(n),
        answer: angle,
        explanation: `Interior angle of a regular \\(n\\)-gon: \\(\\tfrac{(n-2)180^\\circ}{n} = \\tfrac{${n - 2}\\cdot180}{${n}} = ${angle}^\\circ\\).`,
      });
    }
    if (variant === "convex_diagonal") {
      const diagonals = (n * (n - 3)) / 2;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Convex Polygons",
        prompt: `How many diagonals does a convex \\(${n}\\)-gon have?`,
        answer: diagonals,
        explanation: `\\(D = \\tfrac{n(n-3)}{2} = \\tfrac{${n}(${n}-3)}{2} = ${diagonals}\\).`,
      });
    }
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Basic Terminology",
      prompt: `A regular polygon has \\(${n}\\) sides. How many vertices does it have?`,
      answer: n,
      explanation: `A regular \\(n\\)-gon has \\(n\\) sides and \\(n\\) vertices.`,
    });
  },

  interior_angles: () => {
    const n = pick([7, 8, 9, 10, 12, 15]);
    const sum = (n - 2) * 180;
    const variant = pick(["sum", "single_regular", "missing"]);
    if (variant === "sum") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Interior Angle Sum",
        prompt: `Find the sum of interior angles of a convex \\(${n}\\)-gon.`,
        diagram: polygonSvg(Math.min(n, 10)),
        answer: sum,
        explanation: `Sum of interior angles \\(= (n-2)\\cdot180^\\circ = (${n}-2)\\cdot180^\\circ = ${sum}^\\circ\\).`,
      });
    }
    if (variant === "single_regular") {
      const niceN = pick(NICE_POLYGON_N.filter((x) => x >= 5 && x <= 15));
      const niceSum = (niceN - 2) * 180;
      const angle = niceSum / niceN;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Interior Angle (Regular)",
        prompt: `Find the measure of one interior angle of a regular \\(${niceN}\\)-gon.`,
        answer: angle,
        explanation: `Total sum is \\(${niceSum}^\\circ\\). Each of \\(n\\) equal angles: \\(\\tfrac{${niceSum}}{${niceN}} = ${angle}^\\circ\\).`,
      });
    }
    const given = randInt(120, 160);
    const remaining = sum - given * (n - 1);
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Interior Angle Sum",
      difficulty: "challenge",
      prompt: `A convex \\(${n}\\)-gon has \\(${n - 1}\\) interior angles each measuring \\(${given}^\\circ\\). Find the remaining interior angle.`,
      answer: remaining,
      explanation: `Sum must be \\(${sum}^\\circ\\). Known angles total \\(${(n - 1) * given}^\\circ\\). Remaining: \\(${sum} - ${(n - 1) * given} = ${remaining}^\\circ\\).`,
    });
  },

  exterior_angles: () => {
    const n = pick(NICE_POLYGON_N.filter((x) => x >= 6 && x <= 12));
    const regular = 360 / n;
    const variant = pick(["sum_any", "regular_one", "interior_exterior"]);
    if (variant === "sum_any") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Exterior Angles",
        prompt: `What is the sum of exterior angles (one at each vertex) of any convex \\(${n}\\)-gon?`,
        answer: 360,
        explanation: `The sum of exterior angles of any convex polygon is always \\(360^\\circ\\), regardless of \\(n\\).`,
      });
    }
    if (variant === "regular_one") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Exterior Angles",
        prompt: `Each exterior angle of a regular \\(${n}\\)-gon measures how many degrees?`,
        answer: regular,
        explanation: `Exterior angles sum to \\(360^\\circ\\). For a regular \\(n\\)-gon: \\(\\tfrac{360^\\circ}{${n}} = ${regular}^\\circ\\).`,
      });
    }
    const interior = 180 - regular;
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Exterior Angles",
      prompt: `A regular \\(${n}\\)-gon has exterior angle \\(${regular}^\\circ\\). Find one interior angle.`,
      answer: interior,
      explanation: `Interior and exterior angles at a vertex are supplementary: \\(180^\\circ - ${regular}^\\circ = ${interior}^\\circ\\).`,
    });
  },

  diagonals: () => {
    const n = randInt(8, 20);
    const d = (n * (n - 3)) / 2;
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Diagonals",
      prompt: `How many diagonals can be drawn in a convex \\(${n}\\)-gon?`,
      answer: d,
      explanation: `From each vertex you can connect to \\(n-3\\) non-adjacent vertices. Total: \\(\\tfrac{n(n-3)}{2} = \\tfrac{${n}(${n}-3)}{2} = ${d}\\).`,
    });
  },

  regular_polygon_geometry: () => {
    const n = pick([6, 8, 10, 12]);
    const side = pick([4, 6, 8, 10]);
    const central = 360 / n;
    if (n === 6) {
      const apothem = (side * Math.sqrt(3)) / 2;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Regular Polygon Geometry",
        difficulty: "challenge",
        prompt: `A regular hexagon has side length \\(${side}\\). Find the apothem (round to one decimal place).`,
        diagram: polygonSvg(6),
        answer: apothem,
        explanation: `A regular hexagon splits into 6 equilateral triangles. Apothem \\(= \\tfrac{s\\sqrt3}{2} = \\tfrac{${side}\\sqrt3}{2} \\approx ${(Math.round(apothem * 10) / 10).toFixed(1)}\\).`,
      });
    }
    const isoBase = side / 2;
    const apothem = isoBase / Math.tan((central * Math.PI) / 360);
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Regular Polygon Geometry",
      difficulty: "challenge",
      prompt: `A regular \\(${n}\\)-gon has side length \\(${side}\\). Find the apothem (round to one decimal place).`,
      diagram: polygonSvg(n),
      answer: apothem,
      explanation: `Apothem bisects a central angle of \\(${central}^\\circ\\): \\(a = \\tfrac{s/2}{\\tan(${central / 2}^\\circ)} \\approx ${(Math.round(apothem * 10) / 10).toFixed(1)}\\).`,
    });
  },

  radius_apothem: () => {
    const n = pick([6, 8, 10]);
    const side = pick([4, 6, 8, 10, 12]);
    const ask = pick(["circumradius", "inradius", "perimeter"]);
    if (ask === "perimeter") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Perimeter",
        prompt: `A regular \\(${n}\\)-gon has side length \\(${side}\\). Find its perimeter.`,
        answer: n * side,
        explanation: `\\(P = n \\cdot s = ${n} \\cdot ${side} = ${n * side}\\).`,
      });
    }
    if (n === 6 && ask === "circumradius") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Circumradius",
        prompt: `A regular hexagon has side length \\(${side}\\). Find the circumradius \\(R\\).`,
        diagram: polygonSvg(6),
        answer: side,
        explanation: `In a regular hexagon, the circumradius equals the side length: \\(R = s = ${side}\\).`,
      });
    }
    if (n === 6 && ask === "inradius") {
      const r = (side * Math.sqrt(3)) / 2;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Inradius (Apothem)",
        prompt: `A regular hexagon has side length \\(${side}\\). Find the apothem \\(r\\) (round to one decimal place).`,
        diagram: polygonSvg(6),
        answer: r,
        explanation: `\\(r = \\tfrac{s\\sqrt3}{2} = \\tfrac{${side}\\sqrt3}{2} \\approx ${(Math.round(r * 10) / 10).toFixed(1)}\\).`,
      });
    }
    const central = (360 / n) * (Math.PI / 180);
    const R = side / (2 * Math.sin(central / 2));
    const r = R * Math.cos(central / 2);
    if (ask === "inradius") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Inradius (Apothem)",
        difficulty: "challenge",
        prompt: `A regular \\(${n}\\)-gon has circumradius \\(R = ${(Math.round(R * 10) / 10).toFixed(1)}\\). Find the apothem \\(r\\) (round to one decimal place).`,
        answer: r,
        explanation: `\\(r = R\\cos\\!\\left(\\tfrac{180^\\circ}{n}\\right) = ${(Math.round(R * 10) / 10).toFixed(1)}\\cos(${180 / n}^\\circ) \\approx ${(Math.round(r * 10) / 10).toFixed(1)}\\).`,
      });
    }
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Circumradius",
      difficulty: "challenge",
      prompt: `A regular \\(${n}\\)-gon has side length \\(${side}\\). Find the circumradius \\(R\\) (round to one decimal place).`,
      answer: R,
      explanation: `\\(R = \\tfrac{s}{2\\sin(\\pi/n)} = \\tfrac{${side}}{2\\sin(${180 / n}^\\circ)} \\approx ${(Math.round(R * 10) / 10).toFixed(1)}\\).`,
    });
  },

  polygon_area: () => {
    const n = pick([6, 8, 10]);
    const side = pick([4, 6, 8]);
    if (n === 6) {
      const area = ((3 * Math.sqrt(3)) / 2) * side * side;
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Area of Regular Polygons",
        prompt: `A regular hexagon has side length \\(${side}\\). Find its area (round to one decimal place).`,
        diagram: polygonSvg(6),
        answer: area,
        explanation: `\\(A = \\tfrac{3\\sqrt3}{2}s^2 = \\tfrac{3\\sqrt3}{2} \\cdot ${side * side} \\approx ${(Math.round(area * 10) / 10).toFixed(1)}\\). (Equivalently: 6 equilateral triangles of side \\(${side}\\).)`,
      });
    }
    const perimeter = n * side;
    const central = (360 / n) * (Math.PI / 180);
    const apothem = side / (2 * Math.tan(central / 2));
    const area = 0.5 * perimeter * apothem;
    const variant = pick(["apothem_formula", "triangle_decomposition"]);
    if (variant === "apothem_formula") {
      return makeQuestion({
        topic: "Polygons (n-gons)",
        subtopic: "Area of Regular Polygons",
        prompt: `A regular \\(${n}\\)-gon has apothem \\(${(Math.round(apothem * 10) / 10).toFixed(1)}\\) and perimeter \\(${perimeter}\\). Find its area (round to one decimal place).`,
        answer: area,
        explanation: `\\(A = \\tfrac12 r \\cdot P = \\tfrac12 \\cdot ${(Math.round(apothem * 10) / 10).toFixed(1)} \\cdot ${perimeter} \\approx ${(Math.round(area * 10) / 10).toFixed(1)}\\).`,
      });
    }
    const triArea = 0.5 * side * apothem;
    const total = n * triArea;
    return makeQuestion({
      topic: "Polygons (n-gons)",
      subtopic: "Area (Triangle Decomposition)",
      difficulty: "challenge",
      prompt: `A regular \\(${n}\\)-gon is divided into \\(${n}\\) congruent triangles, each with base \\(${side}\\) and height (apothem) \\(${(Math.round(apothem * 10) / 10).toFixed(1)}\\). Find the total area (round to one decimal place).`,
      diagram: polygonSvg(n),
      answer: total,
      explanation: `Each triangle: \\(\\tfrac12 \\cdot ${side} \\cdot ${(Math.round(apothem * 10) / 10).toFixed(1)} \\approx ${(Math.round(triArea * 10) / 10).toFixed(1)}\\). Total: \\(${n} \\times ${(Math.round(triArea * 10) / 10).toFixed(1)} \\approx ${(Math.round(total * 10) / 10).toFixed(1)}\\).`,
    });
  },
};
