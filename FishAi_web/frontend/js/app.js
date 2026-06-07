const ICON_MAP = {
  fish: "ri-fish-line",
  factory: "ri-building-2-line",
  leaf: "ri-plant-line",
  droplet: "ri-drop-line",
  trash: "ri-delete-bin-6-line",
};

const state = {
  models: [],
  selectedFile: null,
  enabledModels: new Set(),
};

const $ = (sel) => document.querySelector(sel);

const fileInput = $("#fileInput");
const uploadZone = $("#uploadZone");
const uploadPlaceholder = $("#uploadPlaceholder");
const previewWrap = $("#previewWrap");
const previewImg = $("#previewImg");
const selectBtn = $("#selectBtn");
const clearBtn = $("#clearBtn");
const detectBtn = $("#detectBtn");
const confSlider = $("#confSlider");
const confValue = $("#confValue");
const modelGrid = $("#modelGrid");
const toggleAllBtn = $("#toggleAllBtn");
const resultImg = $("#resultImg");
const resultPlaceholder = $("#resultPlaceholder");
const resultCards = $("#resultCards");
const resultText = $("#resultText");
const systemStatus = $("#systemStatus");
const modelsDirHint = $("#modelsDirHint");
const loadingOverlay = $("#loadingOverlay");
const toast = $("#toast");
const toastMsg = $("#toastMsg");

function showToast(msg, type = "info") {
  toastMsg.textContent = msg;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => toast.classList.add("hidden"), 3200);
}

function setLoading(on) {
  loadingOverlay.classList.toggle("hidden", !on);
  detectBtn.disabled = on || !state.selectedFile;
}

async function fetchHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const dot = systemStatus.querySelector(".status-dot");
    dot.className = "status-dot ok";
    systemStatus.innerHTML = `
      <span class="status-dot ok"></span>
      <i class="ri-server-line"></i>
      <span>在线 · 模型 ${data.models_available}/${data.models_total} 可用</span>
    `;
    modelsDirHint.innerHTML = `<i class="ri-folder-line"></i> ${data.models_dir}`;
    return data;
  } catch {
    systemStatus.innerHTML = `
      <span class="status-dot error"></span>
      <i class="ri-wifi-off-line"></i>
      <span>服务未连接，请先启动后端</span>
    `;
    return null;
  }
}

async function fetchModels() {
  try {
    const res = await fetch("/api/models");
    const data = await res.json();
    state.models = data.models;
    confSlider.value = data.default_confidence;
    confValue.textContent = Number(data.default_confidence).toFixed(2);
    renderModels();
  } catch {
    showToast("无法加载模型列表", "error");
  }
}

function renderModels() {
  modelGrid.innerHTML = "";
  state.enabledModels.clear();

  state.models.forEach((m) => {
    if (m.default_enabled && m.available) {
      state.enabledModels.add(m.id);
    }

    const card = document.createElement("div");
    card.className = "model-card";
    card.dataset.id = m.id;
    card.style.setProperty("--card-color", m.color);

    if (state.enabledModels.has(m.id)) card.classList.add("active");
    if (!m.available) card.classList.add("unavailable");

    const iconClass = ICON_MAP[m.icon] || "ri-brain-line";
    card.innerHTML = `
      <div class="model-icon"><i class="${iconClass}"></i></div>
      <div class="model-info">
        <h3>${m.emoji} ${m.name}</h3>
        <p>${m.desc}${m.available ? "" : " · 文件缺失"}</p>
      </div>
      <i class="model-check ${state.enabledModels.has(m.id) ? "ri-checkbox-circle-fill" : "ri-checkbox-blank-circle-line"}"></i>
    `;

    card.addEventListener("click", () => toggleModel(m.id, card));
    modelGrid.appendChild(card);
  });

  updateDetectBtn();
  updateToggleAllLabel();
}

function toggleModel(id, card) {
  const model = state.models.find((m) => m.id === id);
  if (!model?.available) {
    showToast(`${model?.name || id} 模型文件不存在，请将 .pt 放入 models 目录`, "error");
    return;
  }

  if (state.enabledModels.has(id)) {
    state.enabledModels.delete(id);
    card.classList.remove("active");
    card.querySelector(".model-check").className = "model-check ri-checkbox-blank-circle-line";
  } else {
    state.enabledModels.add(id);
    card.classList.add("active");
    card.querySelector(".model-check").className = "model-check ri-checkbox-circle-fill";
  }
  updateDetectBtn();
  updateToggleAllLabel();
}

