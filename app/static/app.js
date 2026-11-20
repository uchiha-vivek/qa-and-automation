const $ = (sel) => document.querySelector(sel);
let currentTicketId = null;

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail ? JSON.stringify(body.detail) : `HTTP ${res.status}`);
  return body;
}

function formatDate(iso) {
  return new Date(iso).toLocaleString();
}

async function loadVersion() {
  const h = await api("/api/health");
  $("#version").textContent = `v${h.version} · LLM: ${h.llm_mode}`;
}

async function loadTickets() {
  const params = new URLSearchParams();
  if ($("#filter-priority").value) params.set("priority", $("#filter-priority").value);
  if ($("#filter-category").value) params.set("category", $("#filter-category").value);
  if ($("#search").value) params.set("q", $("#search").value);

  const tickets = await api(`/api/tickets?${params}`);
  $("#ticket-rows").innerHTML = tickets.map((t) => `
    <tr data-id="${t.id}" data-testid="ticket-row">
      <td>${t.id}</td>
      <td>${t.subject || "(no subject)"}</td>
      <td>${t.category}</td>
      <td><span class="badge ${t.priority}" data-testid="priority-badge">${t.priority}</span></td>
      <td>${t.sentiment}</td>
      <td>${Math.round(t.confidence * 100)}%</td>
      <td>${formatDate(t.created_at)}</td>
    </tr>`).join("");

  document.querySelectorAll("#ticket-rows tr").forEach((row) =>
    row.addEventListener("click", () => showTicket(row.dataset.id)));

  const m = await api("/api/metrics");
  $("#metrics").textContent =
    `Total: ${m.total_tickets} · Overrides: ${m.overrides} · AI accuracy: ` +
    (m.ai_accuracy === null ? "n/a" : `${(m.ai_accuracy * 100).toFixed(1)}%`);
}

async function showTicket(id) {
  const t = await api(`/api/tickets/${id}`);
  currentTicketId = id;
  $("#detail").classList.remove("hidden");
  $("#detail-id").textContent = `#${t.id}`;
  $("#detail-body").innerHTML = `
    <p><b>From:</b> ${t.customer_name} &lt;${t.email}&gt;</p>
    <p><b>Subject:</b> ${t.subject}</p>
    <p><b>Message:</b><br>${t.message}</p>
    <p><b>AI result:</b> ${t.ai_category} / ${t.ai_priority} · sentiment ${t.sentiment} ·
       confidence ${t.confidence} · language ${t.language}</p>
    <p><b>Current:</b> <span data-testid="detail-category">${t.category}</span> /
       <span data-testid="detail-priority">${t.priority}</span> · status ${t.status}</p>
    <p><b>Suggested reply:</b></p>
    <pre data-testid="suggested-reply">${t.suggested_reply}</pre>
    <p><b>Audit log:</b> ${t.audit_log.length} entr${t.audit_log.length === 1 ? "y" : "ies"}</p>`;
}

$("#ticket-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  $("#form-status").textContent = "Triaging with AI...";
  try {
    const t = await api("/api/tickets", { method: "POST", body: JSON.stringify(data) });
    $("#form-status").textContent = `Created ticket #${t.id}: ${t.priority} / ${t.category}`;
    e.target.reset();
    await loadTickets();
    await showTicket(t.id);
  } catch (err) {
    $("#form-status").textContent = `Error: ${err.message}`;
  }
});

$("#override-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  try {
    await api(`/api/tickets/${currentTicketId}/override`, { method: "PATCH", body: JSON.stringify(data) });
    await loadTickets();
    await showTicket(currentTicketId);
  } catch (err) {
    alert(`Override failed: ${err.message}`);
  }
});

$("#refresh").addEventListener("click", loadTickets);
$("#filter-priority").addEventListener("change", loadTickets);
$("#filter-category").addEventListener("change", loadTickets);
$("#search").addEventListener("keyup", (e) => { if (e.key === "Enter") loadTickets(); });

loadVersion();
loadTickets();
