async function fetchJSON(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`Failed to fetch ${path}`);
  return resp.json();
}

function formatPercent(val) {
  if (val === undefined || val === null) return "—";
  return `${(val * 100).toFixed(1)}%`;
}

function setKPIs(summary) {
  const total = summary.total_decisions || 0;
  document.getElementById("kpi-total").textContent = total;
  document.getElementById("kpi-escalation").textContent = formatPercent(summary.escalation_rate);
  document.getElementById("kpi-block").textContent = formatPercent(summary.block_rate);
}

function buildTimelineChart(ctx, timeline) {
  const labels = timeline.map((t) => t.date);
  const statuses = ["completed", "escalate_to_max", "blocked"];
  const colors = {
    completed: "#0ea5e9",
    escalate_to_max: "#f59e0b",
    blocked: "#ef4444",
  };

  const datasets = statuses.map((s) => ({
    label: s,
    data: timeline.map((t) => (t.counts[s] || 0)),
    borderColor: colors[s],
    backgroundColor: colors[s],
    tension: 0.2,
  }));

  new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom" } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}

function renderOpenTasks(tasks) {
  const tbody = document.querySelector("#tasks-table tbody");
  tbody.innerHTML = "";
  tasks.forEach((t) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.id || "—"}</td>
      <td>${t.kind || "—"}</td>
      <td>${t.target || "—"}</td>
      <td>${t.summary || "—"}</td>
      <td>${t.allow_codegen ? "yes" : "no"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderDecisions(decisions) {
  const tbody = document.querySelector("#decisions-table tbody");
  tbody.innerHTML = "";
  // Sort latest first, limit to 20
  const limited = decisions
    .slice()
    .sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""))
    .slice(0, 20);

  limited.forEach((d) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.task_id || "—"}</td>
      <td>${d.status || "—"}</td>
      <td>${d.source || "—"}</td>
      <td>${d.confidence ?? "—"}</td>
      <td>${d.timestamp || "—"}</td>
      <td>${(d.trace && d.trace.claim) || "—"}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function init() {
  try {
    const [summary, decisions, tasksOpen] = await Promise.all([
      fetchJSON("data/summary.json"),
      fetchJSON("data/decisions.json"),
      fetchJSON("data/tasks_open.json"),
    ]);

    setKPIs(summary);
    renderOpenTasks(tasksOpen);
    renderDecisions(decisions);
    const timeline = summary.timeline || [];
    const ctx = document.getElementById("timelineChart").getContext("2d");
    buildTimelineChart(ctx, timeline);
  } catch (err) {
    console.error("Dashboard init failed:", err);
    const main = document.querySelector("main");
    main.innerHTML = `<p style="color:#b91c1c">Failed to load dashboard data: ${err}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", init);

