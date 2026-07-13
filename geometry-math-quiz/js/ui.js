import { TOPICS, buildQuiz, gradeAnswer, summarizeResults } from "./app.js";

const state = {
  topicId: "triangles",
  subtopicIds: [],
  mode: "practice",
  count: 10,
  questions: [],
  currentIndex: 0,
  responses: [],
};

const $ = (sel) => document.querySelector(sel);

function renderMath() {
  if (window.MathJax?.typesetPromise) {
    window.MathJax.typesetPromise().catch(() => {});
  }
}

function initSetup() {
  const grid = $("#topic-grid");
  grid.innerHTML = Object.values(TOPICS)
    .map(
      (t) => `
      <div class="topic-card ${t.id === state.topicId ? "selected" : ""}" data-topic="${t.id}">
        <h3>${t.name}</h3>
        <p>${t.description}</p>
      </div>`
    )
    .join("");

  grid.querySelectorAll(".topic-card").forEach((card) => {
    card.addEventListener("click", () => {
      state.topicId = card.dataset.topic;
      grid.querySelectorAll(".topic-card").forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      renderSubtopics();
    });
  });

  renderSubtopics();

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.mode = btn.dataset.mode;
      document.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  $("#select-all-btn").addEventListener("click", () => {
    state.subtopicIds = TOPICS[state.topicId].subtopics.map((s) => s.id);
    renderSubtopics();
  });

  $("#clear-all-btn").addEventListener("click", () => {
    state.subtopicIds = [];
    renderSubtopics();
  });

  $("#start-btn").addEventListener("click", startQuiz);
  $("#restart-btn").addEventListener("click", () => showScreen("setup"));
}

function renderSubtopics() {
  const topic = TOPICS[state.topicId];
  if (!state.subtopicIds.length) {
    state.subtopicIds = topic.subtopics.map((s) => s.id);
  } else {
    state.subtopicIds = state.subtopicIds.filter((id) =>
      topic.subtopics.some((s) => s.id === id)
    );
    if (!state.subtopicIds.length) {
      state.subtopicIds = topic.subtopics.map((s) => s.id);
    }
  }

  const list = $("#subtopic-list");
  list.innerHTML = topic.subtopics
    .map(
      (s) => `
      <label class="check-item">
        <input type="checkbox" value="${s.id}" ${state.subtopicIds.includes(s.id) ? "checked" : ""}>
        <span>${s.label}</span>
      </label>`
    )
    .join("");

  list.querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) {
        if (!state.subtopicIds.includes(input.value)) state.subtopicIds.push(input.value);
      } else {
        state.subtopicIds = state.subtopicIds.filter((id) => id !== input.value);
      }
    });
  });
}

function showScreen(name) {
  $("#setup-screen").classList.toggle("hidden", name !== "setup");
  $("#quiz-screen").classList.toggle("hidden", name !== "quiz");
  $("#results-screen").classList.toggle("hidden", name !== "results");
}

function startQuiz() {
  const count = parseInt($("#question-count").value, 10);
  if (!count || count < 1 || count > 30) {
    alert("Please choose between 1 and 30 questions.");
    return;
  }
  if (!state.subtopicIds.length) {
    alert("Select at least one subtopic.");
    return;
  }

  state.count = count;
  state.questions = buildQuiz({
    topicId: state.topicId,
    subtopicIds: state.subtopicIds,
    count,
  });
  state.currentIndex = 0;
  state.responses = state.questions.map(() => ({
    answer: "",
    revealed: false,
    correct: false,
    skipped: false,
  }));

  showScreen("quiz");
  $("#quiz-mode-label").textContent =
    state.mode === "practice" ? "Practice Mode" : "Test Mode";
  renderQuestion();
}

function renderQuestion() {
  const q = state.questions[state.currentIndex];
  const total = state.questions.length;
  const idx = state.currentIndex;
  const resp = state.responses[idx];

  $("#quiz-progress-text").textContent = `Question ${idx + 1} of ${total}`;
  $("#progress-fill").style.width = `${((idx + 1) / total) * 100}%`;

  const diffBadge =
    q.difficulty === "challenge"
      ? `<span class="badge badge-challenge">Challenge</span>`
      : `<span class="badge badge-hard">Hard</span>`;

  const feedbackHtml =
    state.mode === "practice" && resp.revealed
      ? `<div class="feedback ${resp.correct ? "correct" : "incorrect"}">
          <h4>${resp.correct ? "Correct!" : "Not quite."}</h4>
          <p>Answer: <span class="answer-key">\\(${q.answer}\\)</span></p>
          <div class="explanation">${q.explanation}</div>
          ${q.hint && !resp.correct ? `<p class="hint">Hint: ${q.hint}</p>` : ""}
        </div>`
      : "";

  $("#question-area").innerHTML = `
    <div class="question-header">
      <span>${q.subtopic}</span>
      ${diffBadge}
    </div>
    <div class="prompt">${q.prompt}</div>
    ${q.diagram || ""}
    <div class="answer-box">
      <label for="user-answer">Your answer</label>
      <input type="text" id="user-answer" placeholder="Enter an integer, fraction (e.g. 3/2), or decimal to 1 place (e.g. 12.5)"
        value="${resp.answer}" ${state.mode === "practice" && resp.revealed ? "disabled" : ""}>
    </div>
    ${feedbackHtml}
  `;

  const input = $("#user-answer");
  input?.addEventListener("input", (e) => {
    state.responses[idx].answer = e.target.value;
  });
  input?.focus();

  renderQuizActions();
  renderMath();
}

