/* === DOM ELEMENTY ===================================================== */
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

/* === 1) PŘÍJEM SOUBORU =============================================== */
function handleFile(file){
  if(!file || !file.type.startsWith("image/")) return;
  const dt = new DataTransfer(); dt.items.add(file); imageInput.files = dt.files;
  previewImg.src = URL.createObjectURL(file); previewImg.classList.remove("hidden");
  dzText.textContent = "Obrázek připraven ✔︎"; submitBtn.disabled = false;
}
dropZone.addEventListener("dragover",e=>{e.preventDefault();dropZone.classList.add("dragover")});
dropZone.addEventListener("dragleave",()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop",e=>{e.preventDefault();dropZone.classList.remove("dragover");handleFile(e.dataTransfer.files[0])});
dropZone.addEventListener("click",()=>imageInput.click());
imageInput.addEventListener("change",()=>handleFile(imageInput.files[0]));
window.addEventListener("paste",e=>{
  if(e.clipboardData?.items){
    for(const it of e.clipboardData.items){
      if(it.kind==="file"&&it.type.startsWith("image/")){handleFile(it.getAsFile());return;}
    }
  }
  if(e.clipboardData?.files.length) handleFile(e.clipboardData.files[0]);
});

/* === 2) ANALÝZA ====================================================== */
submitBtn.addEventListener("click",analyze);
async function analyze(){
  loader.classList.remove("hidden");
  resultBox.classList.add("hidden");
  submitBtn.disabled = true;

  try{
    const fd=new FormData(); fd.append("image",imageInput.files[0]);
    const res = await fetch("/analyze",{method:"POST",body:fd});
    const json = await res.json();
    if(!res.ok) throw new Error(json.error||"Chyba serveru");
    renderResult(json.analysis||json);  // podporuje i prostý text
  }catch(err){ renderPlain("Chyba: "+err.message); }
  finally{ loader.classList.add("hidden"); }
}

/* === 3) VYKRESLENÍ VÝSLEDKU ========================================== */
function renderResult(data){
  // fallback na starý plain-text
  if(typeof data === "string"){ renderPlain(data); return; }

  analysisTbl.innerHTML=""; sourcesList.innerHTML="";
  // tabulka: tvrzení / verdikt / vysvětlení
  const rows=[
    ["Tvrzení", data.claim||"–"],
    ["Verdikt" , formatVerdict(data.verdict||"–")],
    ["Vysvětlení", data.explanation||"–"]
  ];
  rows.forEach(([k,v])=>{
    const tr=analysisTbl.insertRow();
    tr.insertCell().textContent=k;
    if(typeof v==="string") {tr.insertCell().textContent=v;}
    else tr.insertCell().appendChild(v);           // badge node
  });
  analysisTbl.classList.remove("hidden");
  // zdroje
  if(Array.isArray(data.sources)&&data.sources.length){
    data.sources.forEach(src=>{
      const li=document.createElement("li");
      const a=document.createElement("a");
      a.href=src.url; a.target="_blank"; a.rel="noopener"; a.textContent=src.title||src.url;
      li.appendChild(a);
      li.insertAdjacentHTML("beforeend",` <span class=\"stars\">${'★'.repeat(src.relevance||3)}</span>`);
      sourcesList.appendChild(li);
    });
    sourcesBox.classList.remove("hidden");
  }else{
    sourcesBox.classList.add("hidden");
  }
  plainTextEl.classList.add("hidden");
  resultBox.classList.remove("hidden");
}
function renderPlain(text){
  analysisTbl.classList.add("hidden");
  sourcesBox.classList.add("hidden");
  plainTextEl.textContent=text;
  plainTextEl.classList.remove("hidden");
  resultBox.classList.remove("hidden");
}
function formatVerdict(v){
  const span=document.createElement("span");
  span.className=`badge ${v}`;
  span.textContent=v==="Partial"?"Částečně pravda":v==="True"?"Pravda":v==="False"?"Nepravda":v;
  return span;
}
