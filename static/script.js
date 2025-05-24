/* === DOM ============================================================= */
const imageInput  = document.getElementById("imageInput");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultBox   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
const plainTextEl = document.getElementById("plainText");
const sourcesBox  = document.getElementById("sourcesBox");
const sourcesList = document.getElementById("sourcesList");
const dzText      = document.getElementById("dzText");
const previewImg  = document.getElementById("preview");
const dzOverlay   = document.querySelector(".dz-content");

/* === 1) PŘÍJEM SOUBORU =============================================== */
function handleFile(file){
  if(!file || !file.type.startsWith("image/")) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  imageInput.files = dt.files;

  previewImg.src = URL.createObjectURL(file);
  previewImg.classList.remove("hidden");
  dzOverlay.classList.add("hidden");

  dzText.textContent = "Obrázek připraven ✔︎";
  submitBtn.disabled = false;
}
function resetDropzone(){
  imageInput.value = "";
  previewImg.classList.add("hidden");
  dzOverlay.classList.remove("hidden");
  dzText.textContent = "Sem přetáhni obrázek nebo stiskni Ctrl + V";
  submitBtn.disabled = true;
}
dropZone.addEventListener("dragover",e=>{e.preventDefault();dropZone.classList.add("dragover")});
dropZone.addEventListener("dragleave",()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop",e=>{e.preventDefault();dropZone.classList.remove("dragover");handleFile(e.dataTransfer.files[0])});
dropZone.addEventListener("click",()=>imageInput.click());
imageInput.addEventListener("change",()=>handleFile(imageInput.files[0]));

/* === Ctrl + V – robustní ============================================ */
function registerPasteListener(target){
  target.addEventListener("paste", e=>{
    // items (PrintScreen, snímek schránky)
    if(e.clipboardData?.items?.length){
      for(const it of e.clipboardData.items){
        if(it.kind==="file" && it.type.startsWith("image/")){
          handleFile(it.getAsFile());
          e.preventDefault();
          return;
        }
      }
    }
    // files (Ctrl+C obrázek z Průzkumníka)
    if(e.clipboardData?.files?.length){
      handleFile(e.clipboardData.files[0]);
      e.preventDefault();
    }
  });
}
registerPasteListener(window);
registerPasteListener(document);
registerPasteListener(dropZone);

/* === 2) ANALÝZA ====================================================== */
submitBtn.addEventListener("click", analyze);
async function analyze(){
  loader.classList.remove("hidden");
  resultBox.classList.add("hidden");
  submitBtn.disabled = true;

  try{
    const fd = new FormData();
    fd.append("image", imageInput.files[0]);

    const res  = await fetch("/analyze",{method:"POST",body:fd});
    const json = await res.json();
    if(!res.ok) throw new Error(json.error || "Chyba serveru");

    renderResult(json.analysis || json);
  }catch(err){ renderPlain("Chyba: "+err.message); }
  finally{ loader.classList.add("hidden"); }
}

/* === 3) VÝSLEDEK ===================================================== */
function renderResult(data){
  if(typeof data === "string"){ renderPlain(data); return; }

  analysisTbl.innerHTML = "";
  sourcesList.innerHTML = "";

  const rows = [
    ["Tvrzení"   , data.claim || "–"],
    ["Verdikt"   , verdictBadge(data.verdict)],
    ["Vysvětlení", data.explanation || "–"]
  ];
  rows.forEach(([k,v])=>{
    const tr = analysisTbl.insertRow();
    tr.insertCell().textContent = k;
    if(typeof v === "string") tr.insertCell().textContent = v;
    else tr.insertCell().appendChild(v);
  });
  analysisTbl.classList.remove("hidden");

  if(Array.isArray(data.sources)&&data.sources.length){
    data.sources.forEach(src=>sourcesList.appendChild(sourceLi(src)));
    sourcesBox.classList.remove("hidden");
  }else sourcesBox.classList.add("hidden");

  plainTextEl.classList.add("hidden");
  resultBox.classList.remove("hidden");
  resetDropzone();                       // připrav další Ctrl+V
}
function renderPlain(text){
  analysisTbl.classList.add("hidden");
  sourcesList.innerHTML = "";

  const mdRe = /\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g;
  const matches = [...text.matchAll(mdRe)];
  if(matches.length){
    matches.forEach(m=>sourcesList.appendChild(sourceLi({title:m[1],url:m[2],relevance:3})));
    sourcesBox.classList.remove("hidden");
  }else sourcesBox.classList.add("hidden");

  plainTextEl.textContent = text.replace(mdRe,'$1 ($2)');
  plainTextEl.classList.remove("hidden");
  resultBox.classList.remove("hidden");
  resetDropzone();
}

/* === Pomocné ========================================================= */
function verdictBadge(v){
  if(!v) return document.createTextNode("–");
  const span=document.createElement("span");
  span.className=`badge ${v}`;
  span.textContent=
    v==="True"    ? "Pravda" :
    v==="False"   ? "Nepravda" :
    v==="Partial" ? "Částečně pravda" : v;
  return span;
}
function sourceLi(src){
  const li=document.createElement("li");
  const a=document.createElement("a");
  a.href=src.url; a.target="_blank"; a.rel="noopener"; a.textContent=src.title||src.url;
  li.appendChild(a);
  li.insertAdjacentHTML("beforeend",` <span class="stars">${'★'.repeat(src.relevance||3)}</span>`);
  return li;
}