function renderQuizActions() {
  const idx = state.currentIndex;
  const total = state.questions.length;
  const resp = state.responses[idx];
  const actions = $("#quiz-actions");
  actions.innerHTML = "";

  if (state.mode === "practice") {
    if (!resp.revealed) {
      const checkBtn = document.createElement("button");
      checkBtn.className = "btn-success";
      checkBtn.textContent = "Check Answer";
      checkBtn.addEventListener("click", checkPracticeAnswer);
      actions.appendChild(checkBtn);

      const revealBtn = document.createElement("button");
      revealBtn.className = "btn-secondary";
      revealBtn.textContent = "Reveal Answer";
      revealBtn.addEventListener("click", () => revealPractice(false));
      actions.appendChild(revealBtn);
    } else if (idx < total - 1) {
      const nextBtn = document.createElement("button");
      nextBtn.className = "btn-primary";
      nextBtn.textContent = "Next Question";
      nextBtn.addEventListener("click", () => {
        state.currentIndex += 1;
        renderQuestion();
      });
      actions.appendChild(nextBtn);
    } else {
      const finishBtn = document.createElement("button");
      finishBtn.className = "btn-primary";
      finishBtn.textContent = "View Summary";
      finishBtn.addEventListener("click", showResults);
      actions.appendChild(finishBtn);
    }
  } else {
    if (idx > 0) {
      const prevBtn = document.createElement("button");
      prevBtn.className = "btn-secondary";
      prevBtn.textContent = "Previous";
      prevBtn.addEventListener("click", () => {
        state.currentIndex -= 1;
        renderQuestion();
      });
      actions.appendChild(prevBtn);
    }

    if (idx < total - 1) {
      const nextBtn = document.createElement("button");
      nextBtn.className = "btn-primary";
      nextBtn.textContent = "Next";
      nextBtn.addEventListener("click", () => {
        state.currentIndex += 1;
        renderQuestion();
      });
      actions.appendChild(nextBtn);
    } else {
      const submitBtn = document.createElement("button");
      submitBtn.className = "btn-success";
      submitBtn.textContent = "Submit Test";
      submitBtn.addEventListener("click", submitTest);
      actions.appendChild(submitBtn);
    }
  }
}

function checkPracticeAnswer() {
  const idx = state.currentIndex;
  const q = state.questions[idx];
  const input = $("#user-answer");
  const answer = input?.value?.trim() || "";
  if (!answer) {
    alert("Enter an answer first, or use Reveal Answer.");
    return;
  }
  state.responses[idx].answer = answer;
  state.responses[idx].correct = gradeAnswer(q, answer);
  state.responses[idx].revealed = true;
  renderQuestion();
}

function revealPractice(markSkipped = false) {
  const idx = state.currentIndex;
  const q = state.questions[idx];
  state.responses[idx].revealed = true;
  state.responses[idx].skipped = markSkipped;
  if (state.responses[idx].answer) {
    state.responses[idx].correct = gradeAnswer(q, state.responses[idx].answer);
  } else {
    state.responses[idx].correct = false;
  }
  renderQuestion();
}

function submitTest() {
  state.questions.forEach((q, i) => {
    const answer = state.responses[i].answer;
    state.responses[i].correct = answer ? gradeAnswer(q, answer) : false;
    state.responses[i].revealed = true;
  });
  showResults();
}

function showResults() {
  const summary = summarizeResults(state.questions, state.responses);
  $("#score-percent").textContent = `${summary.percent}%`;
  $("#score-summary").textContent = `${summary.correct} of ${summary.total} correct`;

  $("#results-list").innerHTML = summary.details
    .map(
      ({ question: q, response: r, isCorrect }, i) => `
      <div class="result-item ${isCorrect ? "correct-item" : "wrong-item"}">
        <div class="question-header">
          <strong>Q${i + 1}: ${q.subtopic}</strong>
          <span>${isCorrect ? "✓ Correct" : "✗ Incorrect"}</span>
        </div>
        <div class="prompt" style="font-size:0.95rem">${q.prompt}</div>
        ${q.diagram || ""}
        <p><strong>Your answer:</strong> ${r.answer || "(blank)"}</p>
        <p><strong>Correct answer:</strong> <span class="answer-key">\\(${q.answer}\\)</span></p>
        <div class="explanation">${q.explanation}</div>
      </div>`
    )
    .join("");

  showScreen("results");
  renderMath();
}

initSetup();
