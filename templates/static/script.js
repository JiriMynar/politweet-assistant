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

  /* uložíme do skrytého <input>, aby šel poslat přes FormData */
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

/* Kliknutí = otevře file-picker */
dropZone.addEventListener("click", () => imageInput.click());

/* Klasické vybrání souboru */
imageInput.addEventListener("change", () => handleFile(imageInput.files[0]));

/* Ctrl + V kdekoliv v okně */
window.addEventListener("paste", e => {
  const items = e.clipboardData.files || [];
  if (items.length) handleFile(items[0]);
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

  /* jednoduchá heuristika: "klíč: hodnota" nebo celý řádek */
  const rows = rawText.split(/\n+/).filter(Boolean);
  rows.forEach(line => {
    const [left, ...rest] = line.split(/[:–-]/);  // podporuje : – -
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
