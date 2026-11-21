"use strict";
// Browser-port of KN-RBG/Interferenz-am-Mehrfachspalt/Mehrfachspalt_GUI.py
const $=id=>document.getElementById(id);
const canvas=$("diagram"),ctx=canvas.getContext("2d");
const defaults={number:"2",width:"0,05",spacing:"0,20",screenDistance:"2,0",wavelength:"650",from:"-60",to:"60"};
const form=$("settings");
function parseDecimal(id){
  const str=$(id).value.trim().replace(",",".");
  if(!str||!Number.isFinite(Number(str)))throw Error("Bitte eine gültige Zahl für "+label(id)+" eingeben.");
  return Number(str);
}
const labels={number:"die Anzahl der Spalte",width:"die Spaltbreite b",spacing:"den Spaltabstand g",screenDistance:"den Schirmabstand a",wavelength:"die Wellenlänge λ",from:"den Schirmbereich von",to:"den Schirmbereich bis"};
function label(id){return labels[id]||id}
function deutsch(v,n){return v.toFixed(n).replace(".",",")}
function values(){
  const n=parseDecimal("number"),b=parseDecimal("width"),g=parseDecimal("spacing"),a=parseDecimal("screenDistance"),lambda=parseDecimal("wavelength"),from=parseDecimal("from"),to=parseDecimal("to");
  if(!Number.isInteger(n)||n<1)throw Error("Die Anzahl der Spalte muss eine ganze Zahl ab 1 sein.");
  if(n>2000)throw Error("Bitte höchstens 2000 Spalte eingeben, damit das Diagramm zuverlässig berechnet werden kann.");
  if(b<=0)throw Error("Die Spaltbreite b muss größer als 0 sein.");
  if(g<=0)throw Error("Der Spaltabstand g muss größer als 0 sein.");
  if(b>g)throw Error("Die Spaltbreite b darf nicht größer als der Spaltabstand g sein.");
  if(a<=0)throw Error("Der Abstand zum Schirm a muss größer als 0 sein.");
  if(lambda<=0)throw Error("Die Wellenlänge muss größer als 0 sein.");
  if(from>=to)throw Error("Beim Schirmbereich muss der Wert 'von' kleiner als 'bis' sein.");
  return {n,b,g,a,lambda,from,to};
}
function calculate(p){
  const N=5000,curve=new Float64Array(N),envelope=new Float64Array(N);
  const slitWidth=p.b*1e-3,slitGap=p.g*1e-3,wavelength=p.lambda*1e-9;
  let peak=0;
  for(let i=0;i<N;i++){
    const xMM=p.from+(p.to-p.from)*i/(N-1);
    const theta=Math.atan((xMM*1e-3)/p.a);
    const alpha=Math.PI*slitGap*Math.sin(theta)/wavelength;
    const denominator=Math.sin(alpha);
    // Same limiting-value handling as the Python implementation.
    const interference=Math.abs(denominator)<1e-12 ? p.n*p.n :
      Math.pow(Math.sin(p.n*alpha)/denominator,2);
    const norm=interference/(p.n*p.n);
    const beta=Math.PI*slitWidth*Math.sin(theta)/wavelength;
    const singleSlit=Math.abs(beta)<1e-12 ? 1 : Math.pow(Math.sin(beta)/beta,2);
    envelope[i]=singleSlit;
    curve[i]=norm*($("singleSlit").checked?singleSlit:1);
    if(curve[i]>peak)peak=curve[i];
  }
  if(peak>0){for(let i=0;i<N;i++)curve[i]/=peak;}
  return {curve,envelope};
}
function plot(p,data){
  const dpr=Math.min(window.devicePixelRatio||1,3);
  const W=1120,H=670;
  if(canvas.width!==Math.round(W*dpr)||canvas.height!==Math.round(H*dpr)){
    canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);
  }
  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);
  const L=103,R=1084,T=40,B=579,w=R-L,h=B-T;
  const x=u=>L+(u-p.from)/(p.to-p.from)*w;
  const y=v=>B-v/1.05*h;
  ctx.font="17px system-ui,sans-serif";
  ctx.textBaseline="middle";
  for(let j=0;j<=5;j++){
    const val=j/5*1.05;
    const yy=y(val);
    ctx.strokeStyle="#e0e8ed";ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(R,yy);ctx.stroke();
    ctx.fillStyle="#445c6d";ctx.textAlign="right";ctx.fillText(deutsch(val,2),L-12,yy);
  }
  for(let j=0;j<=8;j++){
    const val=p.from+(p.to-p.from)*j/8;
    const xx=x(val);
    ctx.strokeStyle="#eef2f5";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();
    ctx.fillStyle="#445c6d";ctx.textAlign="center";ctx.fillText(deutsch(val,1),xx,B+23);
  }
  ctx.strokeStyle="#8595a4";ctx.strokeRect(L,T,w,h);
  ctx.fillStyle="#223d51";ctx.textAlign="center";ctx.fillText("Ort auf dem Schirm x in mm",(L+R)/2,651);
  ctx.save();ctx.translate(30,(T+B)/2);ctx.rotate(-Math.PI/2);ctx.fillText("relative Intensität",0,0);ctx.restore();
  function drawCurve(values,color,width){
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();
    for(let i=0;i<values.length;i++){
      const xx=L+w*i/(values.length-1);
      const yy=y(values[i]);
      if(i===0)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy);
    }
    ctx.stroke();
  }
  drawCurve(data.curve,"#206ea7",2.1);
  if($("envelope").checked)drawCurve(data.envelope,"#c34545",2.7);
}
let current=null;
function update(){
  try{
    const p=values();
    const calculated=calculate(p);
    current={p,calculated};
    plot(p,calculated);
    $("chart-title").textContent="Interferenzbild eines "+p.n+"-fach-Spalts";
    $("chart-subtitle").textContent="λ = "+deutsch(p.lambda,0)+" nm, a = "+deutsch(p.a,2)+" m, b = "+deutsch(p.b,3)+" mm, g = "+deutsch(p.g,3)+" mm";
    $("chart-mode").textContent=$("singleSlit").checked?"mit Einzelspalt-Beugung":"ohne Einzelspalt-Beugung";
    $("envelope-legend").hidden=!$("envelope").checked;
    $("error").textContent="";
  }catch(err){$("error").textContent=String(err.message||err);}
}
form.addEventListener("submit",event=>{event.preventDefault();update()});
$("singleSlit").addEventListener("change",update);
$("envelope").addEventListener("change",update);
$("reset").addEventListener("click",()=>{
  for(const [id,val] of Object.entries(defaults))$(id).value=val;
  $("singleSlit").checked=false;
  $("envelope").checked=false;
  update();
});
window.addEventListener("resize",()=>{if(current)plot(current.p,current.calculated)});
update();
