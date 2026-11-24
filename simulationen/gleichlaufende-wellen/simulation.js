"use strict";
// Parity with Python: v=0.60 λ₀/s, 0<=x<=10 λ₀, f=0.2..1.5 Hz.
// For both the image and the optional audible proxy, sources move to the right.
const SPEED=0.60,XMAX=10,YMAX=4.2,CARRIER=400,GAIN=.12;
const $=id=>document.getElementById(id);
const N=id=>Number($(id).value);
const fmt=(x,n=2)=>x.toFixed(n).replace(".",",");
const canvas=$("plot"),ctx=canvas.getContext("2d");
let playing=true,clock=0,lastFrame=null,raf=0,audioContext=null,audioNode=null,audioSamples=0;
const data=()=>({xh:N("listener"),d:N("distance"),a1:N("amp1"),a2:N("amp2"),f1:N("freq1"),f2:N("freq2"),volume:N("volume")});
const wave=(x,t,p,source)=>p["a"+source]*Math.sin(2*Math.PI*((x-(source===2?p.d:0))*p["f"+source]/SPEED-p["f"+source]*t));
function setup(){
  const scale=window.devicePixelRatio||1;
  const width=1080,height=520;
  if(canvas.width!==Math.round(width*scale)||canvas.height!==Math.round(height*scale)){
    canvas.width=Math.round(width*scale);canvas.height=Math.round(height*scale);
  }
  ctx.setTransform(scale,0,0,scale,0,0);
}
function drawPhasors(p){
  const cv=$("phasor"),g=cv.getContext("2d"),S=420,dpr=window.devicePixelRatio||1;
  if(cv.width!==Math.round(S*dpr)||cv.height!==Math.round(S*dpr)){cv.width=Math.round(S*dpr);cv.height=Math.round(S*dpr)}
  g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,S,S);
  const center=210,scale=190/4.2;
  const X=v=>center+v*scale,Y=v=>center-v*scale;
  g.font="13px system-ui";g.fillStyle="#455f75";
  for(let i=-4;i<=4;i++){g.strokeStyle=i===0?"#808d9a":"#e5ebf1";g.beginPath();g.moveTo(X(i),20);g.lineTo(X(i),400);g.moveTo(20,Y(i));g.lineTo(400,Y(i));g.stroke();if(i!==0){g.fillText(String(i),X(i)+3,center+15);g.fillText(String(i),center+5,Y(i)-4)}}
  const phase1=2*Math.PI*p.f1*(p.xh/SPEED-clock),phase2=2*Math.PI*p.f2*((p.xh-p.d)/SPEED-clock);
  const z1=[-p.a1*Math.cos(phase1),p.a1*Math.sin(phase1)],z2=p.xh>=p.d?[-p.a2*Math.cos(phase2),p.a2*Math.sin(phase2)]:[0,0];
  const sum=[z1[0]+z2[0],z1[1]+z2[1]];
  for(const [z,color,id] of [[z1,"#1976d2","show1"],[z2,"#e59b20","show2"],[sum,"#208c54","showSum"]]){
    if(!$(id).checked||Math.hypot(...z)<1e-8)continue;
    const x=X(z[0]),y=Y(z[1]),angle=Math.atan2(y-center,x-center);
    g.strokeStyle=color;g.fillStyle=color;g.lineWidth=3;g.beginPath();g.moveTo(center,center);g.lineTo(x,y);g.stroke();
    g.beginPath();g.moveTo(x,y);g.lineTo(x-12*Math.cos(angle-.45),y-12*Math.sin(angle-.45));g.lineTo(x-12*Math.cos(angle+.45),y-12*Math.sin(angle+.45));g.closePath();g.fill();
  }
}
function draw(){
  setup();
  const p=data(),W=1080,H=520,L=85,R=1030,T=35,B=447, width=R-L,height=B-T;
  const X=x=>L+x/XMAX*width,Y=y=>(T+B)/2-y/YMAX*height/2;
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);
  ctx.lineWidth=1;ctx.font="15px system-ui,sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";
  for(let x=0;x<=XMAX;x++){
    const xx=X(x);ctx.strokeStyle="#e5ebf1";ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();
    ctx.fillStyle="#455f75";ctx.fillText(String(x),xx,B+20);
  }
  for(let y=-4;y<=4;y++){
    ctx.strokeStyle=y===0?"#808d9a":"#ecf0f4";ctx.lineWidth=y===0?1.7:1;ctx.beginPath();ctx.moveTo(L,Y(y));ctx.lineTo(R,Y(y));ctx.stroke();
    ctx.fillStyle="#455f75";ctx.textAlign="right";ctx.fillText(String(y),L-11,Y(y));ctx.textAlign="center";
  }
  ctx.strokeStyle="#9bafbd";ctx.lineWidth=1;ctx.strokeRect(L,T,width,height);
  ctx.fillStyle="#253d53";ctx.font="17px system-ui,sans-serif";ctx.fillText("Ort x / λ₀",(L+R)/2,H-23);
  ctx.save();ctx.translate(23,(T+B)/2);ctx.rotate(-Math.PI/2);ctx.fillText("Auslenkung (relative Einheiten)",0,0);ctx.restore();
  const curves=[{id:"show1",color:"#1976d2",source:1},{id:"show2",color:"#e59b20",source:2},{id:"showSum",color:"#208c54",source:3}];
  for(const c of curves){
    if(!$(c.id).checked)continue;
    ctx.beginPath();ctx.strokeStyle=c.color;ctx.lineWidth=c.source===3?3:2;
    const begin=c.source===1?0:p.d;
    const n=1400;
    for(let i=0;i<=n;i++){
      const x=begin+(XMAX-begin)*i/n;
      const y=c.source===1?wave(x,clock,p,1):c.source===2?wave(x,clock,p,2):wave(x,clock,p,1)+wave(x,clock,p,2);
      if(i===0)ctx.moveTo(X(x),Y(y));else ctx.lineTo(X(x),Y(y));
    }
    ctx.stroke();
  }
  const sources=[{x:0,y:-p.a1*Math.sin(2*Math.PI*p.f1*clock),color:"#1976d2"},{x:p.d,y:-p.a2*Math.sin(2*Math.PI*p.f2*clock),color:"#e59b20"}];
  for(const source of sources){
    const xx=X(source.x);
    ctx.save();ctx.setLineDash([6,5]);ctx.strokeStyle=source.color;ctx.globalAlpha=.7;ctx.lineWidth=1.4;
    ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();ctx.restore();
    ctx.fillStyle=source.color;ctx.beginPath();ctx.arc(xx,Y(source.y),7,0,2*Math.PI);ctx.fill();
  }
  const hearY=wave(p.xh,clock,p,1)+(p.xh>=p.d?wave(p.xh,clock,p,2):0);
  ctx.save();ctx.strokeStyle="#7a3eb1";ctx.lineWidth=2;ctx.setLineDash([2,5]);ctx.beginPath();ctx.moveTo(X(p.xh),T);ctx.lineTo(X(p.xh),B);ctx.stroke();ctx.restore();
  ctx.fillStyle="#7a3eb1";ctx.beginPath();ctx.moveTo(X(p.xh),Y(hearY)-9);ctx.lineTo(X(p.xh)+9,Y(hearY));ctx.lineTo(X(p.xh),Y(hearY)+9);ctx.lineTo(X(p.xh)-9,Y(hearY));ctx.closePath();ctx.fill();
  drawPhasors(p);
  const l1=SPEED/p.f1,l2=SPEED/p.f2,df=Math.abs(p.f1-p.f2);
  $("info").textContent="λ₁ = "+fmt(l1)+" λ₀     λ₂ = "+fmt(l2)+" λ₀     v = "+fmt(SPEED)+" λ₀/s     "+(df<1e-9?"gleiche Frequenz":"fSchwebung = "+fmt(df)+" Hz");
}
function outputs(){
  for(const id of ["listener","distance","amp1","amp2","freq1","freq2","volume"])$(id+"-out").textContent=fmt(N(id));
}
function frame(now){
  raf=0;
  if(!playing)return;
  if(lastFrame!==null)clock+=Math.min(.25,Math.max(0,(now-lastFrame)/1000));
  lastFrame=now;draw();raf=requestAnimationFrame(frame);
}
function stopFrame(){if(raf)cancelAnimationFrame(raf);raf=0;lastFrame=null}
function setRunning(value){
  playing=value;
  $("play").textContent=value?"⏸ Pause":"▶ Start";
  $("status").textContent=value?"Simulation läuft":"Simulation pausiert";
  stopFrame();draw();
  if(value)raf=requestAnimationFrame(frame);
}
// Optional sound: 400-Hz carrier with interference-phase modulation at the listener.
async function setAudio(on){
  if(!on){if(audioNode){audioNode.disconnect();audioNode.onaudioprocess=null;audioNode=null}if(audioContext){await audioContext.close().catch(()=>{});audioContext=null}$("sound-status").textContent="Ton: aus";return}
  const AudioCtx=window.AudioContext||window.webkitAudioContext;
  if(!AudioCtx){$("sound").checked=false;$("sound-status").textContent="Audio im Browser nicht verfügbar";return}
  try{
    audioContext=new AudioCtx();
    await audioContext.resume();
    audioSamples=0;
    audioNode=audioContext.createScriptProcessor(2048,0,1);
    audioNode.onaudioprocess=event=>{
      const buffer=event.outputBuffer.getChannelData(0),p=data(),sampleRate=audioContext.sampleRate;
      const base=clock;
      for(let i=0;i<buffer.length;i++){
        const tt=base+(playing?i/sampleRate:0);
        const ph1=2*Math.PI*(p.f1*p.xh/SPEED-p.f1*tt);
        const ph2=2*Math.PI*(p.f2*(p.xh-p.d)/SPEED-p.f2*tt);
        const carrier=2*Math.PI*CARRIER*(audioSamples+i)/sampleRate;
        const mixture=p.a1*Math.sin(carrier+ph1)+(p.xh>=p.d?p.a2*Math.sin(carrier+ph2):0);
        buffer[i]=playing?mixture*GAIN*p.volume/4:0;
      }
      audioSamples+=buffer.length;
    };
    audioNode.connect(audioContext.destination);
    $("sound-status").textContent="Ton: an (400-Hz-Träger am Hörpunkt)";
  }catch(err){$("sound").checked=false;$("sound-status").textContent="Audiofehler: "+String(err.message||err);await setAudio(false)}
}
for(const id of ["listener","distance","amp1","amp2","freq1","freq2","volume"]){
  $(id).addEventListener("input",()=>{outputs();draw()});
}
for(const id of ["show1","show2","showSum"])$(id).addEventListener("change",draw);
// Fine intermediate values remain selectable; release near any half
// reference wavelength snaps precisely to the intended special value.
$("distance").addEventListener("change",()=>{
  const value=N("distance");
  const nearest=Math.round(value*2)/2;
  if(Math.abs(value-nearest)<=0.03)$("distance").value=String(nearest);
  outputs();draw();
});
$("play").addEventListener("click",()=>setRunning(!playing));
$("reset").addEventListener("click",()=>{
  for(const [id,v] of Object.entries({listener:5,distance:.25,amp1:1,amp2:1,freq1:.6,freq2:.6,volume:.25}))$(id).value=String(v);
  for(const id of ["show1","show2","showSum"])$(id).checked=true;
  clock=0;outputs();setRunning(true);
});
$("sound").addEventListener("change",event=>{void setAudio(event.target.checked)});
document.addEventListener("visibilitychange",()=>{if(document.hidden)setRunning(false)});
outputs();draw();raf=requestAnimationFrame(frame);
