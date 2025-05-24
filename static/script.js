/* === DOM ============================================================= */
const imageInput  = document.getElementById("imageInput");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultBox   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
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
  dropZone.classList.add("has-image");

  submitBtn.disabled = false;
}
function resetDropzone(){
  imageInput.value = "";
  previewImg.classList.add("hidden");
  dzOverlay.classList.remove("hidden");
  dropZone.classList.remove("has-image");
  submitBtn.disabled = true;
}
dropZone.addEventListener("dragover",e=>{e.preventDefault();dropZone.classList.add("dragover")});
dropZone.addEventListener("dragleave",()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop",e=>{e.preventDefault();dropZone.classList.remove("dragover");handleFile(e.dataTransfer.files[0])});
dropZone.addEventListener("click",()=>imageInput.click());
imageInput.addEventListener("change",()=>handleFile(imageInput.files[0]));

/* === Ctrl + V – univerzální listener ================================= */
["window","document",dropZone].forEach(t=>{
  (t==='window'?window:t==='document'?document:t).addEventListener("paste", e=>{
    if(e.clipboardData?.items?.length){
      for(const it of e.clipboardData.items){
        if(it.kind==="file"&&it.type.startsWith("image/")){
          handleFile(it.getAsFile());e.preventDefault();return;
        }
      }
    }
    if(e.clipboardData?.files?.length){
      handleFile(e.clipboardData.files[0]);e.preventDefault();
    }
  });
});

/* === 2) ANALÝZA ====================================================== */
submitBtn.addEventListener("click", analyze);
async function analyze(){
  loader.classList.remove("hidden");
  resultBox.classList.add("hidden");
  submitBtn.disabled = true;

  try{
    const fd=new FormData(); fd.append("image", imageInput.files[0]);
    const res  = await fetch("/analyze",{method:"POST",body:fd});
    const json = await res.json();
    if(!res.ok) throw new Error(json.error || "Chyba serveru");

    renderResult(json.analysis || json);
  }catch(err){
    renderResult({claim:"–",verdict:"Error",explanation:err.message,sources:[]});
  }finally{
    loader.classList.add("hidden");
    resetDropzone();
  }
}

/* === 3) VÝSLEDEK ===================================================== */
function renderResult(data){
  analysisTbl.innerHTML=""; sourcesList.innerHTML="";

  /* Pokud backend pošle plain text, rozdělíme ho na řádky a vložíme do tabulky */
  if(typeof data === "string"){
    data.split(/\\n+/).forEach(line=>{
      const tr=analysisTbl.insertRow(); tr.insertCell().colSpan=2; tr.cells[0].textContent=line.trim();
    });
  }else{
    const rows=[
      ["Tvrzení"   , data.claim || "–"],
      ["Verdikt"   , badge(data.verdict)],
      ["Vysvětlení", data.explanation || "–"]
    ];
    rows.forEach(([k,v])=>{
      const tr=analysisTbl.insertRow();
      tr.insertCell().textContent=k;
      if(typeof v==="string") tr.insertCell().textContent=v;
      else tr.insertCell().appendChild(v);
    });
    if(Array.isArray(data.sources) && data.sources.length){
      data.sources.forEach(src=>sourcesList.appendChild(sourceLi(src)));
      sourcesBox.classList.remove("hidden");
    }else sourcesBox.classList.add("hidden");
  }
  resultBox.classList.remove("hidden");
}
/* Badge verdiktu */
function badge(v){
  if(!v) return document.createTextNode("–");
  const span=document.createElement("span");
  span.className=`badge ${v}`;
  span.textContent=
    v==="True"?"Pravda":v==="False"?"Nepravda":v==="Partial"?"Částečně pravda":v;
  return span;
}
/* Li se 5★ */
function sourceLi({title,url,relevance=3}){
  const li=document.createElement("li");
  const a=document.createElement("a");
  a.href=url; a.target="_blank"; a.rel="noopener"; a.textContent=title||url;
  li.appendChild(a);

  for(let i=1;i<=5;i++){
    const star=document.createElement("span");
    star.className=`star ${i<=relevance?'fill':'empty'}`;
    star.textContent=i<=relevance?"★":"☆";
    li.appendChild(star);
  }
  return li;
}
