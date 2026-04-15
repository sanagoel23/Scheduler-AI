const modeEl = document.getElementById("mode");
const slotsEl = document.getElementById("slots");
const enrollmentsSectionEl = document.getElementById("enrollments-section");
const pairsSectionEl = document.getElementById("pairs-section");
const enrollmentsTextEl = document.getElementById("enrollments-text");
const subjectsTextEl = document.getElementById("subjects-text");
const pairsTextEl = document.getElementById("pairs-text");
const sampleBtn = document.getElementById("sample-btn");
const solveBtn = document.getElementById("solve-btn");
const statusEl = document.getElementById("status");
const timetableBodyEl = document.getElementById("timetable-body");
const metricsBodyEl = document.getElementById("metrics-body");
const conflictListEl = document.getElementById("conflict-list");
const stepsListEl = document.getElementById("steps-list");
const validationEl = document.getElementById("validation");

function setStatus(message, type = "muted") {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}

function parseEnrollments(text) {
  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const enrollments = {};
  for (const line of lines) {
    const parts = line.split(":");
    if (parts.length < 2) continue;
    const subject = parts[0].trim();
    const students = parts
      .slice(1)
      .join(":")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (subject) enrollments[subject] = students;
  }
  return enrollments;
}

function parsePairs(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const pair = line.split("-").map((v) => v.trim());
      return pair.length === 2 ? pair : null;
    })
    .filter(Boolean);
}

function renderTimetable(rows = []) {
  if (!rows.length) {
    timetableBodyEl.innerHTML = `<tr><td colspan="2" class="muted">No timetable found.</td></tr>`;
    return;
  }
  timetableBodyEl.innerHTML = rows
    .map((row) => `<tr><td>${row.subject}</td><td>Slot ${row.time_slot}</td></tr>`)
    .join("");
}

function renderMetrics(rows = []) {
  if (!rows.length) {
    metricsBodyEl.innerHTML = `<tr><td colspan="4" class="muted">No performance data yet.</td></tr>`;
    return;
  }
  metricsBodyEl.innerHTML = rows
    .map(
      (row) => `
      <tr>
        <td>${row.algorithm}</td>
        <td>${row.execution_time_ms.toFixed(4)}</td>
        <td>${row.recursive_calls}</td>
        <td>${row.constraint_checks}</td>
      </tr>`
    )
    .join("");
}

function renderConflicts(conflicts = []) {
  if (!conflicts.length) {
    conflictListEl.innerHTML = `<li class="muted">No subject conflicts detected.</li>`;
    return;
  }
  conflictListEl.innerHTML = conflicts
    .map((c) => {
      if (c.shared_students.length) {
        return `<li><strong>${c.subject_a}</strong> conflicts with <strong>${c.subject_b}</strong> because of shared students: ${c.shared_students.join(", ")}.</li>`;
      }
      return `<li><strong>${c.subject_a}</strong> conflicts with <strong>${c.subject_b}</strong> (defined directly in conflict pairs).</li>`;
    })
    .join("");
}

function renderSteps(steps = []) {
  if (!steps.length) {
    stepsListEl.innerHTML = `<li class="muted">No assignment explanation available.</li>`;
    return;
  }
  stepsListEl.innerHTML = steps.map((s) => `<li>${s}</li>`).join("");
}

function updateModeView() {
  if (modeEl.value === "enrollments") {
    enrollmentsSectionEl.classList.remove("hidden");
    pairsSectionEl.classList.add("hidden");
  } else {
    enrollmentsSectionEl.classList.add("hidden");
    pairsSectionEl.classList.remove("hidden");
  }
}

modeEl.addEventListener("change", updateModeView);

sampleBtn.addEventListener("click", async () => {
  setStatus("Loading sample data...");
  try {
    const res = await fetch("/api/sample");
    if (!res.ok) throw new Error("Could not load sample data.");
    const data = await res.json();
    modeEl.value = data.input_mode;
    slotsEl.value = data.total_slots;
    updateModeView();

    const lines = Object.entries(data.enrollments).map(
      ([subject, students]) => `${subject}: ${students.join(", ")}`
    );
    enrollmentsTextEl.value = lines.join("\n");
    setStatus("Sample data loaded.", "success");
  } catch (error) {
    setStatus(error.message || "Failed to load sample.", "error");
  }
});

solveBtn.addEventListener("click", async () => {
  const payload = {
    input_mode: modeEl.value,
    total_slots: Number(slotsEl.value),
    enrollments: {},
    subjects: [],
    conflict_pairs: [],
  };

  if (payload.input_mode === "enrollments") {
    payload.enrollments = parseEnrollments(enrollmentsTextEl.value);
    if (!Object.keys(payload.enrollments).length) {
      setStatus("Please add subject-to-students data first.", "error");
      return;
    }
  } else {
    payload.subjects = subjectsTextEl.value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    payload.conflict_pairs = parsePairs(pairsTextEl.value);
    if (!payload.subjects.length) {
      setStatus("Please add subjects first.", "error");
      return;
    }
  }

  setStatus("Solving CSP timetable...");
  validationEl.textContent = "Validation message will appear here.";
  validationEl.className = "validation muted";

  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Unable to solve timetable.");
    }

    renderMetrics(data.algorithm_results || []);
    renderConflicts(data.conflict_reasons || []);
    renderSteps(data.assignment_steps || []);

    if (!data.success) {
      renderTimetable([]);
      validationEl.textContent = data.message;
      validationEl.className = "validation error";
      setStatus("No solution found for current slot count.", "error");
      return;
    }

    renderTimetable(data.timetable || []);
    validationEl.textContent = `${data.message} Selected approach: ${data.selected_algorithm}.`;
    validationEl.className = data.valid ? "validation success" : "validation error";
    setStatus("Timetable generated successfully.", "success");
  } catch (error) {
    setStatus(error.message || "An error occurred.", "error");
  }
});

updateModeView();
