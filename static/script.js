/* === DOM ============================================================= */
const imageInput  = document.getElementById("imageInput");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultBox   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
const sourcesBox  = document.getElementById("sourcesBox");
const sourcesList = document.getElementById("sourcesList");
const previewImg  = document.getElementById("preview");
const dzOverlay   = document.querySelector(".dz-content");

/* === 1) PŘÍJEM SOUBORU =============================================== */
function handleFile(file){
  if(!file || !file.type.startsWith("image/")) return;
  const dt = new DataTransfer(); dt.items.add(file); imageInput.files = dt.files;

  previewImg.src = URL.createObjectURL(file);
  previewImg.classList.remove("hidden");
  dzOverlay.classList.add("hidden");
  dropZone.classList.add("has-image");
  submitBtn.disabled = false;
}
function resetDropzone(){
  imageInput.value=""; previewImg.classList.add("hidden");
  dzOverlay.classList.remove("hidden"); dropZone.classList.remove("has-image");
  submitBtn.disabled = true;
}
dropZone.addEventListener("dragover",e=>{e.preventDefault();dropZone.classList.add("dragover")});
dropZone.addEventListener("dragleave",()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop",e=>{e.preventDefault();dropZone.classList.remove("dragover");handleFile(e.dataTransfer.files[0])});
dropZone.addEventListener("click",()=>imageInput.click());
imageInput.addEventListener("change",()=>handleFile(imageInput.files[0]));

/* === Ctrl + V — univerzální listener ================================ */
/* – naslouchá přímo na document.body
   – funguje, ať je fokus kdekoliv (Chrome, Edge, Firefox, Safari)     */
document.body.addEventListener("paste", e => {
  console.log("paste event", e);              // ↖︎ rychlá kontrola v konzoli

  const items = e.clipboardData?.items;
  if (items?.length) {
    for (const it of items) {
      if (it.kind === "file" && it.type.startsWith("image/")) {
        handleFile(it.getAsFile());
        e.preventDefault();
        return;
      }
    }
  }
  const files = e.clipboardData?.files;
  if (files?.length) {
    handleFile(files[0]);
    e.preventDefault();
  }
});

/* === 2) ANALÝZA ====================================================== */
submitBtn.addEventListener("click",analyse);
async function analyse(){
  loader.classList.remove("hidden"); resultBox.classList.add("hidden"); submitBtn.disabled=true;
  try{
    const fd=new FormData(); fd.append("image",imageInput.files[0]);
    const res = await fetch("/analyze",{method:"POST",body:fd});
    const data = await res.json();
    if(!res.ok) throw new Error(data.error||"Chyba serveru");
    renderResult(typeof data==="string"?parsePlain(data):(data.analysis||data));
  }catch(err){
    renderResult({claim:"–",verdict:"Error",explanation:err.message,sources:[]});
  }finally{ loader.classList.add("hidden"); resetDropzone(); }
}

/* === 3) PARSE PLAIN-TEXT ============================================ */
function parsePlain(txt){
  const lines=txt.split(/\n+/).map(l=>l.trim()).filter(Boolean);
  const ratingIdx=lines.findIndex(l=>/^Rating/i.test(l));
  const srcIdx   =lines.findIndex(l=>/^Zdroje/i.test(l));

  const explLines = lines.slice(0,ratingIdx>-1?ratingIdx:(srcIdx>-1?srcIdx:lines.length));
  const explanation = explLines.join(" ");

  let verdict="Unknown";
  if(ratingIdx>-1){
    const m=lines[ratingIdx].match(/\\*\\*(.*?)\\*\\*/);
    verdict = m?({True:"True",False:"False"}[m[1]]||"Partial"):"Partial";
  }

  const sources=[];
  if(srcIdx>-1){
    for(let i=srcIdx+1;i<lines.length;i++){
      const m=lines[i].match(/\\[(.*?)\\]\\((https?:\\/\\/[^\\s)]+)\\)/);
      if(m) sources.push({title:m[1],url:m[2],relevance:3});
    }
  }
  return {claim:"—",verdict,explanation,sources};
}

/* === 4) VÝSLEDEK ===================================================== */
function renderResult(data){
  analysisTbl.innerHTML=""; sourcesList.innerHTML="";
  const rows=[
    ["Tvrzení"   , data.claim||"–"],
    ["Verdikt"   , badge(data.verdict)],
    ["Vysvětlení", data.explanation||"–"]
  ];
  rows.forEach(([k,v])=>{
    const tr=analysisTbl.insertRow();
    tr.insertCell().textContent=k;
    if(typeof v==="string") tr.insertCell().textContent=v;
    else tr.insertCell().appendChild(v);
  });

  if(data.sources?.length){
    data.sources.forEach(s=>sourcesList.appendChild(sourceLi(s)));
    sourcesBox.classList.remove("hidden");
  }else sourcesBox.classList.add("hidden");

  resultBox.classList.remove("hidden");
}

/* === Pomocné ========================================================= */
function badge(v){
  const span=document.createElement("span");
  span.className=`badge ${v}`; span.textContent=
    v==="True"?"Pravda":v==="False"?"Nepravda":v==="Partial"?"Částečně pravda":v;
  return span;
}
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
