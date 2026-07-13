export function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function pick(arr) {
  return arr[randInt(0, arr.length - 1)];
}

export function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = randInt(0, i);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export function gcd(a, b) {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b) [a, b] = [b, a % b];
  return a;
}

export function simplifyFraction(num, den) {
  const g = gcd(num, den);
  return [num / g, den / g];
}

export function formatFraction(num, den) {
  if (den === 0) return String(num);
  if (num % den === 0) return String(num / den);
  const [n, d] = simplifyFraction(num, den);
  if (d < 0) return formatFraction(-n, -d);
  return `${n}/${d}`;
}

export function roundTo(n, decimals = 1) {
  const f = 10 ** decimals;
  return Math.round(n * f) / f;
}

export function isClose(a, b, tol = 0.06) {
  return Math.abs(a - b) <= tol;
}

/** Format answers as integer, fraction, or decimal with at most one decimal place. */
export function formatAnswer(value, { asFraction = null } = {}) {
  if (typeof value === "string") {
    if (value.includes("/")) return value;
    const parsed = parseFloat(value);
    if (!Number.isNaN(parsed)) return formatNumericAnswer(parsed);
    return value;
  }
  if (asFraction) {
    const [num, den] = asFraction;
    return formatFraction(num, den);
  }
  return formatNumericAnswer(value);
}

function formatNumericAnswer(n) {
  if (Number.isInteger(n) || Math.abs(n - Math.round(n)) < 1e-9) {
    return String(Math.round(n));
  }
  const rounded = roundTo(n, 1);
  if (Number.isInteger(rounded)) return String(rounded);
  return rounded.toFixed(1);
}

export function pythagoreanTriple(scale = 1) {
  const bases = [
    [3, 4, 5],
    [5, 12, 13],
    [8, 15, 17],
    [7, 24, 25],
    [9, 40, 41],
    [6, 8, 10],
    [9, 12, 15],
    [12, 16, 20],
  ];
  const [a, b, c] = pick(bases);
  return [a * scale, b * scale, c * scale];
}

/** Diagonal pairs (d1, d2) for rhombus that yield integer side lengths. */
export function rhombusDiagonalPairs() {
  return [
    [6, 8],
    [8, 15],
    [10, 24],
    [12, 16],
    [14, 48],
    [16, 30],
    [20, 21],
  ];
}

/** n values where 360/n and (n-2)*180/n are integers. */
export const NICE_POLYGON_N = [3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60];

export function makeQuestion(base) {
  const answer = formatAnswer(base.answer, { asFraction: base.asFraction || null });
  const rawAccepted = base.acceptAnswers || [base.answer, answer];
  const acceptAnswers = [...new Set(rawAccepted.map((a) => formatAnswer(a, { asFraction: base.asFraction || null })))];

  return {
    id: crypto.randomUUID(),
    difficulty: base.difficulty || "hard",
    topic: base.topic,
    subtopic: base.subtopic,
    prompt: base.prompt,
    // Diagrams are disabled until accurate, geometry-aware rendering is available.
    diagram: null,
    answerType: base.answerType || "numeric",
    answer,
    acceptAnswers,
    choices: base.choices || null,
    explanation: base.explanation,
    hint: base.hint || null,
  };
}

export function normalizeAnswer(raw) {
  return String(raw)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "")
    .replace(/°/g, "")
    .replace(/degrees?/g, "")
    .replace(/units?/g, "")
    .replace(/cm/g, "")
    .replace(/m/g, "");
}

export function answersMatch(user, accepted) {
  const u = normalizeAnswer(user);
  if (!u) return false;
  return accepted.some((a) => {
    const norm = normalizeAnswer(a);
    if (u === norm) return true;
    const uf = parseFloat(u);
    const af = parseFloat(norm);
    if (!Number.isNaN(uf) && !Number.isNaN(af) && isClose(uf, af)) return true;
    return false;
  });
}
