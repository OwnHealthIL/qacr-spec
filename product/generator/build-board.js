// Generates the standalone HTML milestone board from the same data as the
// Word document, so the two cannot disagree.
const fs = require("fs");
const OUT = process.argv[2];
const DIR = process.argv[3] || ".";
const V = require(DIR + "/version.js");

const sections = [...require(DIR + "/reqs-part1.js"), ...require(DIR + "/reqs-part2.js")];
const APX = require(DIR + "/appendices.js");
const EPICS = require(DIR + "/epics.js");
const domainsFor = require(DIR + "/domains.js");
const specStatusFor = require(DIR + "/spec-status.js");

const REQ = {}; sections.forEach(s => s.reqs.forEach(r => REQ[r[0]] = { m: r[4], t: r[1], src: r[2], note: r[3], sec: s.code + " " + s.title }));

const MS = ["1", "2", "3", "4", "5"];
function roll(ids) {
  const v = ids.map(i => REQ[i].m);
  const n = v.filter(x => MS.includes(x)).map(Number);
  return { first: n.length ? Math.min(...n) : null, last: n.length ? Math.max(...n) : null, tbd: v.filter(x => x === "TBD").length };
}

const data = {
  epics: EPICS.map(e => ({
    code: e.code, title: e.title, kind: e.kind, journey: e.journey, summary: e.summary, open: e.open,
    features: e.features.map(f => {
      const r = roll(f[2]);
      const dom = domainsFor(f[0]);
      const spec = specStatusFor(f[0], e.code, dom);
      if (!spec) { console.error("no spec status on record for " + f[0]); process.exit(1); }
      return { id: f[0], name: f[1], fr: f[2], intent: f[4], ux: f[5], split: f[6] || null,
               dom, spec,
               first: r.first, last: r.last, tbd: r.tbd };
    }),
  })),
  req: REQ,
};

const MSNAME = { 1: "Demo", 2: "Usability rehearsal", 3: "Submission must", 4: "Clinical high", 5: "Future development" };
const KIND = { app: "Application", backend: "Backend / algorithm", content: "Content", process: "Process" };
const DOMAINS = require(DIR + "/domains.js").ORDER;
const SPECORDER = require(DIR + "/spec-status.js").ORDER;
const READINESS = require(DIR + "/spec-status.js").READINESS;

