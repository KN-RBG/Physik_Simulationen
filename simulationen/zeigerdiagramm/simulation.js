"use strict";
// Spiegelung des Modells aus KN-RBG/Zeigerdiagramm/zeigerdiagramm.py
// Python: ANIMATION_STEP=2°, INTERVAL_MS=25, MAX_ALPHA=4*pi (720°).
const SVG_NS="http://www.w3.org/2000/svg";
const svg=document.getElementById("plot");
const slider=document.getElementById("winkel");
const display=document.getElementById("winkelanzeige");
const output=document.getElementById("winkelwert");
const play=document.getElementById("play");
const reset=document.getElementById("reset");
const C={cx:206,cy:207,r:130,left:462,right:1082,sineMid:207,sineScale:130};
const SX=deg=>C.left+(deg/720)*(C.right-C.left);
const SY=y=>C.sineMid-y*C.sineScale;
const CX=x=>C.cx+x*C.r;
const CY=y=>C.cy-y*C.r;
const E=(name,attrs={},parent=svg)=>{
  const e=document.createElementNS(SVG_NS,name);
  for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));
  parent.appendChild(e);
  return e;
};
const text=(x,y,s,attrs={})=>{const el=E("text",{x,y,"font-family":"system-ui,sans-serif","font-size":15,fill:"#293b4c",...attrs});el.textContent=s;return el};
const path=(d,attrs={})=>E("path",{d,fill:"none",...attrs});
const circle=(cx,cy,r,attrs={})=>E("circle",{cx,cy,r,...attrs});
const line=(x1,y1,x2,y2,attrs={})=>E("line",{x1,y1,x2,y2,...attrs});
const grid="#dfe5ec",subgrid="#eef2f5";
svg.replaceChildren();
const defs=E("defs");
const marker=E("marker",{id:"arrow-red",viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:6,markerHeight:6,orient:"auto-start-reverse"},defs);
E("path",{d:"M 0 0 L 10 5 L 0 10 z",fill:"#dc3333"},marker);
const blackMarker=E("marker",{id:"arrow-black",viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:6,markerHeight:6,orient:"auto"},defs);
E("path",{d:"M 0 0 L 10 5 L 0 10 z",fill:"#1c2732"},blackMarker);
// Linker Einheitskreis mit Gitter (Skala ±1,35)
for(let p=-1.25;p<=1.25+1e-8;p+=.25){
  const major=Math.abs(p*2-Math.round(p*2))<1e-7;
  const x=CX(p),y=CY(p);
  line(x,CY(1.35),x,CY(-1.35),{stroke:major?grid:subgrid,"stroke-width":major?1.15:.8});
  line(CX(-1.35),y,CX(1.35),y,{stroke:major?grid:subgrid,"stroke-width":major?1.15:.8});
}
line(CX(-1.35),CY(0),CX(1.35),CY(0),{stroke:"#25313c","stroke-width":1.5,"stroke-dasharray":"7 5"});
circle(C.cx,C.cy,C.r,{fill:"none",stroke:"#d92f32","stroke-width":3});
text(206,23,"Zeigerdiagramm",{"text-anchor":"middle","font-weight":650});
// Winkelgeschwindigkeits-Pfeil (in positiver mathematischer Drehrichtung)
const omegaRadius=1.14;
const omega=[];
for(let i=0;i<=24;i++){const angle=(72+(145-72)*i/24)*Math.PI/180;omega.push((i?"L":"M")+" "+CX(omegaRadius*Math.cos(angle)).toFixed(2)+" "+CY(omegaRadius*Math.sin(angle)).toFixed(2))}
path(omega.join(" "),{stroke:"#1c2732","stroke-width":1.8,"marker-end":"url(#arrow-black)"});
text(CX(-.51),CY(1.2),"ω",{"text-anchor":"middle","font-size":20});
// Rechtes Diagramm, Winkelachse 0..720°, Auslenkung -1,35..1,35
text((C.left+C.right)/2,23,"Entstehung der Sinuskurve",{"font-weight":650,"text-anchor":"middle"});
for(let y=-1.25;y<=1.25+1e-9;y+=.25){
  const major=Math.abs(y*4-Math.round(y*4))<1e-7;
  line(C.left,SY(y),C.right,SY(y),{stroke:major?grid:subgrid,"stroke-width":major?1.1:.75});
}
for(let deg=0;deg<=720;deg+=22.5){
  const major=(deg%90===0);
  line(SX(deg),SY(1.35),SX(deg),SY(-1.35),{stroke:major?grid:subgrid,"stroke-width":major?1.1:.75});
}
line(C.left,SY(0),C.right-30,SY(0),{stroke:"#1b2734","stroke-width":2,"marker-end":"url(#arrow-black)"});
line(C.left,SY(-1.05),C.left,SY(1.2),{stroke:"#1b2734","stroke-width":2,"marker-end":"url(#arrow-black)"});
for(const y of [-1,1])line(C.left,SY(y),C.right,SY(y),{stroke:"#3268b6","stroke-width":1.2,"stroke-dasharray":"7 5"});
text(C.left-15,SY(1.12),"y",{"font-style":"italic","font-size":20,"text-anchor":"end"});
text(C.right-33,SY(0)+28,"t",{"font-style":"italic","font-size":19});
// Winkelskalen unter dem Diagramm, gleiche x-Koordinaten wie Sinusdiagramm.
const rad=["0","π/2","π","3π/2","2π","5π/2","3π","7π/2","4π"];
for(const [idx,y,cap] of [[0,403,"α (Bogenmaß)"],[1,466,"α (Winkel)"]]){
  line(C.left,y,C.right,y,{stroke:"#ce3a3a","stroke-width":1.6});
  for(let i=0;i<=8;i++){
    const x=SX(i*90);
    line(x,y-8,x,y+8,{stroke:"#4a5765","stroke-width":1});
    text(x,y+29,idx===0?rad[i]:String(i*90),{"text-anchor":"middle","font-size":14});
  }
  text(C.right,y-13,cap,{"text-anchor":"end","font-size":15});
}
// Dynamische Komponenten
const projectionCircle=line(0,0,0,0,{stroke:"#2a2d31","stroke-width":1.4,"stroke-dasharray":"3 5"});
const projectionSine=line(0,0,0,0,{stroke:"#2a2d31","stroke-width":1.25,"stroke-dasharray":"3 5"});
const angleArc=path("",{stroke:"#252a2f","stroke-width":1.4});
const angleText=text(0,0,"α",{"font-size":19,"font-style":"italic","text-anchor":"middle"});
const phasor=line(C.cx,C.cy,CX(1),C.cy,{stroke:"#db3030","stroke-width":3.5,"marker-end":"url(#arrow-red)"});
const sinePath=path("",{stroke:"#1861b4","stroke-width":2.1,"stroke-linejoin":"round"});
const sineMarker=line(0,0,0,0,{stroke:"#1c2732","stroke-width":1.5,"stroke-dasharray":"3 5"});
const dot=circle(0,0,5.7,{fill:"#df3232",stroke:"white","stroke-width":1});
let deg=0,running=false,frame=0,lastFrame=null,accum=0;
const fmt=n=>Number(n).toFixed(2).replace(".",",");
function redraw(){
  const a=deg*Math.PI/180;
  const x=Math.cos(a),y=Math.sin(a),endX=CX(x),endY=CY(y);
  phasor.setAttribute("x2",CX(1.03*x));
  phasor.setAttribute("y2",CY(1.03*y));
  projectionCircle.setAttribute("x1",endX);projectionCircle.setAttribute("x2",endX);
  projectionCircle.setAttribute("y1",endY);projectionCircle.setAttribute("y2",C.cy);
  projectionSine.setAttribute("x1",endX);projectionSine.setAttribute("x2",SX(deg));
  projectionSine.setAttribute("y1",endY);projectionSine.setAttribute("y2",SY(y));
  sineMarker.setAttribute("x1",SX(deg));sineMarker.setAttribute("x2",SX(deg));
  sineMarker.setAttribute("y1",SY(0));sineMarker.setAttribute("y2",SY(y));
  dot.setAttribute("cx",SX(deg));dot.setAttribute("cy",SY(y));
  const n=Math.max(2,Math.floor(1400*deg/720));
  const coords=[];
  for(let i=0;i<n;i++){
    const z=deg*i/(n-1);
    coords.push((i?"L":"M")+SX(z).toFixed(2)+","+SY(Math.sin(z*Math.PI/180)).toFixed(2));
  }
  sinePath.setAttribute("d",coords.join(" "));
  let angle=deg%360;if(angle===0&&deg>0)angle=360;
  const R=49;
  const arc=[];
  const steps=Math.max(2,Math.ceil(angle/5));
  for(let i=0;i<=steps;i++){const a2=(angle*i/steps)*Math.PI/180;arc.push((i?"L":"M")+(C.cx+R*Math.cos(a2)).toFixed(2)+","+(C.cy-R*Math.sin(a2)).toFixed(2))}
  angleArc.setAttribute("d",arc.join(" "));
  const mid=(angle>0?angle/2:8)*Math.PI/180;
  angleText.setAttribute("x",C.cx+35*Math.cos(mid));
  angleText.setAttribute("y",C.cy-35*Math.sin(mid));
  slider.value=String(deg);
  output.textContent=deg+"°";
  display.textContent="α = "+deg+"°   |   α = "+fmt(deg/360)+" · 2π";
}
function stop(){running=false;lastFrame=null;accum=0;if(frame)cancelAnimationFrame(frame);frame=0;play.textContent="▶ Start";play.setAttribute("aria-pressed","false")}
function tick(timestamp){
  if(!running)return;
  if(lastFrame!==null){
    accum+=Math.max(0,timestamp-lastFrame);
    const steps=Math.floor(accum/25);
    if(steps>0){accum-=steps*25;deg=((deg+steps*2)>720)?((deg+steps*2-2)%722):deg+steps*2;redraw()}
  }
  lastFrame=timestamp;
  frame=requestAnimationFrame(tick);
}
play.addEventListener("click",()=>{
  if(running){stop();return}
  running=true;lastFrame=null;accum=0;play.textContent="⏸ Stopp";play.setAttribute("aria-pressed","true");
  frame=requestAnimationFrame(tick);
});
reset.addEventListener("click",()=>{stop();deg=0;redraw()});
slider.addEventListener("input",()=>{deg=Number(slider.value);redraw()});
document.addEventListener("visibilitychange",()=>{if(document.hidden)stop()});
redraw();
