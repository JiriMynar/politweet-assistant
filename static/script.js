/* === DOM ELEMENTY ===================================================== */
const imageInput  = document.getElementById("imageInput");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultDiv   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
const dzText      = document.getElementById("dzText");
const previewImg  = document.getElementById("preview");

/* === 1) PŘÍJEM SOUBORU =============================================== */
function handleFile(file){
  if(!file || !file.type.startsWith("image/")) return;

  /* vložíme do skrytého inputu */
  const dt = new DataTransfer();
  dt.items.add(file);
  imageInput.files = dt.files;

  /* náhled */
  previewImg.src = URL.createObjectURL(file);
  previewImg.classList.remove("hidden");

  dzText.textContent = "Obrázek připraven ✔︎";
  submitBtn.disabled = false;
}

/* Drag & Drop */
dropZone.addEventListener("dragover", e=>{e.preventDefault();dropZone.classList.add("dragover");});
dropZone.addEventListener("dragleave", ()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e=>{
  e.preventDefault();dropZone.classList.remove("dragover");
  handleFile(e.dataTransfer.files[0]);
});

/* Kliknutí dovnitř zóny */
dropZone.addEventListener("click", ()=>imageInput.click());
imageInput.addEventListener("change", ()=>handleFile(imageInput.files[0]));

/* Ctrl + V (PrintScreen) */
window.addEventListener("paste", e=>{
  if(e.clipboardData?.items){
    for(const item of e.clipboardData.items){
      if(item.kind==="file" && item.type.startsWith("image/")){
        handleFile(item.getAsFile());return;
      }
    }
  }
  const files = e.clipboardData?.files || [];
  if(files.length) handleFile(files[0]);
});

/* === 2) ANALÝZA ====================================================== */
async function analyze(){
  loader.classList.remove("hidden");
  resultDiv.classList.add("hidden");
  submitBtn.disabled = true;

  try{
    const fd = new FormData();
    fd.append("image", imageInput.files[0]);

    const res  = await fetch("/analyze", {method:"POST", body:fd});
    const json = await res.json();
    if(!res.ok) throw new Error(json.error || "Chyba serveru");

    fillTable(json.analysis);
  }catch(err){ fillTable("Chyba: "+err.message); }
  finally{ loader.classList.add("hidden"); }
}
submitBtn.addEventListener("click", analyze);

/* === 3) TABULKA VÝSLEDKŮ ============================================= */
function fillTable(rawText){
  analysisTbl.innerHTML = "";
  resultDiv.classList.remove("hidden");

  rawText.split(/\n+/).filter(Boolean).forEach(line=>{
    const [left,...rest] = line.split(/[:–-]/);
    const tr = analysisTbl.insertRow();
    if(rest.length){
      tr.insertCell().textContent = left.trim();
      tr.insertCell().textContent = rest.join("–").trim();
    }else{
      const td = tr.insertCell();td.colSpan = 2;td.textContent = line.trim();
    }
  });
}