const html = `<!DOCTYPE html>
<meta charset="utf-8">
<title>QACR Epic and Feature Board</title>
<style>
:root{color-scheme:light;--ink:#16202e;--mut:#6b7789;--line:#dde3ec;--bg:#f6f8fb;--card:#fff;--acc:#1f3864;
--m1:#c6553f;--m2:#b07a1e;--m3:#1f3864;--m4:#5a739b;--m5:#6e7480;--tbd:#8a2f2f;--def:#8a6d3b}
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}
header{background:var(--card);border-bottom:1px solid var(--line);padding:18px 26px 0;position:sticky;top:0;z-index:20}
h1{margin:0;font-size:19px;letter-spacing:-.2px}
h1 span{color:var(--mut);font-weight:400;font-size:14px;margin-left:10px}
.bar{display:flex;gap:20px;align-items:flex-end;flex-wrap:wrap;padding:14px 0 0}
.grp{display:flex;flex-direction:column;gap:5px}
.grp label{font-size:10px;text-transform:uppercase;letter-spacing:.7px;color:var(--mut);font-weight:600}
.chips{display:flex;gap:5px}
.chip{border:1px solid var(--line);background:#fff;border-radius:14px;padding:4px 11px;font-size:12px;cursor:pointer;color:var(--mut);white-space:nowrap;font-weight:500}
.chip.on{background:var(--acc);border-color:var(--acc);color:#fff}
.chip.m1.on{background:var(--m1);border-color:var(--m1)}.chip.m2.on{background:var(--m2);border-color:var(--m2)}
.chip.m4.on{background:var(--m4);border-color:var(--m4)}.chip.m5.on{background:var(--m5);border-color:var(--m5)}.chip.tbd.on{background:var(--tbd);border-color:var(--tbd)}
.chip.def.on{background:var(--def);border-color:var(--def)}
input[type=search]{border:1px solid var(--line);border-radius:6px;padding:6px 10px;font-size:13px;width:230px;font-family:inherit}
.tabs{display:flex;gap:0;margin:16px 0 0;border-bottom:1px solid var(--line)}
.tab{padding:8px 16px;font-size:13px;cursor:pointer;color:var(--mut);border-bottom:2px solid transparent;font-weight:500}
.tab.on{color:var(--acc);border-bottom-color:var(--acc);font-weight:600}
main{padding:22px 26px 90px}
.epic{background:var(--card);border:1px solid var(--line);border-radius:9px;margin-bottom:16px;overflow:hidden}
.eh{padding:14px 18px;border-bottom:1px solid var(--line);cursor:pointer;display:flex;gap:12px;align-items:baseline}
.eh:hover{background:#fbfcfe}
.ec{font-weight:700;color:var(--acc);font-size:13px;min-width:34px}
.et{font-weight:600;font-size:15px;flex:1}
.meta{font-size:11px;color:var(--mut)}
.esum{padding:0 18px 12px;font-size:12.5px;color:var(--mut);max-width:96ch}
.feats{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:10px;padding:12px 18px 18px}
.f{border:1px solid var(--line);border-radius:7px;padding:11px 12px;background:#fff}
.f.dim{opacity:.28}
.fh{display:flex;gap:8px;align-items:center;margin-bottom:6px}
.fid{font-weight:700;font-size:11px;color:var(--mut);font-variant-numeric:tabular-nums}
.badge{font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;color:#fff;letter-spacing:.3px}
.b1{background:var(--m1)}.b2{background:var(--m2)}.b3{background:var(--m3)}.b4{background:var(--m4)}.b5{background:var(--m5)}
.btbd{background:var(--tbd)}.bdef{background:var(--def)}
.dm{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:5px}
.dm span{font-size:9.5px;font-weight:700;letter-spacing:.4px;padding:1px 6px;border-radius:9px;background:#eef2f8;color:#3d4b60}
.dm .iOS{background:#e6eef6;color:#2b5878}.dm .Android{background:#e4f0ea;color:#245c44}
.dm .Backend{background:#eee7f6;color:#523a7a}.dm .Algo{background:#f7ece2;color:#7a4623}
.dm .Content{background:#f7f0e0;color:#7a6224}.dm .Process{background:#eef0f3;color:#535e6d}
.fn{font-weight:600;font-size:13.5px;margin-bottom:5px}
.fi{font-size:12px;color:#3c4859;margin-bottom:7px}
.sp{font-size:11.5px;color:#3c4859;margin:0 0 7px;display:grid;grid-template-columns:auto 1fr;gap:2px 6px}
.sp b{font-weight:700;white-space:nowrap}
.spm1{color:var(--m1)}.spm2{color:var(--m2)}.spm3{color:var(--m3)}.spm4{color:var(--m4)}.sptbd{color:var(--tbd)}.spdef{color:var(--def)}
.fux{font-size:11.5px;color:var(--mut);border-left:2px solid var(--line);padding-left:8px;margin-bottom:8px;font-style:italic}
.ids{display:flex;flex-wrap:wrap;gap:3px}
.id{font-size:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#eef2f8;border-radius:3px;padding:2px 5px;cursor:pointer;color:#3d4b60}
.id:hover{background:var(--acc);color:#fff}
.id.m5{background:#eceff3;color:#5a6674;font-style:italic}
.open{padding:0 18px 16px;font-size:11.5px;color:var(--tbd)}
.open b{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut);margin-bottom:4px}
.open div{margin:2px 0}
#panel{position:fixed;right:0;top:0;bottom:0;width:430px;background:#fff;border-left:1px solid var(--line);box-shadow:-8px 0 30px rgba(20,30,50,.10);padding:22px 24px;overflow:auto;transform:translateX(100%);transition:transform .18s;z-index:40}
#panel.on{transform:none}
#panel .x{position:absolute;right:16px;top:14px;cursor:pointer;color:var(--mut);font-size:20px;line-height:1}
#panel h3{margin:0 0 3px;font-size:15px;color:var(--acc)}
#panel .k{font-size:10px;text-transform:uppercase;letter-spacing:.7px;color:var(--mut);margin:16px 0 3px;font-weight:600}
#panel p{margin:0;font-size:13px}
.stats{display:flex;gap:0;background:var(--card);border:1px solid var(--line);border-radius:9px;overflow:hidden;margin-bottom:18px}
.st{flex:1;padding:12px 16px;border-right:1px solid var(--line)}
.st:last-child{border:0}
.st b{display:block;font-size:22px;font-weight:700;letter-spacing:-.5px}
.st span{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
.empty{color:var(--mut);font-size:13px;padding:30px 0;text-align:center}
.note{font-size:11.5px;color:var(--mut);margin:-6px 0 16px}
.sb{font-size:9.5px;font-weight:800;letter-spacing:.4px;padding:2px 7px;border-radius:4px;text-transform:uppercase}
.sNew{background:#fde8e4;color:#a3341c}.sChanged{background:#fdf0dc;color:#8a5d10}
.sUnchanged{background:#e3f1e8;color:#1f5c3a}.sNospec{background:#eceff3;color:#5a6674}
.sn{font-size:11.5px;border-radius:6px;padding:7px 9px;margin-bottom:7px;background:#f7f9fc;border:1px solid #e7ecf3}
.sn.wait{background:#fdf6ee;border-color:#f0e0c9}
.sn.start{background:#f1f8f3;border-color:#d9eadf}
.sn.other{background:#f5f6f8;border-color:#e5e8ed}
.sn .rl{display:block;font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px}
.sn.wait .rl{color:#8a5d10}.sn.start .rl{color:#1f5c3a}.sn.other .rl{color:#5a6674}
.sn .dv{display:block;margin-top:4px;font-size:10.5px;color:#8a5d10;font-style:italic}
.sn .dc{display:block;margin-top:4px;font-size:10.5px;color:var(--mut);font-family:ui-monospace,Menlo,monospace}
</style>
<header>
<h1>QACR Mobile Application — Epic and Feature Board<span>QACR-APP-EPIC-01 Rev ${V.EPIC} · derived from QACR-APP-FR-01 Rev ${V.FR} · spec triage QACR-APP-SPEC-00</span></h1>
<div class="bar">
  <div class="grp"><label>Milestone</label><div class="chips" id="ms"></div></div>
  <div class="grp"><label>Kind of work</label><div class="chips" id="kd"></div></div>
  <div class="grp"><label>Domain</label><div class="chips" id="dm"></div></div>
  <div class="grp"><label>Spec status</label><div class="chips" id="sp"></div></div>
  <div class="grp"><label>Ready to work</label><div class="chips" id="rd"></div></div>
  <div class="grp"><label>Find</label><input type="search" id="q" placeholder="feature, requirement id, word…"></div>
  <div class="grp"><label>&nbsp;</label><div class="chips"><button class="chip" id="reset">Reset</button></div></div>
</div>
<div class="tabs"><div class="tab on" data-v="epic">By epic</div><div class="tab" data-v="ms">By milestone</div><div class="tab" data-v="rd">By what you can start</div></div>
</header>
<main><div class="stats" id="stats"></div><div class="note" id="note"></div><div id="body"></div></main>
<div id="panel"><span class="x" onclick="closeP()">×</span><div id="pc"></div></div>
<script>
const D=${JSON.stringify(data)};
const MSNAME=${JSON.stringify(MSNAME)}, KIND=${JSON.stringify(KIND)}, DOMAINS=${JSON.stringify(DOMAINS)};
const SPECORDER=${JSON.stringify(SPECORDER)}, READINESS=${JSON.stringify(READINESS)};
const state={ms:new Set(),kd:new Set(),dm:new Set(),sp:new Set(),rd:new Set(),q:"",view:"epic"};

function bcls(f){ if(f.first) return "b"+f.first; return "btbd"; }
function blab(f){ if(!f.first) return "TBD";
  return "M"+f.first+(f.last!==f.first?"–M"+f.last:"")+(f.tbd?" +TBD":""); }
function keys(f){ const k=[]; if(f.first){for(let i=f.first;i<=f.last;i++)k.push(String(i));} if(f.tbd)k.push("TBD"); return k; }

function match(f,e){
  if(state.kd.size&&!state.kd.has(e.kind))return false;
  if(state.dm.size&&!(f.dom||[]).some(d=>state.dm.has(d)))return false;
  if(state.ms.size&&!keys(f).some(k=>state.ms.has(k)))return false;
  if(state.sp.size&&!state.sp.has(f.spec.status))return false;
  if(state.rd.size&&!state.rd.has(f.spec.readiness))return false;
  if(state.q){const q=state.q.toLowerCase();
    const hay=[f.id,f.name,f.intent,f.ux,...(f.dom||[]),...f.fr,e.code,e.title,
               f.spec.status,f.spec.note||"",f.spec.doc||""].join(" ").toLowerCase();
    const rt=f.fr.map(i=>D.req[i].t).join(" ").toLowerCase();
    if(!hay.includes(q)&&!rt.includes(q))return false;}
  return true;
}

function fcard(f,e){
  const ids=f.fr.map(i=>'<span class="id'+(D.req[i].m==="5"?' m5':'')+'" onclick="showR(\\''+i+'\\')">'+i.replace(/^FR-/,'')+'</span>').join("");
  const sp = f.split ? '<div class="sp">'+f.split.map(x=>{
      const k=x[0].toLowerCase().replace('m','m').replace(/\s/g,'');
      const cls = x[0]==='TBD'?'sptbd':(x[0]==='Deferred'?'spdef':'sp'+x[0].toLowerCase());
      return '<b class="'+cls+'">'+x[0]+'</b><span>'+x[1]+'</span>';}).join('')+'</div>' : '';
  const dm = (f.dom&&f.dom.length) ? '<div class="dm">'+f.dom.map(d=>'<span class="'+d+'">'+d+'</span>').join('')+'</div>' : '';
  const S=f.spec;
  const scls='s'+S.status.replace(/\s/g,'');
  const doc = S.doc ? ('Spec: QACR-APP-'+S.doc+' — '+S.stateLabel) : 'No spec document is coming';
  const sn = '<div class="sn '+S.readiness+'"><span class="rl">'+READINESS[S.readiness]+'</span>'
           + (S.note||'')
           + (S.src==='derived'?'<span class="dv">Read off the requirements, not confirmed by product.</span>':'')
           + '<span class="dc">'+doc+'</span></div>';
  return '<div class="f"><div class="fh"><span class="fid">'+f.id+'</span><span class="badge '+bcls(f)+'">'+blab(f)+'</span>'
   +'<span class="sb '+scls+'">'+S.status+'</span></div>'
   +dm+'<div class="fn">'+f.name+'</div><div class="fi">'+f.intent+'</div>'+sn+sp
   +(f.ux?'<div class="fux">'+f.ux+'</div>':'')+'<div class="ids">'+(ids||'—')+'</div></div>';
}

function cnt(p){let n=0;D.epics.forEach(e=>e.features.forEach(f=>{if(p(f))n++;}));return n;}
function render(){
  let nf=0,nr=0;
  const body=document.getElementById("body");
  if(state.view==="epic"){
    body.innerHTML=D.epics.map(e=>{
      const fs=e.features.filter(f=>match(f,e));
      if(!fs.length)return "";
      nf+=fs.length; fs.forEach(f=>nr+=f.fr.length);
      const rr=e.features.flatMap(f=>f.fr);
      const ms=rr.map(i=>D.req[i].m).filter(m=>m!=="TBD").map(Number);
      const span=ms.length?("M"+Math.min(...ms)+(Math.max(...ms)!==Math.min(...ms)?"–M"+Math.max(...ms):"")):"deferred";
      return '<div class="epic"><div class="eh"><span class="ec">'+e.code+'</span><span class="et">'+e.title+'</span>'
        +'<span class="meta">'+KIND[e.kind]+' · '+span+' · '+rr.length+' requirements · '+rr.filter(i=>D.req[i].m==="5").length+' future development</span></div>'
        +'<div class="esum">'+e.summary+'<br><span style="color:#93a0b2">Journey: '+e.journey+'</span></div>'
        +'<div class="feats">'+fs.map(f=>fcard(f,e)).join("")+'</div>'
        +(e.open.length?'<div class="open"><b>Open items bearing on this epic</b>'+e.open.map(o=>'<div>· '+o+'</div>').join("")+'</div>':'')
        +'</div>';
    }).join("")||'<div class="empty">Nothing matches those filters.</div>';
  } else if(state.view==="ms"){
    const groups=[["1"],["2"],["3"],["4"],["5"],["TBD"]];
    body.innerHTML=groups.map(([g])=>{
      const rows=[];
      D.epics.forEach(e=>e.features.forEach(f=>{
        if(!match(f,e))return;
        const first=f.first?String(f.first):"TBD";
        if(first!==g)return;
        rows.push({f,e});
      }));
      if(!rows.length)return "";
      nf+=rows.length; rows.forEach(r=>nr+=r.f.fr.length);
      const title=g==="TBD"?"Priority undecided":"Milestone "+g+" — "+MSNAME[g];
      return '<div class="epic"><div class="eh"><span class="ec">'+g+'</span><span class="et">'+title+'</span>'
        +'<span class="meta">'+rows.length+' features first needed here</span></div>'
        +'<div class="feats">'+rows.map(r=>fcard(r.f,r.e).replace('<div class="fn">','<div class="fn"><span style="color:#93a0b2;font-weight:600;font-size:11px">'+r.e.code+' </span>')).join("")+'</div></div>';
    }).join("")||'<div class="empty">Nothing matches those filters.</div>';
  } else {
    const order=["start","wait","other"];
    const blurb={start:"Nothing is coming that changes these, or what is coming only records what already exists. Build them from the existing application.",
                 wait:"A spec is being written. Starting these before it lands risks building the wrong thing.",
                 other:"Not application code — content, process or algorithm work."};
    body.innerHTML=order.map(g=>{
      const rows=[];
      D.epics.forEach(e=>e.features.forEach(f=>{ if(match(f,e)&&f.spec.readiness===g) rows.push({f,e}); }));
      if(!rows.length)return "";
      nf+=rows.length; rows.forEach(r=>nr+=r.f.fr.length);
      rows.sort((a,b)=>(a.f.first||99)-(b.f.first||99)||a.f.id.localeCompare(b.f.id));
      const by={}; rows.forEach(r=>by[r.f.spec.status]=(by[r.f.spec.status]||0)+1);
      const mix=SPECORDER.filter(k=>by[k]).map(k=>by[k]+" "+k).join(" · ");
      return '<div class="epic"><div class="eh"><span class="ec">'+rows.length+'</span><span class="et">'+READINESS[g]+'</span>'
        +'<span class="meta">'+mix+'</span></div>'
        +'<div class="esum">'+blurb[g]+'</div>'
        +'<div class="feats">'+rows.map(r=>fcard(r.f,r.e).replace('<div class="fn">','<div class="fn"><span style="color:#93a0b2;font-weight:600;font-size:11px">'+r.e.code+' </span>')).join("")+'</div></div>';
    }).join("")||'<div class="empty">Nothing matches those filters.</div>';
  }
  document.getElementById("stats").innerHTML=
    '<div class="st"><b>'+nf+'</b><span>features shown</span></div>'
   +'<div class="st"><b>'+nr+'</b><span>requirements</span></div>'
   +'<div class="st"><b>'+D.epics.length+'</b><span>epics</span></div>'
   +'<div class="st"><b>'+cnt(f=>f.spec.readiness==="start")+'</b><span>can start now</span></div>'
   +'<div class="st"><b>'+cnt(f=>f.spec.readiness==="wait")+'</b><span>waiting on a spec</span></div>'
   +'<div class="st"><b>'+cnt(f=>f.spec.readiness==="other")+'</b><span>not app code</span></div>'
   +'<div class="st"><b>'+Object.values(D.req).filter(r=>r.m==="5").length+'</b><span>future development</span></div>';
  document.getElementById("note").innerHTML=
    "Milestones are derived from the priority of each requirement in QACR-APP-FR-01 Rev ${V.FR} and cannot be edited here. "
   +"Milestone 1 is mid-October 2026, 2 is early December, 3 and 4 are both early January 2027. A range means the feature is first needed at the earlier milestone and not complete until the later one. Click any requirement identifier to read it."
   +"<br><br><b>Spec status</b> says how much writing a spec needs, not whether the feature is in scope — milestone carries scope. "
   +"<b>Unchanged</b> means the behaviour is a recreation of Minuteful Kidney and the spec will record it rather than redesign it, so the work can start now. "
   +"<b>New</b> and <b>Changed</b> are waiting on a spec. <b>No spec</b> means nothing is coming at all: either the requirements are already the specification, or the work is content, process or algorithm."
   +"<br>Notes in each card are the product manager's own words except where marked as read off the requirements, which means they still need confirming.";
}

function showR(id){const r=D.req[id];
  document.getElementById("pc").innerHTML='<h3>'+id+'</h3><div class="meta">Milestone '+r.m+' · '+r.sec+'</div>'
   +'<div class="k">Requirement</div><p>'+r.t+'</p><div class="k">Traceability</div><p>'+(r.src||"—")+'</p>'
   +'<div class="k">Owned by</div><p>'+own(id)+'</p>';
  document.getElementById("panel").classList.add("on");}
function own(id){for(const e of D.epics)for(const f of e.features)
  if(f.fr.includes(id))return f.id+" "+f.name+" — "+e.code+" "+e.title; return "—";}
function closeP(){document.getElementById("panel").classList.remove("on");}

function chips(el,items,set){
  document.getElementById(el).innerHTML=items.map(i=>'<span class="chip '+(i.c||"")+'" data-k="'+i.k+'">'+i.l+'</span>').join("");
  document.getElementById(el).onclick=ev=>{const c=ev.target.closest(".chip"); if(!c)return;
    const k=c.dataset.k; set.has(k)?set.delete(k):set.add(k); c.classList.toggle("on"); render();};
}
chips("ms",[{k:"1",l:"M1 Demo",c:"m1"},{k:"2",l:"M2 Usability",c:"m2"},{k:"3",l:"M3 Must",c:"m3"},
            {k:"4",l:"M4 High",c:"m4"},{k:"5",l:"M5 Future",c:"m5"},{k:"TBD",l:"TBD",c:"tbd"}],state.ms);
chips("kd",Object.entries(KIND).map(([k,l])=>({k,l})),state.kd);
chips("dm",DOMAINS.map(d=>({k:d,l:d})),state.dm);
chips("sp",SPECORDER.map(k=>({k,l:k})),state.sp);
chips("rd",Object.entries(READINESS).map(([k,l])=>({k,l})),state.rd);
document.getElementById("q").oninput=e=>{state.q=e.target.value;render();};
document.getElementById("reset").onclick=()=>{state.ms.clear();state.kd.clear();state.dm.clear();state.sp.clear();state.rd.clear();state.q="";
  document.getElementById("q").value="";document.querySelectorAll(".chip.on").forEach(c=>c.classList.remove("on"));render();};
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));t.classList.add("on");
  state.view=t.dataset.v;render();});
document.onkeydown=e=>{if(e.key==="Escape")closeP();};
render();
</script>
`;
fs.writeFileSync(OUT, html);
console.log("wrote " + OUT + "  " + html.length + " bytes");
