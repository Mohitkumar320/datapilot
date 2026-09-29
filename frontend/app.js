let sessionId = crypto.randomUUID();
let hasAsked = false;

// Tab switching
document.getElementById("tab-csv").onclick = () => setTab("csv");
document.getElementById("tab-db").onclick = () => setTab("db");

function setTab(which) {
  document.getElementById("csv-panel").style.display = which === "csv" ? "block" : "none";
  document.getElementById("db-panel").style.display = which === "db" ? "block" : "none";
  document.getElementById("tab-csv").className = which === "csv" ? "" : "inactive";
  document.getElementById("tab-db").className = which === "db" ? "" : "inactive";
}

// CSV upload
document.getElementById("upload-btn").onclick = async () => {
  const file = document.getElementById("csv-file").files[0];
  if (!file) return alert("Choose a file first");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("session_id", sessionId);

  const res = await fetch("/upload-csv", { method: "POST", body: formData });
   if (res.ok) {
    const data = await res.json();
    updateSessionStatus(`CSV: ${file.name}`);
    showChatUI();
    if (data.profile) renderProfile(data.profile);
  } else {
    alert("Upload failed");
  }
};

// DB connect
document.getElementById("connect-btn").onclick = async () => {
  const payload = {
    session_id: sessionId,
    host: document.getElementById("db-host").value,
    port: document.getElementById("db-port").value,
    user: document.getElementById("db-user").value,
    password: document.getElementById("db-pass").value,
    database: document.getElementById("db-name").value
  };

  const res = await fetch("/connect-db", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    updateSessionStatus(`DB: ${payload.database}`);
    showChatUI();
  } else {
    alert("Connection failed");
  }
};

function updateSessionStatus(text) {
  document.getElementById("session-status").textContent = text;
}

function showChatUI() {
  document.getElementById("setup-overlay").style.display = "none";
  document.getElementById("chat-column").style.display = "flex";
}

// New Session button — full reset
document.getElementById("new-session-btn").onclick = () => {
  location.reload();
};

// "+" button — reopen setup without full reload
document.getElementById("switch-source-btn").onclick = () => {
  document.getElementById("setup-overlay").style.display = "flex";
};

// Ask question
document.getElementById("ask-btn").onclick = async () => {
  const input = document.getElementById("question-input");
  const question = input.value.trim();
  if (!question) return;

  if (!hasAsked) {
    document.getElementById("greeting").style.display = "none";
    hasAsked = true;
  }

  addMessage(question, "user");
  input.value = "";
  addToHistory(question);

  document.getElementById("loading-indicator").style.display = "block";

  const res = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question })
  });
  const result = await res.json();

  document.getElementById("loading-indicator").style.display = "none";

  renderAnswer(result);

  if (result.chart_path) {
    addChart();
  }
};

function addMessage(text, type) {
  const messages = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function renderAnswer(result) {
  const messages = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg answer";

  let data = result.data;
    if (data && typeof data === "object" && Array.isArray(data.columns) && typeof data.rows === "number") {
    renderProfile(data);
    return;
  }
  if (typeof data === "string") {
    try { data = JSON.parse(data); } catch (e) {}
  }
  if (data && !Array.isArray(data) && typeof data === "object") data = [data];

  const hasRows = Array.isArray(data) && data.length > 0 && typeof data[0] === "object";

  if (result.message) {
    const p = document.createElement("div");
    p.textContent = result.message;
    div.appendChild(p);
  }

    if (hasRows && !result.chart_path) {
    const cols = Object.keys(data[0]);
    if (data.length === 1 && cols.length === 1) {
      const p = document.createElement("div");
      p.textContent = `${cols[0].replace(/_/g, " ")}: ${formatValue(data[0][cols[0]])}`;
      div.appendChild(p);
    } else {
      div.appendChild(buildTable(data, cols));
    }
   } else if (!result.message && !result.chart_path) {
    div.textContent = "No result.";
  }

  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function formatValue(v) {
  if (typeof v === "number" && !Number.isInteger(v)) return v.toFixed(2);
  return v ?? "";
}

function buildTable(rows, cols) {
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const table = document.createElement("table");

  const headRow = table.createTHead().insertRow();
  cols.forEach(c => {
    const th = document.createElement("th");
    th.textContent = c;
    headRow.appendChild(th);
  });

  const body = table.createTBody();
  rows.slice(0, 50).forEach(r => {
    const tr = body.insertRow();
    cols.forEach(c => { tr.insertCell().textContent = formatValue(r[c]); });
  });

  wrap.appendChild(table);
  if (rows.length > 50) {
    const note = document.createElement("div");
    note.className = "table-note";
    note.textContent = `Showing first 50 of ${rows.length} rows`;
    wrap.appendChild(note);
  }
  return wrap;
}
function addChart() {
  const messages = document.getElementById("messages");
  const wrapper = document.createElement("div");
  wrapper.id = "chart-wrapper";

  const img = document.createElement("img");
  img.id = "chart-img";
  img.src = "/chart?t=" + Date.now();

  const downloadBtn = document.createElement("button");
  downloadBtn.id = "download-chart-btn";
  downloadBtn.textContent = "Download Chart";
  downloadBtn.onclick = () => {
    const a = document.createElement("a");
    a.href = img.src;
    a.download = "chart.png";
    a.click();
  };

  wrapper.appendChild(img);
  wrapper.appendChild(downloadBtn);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

function addToHistory(question) {
  const list = document.getElementById("history-list");
  const item = document.createElement("div");
  item.className = "history-item";
  item.textContent = question;
  item.title = question;
  list.appendChild(item);
}

// Enter key sends the question
document.getElementById("question-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("ask-btn").click();
  }
});

function renderProfile(profile) {
  document.getElementById("greeting").style.display = "none";

  const messages = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg answer";

  const title = document.createElement("div");
  title.textContent = `Your data: ${profile.rows.toLocaleString()} rows × ${profile.columns.length} columns`;
  div.appendChild(title);

  const cols = ["Column", "Type", "Nulls", "Unique", "Min", "Max", "Mean", "Median", "Most common"];
  const rows = profile.columns.map(c => ({
    "Column": c.name,
    "Type": c.type,
    "Nulls": c.nulls,
    "Unique": c.unique,
    "Min": c.min,
    "Max": c.max,
    "Mean": c.mean,
    "Median": c.median,
    "Most common": c.top !== undefined ? `${c.top} (${c.top_count})` : ""
  }));

  div.appendChild(buildTable(rows, cols));
  messages.appendChild(div);
}