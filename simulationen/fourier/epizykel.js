"use strict";
// Complex Fourier reconstruction of a word silhouette.
// Unlike Python TextPath, browser glyph contours are extracted from canvas pixels.
const N=2200,MAX=250,PI=Math.PI,$=id=>document.getElementById(id);
let sourceR=new Float64Array(N),sourceI=new Float64Array(N);
let coeffR=new Float64Array(N),coeffI=new Float64Array(N);
let sorted=[],selected=[],reconR=new Float64Array(N),reconI=new Float64Array(N);
let frame=0,running=false,raf=0,lastFrame=null,extents={minX:-4,maxX:4,minY:-2,maxY:2},scaleError=0;
function fft(r,i,inverse=false){
  const n=r.length;
  for(let a=1,b=0;a<n;a++){
    let bit=n>>1;for(;b&bit;bit>>=1)b^=bit;b^=bit;
    if(a<b){[r[a],r[b]]=[r[b],r[a]];[i[a],i[b]]=[i[b],i[a]];}
  }
  for(let len=2;len<=n;len*=2){
    const theta=2*PI/len*(inverse?1:-1),wr0=Math.cos(theta),wi0=Math.sin(theta);
    for(let start=0;start<n;start+=len){
      let wr=1,wi=0;
      for(let k=0;k<len/2;k++){
        const u=start+k,v=u+len/2;
        const tr=wr*r[v]-wi*i[v],ti=wr*i[v]+wi*r[v];
        r[v]=r[u]-tr;i[v]=i[u]-ti;
        r[u]+=tr;i[u]+=ti;
        const nr=wr*wr0-wi*wi0;wi=wr*wi0+wi*wr0;wr=nr;
      }
    }
  }
  if(inverse)for(let k=0;k<n;k++){r[k]/=n;i[k]/=n;}
}
function dftBluestein(re,im){
  const n=re.length;let size=1;while(size<2*n-1)size*=2;
  const ar=new Float64Array(size),ai=new Float64Array(size),br=new Float64Array(size),bi=new Float64Array(size);
  for(let k=0;k<n;k++){
    const angle=PI*(k*k%n)/n,cs=Math.cos(angle),sn=Math.sin(angle);
    ar[k]=re[k]*cs+im[k]*sn;ai[k]=im[k]*cs-re[k]*sn;
    br[k]=cs;bi[k]=sn;
    if(k>0){br[size-k]=cs;bi[size-k]=sn;}
  }
  fft(ar,ai);fft(br,bi);
  for(let k=0;k<size;k++){
    const tr=ar[k]*br[k]-ai[k]*bi[k],ti=ar[k]*bi[k]+ai[k]*br[k];
    ar[k]=tr;ai[k]=ti;
  }
  fft(ar,ai,true);
  const outR=new Float64Array(n),outI=new Float64Array(n);
  for(let k=0;k<n;k++){
    const angle=PI*(k*k%n)/n,cs=Math.cos(angle),sn=Math.sin(angle);
    outR[k]=(ar[k]*cs+ai[k]*sn)/n;
    outI[k]=(ai[k]*cs-ar[k]*sn)/n;
  }
  return [outR,outI];
}
function glyphPoints(word){
  if(!word.trim())throw Error("Bitte ein Wort eingeben.");
  const c=document.createElement("canvas");c.width=520;c.height=130;
  const ctx=c.getContext("2d",{willReadFrequently:true});if(!ctx)throw Error("Canvas nicht verfügbar.");
  let size=110;ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="bold "+size+"px sans-serif";
  const measured=ctx.measureText(word).width;
  if(measured>c.width-24)size*= (c.width-24)/measured;
  if(size<13)throw Error("Bitte ein kürzeres Wort eingeben.");
  ctx.font="bold "+size+"px sans-serif";ctx.fillStyle="#000";ctx.fillText(word,c.width/2,c.height/2+3);
  const raw=ctx.getImageData(0,0,c.width,c.height).data;
  const stride=2,width=c.width/stride,height=c.height/stride;
  const bitmap=new Uint8Array(width*height);
  let count=0;
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    const px=Math.min(c.width-1,x*stride+1),py=Math.min(c.height-1,y*stride+1);
    const a=raw[(py*c.width+px)*4+3];
    if(a>80){bitmap[y*width+x]=1;count++;}
  }
  if(count<20)throw Error("Aus diesem Wort konnte keine Kontur erzeugt werden.");
  const active=(x,y)=>x>=0&&y>=0&&x<width&&y<height&&bitmap[y*width+x]>0;
  const edges=new Map();let edgesCount=0;
  const edge=(x1,y1,x2,y2)=>{
    const key=x1+","+y1,existing=edges.get(key)||[];
    existing.push([x2,y2]);edges.set(key,existing);edgesCount++;
  };
  for(let y=0;y<height;y++)for(let x=0;x<width;x++)if(active(x,y)){
    if(!active(x,y-1))edge(x,y,x+1,y);
    if(!active(x+1,y))edge(x+1,y,x+1,y+1);
    if(!active(x,y+1))edge(x+1,y+1,x,y+1);
    if(!active(x-1,y))edge(x,y+1,x,y);
  }
  const loops=[];
  while(edgesCount>0){
    const first=edges.entries().next();if(first.done)break;
    const [startKey]=first.value,start=startKey.split(",").map(Number);
    let current=start.slice();const loop=[start.slice()],limit=edgesCount+2;
    for(let n=0;n<limit;n++){
      const key=current[0]+","+current[1],list=edges.get(key);
      if(!list||!list.length)break;
      const next=list.pop();edgesCount--;
      if(!list.length)edges.delete(key);
      current=next;loop.push(next);
      if(next[0]===start[0]&&next[1]===start[1])break;
    }
    if(loop.length>5)loops.push(loop);
  }
  if(!loops.length)throw Error("Keine geschlossene Wortkontur gefunden.");
  // Each contour is traversed by arc length, including short paths between letters.
  const chain=[];
  for(const loop of loops){
    if(chain.length){
      const prev=chain[chain.length-1],next=loop[0];
      for(let j=1;j<=15;j++)chain.push([prev[0]+(next[0]-prev[0])*j/16,prev[1]+(next[1]-prev[1])*j/16]);
    }
    chain.push(...loop);
  }
  chain.push(chain[0].slice());
  let meanX=0,meanY=0;for(const [x,y] of chain){meanX+=x;meanY+=y;}
  meanX/=chain.length;meanY/=chain.length;
  const xs=chain.map(p=>(p[0]-meanX)*.03),ys=chain.map(p=>(meanY-p[1])*.03);
  const lengths=[0];
  for(let i=1;i<xs.length;i++)lengths.push(lengths[i-1]+Math.hypot(xs[i]-xs[i-1],ys[i]-ys[i-1]));
  const total=lengths[lengths.length-1];
  if(total<=1e-9)throw Error("Wortkontur hat keine messbare Länge.");
  const outR=new Float64Array(N),outI=new Float64Array(N);let cursor=1;
  for(let n=0;n<N;n++){
    const distance=total*n/N;
    while(cursor<lengths.length-1&&lengths[cursor]<distance)cursor++;
    const p=cursor-1,q=cursor,span=lengths[q]-lengths[p];
    const ratio=span? (distance-lengths[p])/span:0;
    outR[n]=xs[p]+(xs[q]-xs[p])*ratio;
    outI[n]=ys[p]+(ys[q]-ys[p])*ratio;
  }
  return [outR,outI];
}
function freq(k){return k<=N/2?k:k-N;}
function recompute(){
  running=false;stopFrame();$("animate").textContent="▶ Animation starten";
  try{
    const [r,i]=glyphPoints($("word").value);
    sourceR=r;sourceI=i;
    [coeffR,coeffI]=dftBluestein(r,i);
    sorted=Array.from({length:N},(_,k)=>k).sort((a,b)=>Math.hypot(coeffR[b],coeffI[b])-Math.hypot(coeffR[a],coeffI[a])||a-b);
    frame=0;selection();$("epicycle-error").textContent="";
  }catch(e){$("epicycle-error").textContent=String(e.message||e);}
}
function selection(){
  if(!sorted.length)return;
  selected=sorted.slice(0,Number($("epicycle-components").value));
  $("epicycle-out").textContent=String(selected.length);
  $("epicycle-title").textContent="1. Rekonstruktion: „"+$("word").value.trim()+"“ mit "+selected.length+" Fourier-Komponenten";
  $("coeff-title").textContent="2. Frequenzspektrum – "+selected.length+" verwendete Komponenten";
  for(let n=0;n<N;n++){
    const t=n/N;let rr=0,ii=0;
    for(const k of selected){
      const angle=2*PI*freq(k)*t,cs=Math.cos(angle),sn=Math.sin(angle);
      rr+=coeffR[k]*cs-coeffI[k]*sn;
      ii+=coeffR[k]*sn+coeffI[k]*cs;
    }
    reconR[n]=rr;reconI[n]=ii;
  }
  let diff=0,minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(let n=0;n<N;n++){
    diff+=(sourceR[n]-reconR[n])**2+(sourceI[n]-reconI[n])**2;
    minX=Math.min(minX,sourceR[n]);maxX=Math.max(maxX,sourceR[n]);
    minY=Math.min(minY,sourceI[n]);maxY=Math.max(maxY,sourceI[n]);
  }
  extents={minX,maxX,minY,maxY};
  scaleError=Math.sqrt(diff/N)/Math.max(maxX-minX,maxY-minY,1e-12)*100;
  $("epicycle-info").textContent="Komponenten: "+selected.length+"   |   relativer RMS-Fehler: "+scaleError.toFixed(1).replace(".",",")+" %";
  draw();
}
function canvas(id){
  const el=$(id),W=Number(el.getAttribute("width")),H=Number(el.getAttribute("height")),dpr=Math.min(devicePixelRatio||1,2.5);
  if(el.width!==Math.round(W*dpr)||el.height!==Math.round(H*dpr)){el.width=Math.round(W*dpr);el.height=Math.round(H*dpr);}
  const ctx=el.getContext("2d");ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.clearRect(0,0,W,H);ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);
  return {ctx,W,H,L:58,R:W-20,T:25,B:H-47};
}
function polyline(ctx,N,fnx,fny,color,width=2,dash=[],alpha=1){
  ctx.beginPath();for(let n=0;n<N;n++){const x=fnx(n),y=fny(n);if(n===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.globalAlpha=alpha;ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;
}
function contour(){
  const g=canvas("contour-plot"),{ctx,L,R,T,B}=g;
  const mx=(extents.minX+extents.maxX)/2,my=(extents.minY+extents.maxY)/2;
  const sx=(R-L)/Math.max(1,extents.maxX-extents.minX+1.6),sy=(B-T)/Math.max(1,extents.maxY-extents.minY+1.6);
  const scale=Math.min(sx,sy),X=x=>(L+R)/2+(x-mx)*scale,Y=y=>(T+B)/2-(y-my)*scale;
  ctx.strokeStyle="#e5ebef";ctx.lineWidth=1;ctx.strokeRect(L,T,R-L,B-T);
  if($("target").checked)polyline(ctx,N,n=>X(sourceR[n]),n=>Y(sourceI[n]),"#88929d",1.2,[],.55);
  if(frame>0)polyline(ctx,frame+1,n=>X(reconR[n]),n=>Y(reconI[n]),"#884cb0",2.5);
  const t=frame/N;
  let rr=0,ii=0;
  const circles=$("circles").checked;
  for(let a=0;a<selected.length;a++){
    const k=selected[a],angle=2*PI*freq(k)*t,cs=Math.cos(angle),sn=Math.sin(angle);
    const nr=rr+coeffR[k]*cs-coeffI[k]*sn,ni=ii+coeffR[k]*sn+coeffI[k]*cs;
    if(circles&&a<40){
      ctx.strokeStyle="rgba(100,112,130,.45)";ctx.lineWidth=.85;
      ctx.beginPath();ctx.arc(X(rr),Y(ii),Math.hypot(coeffR[k],coeffI[k])*scale,0,2*PI);ctx.stroke();
      ctx.strokeStyle="rgba(83,93,108,.7)";ctx.beginPath();ctx.moveTo(X(rr),Y(ii));ctx.lineTo(X(nr),Y(ni));ctx.stroke();
    }
    rr=nr;ii=ni;
  }
  ctx.fillStyle="#ca3e42";ctx.beginPath();ctx.arc(X(rr),Y(ii),4.8,0,2*PI);ctx.fill();
  ctx.fillStyle="#344b60";ctx.font="15px system-ui,sans-serif";ctx.textAlign="center";ctx.fillText("x",(L+R)/2,g.H-15);
  ctx.save();ctx.translate(18,(T+B)/2);ctx.rotate(-PI/2);ctx.fillText("y",0,0);ctx.restore();
}
function spectrum(){
  const g=canvas("coefficient-plot"),{ctx,L,R,T,B}=g;
  const shown=sorted.slice(0,80).sort((a,b)=>freq(a)-freq(b));
  const active=selected.slice().sort((a,b)=>freq(a)-freq(b));
  const minF=Math.min(...shown.map(freq),...active.map(freq));
  const maxF=Math.max(...shown.map(freq),...active.map(freq));
  const maxAmplitude=Math.max(.01,...shown.map(k=>Math.hypot(coeffR[k],coeffI[k])))*1.2;
  const X=f=>L+(f-minF)/Math.max(1,maxF-minF)*(R-L),Y=a=>B-a/maxAmplitude*(B-T);
  ctx.strokeStyle="#b7c8d5";ctx.lineWidth=1;ctx.strokeRect(L,T,R-L,B-T);
  ctx.textAlign="center";ctx.font="13px system-ui,sans-serif";
  for(let i=0;i<=4;i++){
    const f=minF+(maxF-minF)*i/4,xx=X(f),y=maxAmplitude*i/4,yy=Y(y);
    ctx.strokeStyle="#edf0f3";ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();
    ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(R,yy);ctx.stroke();
    ctx.fillStyle="#4f6173";ctx.fillText(String(Math.round(f)),xx,B+17);
    ctx.textAlign="right";ctx.fillText(y.toFixed(1),L-8,yy);ctx.textAlign="center";
  }
  const drawStem=(k,color,w,alpha)=>{
    const x=X(freq(k)),y=Y(Math.hypot(coeffR[k],coeffI[k]));ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.lineWidth=w;
    ctx.beginPath();ctx.moveTo(x,B);ctx.lineTo(x,y);ctx.stroke();ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,w+1,0,2*PI);ctx.fill();ctx.globalAlpha=1;
  };
  for(const k of shown)drawStem(k,"#808891",.8,.28);
  for(const k of active)drawStem(k,"#884cb0",1.7,.95);
  ctx.fillStyle="#344b60";ctx.font="14px system-ui,sans-serif";ctx.fillText("Frequenzindex k",(L+R)/2,g.H-12);
  ctx.save();ctx.translate(18,(T+B)/2);ctx.rotate(-PI/2);ctx.fillText("Amplitude |cₖ|",0,0);ctx.restore();
}
function xy(){
  const g=canvas("xy-plot"),{ctx,L,R,T,B}=g;
  let bound=1;
  for(let n=0;n<N;n++)bound=Math.max(bound,Math.abs(sourceR[n]),Math.abs(sourceI[n]),Math.abs(reconR[n]),Math.abs(reconI[n]));
  bound*=1.15;
  const X=t=>L+t*(R-L),Y=v=>(T+B)/2-v/bound*(B-T)/2;
  ctx.strokeStyle="#b7c8d5";ctx.strokeRect(L,T,R-L,B-T);ctx.lineWidth=1;ctx.strokeStyle="#e2e8ed";
  for(let i=0;i<=4;i++){const xx=X(i/4);ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();ctx.fillStyle="#516477";ctx.font="13px system-ui,sans-serif";ctx.textAlign="center";ctx.fillText((i/4).toFixed(2),xx,B+15);}
  if($("target").checked){
    polyline(ctx,N,n=>X(n/N),n=>Y(sourceR[n]),"#9c9c9c",.9,[4,4],.35);
    polyline(ctx,N,n=>X(n/N),n=>Y(sourceI[n]),"#757575",.9,[2,5],.35);
  }
  polyline(ctx,N,n=>X(n/N),n=>Y(reconR[n]),"#2478ba",1.8);
  polyline(ctx,N,n=>X(n/N),n=>Y(reconI[n]),"#27875e",1.8);
  const xx=X(frame/N);
  ctx.save();ctx.setLineDash([6,4]);ctx.strokeStyle="#ca3e42";ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,B);ctx.stroke();ctx.restore();
  for(const [v,color] of [[reconR[frame],"#2478ba"],[reconI[frame],"#27875e"]]){ctx.fillStyle=color;ctx.beginPath();ctx.arc(xx,Y(v),4,0,2*PI);ctx.fill();}
  ctx.fillStyle="#344b60";ctx.font="14px system-ui,sans-serif";ctx.textAlign="center";ctx.fillText("Parameter t",(L+R)/2,g.H-13);
}
function draw(){if(!selected.length)return;contour();spectrum();xy();}
function stopFrame(){if(raf)cancelAnimationFrame(raf);raf=0;lastFrame=null;}
function animate(now){
  raf=0;if(!running)return;
  if(lastFrame!==null){frame=(frame+Math.min(144,Math.max(1,Math.round((now-lastFrame)/15*16))))%N;draw();}
  lastFrame=now;raf=requestAnimationFrame(animate);
}
function setRunning(value){
  running=value;stopFrame();$("animate").textContent=value?"⏸ Animation stoppen":"▶ Animation starten";
  if(value)raf=requestAnimationFrame(animate);
}
$("recompute").addEventListener("click",recompute);
$("word").addEventListener("keydown",e=>{if(e.key==="Enter")recompute()});
$("epicycle-components").addEventListener("input",selection);
for(const id of ["circles","target"])$(id).addEventListener("change",draw);
$("animate").addEventListener("click",()=>setRunning(!running));
$("restart").addEventListener("click",()=>{setRunning(false);frame=0;draw()});
document.addEventListener("visibilitychange",()=>{if(document.hidden)setRunning(false)});
recompute();
