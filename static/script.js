// === DOM ===
const imageInput  = document.getElementById("image");
const dropZone    = document.getElementById("dropZone");
const submitBtn   = document.getElementById("submitBtn");
const loader      = document.getElementById("loader");
const resultBox   = document.getElementById("result");
const analysisTbl = document.getElementById("analysisTable");
const sourcesBox  = document.getElementById("sourcesBox");
const sourcesList = document.getElementById("sourcesList");
const previewImg  = document.getElementById("preview");
const dzOverlay   = document.querySelector(".dz-content");

// === 1) PŘÍJEM SOUBORU ===
function handleFile(file){
  if(!file || !(file.type||"").startsWith("image/")) return;
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

// === 2) Ctrl + V ===
document.addEventListener("paste", e=>{
  const items=[...(e.clipboardData?.items||[])];
  const fileItem=items.find(it=>it.kind==="file"&&it.type.startsWith("image/"));
  if(fileItem){ handleFile(fileItem.getAsFile()); e.preventDefault(); return; }
  const files=e.clipboardData?.files||[]; if(files.length){ handleFile(files[0]); e.preventDefault(); }
});

// === 3) ANALÝZA ===
submitBtn.addEventListener("click", analyse);
async function analyse(){
  if(!imageInput.files.length && !document.getElementById("text").value.trim()) return;

  loader.classList.remove("hidden");
  resultBox.classList.add("hidden");
  submitBtn.disabled = true;

  try{
    const fd = new FormData();
    if (imageInput.files.length) fd.append("image", imageInput.files[0]);
    fd.append("text", document.getElementById("text").value.trim());
    const res  = await fetch("/analyze",{method:"POST",body:fd});
    const data = await res.json();
    if(!res.ok) throw new Error(data.error||"Chyba serveru");

    let payload = data.analysis ?? data;
    if(typeof payload === "string") payload = parsePlain(payload);
    renderResult(payload);

  }catch(err){
    renderResult({claim:"–",verdict:"Error",explanation:err.message,sources:[]});
  }finally{
    loader.classList.add("hidden");
    resetDropzone();
  }
}

// === 4) PARSE PLAIN-TEXT (Markdown) ===
function parsePlain(txt){
  const clean = txt.replace(/\r/g,"");              
  const firstDot = clean.indexOf(".");
  const claim = firstDot>0 ? clean.slice(0,firstDot+1).trim() : "—";

  let verdict="Unknown";
  if(/\bLež\b/i.test(clean)) verdict="False";
  else if(/\bPravda\b/i.test(clean) && !/\bLež\b/i.test(clean)) verdict="True";
el        else if(/\bspíše pravda\b/i.test(clean)) verdict="Mostly True";
        else if(/\bspíše lež\b/i.test(clean)) verdict="Mostly False";
        else if(/\bzavádějící\b/i.test(clean)) verdict="Partial";

  const linkRe=/\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g;
  const sources=[]; let m;
  while((m=linkRe.exec(clean))!==null){
    sources.push({title:m[1],url:m[2],relevance:3});
  }
  return {claim,verdict,explanation:clean,sources};
}

// === 5) VÝSLEDEK + POMOCNÉ ===
function renderResult(data){
  analysisTbl.innerHTML=""; sourcesList.innerHTML="";

  [["Tvrzení",data.claim||"–"],
   ["Verdikt",badge(data.verdict)],
   ["Vysvětlení",data.explanation||"–"]
  ].forEach(([k,v])=>{
    const tr=analysisTbl.insertRow();
    tr.insertCell().textContent=k;
    typeof v==="string" ? tr.insertCell().textContent=v
                        : tr.insertCell().appendChild(v);
  });

  if(data.sources?.length){
    data.sources.forEach(s=>sourcesList.appendChild(sourceLi(s)));
    sourcesBox.classList.remove("hidden");
  }else sourcesBox.classList.add("hidden");

  resultBox.classList.remove("hidden");
}
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
    star.className=`star ${i<=relevance?'fill':'empty'}`; star.textContent=i<=relevance?"★":"☆";
    li.appendChild(star);
  }
  return li;
}