function updateToggleAllLabel() {
  const available = state.models.filter((m) => m.available);
  const allOn = available.length > 0 && available.every((m) => state.enabledModels.has(m.id));
  toggleAllBtn.textContent = allOn ? "取消全选" : "全选";
}

toggleAllBtn.addEventListener("click", () => {
  const available = state.models.filter((m) => m.available);
  const allOn = available.every((m) => state.enabledModels.has(m.id));

  state.enabledModels.clear();
  if (!allOn) available.forEach((m) => state.enabledModels.add(m.id));
  renderModels();
});

function updateDetectBtn() {
  detectBtn.disabled = !state.selectedFile || state.enabledModels.size === 0;
}

function setPreview(file) {
  if (!file || !file.type.startsWith("image/")) {
    showToast("请选择有效的图片文件", "error");
    return;
  }
  state.selectedFile = file;
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  uploadPlaceholder.classList.add("hidden");
  previewWrap.classList.remove("hidden");
  updateDetectBtn();
}

function clearPreview() {
  state.selectedFile = null;
  fileInput.value = "";
  previewImg.src = "";
  uploadPlaceholder.classList.remove("hidden");
  previewWrap.classList.add("hidden");
  updateDetectBtn();
}

selectBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) setPreview(e.target.files[0]);
});

clearBtn.addEventListener("click", clearPreview);

uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("dragover");
});
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragover"));
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) setPreview(file);
});
uploadZone.addEventListener("click", (e) => {
  if (e.target.closest("button")) return;
  if (!state.selectedFile) fileInput.click();
});

confSlider.addEventListener("input", () => {
  confValue.textContent = Number(confSlider.value).toFixed(2);
});

function renderResults(data) {
  if (data.image_base64) {
    resultImg.src = `data:image/jpeg;base64,${data.image_base64}`;
    resultImg.classList.remove("hidden");
    resultPlaceholder.classList.add("hidden");
  }

  resultCards.innerHTML = "";
  (data.results || []).forEach((r) => {
    const item = document.createElement("div");
    item.className = `result-card-item ${r.type || "detect"}`;
    const model = state.models.find((m) => m.id === r.model_id);
    if (model) item.style.setProperty("--card-color", model.color);

    let icon = "ri-focus-3-line";
    if (r.type === "classify") icon = "ri-brain-line";
    if (r.type === "error") icon = "ri-error-warning-line";

    item.innerHTML = `
      <span class="rc-icon"><i class="${icon}"></i></span>
      <span>${r.text || r.model_name}</span>
    `;
    resultCards.appendChild(item);
  });

  let text = `🔍 ===== AI 综合检测结果 =====\n\n${data.summary}`;
  if (data.saved_path) {
    text += `\n\n💾 检测图片已保存:\n${data.saved_path}`;
  }

  const temp = $("#tempInput").value.trim();
  const ph = $("#phInput").value.trim();
  const level = $("#levelInput").value.trim();
  if (temp || ph || level) {
    text += "\n\n📋 环境参数:";
    if (temp) text += `\n  🌡️ 水温: ${temp} ℃`;
    if (ph) text += `\n  🧪 pH: ${ph}`;
    if (level) text += `\n  💧 水位: ${level} cm`;
  }

  resultText.textContent = text;
}

detectBtn.addEventListener("click", async () => {
  if (!state.selectedFile || state.enabledModels.size === 0) return;

  const form = new FormData();
  form.append("file", state.selectedFile);
  form.append("confidence", confSlider.value);
  form.append("enabled_models", [...state.enabledModels].join(","));

  setLoading(true);
  try {
    const res = await fetch("/api/detect", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "检测失败");
    renderResults(data);
    showToast("检测完成！", "success");
  } catch (err) {
    showToast(err.message || "检测出错", "error");
  } finally {
    setLoading(false);
  }
});

async function init() {
  await fetchHealth();
  await fetchModels();
}

init();
