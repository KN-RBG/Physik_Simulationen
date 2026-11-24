"use strict";
// Physikalisches Modell nach Ueberlagerung_Wellen.py (KN-RBG/Wellenueberlagerung).
const $ = (id) => document.getElementById(id);
const canvas = $("diagramm");
const ctx = canvas.getContext("2d");
const fmt = (n, digits=2) => n.toFixed(digits).replace(".", ",");
const palette = {one:"#2d80bd",two:"#dd7d2b",sum:"#198251",grid:"#dce4ec",axis:"#63758a"};
let parameter = null;
let tBasis = 1;
let progress = 0;
let playing = false;
let lastFrame = null;
let frameId = 0;

function numberFrom(id) {
  const raw = $(id).value.trim().replace(/\s/g,"").replace(",",".");
  if (!raw || !/^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(raw)) throw new Error("Bitte gültige Zahlen eingeben, z. B. 1,5.");
  const n = Number(raw);
  if (!Number.isFinite(n)) throw new Error("Bitte gültige, endliche Zahlen eingeben.");
  return n;
}
function radio(name) { return Number(document.querySelector('input[name="'+name+'"]:checked').value); }
function readParameters() {
  const p = {
    L:numberFrom("L"),
    waves:[
      {A:numberFrom("A1"),lambda:numberFrom("lambda1"),f:numberFrom("f1"),dir:radio("richtung1"),sign:radio("vorzeichen1")},
      {A:numberFrom("A2"),lambda:numberFrom("lambda2"),f:numberFrom("f2"),dir:radio("richtung2"),sign:radio("vorzeichen2")}
    ]
  };
  if(p.L<=0)throw new Error("Der Abstand der beiden Enden muss größer als 0 sein.");
  if(p.waves.some(w=>w.lambda<=0))throw new Error("Die Wellenlänge muss größer als 0 sein.");
  if(p.waves.some(w=>w.f<=0))throw new Error("Die Frequenz muss größer als 0 sein.");
  return p;
}
function waveAt(w,x,t,L){
  const v=w.f*w.lambda;
  if(t<=0)return {active:false,y:0};
  const s=w.dir===1?x:L-x;
  if(s>v*t+1e-10)return {active:false,y:0};
  const phase=2*Math.PI*s/w.lambda-2*Math.PI*w.f*t;
  return {active:true,y:-w.sign*w.A*Math.sin(phase)};
}
function pause(){
  playing=false; lastFrame=null;
  if(frameId) cancelAnimationFrame(frameId);
  frameId=0; $("play").textContent="▶ Play";
  $("play").setAttribute("aria-pressed","false");
}
function showError(e){$("fehler").hidden=false;$("fehler").textContent=e.message||String(e)}
function clearError(){$("fehler").hidden=true;$("fehler").textContent=""}
function apply(){
  pause();
  try{
    parameter=readParameters();
    const [a,b]=parameter.waves;
    tBasis=parameter.L/Math.min(a.f*a.lambda,b.f*b.lambda);
    if(!Number.isFinite(tBasis)||tBasis<=0)throw new Error("Diese Parameter erzeugen keine gültige Zeitskala.");
    progress=0;$("zeit").value="0";
    clearError();draw();
  }catch(e){showError(e)}
}
function playPause(){
  if(playing){pause();return}
  // Bei geänderten Eingabewerten wie in Python zunächst Zeitskala neu bestimmen.
  try{
    const p=readParameters(); const basis=p.L/Math.min(...p.waves.map(w=>w.f*w.lambda));
    if(!Number.isFinite(basis)||basis<=0)throw new Error("Diese Parameter erzeugen keine gültige Zeitskala.");
    parameter=p;tBasis=basis;clearError();
  }catch(e){showError(e);return}
  if(progress>=200){progress=0;$("zeit").value="0"}
  playing=true;lastFrame=null;$("play").textContent="⏸ Pause";
  $("play").setAttribute("aria-pressed","true");
  frameId=requestAnimationFrame(animate);
}
function animate(stamp){
  if(!playing)return;
  if(lastFrame!==null){
    // wall-clock elapsed seconds => model time elapsed seconds
    const dt=Math.max(0,(stamp-lastFrame)/1000);
    progress=Math.min(200,progress+100*dt/tBasis);
    $("zeit").value=String(progress);
    draw();
  }
  lastFrame=stamp;
  if(progress>=200){pause();return}
  frameId=requestAnimationFrame(animate);
}
function getSize(){
  const rect=canvas.getBoundingClientRect();
  const w=Math.max(200,Math.round(rect.width)),h=Math.max(180,Math.round(rect.height));
  const dpr=Math.min(window.devicePixelRatio||1,2.5);
  if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
  ctx.setTransform(dpr,0,0,dpr,0,0);
  return {w,h};
}
function line(x1,y1,x2,y2,color,width=1,dash=[]){
  ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.setLineDash([]);
}
function tickLabel(v){if(Math.abs(v)<1e-9)v=0;return (Math.abs(v)>=100?fmt(v,0):fmt(v,1)).replace(/,0$/,"")}
function plotCurve(toPoint,N,col,width,fn){
  ctx.beginPath();ctx.strokeStyle=col;ctx.lineWidth=width;ctx.lineJoin="round";ctx.setLineDash([]);
  let started=false;
  for(let i=0;i<=N;i++){
    const x=parameter.L*i/N;
    const val=fn(x);
    if(val===null||!Number.isFinite(val)){started=false;continue}
    const [px,py]=toPoint(x,val);
    if(!started){ctx.moveTo(px,py);started=true}else ctx.lineTo(px,py)
  }
  ctx.stroke();
}
function draw(){
  if(!parameter)return;
  const {w,h}=getSize();
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#fff";ctx.fillRect(0,0,w,h);
  const margins={left:w<440?57:74,right:20,top:20,bottom:55};
  const pw=Math.max(60,w-margins.left-margins.right),ph=Math.max(80,h-margins.top-margins.bottom);
  const maxAbs=Math.abs(parameter.waves[0].A)+Math.abs(parameter.waves[1].A)||1;
  const Y=1.2*maxAbs,t=(progress/100)*tBasis,L=parameter.L;
  const Xpx=x=>margins.left+x/L*pw;
  const Ypx=y=>margins.top+(Y-y)/(2*Y)*ph;
  const map=(x,y)=>[Xpx(x),Ypx(y)];
  ctx.font="12px system-ui, sans-serif";ctx.fillStyle="#546879";
  ctx.textAlign="center";ctx.textBaseline="top";
  for(let i=0;i<=5;i++){
    const x=L*i/5,px=Xpx(x);
    line(px,margins.top,px,margins.top+ph,palette.grid);
    ctx.fillText(tickLabel(x),px,margins.top+ph+7);
  }
  ctx.textAlign="right";ctx.textBaseline="middle";
  for(let i=0;i<=4;i++){
    const y=-Y+2*Y*i/4,py=Ypx(y);
    line(margins.left,py,margins.left+pw,py,palette.grid);
    ctx.fillText(tickLabel(y),margins.left-8,py);
  }
  line(margins.left,Ypx(0),margins.left+pw,Ypx(0),palette.axis,1.4);
  line(margins.left,margins.top,margins.left,margins.top+ph,palette.axis,1.2);
  line(Xpx(L),margins.top,Xpx(L),margins.top+ph,palette.axis,1.2);
  ctx.fillStyle="#263a4f";ctx.textBaseline="alphabetic";ctx.textAlign="center";
  ctx.fillText("Ort x in m",margins.left+pw/2,h-8);
  ctx.save();ctx.translate(18,margins.top+ph/2);ctx.rotate(-Math.PI/2);ctx.fillText("Auslenkung y in m",0,0);ctx.restore();
  ctx.save();ctx.beginPath();ctx.rect(margins.left,margins.top,pw,ph);ctx.clip();
  // Linien mit NaN-Lücken entsprechen aktiven Bereichen der Python-Plots.
  for(let j=0;j<2;j++){
    const visible=$("zeige"+(j+1)).checked,wave=parameter.waves[j];
    if(visible)plotCurve(map,1600,j===0?palette.one:palette.two,2.2,x=>{
      const v=waveAt(wave,x,t,L);return v.active?v.y:null
    });
    if(t>0){
      const front=wave.dir===1?wave.f*wave.lambda*t:L-wave.f*wave.lambda*t;
      if(front>=0&&front<=L)line(Xpx(front),margins.top,Xpx(front),margins.top+ph,j===0?palette.one:palette.two,1.4,[4,5]);
    }
  }
  if($("summe").checked)plotCurve(map,1600,palette.sum,3.0,x=>{
    const a=waveAt(parameter.waves[0],x,t,L);
    const b=waveAt(parameter.waves[1],x,t,L);
    return a.active&&b.active?a.y+b.y:null;
  });
  ctx.restore();
  $("plot-title").textContent="Ausbreitung und Überlagerung – t = "+fmt(t)+" s";
  $("zeit-label").textContent="t = "+fmt(t)+" s   |   "+Math.round(progress)+" %";
  const legend=$("legende");legend.replaceChildren();
  for(const [index,col] of [[0,palette.one],[1,palette.two],[2,palette.sum]]){
    if(index<2&&!$("zeige"+(index+1)).checked||index===2&&!$("summe").checked)continue;
    const span=document.createElement("span"), swatch=document.createElement("i");
    swatch.className="swatch";swatch.style.background=col;span.append(swatch);
    const text=index===2?"Überlagerung":("Welle "+(index+1)+" – f="+fmt(parameter.waves[index].f)+" Hz, v="+fmt(parameter.waves[index].f*parameter.waves[index].lambda)+" m/s");
    span.append(document.createTextNode(text));legend.append(span);
  }
}
$("play").addEventListener("click",playPause);
$("reset").addEventListener("click",()=>{pause();progress=0;$("zeit").value="0";draw()});
$("uebernehmen").addEventListener("click",apply);
$("zeit").addEventListener("input",()=>{pause();progress=Number($("zeit").value);draw()});
for(const input of document.querySelectorAll('input[type="radio"]')){
  input.addEventListener("change",()=>{
    if(input.name.startsWith("richtung"))apply();else{if(parameter)parameter=readParameters();draw()}
  })
}
for(const input of document.querySelectorAll('input[type="checkbox"]')){
  input.addEventListener("change",draw);
}
for(const input of document.querySelectorAll('input[inputmode="decimal"]')){
  input.addEventListener("keydown",event=>{if(event.key==="Enter")apply()});
}
window.addEventListener("resize",draw);
if(window.ResizeObserver)new ResizeObserver(draw).observe(canvas.parentElement);
document.addEventListener("visibilitychange",()=>{if(document.hidden)pause()});
apply();
