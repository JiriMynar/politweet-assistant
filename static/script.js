/* ======  DOM ELEMENTY  ================================================= */
const imageInput  = document.getElementById("imageInput");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultDiv   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
const dzText      = document.getElementById("dzText");

/* ======  1) PŘÍJEM SOUBORU  ============================================ */
function handleFile(file) {
  if (!file || !file.type.startsWith("image/")) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  imageInput.files = dt.files;

  dzText.textContent = "Obrázek připraven ✔︎";
  submitBtn.disabled = false;
}

/* Drag & Drop */
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave",   () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  handleFile(e.dataTransfer.files[0]);
});

/* Kliknutí – otevře file-picker (platí i pro pseudo-button uvnitř) */
dropZone.addEventListener("click", () => imageInput.click());

/* Klasické vybrání souboru */
imageInput.addEventListener("change", () => handleFile(imageInput.files[0]));

/* Ctrl + V – podpora clipboardData.items (PrintScreen) i files */
window.addEventListener("paste", e => {
  // 1) moderní prohlížeče: items
  if (e.clipboardData && e.clipboardData.items) {
    for (const item of e.clipboardData.items) {
      if (item.kind === "file" && item.type.startsWith("image/")) {
        handleFile(item.getAsFile());
        return;
      }
    }
  }
  // 2) fallback: files (některé webkity)
  const files = e.clipboardData?.files || [];
  if (files.length) handleFile(files[0]);
});

/* ======  2) ANALÝZA  =================================================== */
async function analyze() {
  loader.classList.remove("hidden");
  resultDiv.classList.add("hidden");
  submitBtn.disabled = true;

  try {
    const formData = new FormData();
    formData.append("image", imageInput.files[0]);

    const res  = await fetch("/analyze", { method:"POST", body:formData });
    const json = await res.json();

    if (!res.ok) throw new Error(json.error || "Chyba serveru");
    fillTable(json.analysis);
  } catch (err) {
    fillTable("Chyba: " + err.message);
  } finally {
    loader.classList.add("hidden");
  }
}

submitBtn.addEventListener("click", analyze);

/* ======  3) VYKRESLENÍ TABULKY  ======================================== */
function fillTable(rawText) {
  analysisTbl.innerHTML = "";
  resultDiv.classList.remove("hidden");

  const rows = rawText.split(/\n+/).filter(Boolean);
  rows.forEach(line => {
    const [left, ...rest] = line.split(/[:–-]/);
    if (rest.length) {
      const tr = analysisTbl.insertRow();
      tr.insertCell().textContent = left.trim();
      tr.insertCell().textContent = rest.join("–").trim();
    } else {
      const tr = analysisTbl.insertRow();
      const td = tr.insertCell();
      td.colSpan = 2;
      td.textContent = line.trim();
    }
  });
}
