"use strict";
const $=id=>document.getElementById(id);
const canvas=$("plot");
const ctx=canvas.getContext("2d");
const defaults={a:1,b:1,c:0,d:0};
const fmt=v=>v.toFixed(1).replace(".",",");
const value=id=>Number($(id).value);
const tickNames=["−2π","−3π/2","−π","−π/2","0","π/2","π","3π/2","2π"];
function draw(){
  const {a,b,c,d}=Object.fromEntries(["a","b","c","d"].map(id=>[id,value(id)]));
  for(const id of ["a","b","c","d"])$(id+"Out").textContent=fmt(value(id));
  const ratio=Math.min(window.devicePixelRatio||1,3),W=1040,H=590;
  if(canvas.width!==Math.round(W*ratio)||canvas.height!==Math.round(H*ratio)){
    canvas.width=Math.round(W*ratio);canvas.height=Math.round(H*ratio);
  }
  ctx.setTransform(ratio,0,0,ratio,0,0);
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);
  const left=65,right=1015,top=28,bottom=520;
  const xMin=-2*Math.PI,xMax=2*Math.PI;
  const bound=Math.max(4,Math.abs(a)+Math.abs(d)+0.4);
  const tx=x=>left+(x-xMin)/(xMax-xMin)*(right-left);
  const ty=y=>bottom-(y+bound)/(2*bound)*(bottom-top);
  ctx.textBaseline="middle";
  ctx.font="15px system-ui,sans-serif";
  for(let k=0;k<9;k++){
    const px=tx((-2+k*.5)*Math.PI);
    ctx.beginPath();ctx.moveTo(px,top);ctx.lineTo(px,bottom);
    ctx.strokeStyle=k===4?"#879bad":"#e5edf3";ctx.lineWidth=k===4?1.4:1;ctx.stroke();
    ctx.fillStyle="#40566b";ctx.textAlign="center";ctx.fillText(tickNames[k],px,bottom+21);
  }
  // Symmetric y-ticks use real values, with the visible range adapted to the curves.
  for(let k=0;k<=8;k++){
    const y=-bound+(2*bound*k/8),py=ty(y);
    ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(right,py);
    ctx.strokeStyle=k===4?"#879bad":"#e5edf3";ctx.lineWidth=k===4?1.4:1;ctx.stroke();
    ctx.textAlign="right";ctx.fillStyle="#40566b";ctx.fillText(fmt(y),left-9,py);
  }
  ctx.strokeStyle="#bdcdd9";ctx.lineWidth=1;ctx.strokeRect(left,top,right-left,bottom-top);
  ctx.font="17px system-ui,sans-serif";ctx.fillStyle="#284358";ctx.textAlign="center";
  ctx.fillText("x",W/2,H-15);
  ctx.save();ctx.translate(17,(top+bottom)/2);ctx.rotate(-Math.PI/2);ctx.fillText("f(x)",0,0);ctx.restore();
  const curves=[
    {visible:$("showSin").checked,color:"#235ab4",calc:x=>a*Math.sin(b*(x-c))+d},
    {visible:$("showCos").checked,color:"#c26c20",calc:x=>a*Math.cos(b*(x-c))+d}
  ];
  for(const curve of curves){
    if(!curve.visible)continue;
    ctx.strokeStyle=curve.color;ctx.lineWidth=2.9;ctx.beginPath();
    for(let i=0;i<=1600;i++){
      const x=xMin+(xMax-xMin)*i/1600,px=tx(x),py=ty(curve.calc(x));
      if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);
    }
    ctx.stroke();
  }
}
for(const id of ["a","b","c","d"])$(id).addEventListener("input",draw);
for(const id of ["showSin","showCos"])$(id).addEventListener("change",draw);
$("reset").addEventListener("click",()=>{
  for(const [id,v] of Object.entries(defaults))$(id).value=String(v);
  $("showSin").checked=true;
  $("showCos").checked=false;
  draw();
});
draw();
