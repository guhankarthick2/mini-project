import { triangleGenerators } from "./generators/triangles.js";
import { quadrilateralGenerators } from "./generators/quadrilaterals.js";
import { polygonGenerators } from "./generators/polygons.js";
import { challengeQuestions } from "./generators/challenges.js";
import { pick, shuffle, answersMatch } from "./utils.js";

export const TOPICS = {
  triangles: {
    id: "triangles",
    name: "Triangle Geometry",
    description: "Angles, segment lengths, triangle centers, and area (3 methods).",
    subtopics: [
      { id: "supplementary_angles", label: "Supplementary Angles" },
      { id: "pythagorean_theorem", label: "Pythagorean Theorem" },
      { id: "congruence_similarity", label: "Congruence & Similarity" },
      { id: "triangle_centers", label: "Centroid, Incenter, Circumcenter, Orthocenter" },
      { id: "triangle_area", label: "Triangle Area (3 Methods)" },
      { id: "challenge", label: "Challenge (AMC / MAO style)" },
    ],
    generators: triangleGenerators,
  },
  quadrilaterals: {
    id: "quadrilaterals",
    name: "Quadrilateral Geometry",
    description: "Angle sums, parallelograms, trapezoids, kites, and area formulas.",
    subtopics: [
      { id: "angle_sum", label: "Angle Sum Property" },
      { id: "general_properties", label: "General Properties" },
      { id: "parallelograms", label: "Parallelograms" },
      { id: "special_parallelograms", label: "Rectangles, Rhombuses, Squares" },
      { id: "trapezoids", label: "Trapezoids & Isosceles Trapezoids" },
      { id: "kites", label: "Kites" },
      { id: "quad_area", label: "Area Calculations" },
      { id: "challenge", label: "Challenge (AMC / MAO style)" },
    ],
    generators: quadrilateralGenerators,
  },
  polygons: {
    id: "polygons",
    name: "Polygons (n-gons)",
    description: "Interior/exterior angles, diagonals, apothem, radius, and area.",
    subtopics: [
      { id: "terminology", label: "Basic Terminology" },
      { id: "interior_angles", label: "Interior Angle Formulas" },
      { id: "exterior_angles", label: "Exterior Angle Properties" },
      { id: "diagonals", label: "Diagonals" },
      { id: "regular_polygon_geometry", label: "Regular Polygon Geometry" },
      { id: "radius_apothem", label: "Radius & Apothem" },
      { id: "polygon_area", label: "Area of Regular Polygons" },
      { id: "challenge", label: "Challenge (AMC / MAO style)" },
    ],
    generators: polygonGenerators,
  },
};

function generateFromSubtopic(topicId, subtopicId) {
  const topic = TOPICS[topicId];
  if (subtopicId === "challenge") {
    const pool = challengeQuestions.filter((q) =>
      topicId === "triangles"
        ? q.topic === "Triangles"
        : topicId === "quadrilaterals"
          ? q.topic === "Quadrilaterals"
          : q.topic === "Polygons (n-gons)"
    );
    return pick(pool);
  }
  const gen = topic.generators[subtopicId];
  return gen ? gen() : null;
}

export function buildQuiz({ topicId, subtopicIds, count, includeChallenge = true }) {
  const topic = TOPICS[topicId];
  const selected = subtopicIds.length ? subtopicIds : topic.subtopics.map((s) => s.id);
  const pool = includeChallenge ? selected : selected.filter((id) => id !== "challenge");
  const questions = [];
  const seen = new Set();

  let guard = 0;
  while (questions.length < count && guard < count * 30) {
    guard += 1;
    const subtopicId = pick(pool);
    const q = generateFromSubtopic(topicId, subtopicId);
    if (!q) continue;
    const key = `${q.subtopic}:${q.prompt}`;
    if (seen.has(key)) continue;
    seen.add(key);
    questions.push({ ...q, number: questions.length + 1 });
  }

  return questions;
}

export function gradeAnswer(question, userAnswer) {
  return answersMatch(userAnswer, question.acceptAnswers);
}

export function summarizeResults(questions, responses) {
  let correct = 0;
  const details = questions.map((q, i) => {
    const response = responses[i] || { answer: "", revealed: false, correct: false };
    const isCorrect = response.correct;
    if (isCorrect) correct += 1;
    return { question: q, response, isCorrect };
  });
  return {
    total: questions.length,
    correct,
    percent: questions.length ? Math.round((correct / questions.length) * 100) : 0,
    details,
  };
}

export { shuffle };
