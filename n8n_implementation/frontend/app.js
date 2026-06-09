const N8N_WEBHOOK_URL = "http://localhost:5678/webhook/mailopsai";

const analyzeBtn = document.getElementById("analyzeBtn");
const emailInput = document.getElementById("emailInput");
const loadingState = document.getElementById("loadingState");
const errorBox = document.getElementById("errorBox");
const results = document.getElementById("results");

const fields = {
  classificationPattern: document.getElementById("classificationPattern"),
  classificationOutput: document.getElementById("classificationOutput"),
  responsePattern: document.getElementById("responsePattern"),
  responseOutput: document.getElementById("responseOutput"),
  taskPattern: document.getElementById("taskPattern"),
  taskOutput: document.getElementById("taskOutput"),
  summaryOutput: document.getElementById("summaryOutput"),
};

function labelize(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function renderDefinitionList(container, data, excluded = []) {
  container.innerHTML = "";
  Object.entries(data)
    .filter(([key]) => !excluded.includes(key))
    .forEach(([key, value]) => {
      const wrapper = document.createElement("div");
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = labelize(key);
      dd.textContent = typeof value === "boolean" ? (value ? "Yes" : "No") : String(value);
      wrapper.append(dt, dd);
      container.appendChild(wrapper);
    });
}

function renderTasks(agent) {
  fields.taskOutput.innerHTML = "";
  const list = document.createElement("div");
  list.className = "task-list";

  agent.tasks.forEach((task) => {
    const item = document.createElement("div");
    item.className = "task-item";
    const title = document.createElement("strong");
    const details = document.createElement("dl");
    title.textContent = task.task;
    renderDefinitionList(details, {
      deadline: task.deadline,
      suggested_owner: task.suggested_owner,
    });
    item.append(title, details);
    list.appendChild(item);
  });

  const details = document.createElement("dl");
  renderDefinitionList(details, {
    follow_up_recommendation: agent.follow_up_recommendation,
    reflection: agent.reflection,
  });

  fields.taskOutput.append(list, details);
}

function renderResults(data) {
  fields.classificationPattern.textContent = data.classification_agent.design_pattern;
  renderDefinitionList(fields.classificationOutput, data.classification_agent, ["agent_name", "design_pattern"]);

  fields.responsePattern.textContent = data.response_agent.design_pattern;
  renderDefinitionList(fields.responseOutput, data.response_agent, ["agent_name", "design_pattern"]);

  fields.taskPattern.textContent = data.task_followup_agent.design_pattern;
  renderTasks(data.task_followup_agent);

  renderDefinitionList(fields.summaryOutput, data.final_summary);
  results.hidden = false;
}

async function analyzeEmail() {
  const emailText = emailInput.value.trim();
  errorBox.hidden = true;

  if (N8N_WEBHOOK_URL === "PASTE_YOUR_N8N_WEBHOOK_URL_HERE") {
    errorBox.textContent = "Paste your n8n webhook URL in app.js before testing.";
    errorBox.hidden = false;
    return;
  }

  if (emailText.length < 5) {
    errorBox.textContent = "Please paste a complete email before analyzing.";
    errorBox.hidden = false;
    return;
  }

  analyzeBtn.disabled = true;
  loadingState.hidden = false;

  try {
    const response = await fetch(N8N_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_text: emailText }),
    });

    if (!response.ok) {
      throw new Error("The n8n webhook did not return a successful response.");
    }

    const data = await response.json();
    renderResults(data);
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  } finally {
    analyzeBtn.disabled = false;
    loadingState.hidden = true;
  }
}

analyzeBtn.addEventListener("click", analyzeEmail);
