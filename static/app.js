async function apiGet(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost(path, payload) {
  const res = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `${path} failed: ${res.status}`);
  return data;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"
  }[c]));
}

function renderStats(stats) {
  const total = stats.total ?? 0;

  const byCategory = stats.by_category || [];
  const byPriority = stats.by_priority || [];

  const catRows = byCategory.map(r => `<tr><td>${escapeHtml(r.category)}</td><td>${r.count}</td></tr>`).join("");
  const priRows = byPriority.map(r => `<tr><td>${escapeHtml(r.priority)}</td><td>${r.count}</td></tr>`).join("");

  return `
    <div class="kpi">
      <div class="box">
        <div class="muted">Total tickets</div>
        <div class="value">${total}</div>
      </div>
    </div>

    <div class="muted" style="margin-top:6px;">By category</div>
    <table>
      <thead><tr><th>Category</th><th>Count</th></tr></thead>
      <tbody>${catRows || `<tr><td colspan="2">No data</td></tr>`}</tbody>
    </table>

    <div class="muted" style="margin-top:10px;">By priority</div>
    <table>
      <thead><tr><th>Priority</th><th>Count</th></tr></thead>
      <tbody>${priRows || `<tr><td colspan="2">No data</td></tr>`}</tbody>
    </table>
  `;
}

function renderTickets(items) {
  const rows = (items || []).map(t => `
    <tr>
      <td>${t.id}</td>
      <td>${escapeHtml(t.subject)}</td>
      <td>${escapeHtml(t.category)}</td>
      <td>${escapeHtml(t.priority)}</td>
      <td>${escapeHtml(t.routed_to)}</td>
      <td>${escapeHtml(t.created_at)}</td>
    </tr>
  `).join("");

  return `
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Subject</th><th>Category</th><th>Priority</th><th>Routed to</th><th>Created</th>
        </tr>
      </thead>
      <tbody>
        ${rows || `<tr><td colspan="6">No tickets</td></tr>`}
      </tbody>
    </table>
  `;
}

function showResult(data) {
  const el = document.getElementById("result");
  el.classList.remove("hidden");
  el.innerHTML = `
    <div><b>Created ticket #${data.id}</b></div>
    <div class="muted" style="margin-top:6px;">Classification</div>
    <ul style="margin:6px 0 0 18px;">
      <li><b>Category:</b> ${escapeHtml(data.category)}</li>
      <li><b>Priority:</b> ${escapeHtml(data.priority)}</li>
      <li><b>Routed to:</b> ${escapeHtml(data.routed_to)}</li>
      <li><b>Confidence:</b> ${Number(data.confidence).toFixed(2)}</li>
    </ul>
  `;
}

const DEMOS = [
  {
    source: "email",
    subject: "Server down - production outage",
    body: "Our main server is down since 9AM. Production is impacted and users cannot access the app. Urgent.",
  },
  {
    source: "email",
    subject: "Possible phishing email",
    body: "We received a suspicious email asking for MFA codes. Is this phishing? Please advise urgently.",
  },
  {
    source: "email",
    subject: "Invoice request",
    body: "Can you resend our March invoice and payment details? We need it for reconciliation.",
  },
  {
    source: "chat",
    subject: "VPN access problem",
    body: "I cannot login to the VPN. Password reset did not work and I need access ASAP.",
  },
  {
    source: "form",
    subject: "Laptop screen flickering",
    body: "My laptop screen is flickering and sometimes goes black. It happens intermittently.",
  },
  {
    source: "email",
    subject: "WiFi unstable in office",
    body: "The WiFi keeps disconnecting and latency is high. Teams calls drop frequently.",
  },
];

let demoIndex = 0;

function loadDemo() {
  const d = DEMOS[demoIndex % DEMOS.length];
  demoIndex += 1;

  document.getElementById("source").value = d.source;
  document.getElementById("subject").value = d.subject;
  document.getElementById("body").value = d.body;

  // Optionnel: cacher le résultat précédent quand on charge une nouvelle démo
  const result = document.getElementById("result");
  result.classList.add("hidden");
  result.innerHTML = "";
}

async function refresh() {
  const statsEl = document.getElementById("stats");
  const ticketsEl = document.getElementById("tickets");

  statsEl.textContent = "Loading...";
  ticketsEl.textContent = "Loading...";

  const stats = await apiGet("/stats");
  const tickets = await apiGet("/tickets?limit=25");

  statsEl.innerHTML = renderStats(stats);
  ticketsEl.innerHTML = renderTickets(tickets);
}

async function checkHealth() {
  const el = document.getElementById("api-status");
  try {
    await apiGet("/health");
    el.textContent = "OK";
  } catch {
    el.textContent = "DOWN";
  }
}

document.getElementById("btn-demo").addEventListener("click", loadDemo);
document.getElementById("btn-refresh").addEventListener("click", refresh);

document.getElementById("btn-create").addEventListener("click", async () => {
  const source = document.getElementById("source").value;
  const subject = document.getElementById("subject").value.trim();
  const body = document.getElementById("body").value.trim();

  try {
    const data = await apiPost("/tickets", { source, subject, body });
    showResult(data);
    await refresh();
  } catch (e) {
    alert(e.message || String(e));
  }
});

(async function init() {
  await checkHealth();
  await refresh();
})();