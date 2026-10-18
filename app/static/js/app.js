const cropEmoji = {
  rice: "🌾",
  maize: "🌽",
  chickpea: "🫘",
  coffee: "☕",
  banana: "🍌",
  mango: "🥭",
  grapes: "🍇",
  apple: "🍎",
  orange: "🍊",
  cotton: "🧵",
  coconut: "🥥",
};

function showToast(message) {
  const t = document.getElementById("toast");
  t.textContent = message;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 4200);
}

function cropIcon(name) {
  const key = (name || "").toLowerCase();
  return cropEmoji[key] || "🌱";
}

const countrySelect = document.getElementById("countrySelect");
const tempInput = document.getElementById("tempInput");
const rainInput = document.getElementById("rainInput");
const pestInput = document.getElementById("pestInput");
const form = document.getElementById("predictionForm");
const result = document.getElementById("result");
const resultContent = document.getElementById("resultContent");
const resultPlaceholder = document.getElementById("resultPlaceholder");

function resetResultsPanel() {
  resultContent.hidden = true;
  resultPlaceholder.hidden = false;
  result.classList.remove("visible");
}

document.addEventListener("DOMContentLoaded", () => {
  resetResultsPanel();
});

countrySelect.addEventListener("change", async () => {
  const country = countrySelect.value;
  if (!country) return;
  [tempInput, rainInput, pestInput].forEach((el) => {
    el.style.opacity = "0.55";
    el.style.transition = "opacity 0.25s ease";
  });
  try {
    const res = await fetch("/get_defaults", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ country }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || "Could not load defaults");
      return;
    }
    if (data.success) {
      tempInput.value = data.temperature;
      rainInput.value = data.rainfall;
      pestInput.value = data.pesticides;
    }
  } catch (e) {
    showToast("Network error loading defaults");
  } finally {
    [tempInput, rainInput, pestInput].forEach((el) => {
      el.style.opacity = "1";
    });
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("predictBtn");
  const original = btn.textContent;
  btn.innerHTML = 'Analyzing <span class="loader"></span>';
  btn.disabled = true;
  resetResultsPanel();

  const fd = new FormData(form);
  const payload = Object.fromEntries(fd.entries());

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) {
      showToast(body.error || "Prediction failed");
      return;
    }
    if (body.success) {
      const icon = cropIcon(body.crop);
      document.getElementById("cropName").textContent = `${icon} ${body.crop}`;
      document.getElementById("yieldValue").textContent = body.yield;
      document.getElementById("confidenceValue").textContent = `${body.confidence.min} – ${body.confidence.max}`;
      document.getElementById("explanationText").textContent = body.explanation;
      const conf = body.confidence_pct != null ? `${body.confidence_pct}% confident` : "Confidence n/a";
      document.getElementById("confidenceBadge").textContent = conf;
      const cm = body.crop_model || "—";
      const ym = body.yield_model || "—";
      document.getElementById("modelBadge").textContent = `Crop: ${cm} · Yield: ${ym}`;
      resultPlaceholder.hidden = true;
      resultContent.hidden = false;
      result.classList.add("visible");
      result.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      showToast(body.error || "Unknown error");
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`);
  } finally {
    btn.textContent = original;
    btn.disabled = false;
  }
});

async function populateModelModal() {
  const host = document.getElementById("modalTables");
  host.innerHTML = "<p>Loading…</p>";
  try {
    const res = await fetch("/model-info");
    const data = await res.json();
    const cropModels = (data.crop && data.crop.models) || {};
    const yieldModels = (data.yield && data.yield.models) || {};
    let html = "<h3>Crop classifiers</h3><table><thead><tr><th>Model</th><th>Accuracy</th><th>F1 macro</th><th>ROC-AUC</th></tr></thead><tbody>";
    for (const [name, m] of Object.entries(cropModels)) {
      html += `<tr><td>${name}</td><td>${(m.accuracy ?? "").toString().slice(0, 6)}</td><td>${(m.f1_macro ?? "").toString().slice(0, 6)}</td><td>${(m.roc_auc_macro ?? "n/a")}</td></tr>`;
    }
    html += "</tbody></table><h3>Yield regressors</h3><table><thead><tr><th>Model</th><th>R²</th><th>MAE</th><th>RMSE</th></tr></thead><tbody>";
    for (const [name, m] of Object.entries(yieldModels)) {
      html += `<tr><td>${name}</td><td>${(m.r2 ?? "").toString().slice(0, 7)}</td><td>${(m.mae ?? "").toString().slice(0, 8)}</td><td>${(m.rmse ?? "").toString().slice(0, 8)}</td></tr>`;
    }
    html += "</tbody></table>";
    host.innerHTML = html;
  } catch (e) {
    host.innerHTML = "<p>Could not load model metadata.</p>";
  }
}

const backdrop = document.getElementById("modalBackdrop");
document.getElementById("openModelInfo").addEventListener("click", async () => {
  backdrop.classList.add("open");
  backdrop.setAttribute("aria-hidden", "false");
  await populateModelModal();
});
document.getElementById("closeModal").addEventListener("click", () => {
  backdrop.classList.remove("open");
  backdrop.setAttribute("aria-hidden", "true");
});
backdrop.addEventListener("click", (ev) => {
  if (ev.target === backdrop) {
    backdrop.classList.remove("open");
    backdrop.setAttribute("aria-hidden", "true");
  }
});
