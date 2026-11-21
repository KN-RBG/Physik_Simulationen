"use strict";
// Modell und Standardwerte aus KN-RBG/Federschwerependel/federschwerependel_animation.py
const g=9.81,L0=0.30,forceScale=0.055, springWidth=0.035, massWidth=0.13,massHeight=0.075;
const $=id=>document.getElementById(id);
const N=(id)=>Number($(id).value);
const fmt=(v,d=2)=>(Number(v).toFixed(d)).replace(".",",");
const signed=(v,d=1)=>(v>=0?"+":"")+fmt(v,d);
const yPx=y=>68+(y-0.02)*690; // 0.02m at ceiling; downward-positive physical coordinate
const xPx=x=>370+x*620;
let phase=0,paused=false,lastFrame=null,raf=0;
const pyElements=["phase","amplitude","federhaerte","masse-regler"];
function setLine(id,x1,y1,x2,y2){
  const e=$(id);e.setAttribute("x1",x1);e.setAttribute("y1",y1);e.setAttribute("x2",x2);e.setAttribute("y2",y2);
}
function setText(id,x,y,t){
  const e=$(id);e.setAttribute("x",x);e.setAttribute("y",y);if(t!==undefined)e.textContent=t;
}
function show(id,on){$(id).style.display=on?"":"none"}
function draw(){
  const A=N("amplitude"),D=N("federhaerte"),m=N("masse-regler");
  const L_eq=L0+m*g/D,omega=Math.sqrt(D/m);
  const s=A*Math.cos(phase);
  const L=L_eq-s; // upper displacement positive
  const Fg=m*g,Ff=D*(L-L0),Fres=Fg-Ff;
  const massY=yPx(L),eqY=yPx(L_eq);
  $("phase").value=String(Math.round(((phase%(2*Math.PI))+2*Math.PI)%(2*Math.PI)*180/Math.PI));
  $("phase-out").textContent=$("phase").value+"°";
  $("amplitude-out").textContent=fmt(A,3)+" m";
  $("federhaerte-out").textContent=fmt(D,1)+" N/m";
  $("masse-out").textContent=fmt(m,2)+" kg";
  $("wert-d").textContent=fmt(D,1)+" N/m";
  $("wert-m").textContent=fmt(m,2)+" kg";
  $("wert-s").textContent=signed(s*100,1)+" cm";
  $("wert-fg").textContent=fmt(Fg,2)+" N";
  $("wert-ff").textContent=fmt(Ff,2)+" N";
  $("wert-fres").textContent=signed(Fres,2)+" N";
  show("titel-fg",$("einzelkraefte-check").checked);show("wert-fg",$("einzelkraefte-check").checked);
  show("titel-ff",$("einzelkraefte-check").checked);show("wert-ff",$("einzelkraefte-check").checked);
  show("titel-fres",$("resultierende-check").checked);show("wert-fres",$("resultierende-check").checked);
  show("einzelkraefte",$("einzelkraefte-check").checked);
  show("resultierende",$("resultierende-check").checked);
  setLine("gleichgewicht",xPx(-.07),eqY,xPx(.39),eqY);
  setText("gleichgewicht-label",xPx(.17),eqY-11,"Gleichgewichtslage");
  // Mass center = actual spring length L. Spring ends at upper edge of mass.
  const springBottom=L-massHeight/2, springTop=.02;
  const lead=.035, bodyTop=springTop+lead,bodyBottom=springBottom-lead;
  const p=[];
  p.push("M "+xPx(0)+" "+yPx(springTop),"L "+xPx(0)+" "+yPx(bodyTop));
  for(let i=0;i<=420;i++){
    const u=i/420;
    const yy=bodyTop+(bodyBottom-bodyTop)*u;
    const envelope=Math.pow(Math.sin(Math.PI*u),.25);
    const xx=springWidth*envelope*Math.sin(2*Math.PI*16*u);
    p.push("L "+xPx(xx).toFixed(2)+" "+yPx(yy).toFixed(2));
  }
  p.push("L "+xPx(0)+" "+yPx(springBottom));
  $("feder").setAttribute("d",p.join(" "));
  const mass=$("masse");
  mass.setAttribute("x",xPx(-massWidth/2));mass.setAttribute("y",yPx(L-massHeight/2));
  mass.setAttribute("width",massWidth*620);mass.setAttribute("height",massHeight*690);
  // All forces originate at center of mass. Positive forces point down.
  const fx=xPx(-.17),resx=xPx(-.34);
  const fgy=yPx(L+Fg*forceScale),ffy=yPx(L-Ff*forceScale);
  const fresy=yPx(L+Fres*forceScale);
  setLine("fg",fx,massY,fx,fgy);
  setLine("ff",fx,massY,fx,ffy);
  setLine("fres",resx,massY,resx,fresy);
  setText("fgtext",fx-19,(massY+fgy)/2,"Fɢ");
  setText("fftext",fx-19,(massY+ffy)/2,"Fꜰ");
  setText("frestext",resx-20,Math.abs(fresy-massY)>5?(massY+fresy)/2:massY-16,"Fᵣₑₛ");
  // Purple double arrow from equilibrium to current mass centre.
  if(Math.abs(massY-eqY)<3){
    show("auslenkung",false);
  }else{show("auslenkung",true);setLine("auslenkung",xPx(.19),eqY,xPx(.19),massY)}
  setText("stext",xPx(.22),(massY+eqY)/2,"s");
}
function setPaused(on){
  paused=on;
  $("play").textContent=paused?"▶ Weiter":"⏸ Pause";
  $("play").setAttribute("aria-pressed",String(!paused));
  $("laufstatus").textContent=paused?"Simulation angehalten":"Simulation läuft";
  lastFrame=null;
  if(paused&&raf){cancelAnimationFrame(raf);raf=0}
  if(!paused&&!raf)raf=requestAnimationFrame(frame);
}
function frame(now){
  raf=0;
  if(paused)return;
  if(lastFrame!==null){
    // Frame-independent phase progression: omega = sqrt(D/m) rad/s.
    // Equivalent to dt=0.035s per 35ms frame in the Python source.
    const dt=Math.min(.2,Math.max(0,(now-lastFrame)/1000));
    const omega=Math.sqrt(N("federhaerte")/N("masse-regler"));
    phase=(phase+omega*dt)%(2*Math.PI);
    draw();
  }
  lastFrame=now;
  raf=requestAnimationFrame(frame);
}
$("play").addEventListener("click",()=>setPaused(!paused));
$("phase").addEventListener("input",()=>{
  setPaused(true);
  phase=Number($("phase").value)*Math.PI/180;
  draw();
});
for(const id of ["amplitude","federhaerte","masse-regler","einzelkraefte-check","resultierende-check"]){
  $(id).addEventListener("input",draw);
}
document.addEventListener("visibilitychange",()=>{if(document.hidden)setPaused(true)});
draw();
setPaused(false);
