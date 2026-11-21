"use strict";
// Reimplementation of Fourier_1D_GUI.py for N=1600 samples.
// One-sided DFT coefficients c_k = sum_n s_n exp(-2π i k n/N)/N.
// Selection by |c_k|, then optional low-/high-pass filtering.
const N=1600,MAX_K=50,PI=Math.PI,$=id=>document.getElementById(id);
const els=["signal-plot","spectrum-plot","parts-plot"];
let signal=new Float64Array(N),re=new Float64Array(N/2+1),im=new Float64Array(N/2+1),order=[],selected=[],reconstruction=new Float64Array(N);
const get=id=>$(id),num=id=>Number(get(id).value);
const colors={signal:"#7b8590",sum:"#884cb0",active:"#884cb0",component:"#3588ad",limit:"#ce4949"};
function getSignal(kind,x){
  if(kind==="Sinus")return Math.sin(x);
  if(kind==="Rechteck"){const v=Math.sign(Math.sin(x));return v===0?1:v;}
  if(kind==="Dreieck")return 2/PI*Math.asin(Math.sin(x));
  const u=x/(2*PI);return 2*(u-Math.floor(.5+u));
}
function computeSpectrum(){
  const kind=get("signal").value;
  for(let n=0;n<N;n++)signal[n]=getSignal(kind,2*PI*n/N);
  const energy=new Array(N/2);
  for(let k=0;k<=N/2;k++){
    let r=0,j=0;
    for(let n=0;n<N;n++){
      const phi=2*PI*k*n/N,sv=signal[n];
      r+=sv*Math.cos(phi);j-=sv*Math.sin(phi);
    }
    re[k]=r/N;im[k]=j/N;
    if(k>=1)energy[k-1]=k;
  }
  order=energy.sort((a,b)=>Math.hypot(re[b],im[b])-Math.hypot(re[a],im[a])||a-b);
  update();
}
function update(){
  const count=num("components"),filter=get("filter").value,cutoff=num("cutoff");
  get("components-out").textContent=String(count);
  get("cutoff-out").textContent=String(cutoff);
  get("cutoff").disabled=filter==="Alle";
  selected=order.slice(0,count).filter(k=>filter==="Alle"||(filter==="Tiefpass"?k<=cutoff:k>=cutoff));
  // Inverse rFFT for the retained harmonics plus DC.
  // Nyquist is its own unique real coefficient, not a conjugate pair.
  for(let n=0;n<N;n++){
    let y=re[0];
    for(const k of selected){
      const angle=2*PI*k*n/N;
      y+=(k===N/2?1:2)*(re[k]*Math.cos(angle)-im[k]*Math.sin(angle));
    }
    reconstruction[n]=y;
  }
  let error=0;
  for(let n=0;n<N;n++)error+=(signal[n]-reconstruction[n])**2;
  get("info").textContent="aktive Komponenten: "+selected.length+"   |   RMS-Abweichung: "+Math.sqrt(error/N).toFixed(3).replace(".",",");
  get("signal-title").textContent="1. "+get("signal").value+": Original und Fourier-Näherung";
  get("spectrum-title").textContent="2. Frequenzspektrum – "+selected.length+" aktive Komponenten";
  drawAll();
}
function canvasSpace(id){
  const c=get(id),w=Number(c.getAttribute("width")),h=Number(c.getAttribute("height"));
  const r=Math.min(devicePixelRatio||1,2.5);
  if(c.width!==Math.round(w*r)||c.height!==Math.round(h*r)){c.width=Math.round(w*r);c.height=Math.round(h*r);}
  const ctx=c.getContext("2d");
  ctx.setTransform(r,0,0,r,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle="white";ctx.fillRect(0,0,w,h);
  const g={ctx,w,h,L:55,R:w-16,T:22,B:h-52};
  return g;
}
function grid(g,xmax,ymin,ymax,xLabel,yLabel,piTicks=true){
  const {ctx,L,R,T,B}=g,xx=x=>L+x/xmax*(R-L),yy=y=>B-(y-ymin)/(ymax-ymin)*(B-T);
  ctx.font="13px system-ui,sans-serif";ctx.textBaseline="middle";
  for(let i=0;i<=4;i++){
    const x=xmax*i/4;
    ctx.beginPath();ctx.moveTo(xx(x),T);ctx.lineTo(xx(x),B);ctx.strokeStyle="#e9edf1";ctx.lineWidth=1;ctx.stroke();
    ctx.fillStyle="#536577";ctx.textAlign="center";
    ctx.fillText(piTicks?["0","π/2","π","3π/2","2π"][i]:String(Math.round(x)),xx(x),B+16);
  }
  for(let i=0;i<=4;i++){
    const y=ymin+(ymax-ymin)*i/4;
    ctx.beginPath();ctx.moveTo(L,yy(y));ctx.lineTo(R,yy(y));ctx.strokeStyle="#e9edf1";ctx.stroke();
    ctx.fillStyle="#536577";ctx.textAlign="right";ctx.fillText(y.toFixed(1).replace(".",","),L-7,yy(y));
  }
  ctx.strokeStyle="#b9cbd9";ctx.strokeRect(L,T,R-L,B-T);
  ctx.fillStyle="#2d4559";ctx.textAlign="center";ctx.font="14px system-ui,sans-serif";ctx.fillText(xLabel,(L+R)/2,g.h-15);
  ctx.save();ctx.translate(14,(T+B)/2);ctx.rotate(-PI/2);ctx.fillText(yLabel,0,0);ctx.restore();
  return {x:xx,y:yy};
}
function strokeArray(g,values,color,width,dashed=false,alpha=1){
  const {ctx}=g,xy=g.axes;ctx.beginPath();
  for(let n=0;n<values.length;n++){
    const x=xy.x(2*PI*n/(N-1)),y=xy.y(values[n]);
    if(n===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  }
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.globalAlpha=alpha;ctx.setLineDash(dashed?[6,4]:[]);ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;
}
function drawSignal(){
  const g=canvasSpace("signal-plot"),{ctx}=g;let bound=1.25;
  for(let n=0;n<N;n++)bound=Math.max(bound,Math.abs(signal[n]),Math.abs(reconstruction[n]));
  bound=Math.max(1.25,Math.ceil(bound*2)/2);
  g.axes=grid(g,2*PI,-bound,bound,"x","y");
  if(get("original").checked)strokeArray(g,signal,colors.signal,1.5,true);
  if(get("sum").checked)strokeArray(g,reconstruction,colors.sum,2.4);
  if(get("signal").value==="Rechteck"&&num("components")>=5){
    ctx.font="12px system-ui,sans-serif";ctx.fillStyle="#9e5220";ctx.textAlign="left";ctx.fillText("Gibbs-Phänomen an Sprungstellen",g.L+8,g.B-12);
  }
}
function drawSpectrum(){
  const g=canvasSpace("spectrum-plot"),{ctx,L,R,T,B}=g;
  const top=order.slice(0,40).sort((a,b)=>a-b);
  const active=new Set(selected);
  const xMax=Math.max(10,...top,...selected);
  let ymax=0.05;
  for(const k of top)ymax=Math.max(ymax,2*Math.hypot(re[k],im[k]));
  ymax*=1.15;
  const x=k=>L+k/xMax*(R-L),y=v=>B-v/ymax*(B-T);
  ctx.font="13px system-ui,sans-serif";ctx.textBaseline="middle";
  for(let i=0;i<=5;i++){
    const xx=x(xMax*i/5),val=ymax*i/5;
    ctx.strokeStyle="#ebeff4";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();
    ctx.fillStyle="#506477";ctx.textAlign="center";ctx.fillText(String(Math.round(xMax*i/5)),xx,B+15);
    const yy=y(val);ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(R,yy);ctx.stroke();
    ctx.textAlign="right";ctx.fillText(val.toFixed(2).replace(".",","),L-8,yy);
  }
  ctx.strokeStyle="#b9cbd9";ctx.strokeRect(L,T,R-L,B-T);
  const drawStem=(k,color,thickness,alpha)=>{
    const amp=2*Math.hypot(re[k],im[k]),xx=x(k),yy=y(amp);
    ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=thickness;
    ctx.beginPath();ctx.moveTo(xx,B);ctx.lineTo(xx,yy);ctx.stroke();
    ctx.beginPath();ctx.arc(xx,yy,thickness+1,0,2*PI);ctx.fill();ctx.globalAlpha=1;
  };
  for(const k of top)drawStem(k,colors.signal,.8,.28);
  for(const k of selected)drawStem(k,colors.active,1.8,1);
  if(get("filter").value!=="Alle"){
    const xx=x(num("cutoff"));ctx.save();ctx.setLineDash([6,4]);ctx.strokeStyle=colors.limit;ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();ctx.restore();
  }
  ctx.fillStyle="#2d4559";ctx.font="14px system-ui,sans-serif";ctx.textAlign="center";ctx.fillText("Frequenz / Harmonische",(L+R)/2,g.h-14);
  ctx.save();ctx.translate(14,(T+B)/2);ctx.rotate(-PI/2);ctx.fillText("Amplitude",0,0);ctx.restore();
}
function drawParts(){
  const g=canvasSpace("parts-plot");let bound=1.25;
  for(let n=0;n<N;n++)bound=Math.max(bound,Math.abs(reconstruction[n]));
  bound=Math.max(1.25,Math.ceil(bound*2)/2);
  g.axes=grid(g,2*PI,-bound,bound,"x","Beitrag");
  if(get("individual").checked){
    const palette=["#208eab","#cb6d2a","#3f9782","#b262a3","#687fc4","#b48e3c","#6ca66b","#9d7373"];
    selected.slice(0,12).forEach((k,i)=>{
      const values=new Float64Array(N);
      for(let n=0;n<N;n++){
        const phi=2*PI*k*n/N;
        values[n]=2*(re[k]*Math.cos(phi)-im[k]*Math.sin(phi));
      }
      strokeArray(g,values,palette[i%palette.length],1.3,false,.8);
    });
  }
  if(get("sum").checked)strokeArray(g,reconstruction,colors.sum,2.6);
}
function drawAll(){drawSignal();drawSpectrum();drawParts();}
get("signal").addEventListener("change",computeSpectrum);
for(const id of ["components","filter","cutoff"])get(id).addEventListener("input",update);
for(const id of ["original","sum","individual"])get(id).addEventListener("change",drawAll);
for(const [id,delta] of [["minus",-1],["plus",1]])get(id).addEventListener("click",()=>{
  get("components").value=String(Math.max(1,Math.min(MAX_K,num("components")+delta)));update();
});
computeSpectrum();
