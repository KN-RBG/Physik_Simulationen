const THEMEN=["Elektrische und magnetische Felder","Induktion","Mechanische Schwingungen und Wellen","Elektromagnetische Schwingungen und Wellen","Atom- und Quantenphysik","Weitere Themen"];
let katalog=[];
const el=(id)=>document.getElementById(id);
function render(){const modus=document.querySelector('input[name=ansicht]:checked').value,stufe=el("klasse").value,gang=el("bildungsgang").value,fach=el("thema").value,q=el("suche").value.toLocaleLowerCase("de");
const gefunden=katalog.filter(s=>(fach==="alle"||s.thema===fach)&&(!stufe||s.klassenstufen.includes(stufe))&&(!gang||s.bildungsgaenge.includes(gang))&&(s.titel+" "+s.beschreibung+" "+s.thema).toLocaleLowerCase("de").includes(q));
const bereiche=modus==="klassen"?[...new Set(gefunden.flatMap(s=>s.klassenstufen))].sort((a,b)=>a.localeCompare(b,"de",{numeric:true})):THEMEN;
const ziel=el("ergebnisse");ziel.replaceChildren();el("anzahl").textContent=gefunden.length+" Einträge";
if(!gefunden.length&&modus==="klassen"){const p=document.createElement("p");p.className="empty";p.textContent="Noch keine geprüften Klassenstufen-Zuordnungen vorhanden. Bitte auf „Nach Themengebiet“ wechseln; die Zuordnungen werden später ergänzt.";ziel.append(p);return}
for(const name of bereiche){const section=document.createElement("section");section.className="topic";const h=document.createElement("h2");h.textContent=name;section.append(h);
const items=gefunden.filter(s=>modus==="klassen"?s.klassenstufen.includes(name):s.thema===name);
if(!items.length){const p=document.createElement("p");p.className="empty";p.textContent="Simulationen in Vorbereitung";section.append(p)}
else{const cards=document.createElement("div");cards.className="grid";for(const s of items){const card=document.createElement("article");card.className="card";const title=document.createElement("h3");title.textContent=s.titel;card.append(title);const desc=document.createElement("p");desc.textContent=s.beschreibung;card.append(desc);const meta=document.createElement("p");meta.className="meta";meta.textContent="Klassenstufen: "+(s.klassenstufen.join(", ")||"noch nicht zugeordnet")+" · Bildungsgang: "+(s.bildungsgaenge.join(", ")||"noch nicht geprüft");card.append(meta);const links=document.createElement("div");links.className="links";for(const [label,url] of [["Python herunterladen",s.python_download_url],["HTML starten",s.html_url],["Webprojekt (Prototyp)",s.webprojekt_url]])if(url){const a=document.createElement("a");a.href=url;a.textContent=label;if(label==="Python herunterladen")a.download=url.split("/").pop();else{a.target="_blank";a.rel="noopener noreferrer"}links.append(a)}if(s.html_url&&s.qr_url){const download=document.createElement("a");download.href=s.qr_url;download.download="QR-Code-"+s.id+".svg";download.textContent="QR-Code (Download)";download.title="QR-Code als hochauflösende SVG-Datei herunterladen";links.append(download);const showQr=document.createElement("button");showQr.type="button";showQr.className="qr-display-button";showQr.textContent="QR-Code (Anzeige)";showQr.addEventListener("click",()=>openQr(s));links.append(showQr)}if(!s.python_download_url&&s.python_url){const note=document.createElement("span");note.className="meta";note.textContent="Python-Download noch in Vorbereitung";links.append(note)}card.append(links);cards.append(card)}section.append(cards)}ziel.append(section)}
}
function openQr(s){
  const dialog=el("qr-dialog");
  if(!dialog||!s.qr_url||!s.html_url)return;
  el("qr-title").textContent="QR-Code: "+s.titel;
  const img=el("qr-image");
  img.src=s.qr_url;
  img.alt="QR-Code für die Simulation "+s.titel;
  const target=new URL(s.html_url,document.baseURI);
  el("qr-target").textContent=target.href;
  dialog.showModal();
}
async function start(){el("qr-close").addEventListener("click",()=>el("qr-dialog").close());el("qr-dialog").addEventListener("click",event=>{if(event.target===el("qr-dialog"))el("qr-dialog").close()});for(const input of document.querySelectorAll("input,select"))input.addEventListener("input",render);try{const r=await fetch("daten/simulationen.json",{cache:"no-cache"});if(!r.ok)throw Error("HTTP "+r.status);katalog=(await r.json()).simulationen;render()}catch(e){el("ergebnisse").textContent="Der Simulationskatalog konnte nicht geladen werden. Bitte die Seite über einen Webserver öffnen."}}
start();
