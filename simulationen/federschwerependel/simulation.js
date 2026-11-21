"use strict";
// Modell und Standardwerte aus KN-RBG/Federschwerependel/federschwerependel_animation.py
const g=9.81,L0=0.30,forceScale=0.055, springWidth=0.035, massWidth=0.13,massHeight=0.075;
const $=id=>document.getElementById(id);
const N=(id)=>Number($(id).value);
const fmt=(v,d=2)=>(Number(v).toFixed(d)).replace(".",",");
const signed=(v,d=1)=>(v>=0?"+":"")+fmt(v,d);
const yPx=y=>68+(y-0.02)*690; // 0.02m at ceiling; downward-positive physical coordinate
const xPx=x=>370+x*620;
let phase=0,paused=false,lastFrame=null,raf=0, elapsed=0;
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
  const cycle=2*Math.PI;
  const twoCycles=4*Math.PI;
  const displayPhase=paused ? phase : ((phase%twoCycles)+twoCycles)%twoCycles;
  const degrees=Math.round(displayPhase*180/Math.PI);
  $("phase").value=String(Math.min(720,degrees));
  const rad=Number($("phase").value)*Math.PI/180;
  $("phase-out").textContent=fmt(rad,2)+" rad ("+fmt(rad/Math.PI,2)+"π)";
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
  drawTimeGraph(A,omega);
}

const SVG_NS="http://www.w3.org/2000/svg";
function drawTimeGraph(A,omega){
  const root=$("zeitdiagramm");
  root.replaceChildren();
  const E=(tag,attrs={},label)=>{
    const el=document.createElementNS(SVG_NS,tag);
    for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));
    if(label!==undefined)el.textContent=label;
    root.appendChild(el);return el;
  };
  const X0=90,X1=555,Y0=25,Y1=240,ym=(Y0+Y1)/2,ampl=(Y1-Y0)*.43;
  const T=2*Math.PI/omega, span=2*T;
  const x=t=>X0+(t/span)*(X1-X0);
  const colors=["#8853a9","#2879b9","#d3852b"];
  const maxs=[A,A*omega,A*omega*omega];
  const names=["s","v","a"];
  const units=["m","m/s","m/s²"];
  const visible=[$("kurve-s").checked,$("kurve-v").checked,$("kurve-a").checked];
  E("rect",{x:X0,y:Y0,width:X1-X0,height:Y1-Y0,fill:"#fff",stroke:"#cbd7e3"});
  for(let k=0;k<=4;k++){
    const t=span*k/4,xx=x(t);
    E("line",{x1:xx,y1:Y0,x2:xx,y2:Y1,stroke:"#e3e9ef","stroke-width":1});
    E("text",{x:xx,y:Y1+21,"text-anchor":"middle","font-size":13,fill:"#526477"},fmt(t,2));
  }
  for(let k=-1;k<=1;k++){
    const yy=ym-k*ampl;
    E("line",{x1:X0,y1:yy,x2:X1,y2:yy,stroke:k===0?"#7b8795":"#edf1f5","stroke-width":k===0?1.3:1});
  }
  const labelsX=[65,613,697];
  for(let i=0;i<3;i++){
    if(!visible[i])continue;
    const max=maxs[i],xx=labelsX[i],color=colors[i];
    for(const k of [-1,0,1]){
      E("text",{x:xx,y:ym-k*ampl+4,"text-anchor":"middle","font-size":11,fill:color},fmt(k*max,Math.abs(max)<.1?3:2));
    }
    E("text",{x:xx,y:14,"text-anchor":"middle","font-size":13,"font-weight":"bold",fill:color},names[i]+" ["+units[i]+"]");
    const points=[];
    for(let j=0;j<=480;j++){
      const t=span*j/480,angle=omega*t;
      const v=i===0?A*Math.cos(angle):i===1?-A*omega*Math.sin(angle):-A*omega*omega*Math.cos(angle);
      points.push((j===0?"M":"L")+x(t).toFixed(2)+" "+(ym-v/max*ampl).toFixed(2));
    }
    E("path",{d:points.join(" "),fill:"none",stroke:color,"stroke-width":2.5});
  }
  const currentTime=paused ? Math.min(span,Math.max(0,elapsed)) : ((elapsed%span)+span)%span;
  const cursor=x(currentTime);
  E("line",{x1:cursor,y1:Y0,x2:cursor,y2:Y1,stroke:"#262c34","stroke-width":2,"stroke-dasharray":"5 5"});
  for(let i=0;i<3;i++)if(visible[i]){
    const angle=omega*currentTime;
    const v=i===0?A*Math.cos(angle):i===1?-A*omega*Math.sin(angle):-A*omega*omega*Math.cos(angle);
    E("circle",{cx:cursor,cy:ym-v/maxs[i]*ampl,r:4,fill:colors[i],stroke:"white","stroke-width":1});
  }
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
    elapsed+=dt;
    phase=omega*elapsed;
    draw();
  }
  lastFrame=now;
  raf=requestAnimationFrame(frame);
}
$("play").addEventListener("click",()=>setPaused(!paused));
$("phase").addEventListener("input",()=>{
  setPaused(true);
  phase=Number($("phase").value)*Math.PI/180;
  elapsed=phase/Math.sqrt(N("federhaerte")/N("masse-regler"));
  draw();
});
for(const id of ["amplitude","federhaerte","masse-regler","einzelkraefte-check","resultierende-check"]){
  $(id).addEventListener("input",()=>{
    if(id==="federhaerte"||id==="masse-regler")elapsed=phase/Math.sqrt(N("federhaerte")/N("masse-regler"));
    draw();
  });
}
for(const id of ["kurve-s","kurve-v","kurve-a"]){$(id).addEventListener("change",draw)}
document.addEventListener("visibilitychange",()=>{if(document.hidden)setPaused(true)});
draw();
setPaused(false);
