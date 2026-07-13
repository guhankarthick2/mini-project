# Geometry Math Quest

A browser-based geometry practice app for ambitious students. Pick a topic, choose subtopics, set the number of questions, and practice with **hard** problems plus **AMC / MAO-style** challenge questions.

## Topics

### 1. Triangle Geometry
- Supplementary angles
- Pythagorean theorem (including altitude-to-hypotenuse)
- Congruence & similarity (ratios, area scaling)
- Triangle centers: centroid, incenter, circumcenter, orthocenter
- Area: base × height, Heron's formula, SAS/trigonometry

### 2. Quadrilateral Geometry
- Angle sum property (360°)
- General properties (sides, vertices, diagonals)
- Parallelograms, rectangles, rhombuses, squares
- Trapezoids & isosceles trapezoids
- Kites
- Area formulas (base/height, diagonals)

### 3. Polygons (n-gons)
- Convex/concave & regular/irregular terminology
- Interior angle sum: 180°(n-2)
- Exterior angles (sum = 360°)
- Diagonal count: n(n-3)/2
- Apothem, circumradius, perimeter
- Area via triangle decomposition

## Modes

- **Practice** — Check your answer after each question and read a full explanation immediately.
- **Test** — Answer all questions first, then review a complete answer key with explanations.

## How to Run

No build step required. Open `index.html` in a browser, or serve the folder locally:

```bash
# Python
python -m http.server 8080

# Node (if npx available)
npx serve .
```

Then visit `http://localhost:8080`.

> **Note:** ES modules require a local server (not `file://`) in most browsers.

## Answer Format

Enter **integers** (e.g. `54`), **fractions** (e.g. `3/2`), or **decimals with one decimal place** (e.g. `12.5`, `13.9`).

## Project Structure

```
geometry-math-quiz/
├── index.html
├── js/
│   ├── app.js              # Quiz builder & grading
│   ├── ui.js               # User interface
│   ├── utils.js            # Helpers
│   └── generators/
│       ├── triangles.js
│       ├── quadrilaterals.js
│       ├── polygons.js
│       └── challenges.js   # Competition-style problems
└── README.md
```
