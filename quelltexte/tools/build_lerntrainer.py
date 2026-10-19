# -*- coding: utf-8 -*-
"""Build the standalone HTML learning trainer from hmbsg.json + erklaerungen.json.

Usage: python3 build_lerntrainer.py [out.html]
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "HmbSG - Lerntrainer.html"

data = json.loads((BASE / "hmbsg.json").read_text(encoding="utf-8"))
erkl = json.loads((BASE / "erklaerungen.json").read_text(encoding="utf-8"))
ORD = ["Erster", "Zweiter", "Dritter", "Vierter", "Fünfter", "Sechster", "Siebter", "Achter", "Neunter"]


def split_fall(t: str):
    sents = re.split(r"(?<=[.!?])\s+", t.strip())
    for i, s in enumerate(sents):
        if i > 0 and re.search(r"Paragraf|Maßstab|Nach |Lösung|Das ist|Das wäre|Nach dem", s):
            return " ".join(sents[:i]), " ".join(sents[i:])
    return sents[0], " ".join(sents[1:])


paras, teile = [], []
for ti, t in enumerate(data["teile"]):
    teil = {"n": ti + 1, "roman": t["roman"], "title": t["title"], "abschnitte": []}
    for si, s in enumerate(t["abschnitte"]):
        sec = {"title": s["title"], "ord": ORD[si] if s["title"] else "", "ids": []}
        for p in s["paragraphen"]:
            aufgehoben = p["title"].strip("() ") == "aufgehoben"
            e = erkl.get(p["id"], {})
            fall = e.get("fall", "")
            sit, loes = split_fall(fall) if fall else ("", "")
            paras.append({
                "id": p["id"], "label": "§ " + re.sub(r"(\d+)([a-z])", r"\1 \2", p["id"]), "title": p["title"],
                "teil": ti + 1, "abschnitt": s["title"], "aufgehoben": aufgehoben,
                "abs": [{"nr": a["nr"], "t": a["text"]} for a in p["absaetze"]],
                "kurz": re.sub(r"^Kurz gesagt:\s*", "", e.get("alltag", "")), "fallSit": sit, "fallLoes": loes,
            })
            sec["ids"].append(p["id"])
        teil["abschnitte"].append(sec)
    teile.append(teil)

audio = {}
for cj in sorted((BASE / "audio").glob("HmbSG *.chapters.json")):
    c = json.loads(cj.read_text(encoding="utf-8"))
    if c.get("teil"):
        audio[str(c["teil"])] = {"file": c["file"], "duration": c["duration"], "chapters": c["chapters"]}
wer = json.loads((BASE / "zustaendigkeit.json").read_text(encoding="utf-8"))
for i, it in enumerate(wer["items"]):
    it["id"] = "w%d" % i
eo = json.loads((BASE / "massnahmen.json").read_text(encoding="utf-8"))
for i, it in enumerate(eo["items"]):
    it["id"] = "e%d" % i
VIDEOS = [
    {"id": "schulhaus", "file": "video/schulhaus.mp4", "poster": "video/schulhaus.jpg", "title": "Das Gesetz als Schulhaus", "dur": "2:08",
     "sub": "Die neun Teile als Stockwerke, dazu ein Merksatz für die Prüfung."},
    {"id": "treppe49", "file": "video/treppe-49.mp4", "poster": "video/treppe-49.jpg", "title": "§ 49: Die Treppe der Maßnahmen", "dur": "1:42",
     "sub": "Erziehungs- und Ordnungsmaßnahmen, wer entscheidet, vier Regeln, der Eilfall."},
]
videos = [v for v in VIDEOS if (BASE / v["file"]).exists()]
payload = json.dumps({"teile": teile, "paras": paras, "stand": data["stand"], "audio": audio, "wer": wer, "eo": eo, "videos": videos}, ensure_ascii=False)

HTML = r'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Schulrecht HH">
<meta name="theme-color" content="#1f4e8c">
<meta name="description" content="Hamburgisches Schulgesetz zum Hören und Üben: Wortlaut, Kurzfassungen, Fälle und Hörbuch für Lehrkräfte im Vorbereitungsdienst.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="icon" href="icon-192.png">
<title>Schulrecht Hamburg: Lerntrainer zum Schulgesetz</title>
<style>
  :root{--bg:#f3f1ec;--card:#fff;--text:#1d1f24;--muted:#646a75;--line:#dcd8cf;--accent:#1f4e8c;--accent-soft:#e4ecf8;
        --law:#3b3f4a;--ok:#1d7a4f;--ok-soft:#e2f3ea;--warn:#b2461c;--warn-soft:#fbeae2;--gold:#8a6a1f;--gold-soft:#f6efdc;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  html,body{margin:0;padding:0;}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--text);
       line-height:1.55;font-size:17px;-webkit-text-size-adjust:100%;padding-bottom:env(safe-area-inset-bottom);}
  .wrap{max-width:820px;margin:0 auto;padding:12px 12px 70px;}
  h1{font-size:1.25rem;margin:4px 0 0;letter-spacing:.2px;}
  .sub{color:var(--muted);font-size:.85rem;margin:0 0 8px;}
  .panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:10px 0;box-shadow:0 1px 2px rgba(0,0,0,.04);}
  .row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}
  select,button,input{font-size:16px;font-family:inherit;}
  select{padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--text);min-height:42px;max-width:100%;}
  .check{display:flex;align-items:center;gap:6px;font-size:.9rem;cursor:pointer;user-select:none;}
  .check input{width:20px;height:20px;}
  .tabs{display:flex;gap:6px;margin:10px 0 0;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:2px;}
  .tab{flex:0 0 auto;padding:9px 12px;border:1px solid var(--line);background:#fff;border-radius:10px;cursor:pointer;font-weight:600;
       color:var(--muted);font-size:.9rem;touch-action:manipulation;white-space:nowrap;}
  .tab.active{background:var(--accent);border-color:var(--accent);color:#fff;}
  .btn{padding:10px 14px;border:1px solid var(--line);background:#fff;border-radius:10px;cursor:pointer;font-weight:600;color:var(--text);
       touch-action:manipulation;min-height:44px;}
  .btn:active{transform:translateY(1px);}
  .btn.primary{background:var(--accent);border-color:var(--accent);color:#fff;}
  .btn.ok{background:var(--ok);border-color:var(--ok);color:#fff;}
  .btn.warn{background:var(--warn);border-color:var(--warn);color:#fff;}
  .btn.ghost{background:transparent;}
  .btn.wide{width:100%;}
  .btn.small{padding:6px 10px;min-height:36px;font-size:.85rem;}
  .bar{height:10px;background:#e4e1da;border-radius:8px;overflow:hidden;margin-top:8px;}
  .bar>span{display:block;height:100%;background:var(--ok);width:0%;transition:width .3s;}
  .meta{display:flex;justify-content:space-between;font-size:.8rem;color:var(--muted);margin-top:4px;}
  .chip{display:inline-block;font-size:.72rem;font-weight:700;color:var(--muted);background:#eceae4;border-radius:20px;padding:2px 10px;margin:0 6px 6px 0;}
  .chip.teil{background:var(--accent-soft);color:var(--accent);}
  .ptitle{font-size:1.15rem;font-weight:700;margin:2px 0 6px;}
  .ptitle .nr{color:var(--accent);margin-right:8px;}
  .law{font-size:.95rem;color:var(--law);}
  .law p{margin:0 0 8px;}
  .law .an{font-weight:700;color:var(--accent);margin-right:4px;}
  .kurz{background:var(--accent-soft);border-left:4px solid var(--accent);padding:10px 12px;border-radius:0 10px 10px 0;margin:10px 0;}
  .kurz b,.fall b{display:block;font-size:.75rem;letter-spacing:.6px;text-transform:uppercase;margin-bottom:4px;}
  .kurz b{color:var(--accent);}
  .fall{background:var(--gold-soft);border-left:4px solid var(--gold);padding:10px 12px;border-radius:0 10px 10px 0;margin:10px 0;}
  .fall b{color:var(--gold);}
  .hidden{display:none !important;}
  .cover{background:#f3f1ec;border:1px dashed var(--line);border-radius:10px;padding:14px;text-align:center;color:var(--muted);}
  .navbar{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;}
  .pos{font-size:.9rem;color:var(--muted);font-variant-numeric:tabular-nums;}
  .dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#c9c5bc;margin-left:6px;vertical-align:middle;}
  .dot.sure{background:var(--ok);} .dot.weak{background:var(--warn);}
  .ratebtns{display:flex;gap:10px;margin-top:12px;} .ratebtns .btn{flex:1;}
  details{margin:8px 0;} summary{cursor:pointer;font-weight:600;color:var(--accent);}
  .opts{display:grid;grid-template-columns:1fr;gap:8px;margin-top:10px;}
  .opt{padding:11px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;cursor:pointer;font-weight:600;text-align:left;font-size:.98rem;touch-action:manipulation;min-height:44px;}
  .opt.right{background:var(--ok-soft);border-color:var(--ok);color:var(--ok);}
  .opt.wrong{background:var(--warn-soft);border-color:var(--warn);color:var(--warn);}
  .mask{display:inline-block;background:#dcd8cf;color:transparent;border-radius:4px;padding:0 4px;}
  .tree h3{margin:12px 0 4px;font-size:1rem;}
  .tree .sec{margin:4px 0 2px 8px;font-weight:600;color:var(--muted);font-size:.9rem;}
  .tree a{display:block;padding:5px 8px 5px 18px;color:var(--text);text-decoration:none;border-radius:6px;font-size:.92rem;}
  .tree a:active{background:var(--accent-soft);}
  .tree a .nr{color:var(--accent);font-weight:700;margin-right:6px;}
  .tree a.off{color:#aaa;}
  .timer{font-variant-numeric:tabular-nums;font-weight:700;color:var(--gold);}
  audio{width:100%;margin:6px 0;}
  .chap{display:flex;gap:8px;align-items:baseline;padding:7px 8px;border-radius:8px;cursor:pointer;touch-action:manipulation;}
  .chap:active{background:var(--accent-soft);} .chap.now{background:var(--accent-soft);}
  .chap .t{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.85rem;min-width:46px;}
  .chap .nr{color:var(--accent);font-weight:700;}
  .live .kurz.now,.live .fall.now{box-shadow:0 0 0 2px var(--accent);} .live .law.now{background:#f6f5f1;border-radius:8px;padding:6px;}
  .speed .btn{min-height:36px;padding:6px 10px;font-size:.85rem;} .speed .btn.on{background:var(--accent);color:#fff;border-color:var(--accent);}
  .teilbtn{display:block;width:100%;text-align:left;margin:6px 0 2px;}
  .offl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:.8rem;color:var(--muted);margin:0 0 10px 6px;}
  .offl .btn{min-height:32px;padding:4px 10px;font-size:.8rem;}
  .offl .ok{color:var(--ok);font-weight:700;}
  .pbar{flex:1 1 80px;height:6px;background:#e4e1da;border-radius:4px;overflow:hidden;min-width:60px;} .pbar>span{display:block;height:100%;background:var(--accent);width:0%;}
  .playlink{font-size:.8rem;color:var(--accent);cursor:pointer;margin-left:8px;font-weight:600;touch-action:manipulation;}
  .foot{color:var(--muted);font-size:.78rem;text-align:center;margin-top:20px;}
  .vcard{border:1px solid var(--line);border-radius:12px;padding:10px;background:#fbfaf7;margin:10px 0;}
  .vcard video{width:100%;border-radius:8px;background:#000;display:block;aspect-ratio:16/9;}
  .vhead{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;}
  .vbadge{background:var(--accent);color:#fff;font-size:.72rem;font-weight:700;border-radius:20px;padding:2px 9px;}
  .vdur{color:var(--muted);font-size:.8rem;font-variant-numeric:tabular-nums;}
  details.vdet summary{list-style:none;} details.vdet summary::-webkit-details-marker{display:none;}
  .house{display:flex;gap:16px;align-items:center;flex-wrap:wrap;}
  .house svg{flex:0 0 auto;} .house .hfl{cursor:pointer;}
  .house .hfill{transition:width .9s cubic-bezier(.2,.8,.2,1);}
  .hstat{flex:1 1 200px;font-size:.92rem;} .hstat b{font-size:1.4rem;color:var(--ok);}
  .streak{display:inline-block;margin-left:8px;font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:6px;padding:0 7px;font-size:.78rem;}
  .toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%) translateY(20px);background:#1d1f24;color:#fff;
         padding:10px 18px;border-radius:24px;font-weight:700;font-size:.95rem;opacity:0;transition:opacity .25s,transform .25s;z-index:50;pointer-events:none;max-width:90vw;text-align:center;}
  .toast.on{opacity:1;transform:translateX(-50%) translateY(0);}
  .opt.right,.opt.wrong{transition:background .25s,border-color .25s,color .25s;}
  .bar.bump>span{animation:bump .5s;} @keyframes bump{50%{filter:brightness(1.35);}}
  @media (prefers-reduced-motion: reduce){ .bar.bump>span{animation:none;} .house .hfill{transition:none;} }
  @media (max-width:480px){ body{font-size:16px;} }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Schulrecht Hamburg <span style="font-weight:400;color:var(--muted)">· Lerntrainer</span></h1>
    <p class="sub">Hamburgisches Schulgesetz zum Hören und Üben: Wortlaut, Kurzfassung, Fälle, Hörbuch. Fortschritt bleibt auf diesem Gerät. <a href="info.html" style="color:var(--accent)">Info und Anleitung</a></p>
  </header>
  <div class="panel">
    <div class="row">
      <select id="teilSel"></select>
      <label class="check"><input type="checkbox" id="weakOnly"> nur Unsichere</label>
      <button class="btn small" id="randomBtn">Zufall ziehen</button>
    </div>
    <div class="tabs">
      <div class="tab active" data-mode="lesen">Lesen</div>
      <div class="tab" data-mode="recall">Paragraf-Recall</div>
      <div class="tab" data-mode="wer">Wer entscheidet?</div>
      <div class="tab" data-mode="eo">E oder O?</div>
      <div class="tab" data-mode="faelle">Fälle</div>
      <div class="tab" data-mode="struktur">Struktur</div>
      <div class="tab" data-mode="hoeren">Hören</div>
    </div>
    <div class="bar"><span id="barFill"></span></div>
    <div class="meta"><span id="barText"></span><button class="btn small ghost" id="resetBtn">Fortschritt löschen</button></div>
  </div>
  <div id="view"></div>
  <p class="foot">Quelle: Hamburgisches Schulgesetz, STAND. Kurzfassungen und Fälle sind Lernhilfen, keine Rechtsberatung. Privates Lernprojekt, erstellt mit Claude. <a href="info.html" style="color:var(--muted)">Info</a></p>
</div>
<script id="data" type="application/json">PAYLOAD</script>
<script>
"use strict";
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var TEILE = DATA.teile, PARAS = DATA.paras, AUDIO = DATA.audio || {}, WER = DATA.wer, EO = DATA.eo, VIDEOS = DATA.videos || [];
  var BY = {}; PARAS.forEach(function(p){ BY[p.id] = p; });
  var STORE_KEY = 'hmbsg-trainer-v1';
  var store = loadStore();
  function loadStore(){ try{ return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }catch(e){ return {}; } }
  function saveStore(){ try{ localStorage.setItem(STORE_KEY, JSON.stringify(store)); }catch(e){} }
  if(!store.status) store.status = {};   // id -> 'sure' | 'weak'   (Recall)
  if(!store.fall) store.fall = {};       // id -> 'sure' | 'weak'   (Fälle)
  if(!store.wer) store.wer = {right:0, total:0};
  if(!store.werStatus) store.werStatus = {};   // item id -> 'sure' | 'weak'
  if(!store.eoStatus) store.eoStatus = {};
  if(!store.best) store.best = 0;
  if(!store.pos) store.pos = {};          // teil -> seconds (letzte Hörposition)
  if(!store.speed) store.speed = 1;

  var state = { mode:'lesen', teil:'all', weakOnly:false, idx:0, fallIdx:0, order:null, fallOrder:null, werItem:null, werOrder:null, werIdx:0, eoOrder:null, eoIdx:0, eoDone:false, streak:0, jumpTo:null, seekTo:null, hoerTeil:null };
  function fmt(sec){ sec=Math.max(0,Math.floor(sec)); return Math.floor(sec/60)+':'+('0'+sec%60).slice(-2); }
  function audioStart(id){ var a = AUDIO[String(BY[id].teil)]; if(!a) return null; for(var i=0;i<a.chapters.length;i++){ if(a.chapters[i].id===id && a.chapters[i].kind==='law') return a.chapters[i].start; } return null; }

  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function shuffle(a){ a = a.slice(); for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=a[i]; a[i]=a[j]; a[j]=t; } return a; }
  function teilLabel(n){ var t = TEILE[n-1]; return t.roman+' Teil: '+t.title; }
  function workList(){
    return PARAS.filter(function(p){
      if(p.aufgehoben) return false;
      if(state.teil!=='all' && p.teil!==parseInt(state.teil,10)) return false;
      if(state.weakOnly && store.status[p.id]==='sure') return false;
      return true;
    });
  }
  function fallList(){
    return PARAS.filter(function(p){
      if(!p.fallSit) return false;
      if(state.teil!=='all' && p.teil!==parseInt(state.teil,10)) return false;
      if(state.weakOnly && store.fall[p.id]==='sure') return false;
      return true;
    });
  }
  function lawHtml(p){
    if(p.aufgehoben) return '<div class="law"><p><i>(aufgehoben)</i></p></div>';
    return '<div class="law">'+p.abs.map(function(a){
      return '<p>'+(a.nr?'<span class="an">('+esc(a.nr)+')</span>':'')+esc(a.t)+'</p>';
    }).join('')+'</div>';
  }
  function kurzHtml(p){ return p.kurz ? '<div class="kurz"><b>Kurz gesagt</b>'+esc(p.kurz)+'</div>' : ''; }
  function fallHtml(p){ return p.fallSit ? '<div class="fall"><b>Beispiel</b>'+esc(p.fallSit)+' '+esc(p.fallLoes)+'</div>' : ''; }
  function head(p){
    return '<span class="chip teil">'+esc(TEILE[p.teil-1].roman+' Teil')+'</span>'+(p.abschnitt?'<span class="chip">'+esc(p.abschnitt)+'</span>':'')+
           '<div class="ptitle"><span class="nr">'+esc(p.label)+'</span>'+esc(p.title)+
           (audioStart(p.id)!==null && state.mode!=='hoeren' ? '<span class="playlink" data-play="'+p.id+'">▶ anhören</span>':'')+'</div>';
  }
  // ----- motivation: confetti, toast, streak -----
  function burst(){}
  var toastEl = null, toastT = null;
  function toast(msg){
    if(!toastEl){ toastEl = document.createElement('div'); toastEl.className = 'toast'; document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function(){ toastEl.classList.remove('on'); }, 2000);
  }
  function bumpBar(){ var b = document.querySelector('.bar'); if(!b) return; b.classList.remove('bump'); void b.offsetWidth; b.classList.add('bump'); }
  function answered(right){
    if(right){
      state.streak++; if(state.streak > store.best){ store.best = state.streak; saveStore(); }
      bumpBar();
      if(state.streak % 5 === 0) toast(state.streak+' in Folge richtig');
    } else {
      state.streak = 0;
    }
  }
  function streakHtml(){ return state.streak >= 2 ? '<span class="streak" title="richtige Antworten in Folge">Serie '+state.streak+'</span>' : ''; }
  function teilStats(n){ var ps = PARAS.filter(function(p){ return p.teil===n && !p.aufgehoben; });
    return {sure: ps.filter(function(p){ return store.status[p.id]==='sure'; }).length, total: ps.length}; }

  // ----- videos -----
  function vid(id){ for(var i=0;i<VIDEOS.length;i++){ if(VIDEOS[i].id===id) return VIDEOS[i]; } return null; }
  function videoCard(id, compact){
    var v = vid(id); if(!v) return '';
    return '<div class="vcard"><div class="vhead"><span class="vbadge">▶ Video</span><b>'+esc(v.title)+'</b><span class="vdur">'+esc(v.dur)+'</span></div>'+
      '<video controls playsinline preload="none" poster="'+v.poster+'" src="'+v.file+'"></video>'+
      (compact ? '' : '<div class="sub" style="margin:6px 0 0">'+esc(v.sub)+'</div>')+'<div class="offl" style="margin:8px 0 0" data-voffl="'+id+'"></div></div>';
  }
  function videoDetails(id){
    var v = vid(id); if(!v) return '';
    return '<details class="vdet" style="margin-top:12px"><summary class="playlink" style="margin-left:0">▶ Video: '+esc(v.title)+' ('+esc(v.dur)+')</summary>'+videoCard(id, true)+'</details>';
  }
  function bindVideoRows(){
    Array.prototype.forEach.call(view.querySelectorAll('[data-voffl]'), function(el){
      var v = vid(el.getAttribute('data-voffl')); if(v) renderOfflineGeneric(el, mediaUrl(v.file), 'video/mp4', 'Video offline speichern');
    });
  }

  // ----- Schulhaus-Fortschritt -----
  function houseHtml(){
    var floors = [[1,330,360],[2,300,330],[3,262,300],[4,214,262],[5,154,214],[6,116,154]];
    var W0 = 30, W1 = 250, svg = '<svg width="280" height="372" viewBox="0 0 280 372" role="img" aria-label="Fortschritt pro Teil">';
    var r = [7,8,9].map(teilStats), rs = r.reduce(function(a,b){ return a+b.sure; },0), rt = r.reduce(function(a,b){ return a+b.total; },0);
    svg += '<polygon points="'+(W0-12)+',116 '+(W1+12)+',116 140,40" fill="#fff" stroke="#1d1f24" stroke-width="3" stroke-linejoin="round"/>';
    svg += '<clipPath id="roofc"><polygon points="'+(W0-12)+',116 '+(W1+12)+',116 140,40"/></clipPath>';
    svg += '<rect class="hfill" clip-path="url(#roofc)" x="'+(W0-12)+'" y="40" height="76" width="0" data-w="'+((W1-W0+24)*(rt?rs/rt:0))+'" fill="#1d7a4f" opacity="0.8"/>';
    svg += '<text x="140" y="104" text-anchor="middle" font-size="12" font-weight="700" fill="#1d1f24">T7–9 · '+rs+'/'+rt+'</text>';
    svg += '<g class="hfl" data-teil="7"><polygon points="'+(W0-12)+',116 '+(W1+12)+',116 140,40" fill="transparent"/></g>';
    floors.forEach(function(f){
      var s = teilStats(f[0]), h = f[2]-f[1], ratio = s.total ? s.sure/s.total : 0, done = ratio >= 1;
      svg += '<g class="hfl" data-teil="'+f[0]+'"><rect x="'+W0+'" y="'+f[1]+'" width="'+(W1-W0)+'" height="'+h+'" fill="'+(f[0]===1?'#d6d3cb':'#fff')+'" stroke="#1d1f24" stroke-width="2.5"/>'+
        '<rect class="hfill" x="'+W0+'" y="'+f[1]+'" height="'+h+'" width="0" data-w="'+((W1-W0)*ratio)+'" fill="'+(done?'#d39b22':'#1d7a4f')+'" opacity="0.8"/>'+
        '<text x="'+(W0+8)+'" y="'+(f[1]+h/2+4)+'" font-size="12" font-weight="700" fill="#1d1f24">Teil '+f[0]+'</text>'+
        '<text x="'+(W1-8)+'" y="'+(f[1]+h/2+4)+'" font-size="12" text-anchor="end" fill="#1d1f24">'+(done?'✓ ':'')+s.sure+'/'+s.total+'</text></g>';
    });
    svg += '<line x1="10" x2="270" y1="330" y2="330" stroke="#1d1f24" stroke-width="3"/></svg>';
    var all = PARAS.filter(function(p){ return !p.aufgehoben; }), sure = all.filter(function(p){ return store.status[p.id]==='sure'; }).length;
    var next = null; for(var n=1;n<=9;n++){ var s = teilStats(n); if(s.sure < s.total && (!next || s.total - s.sure < next.left)) next = {n:n, left: s.total - s.sure}; }
    var stat = '<div class="hstat"><div><b>'+sure+'</b> von '+all.length+' Paragrafen sicher</div>'+
      '<div class="sub" style="margin:6px 0">Jedes Stockwerk füllt sich mit den Paragrafen, die im Paragraf-Recall als sicher markiert sind. Vollständige Stockwerke werden gold.</div>'+
      (next ? '<div style="font-size:.9rem">Am nächsten dran: <b style="font-size:1rem;color:var(--accent)">Teil '+next.n+'</b>, noch '+next.left+' bis komplett.</div>' : '<div><b style="color:var(--gold)">Alle Teile vollständig sicher.</b></div>')+
      '<div class="sub" style="margin-top:6px">Stockwerk antippen: diesen Teil üben.</div></div>';
    return '<div class="panel house">'+svg+stat+'</div>';
  }
  function bindHouse(){
    setTimeout(function(){ Array.prototype.forEach.call(view.querySelectorAll('.hfill'), function(r){ r.setAttribute('width', r.getAttribute('data-w')); }); }, 40);
    Array.prototype.forEach.call(view.querySelectorAll('.hfl'), function(g){
      g.onclick = function(){ var n = g.getAttribute('data-teil'); state.teil = n; document.getElementById('teilSel').value = n; state.order = null; state.idx = 0; setMode('recall'); };
    });
  }

  function bindPlayLinks(){
    Array.prototype.forEach.call(view.querySelectorAll('[data-play]'), function(el){
      el.onclick = function(){ var id = el.getAttribute('data-play'); state.hoerTeil = String(BY[id].teil); state.seekTo = audioStart(id); setMode('hoeren'); };
    });
  }
  function updateProgress(){
    var list, sure, label;
    if(state.mode==='hoeren'){ var n=Object.keys(AUDIO).length; document.getElementById('barFill').style.width=Math.round(n/TEILE.length*100)+'%';
      document.getElementById('barText').textContent = n+' / '+TEILE.length+' Teile als Audio vorhanden'; return; }
    if(state.mode==='wer'){ var wl = werList(); var ws = wl.filter(function(it){return store.werStatus[it.id]==='sure';}).length;
      document.getElementById('barFill').style.width=(wl.length?Math.round(ws/wl.length*100):0)+'%';
      document.getElementById('barText').textContent = ws+' / '+wl.length+' Zuständigkeiten sicher ('+store.wer.right+' / '+store.wer.total+' Antworten richtig)'; return; }
    if(state.mode==='eo'){ var el2 = EO.items, es = el2.filter(function(it){return store.eoStatus[it.id]==='sure';}).length;
      document.getElementById('barFill').style.width=Math.round(es/el2.length*100)+'%';
      document.getElementById('barText').textContent = es+' / '+el2.length+' Maßnahmen sicher'; return; }
    if(state.mode==='faelle'){ list = fallList(); sure = list.filter(function(p){return store.fall[p.id]==='sure';}).length; label=' Fälle sicher'; }
    else { list = workList(); sure = list.filter(function(p){return store.status[p.id]==='sure';}).length; label=' Paragrafen sicher'; }
    var pct = list.length? Math.round(sure/list.length*100):0;
    document.getElementById('barFill').style.width = pct+'%';
    document.getElementById('barText').textContent = sure+' / '+list.length+label+' ('+pct+'%)';
  }
  var view = document.getElementById('view');
  function render(){
    if(state.mode==='lesen') renderLesen();
    else if(state.mode==='recall') renderRecall();
    else if(state.mode==='wer') renderWer();
    else if(state.mode==='eo') renderEO();
    else if(state.mode==='faelle') renderFaelle();
    else if(state.mode==='hoeren') renderHoeren();
    else renderStruktur();
    bindPlayLinks();
    bindVideoRows();
    updateProgress();
  }
  function emptyMsg(){ return '<div class="panel cover">Nichts zu zeigen. Filter ändern oder Fortschritt zurücksetzen.</div>'; }

  // ----- LESEN -----
  function renderLesen(){
    var list = PARAS.filter(function(p){ return state.teil==='all' || p.teil===parseInt(state.teil,10); });
    if(state.weakOnly) list = list.filter(function(p){ return store.status[p.id]!=='sure'; });
    if(!list.length){ view.innerHTML = emptyMsg(); return; }
    var html = (state.teil==='all' || state.teil==='1') && !state.weakOnly ? '<div class="panel">'+videoCard('schulhaus', false)+'</div>' : '', lastSec = null, lastTeil = null;
    list.forEach(function(p){
      if(p.teil!==lastTeil){ html += '<h2 style="font-size:1.05rem;margin:16px 4px 4px;color:var(--accent)">'+esc(teilLabel(p.teil))+'</h2>'; lastTeil=p.teil; lastSec=null; }
      if(p.abschnitt && p.abschnitt!==lastSec){ html += '<div class="sec" style="margin:6px 4px;color:var(--muted);font-weight:600">'+esc(p.abschnitt)+'</div>'; lastSec=p.abschnitt; }
      html += '<div class="panel" id="p-'+p.id+'">'+head(p);
      if(!p.aufgehoben){
        html += '<details'+(p.kurz?'':' open')+'><summary>Wortlaut</summary>'+lawHtml(p)+'</details>';
        html += kurzHtml(p) + fallHtml(p);
        if(p.id==='49') html += videoCard('treppe49', true);
      } else html += lawHtml(p);
      html += '</div>';
    });
    view.innerHTML = html;
    if(state.jumpTo){ var el = document.getElementById('p-'+state.jumpTo); if(el){ el.scrollIntoView(); } state.jumpTo = null; }
  }

  // ----- RECALL -----
  function renderRecall(){
    var list = workList();
    if(!list.length){ view.innerHTML = emptyMsg(); return; }
    if(!state.order || state.order.length!==list.length) state.order = shuffle(list.map(function(p){return p.id;}));
    if(state.idx>=list.length) state.idx = 0;
    var p = BY[state.order[state.idx]];
    if(!p || (state.weakOnly && store.status[p.id]==='sure')){ state.order=null; state.idx=0; return renderRecall(); }
    var st = store.status[p.id] || '';
    var html = '<div class="panel"><div class="navbar"><button class="btn" id="rPrev">‹</button>'+
      '<span class="pos">'+(state.idx+1)+' / '+list.length+'<span class="dot '+st+'"></span></span><button class="btn" id="rNext">›</button></div>';
    html += head(p);
    html += '<div id="rCover" class="cover">Was regelt dieser Paragraf? Laut überlegen, dann aufdecken.</div>';
    html += '<div id="rBody" class="hidden">'+kurzHtml(p)+'<details><summary>Wortlaut</summary>'+lawHtml(p)+'</details>'+fallHtml(p)+'</div>';
    html += '<button class="btn primary wide" id="rReveal" style="margin-top:12px">Aufdecken</button>';
    html += '<div class="ratebtns hidden" id="rRate"><button class="btn ok" id="rSure">Sicher ✓</button><button class="btn warn" id="rWeak">Nochmal ↻</button></div></div>';
    view.innerHTML = html;
    document.getElementById('rPrev').onclick = function(){ state.idx=(state.idx-1+list.length)%list.length; renderRecall(); };
    document.getElementById('rNext').onclick = function(){ state.idx=(state.idx+1)%list.length; renderRecall(); };
    document.getElementById('rReveal').onclick = function(){
      document.getElementById('rCover').classList.add('hidden'); document.getElementById('rBody').classList.remove('hidden');
      document.getElementById('rReveal').classList.add('hidden'); document.getElementById('rRate').classList.remove('hidden');
    };
    function rate(v){
      var before = teilStats(p.teil); store.status[p.id]=v; saveStore(); var after = teilStats(p.teil);
      if(v==='sure'){
        if(after.sure===after.total && before.sure<before.total) toast('Teil '+p.teil+' vollständig sicher');
        else toast('Teil '+p.teil+': '+after.sure+' von '+after.total+' sicher');
      }
      state.idx=(state.idx+1)%list.length; render(); bumpBar();
    }
    document.getElementById('rSure').onclick=function(){rate('sure');};
    document.getElementById('rWeak').onclick=function(){rate('weak');};
  }

  // ----- WER ENTSCHEIDET? -----
  function werList(){
    return WER.items.filter(function(it){
      if(state.teil!=='all' && BY[it.p] && BY[it.p].teil!==parseInt(state.teil,10)) return false;
      if(state.weakOnly && store.werStatus[it.id]==='sure') return false;
      return true;
    });
  }
  function renderWer(){
    var list = werList();
    if(!list.length){ view.innerHTML = emptyMsg(); return; }
    if(!state.werOrder || state.werOrder.length!==list.length){ state.werOrder = shuffle(list.map(function(it){return it.id;})); state.werIdx = 0; }
    if(state.werIdx>=list.length) state.werIdx = 0;
    var it = null; for(var i=0;i<WER.items.length;i++){ if(WER.items[i].id===state.werOrder[state.werIdx]) it = WER.items[i]; }
    if(!it){ state.werOrder=null; return renderWer(); }
    if(!state.werItem || state.werItem.it!==it){
      var pool = (it.alt && it.alt.length) ? it.alt.slice() : shuffle(WER.kern.filter(function(k){return k!==it.a;})).slice(0,3);
      state.werItem = { it: it, opts: shuffle([it.a].concat(pool)), done:false };
    }
    var q = state.werItem, p = BY[it.p];
    var html = '<div class="panel"><div class="navbar"><button class="btn" id="wPrev">‹</button><span class="pos">'+(state.werIdx+1)+' / '+list.length+'<span class="dot '+(store.werStatus[it.id]||'')+'"></span>'+streakHtml()+'</span><button class="btn" id="wNext">›</button></div>';
    html += '<div class="fall"><b>Situation</b>'+esc(it.s)+'</div>';
    html += '<div class="ptitle" style="font-size:1rem">Wer entscheidet oder ist zuständig?</div>';
    html += '<div class="opts">'+q.opts.map(function(k){ return '<div class="opt" data-k="'+k+'">'+esc(WER.akteure[k])+'</div>'; }).join('')+'</div>';
    html += '<div id="wAnswer" class="hidden" style="margin-top:10px"></div>';
    html += '<button class="btn primary wide hidden" id="wNextBtn" style="margin-top:12px">Nächste Situation</button></div>';
    view.innerHTML = html;
    function finish(right){
      q.done = true; store.wer.total++; if(right) store.wer.right++; store.werStatus[it.id] = right ? 'sure' : 'weak'; saveStore();
      Array.prototype.forEach.call(view.querySelectorAll('.opt'), function(x){ if(x.getAttribute('data-k')===it.a) x.classList.add('right'); });
      var a = document.getElementById('wAnswer');
      a.innerHTML = '<div class="kurz"><b>'+(right?'Richtig':'Falsch')+'</b>'+esc(it.b)+'</div>' +
        (p ? '<div class="ptitle" style="font-size:1rem"><span class="nr">'+esc(p.label)+'</span>'+esc(p.title)+(audioStart(p.id)!==null?'<span class="playlink" data-play="'+p.id+'">▶ anhören</span>':'')+'</div><details><summary>Wortlaut</summary>'+lawHtml(p)+'</details>' : '');
      a.classList.remove('hidden'); document.getElementById('wNextBtn').classList.remove('hidden'); bindPlayLinks(); updateProgress();
    }
    Array.prototype.forEach.call(view.querySelectorAll('.opt'), function(o){
      o.onclick = function(){ if(q.done) return; var right = o.getAttribute('data-k')===it.a; if(!right) o.classList.add('wrong'); finish(right);
        answered(right); var pos = view.querySelector('.pos'); if(pos){ var sk = pos.querySelector('.streak'); if(sk) sk.remove(); pos.insertAdjacentHTML('beforeend', streakHtml()); } };
    });
    function step(d){ state.werIdx = (state.werIdx + d + list.length) % list.length; state.werItem = null; renderWer(); }
    document.getElementById('wNextBtn').onclick = function(){ step(1); };
    document.getElementById('wNext').onclick = function(){ step(1); };
    document.getElementById('wPrev').onclick = function(){ step(-1); };
  }

  // ----- ERZIEHUNGS- ODER ORDNUNGSMASSNAHME? -----
  function eoList(){ return EO.items.filter(function(it){ return !(state.weakOnly && store.eoStatus[it.id]==='sure'); }); }
  function renderEO(){
    var list = eoList();
    if(!list.length){ view.innerHTML = emptyMsg(); return; }
    if(!state.eoOrder || state.eoOrder.length!==list.length){ state.eoOrder = shuffle(list.map(function(it){return it.id;})); state.eoIdx = 0; }
    if(state.eoIdx>=list.length) state.eoIdx = 0;
    var it = null; EO.items.forEach(function(x){ if(x.id===state.eoOrder[state.eoIdx]) it = x; });
    if(!it){ state.eoOrder=null; return renderEO(); }
    var p = BY['49'];
    var html = '<div class="panel"><div class="navbar"><button class="btn" id="ePrev">‹</button><span class="pos">'+(state.eoIdx+1)+' / '+list.length+'<span class="dot '+(store.eoStatus[it.id]||'')+'"></span>'+streakHtml()+'</span><button class="btn" id="eNext">›</button></div>';
    html += '<p class="sub" style="margin:0 0 6px">Nach § 49: Was ist das?</p><div class="fall" style="font-size:1.05rem"><b>Maßnahme</b>'+esc(it.m)+'</div>';
    html += '<div class="opts">'+['E','O','X'].map(function(k){ return '<div class="opt" data-k="'+k+'">'+esc(EO.koerbe[k])+'</div>'; }).join('')+'</div>';
    html += '<div id="eAnswer" class="hidden" style="margin-top:10px"></div>';
    html += '<button class="btn primary wide hidden" id="eNextBtn" style="margin-top:12px">Nächste Maßnahme</button>'+videoDetails('treppe49')+'</div>';
    view.innerHTML = html;
    var done = false;
    Array.prototype.forEach.call(view.querySelectorAll('.opt'), function(o){
      o.onclick = function(){ if(done) return; done = true; var right = o.getAttribute('data-k')===it.k;
        store.eoStatus[it.id] = right ? 'sure' : 'weak'; saveStore();
        Array.prototype.forEach.call(view.querySelectorAll('.opt'), function(x){ if(x.getAttribute('data-k')===it.k) x.classList.add('right'); else if(x===o) x.classList.add('wrong'); });
        var a = document.getElementById('eAnswer');
        a.innerHTML = '<div class="kurz"><b>'+(right?'Richtig':'Falsch')+'</b>'+esc(it.b)+'</div>' +
          (p ? '<details><summary>Wortlaut § 49</summary>'+lawHtml(p)+'</details>' : '');
        a.classList.remove('hidden'); document.getElementById('eNextBtn').classList.remove('hidden'); updateProgress();
        answered(right); var pos = view.querySelector('.pos'); if(pos){ var sk = pos.querySelector('.streak'); if(sk) sk.remove(); pos.insertAdjacentHTML('beforeend', streakHtml()); } };
    });
    function step(d){ state.eoIdx = (state.eoIdx + d + list.length) % list.length; renderEO(); }
    document.getElementById('eNextBtn').onclick = function(){ step(1); };
    document.getElementById('eNext').onclick = function(){ step(1); };
    document.getElementById('ePrev').onclick = function(){ step(-1); };
  }

  // ----- FÄLLE -----
  var timerHandle = null;
  function renderFaelle(){
    if(timerHandle){ clearInterval(timerHandle); timerHandle=null; }
    var list = fallList();
    if(!list.length){ view.innerHTML = emptyMsg(); return; }
    if(!state.fallOrder || state.fallOrder.length!==list.length) state.fallOrder = shuffle(list.map(function(p){return p.id;}));
    if(state.fallIdx>=list.length) state.fallIdx=0;
    var p = BY[state.fallOrder[state.fallIdx]];
    if(!p || !p.fallSit || (state.weakOnly && store.fall[p.id]==='sure')){ state.fallOrder=null; state.fallIdx=0; return renderFaelle(); }
    var st = store.fall[p.id] || '';
    var html = '<div class="panel"><div class="navbar"><button class="btn" id="fPrev">‹</button>'+
      '<span class="pos">Fall '+(state.fallIdx+1)+' / '+list.length+'<span class="dot '+st+'"></span></span><button class="btn" id="fNext">›</button></div>';
    html += '<div class="fall"><b>Praxissituation</b>'+esc(p.fallSit)+'</div>';
    html += '<p style="color:var(--muted);font-size:.9rem;margin:6px 0">Wie in der Prüfung: Situation rechtlich einordnen, Paragraf nennen, Verfahren und Zuständigkeit erklären. <span class="timer" id="fTimer">5:00</span></p>';
    html += '<div id="fBody" class="hidden"><div class="kurz"><b>Einordnung</b>'+esc(p.fallLoes)+'</div>'+
            '<div class="ptitle"><span class="nr">'+esc(p.label)+'</span>'+esc(p.title)+'</div>'+kurzHtml(p)+'<details><summary>Wortlaut</summary>'+lawHtml(p)+'</details></div>';
    html += '<button class="btn primary wide" id="fReveal" style="margin-top:12px">Lösung zeigen</button>';
    html += '<div class="ratebtns hidden" id="fRate"><button class="btn ok" id="fSure">Konnte ich ✓</button><button class="btn warn" id="fWeak">Nochmal ↻</button></div></div>';
    view.innerHTML = html;
    var secs = 300, tEl = document.getElementById('fTimer');
    timerHandle = setInterval(function(){ secs--; if(secs<0){ clearInterval(timerHandle); timerHandle=null; return; }
      tEl.textContent = Math.floor(secs/60)+':'+('0'+secs%60).slice(-2); }, 1000);
    document.getElementById('fPrev').onclick = function(){ state.fallIdx=(state.fallIdx-1+list.length)%list.length; renderFaelle(); };
    document.getElementById('fNext').onclick = function(){ state.fallIdx=(state.fallIdx+1)%list.length; renderFaelle(); };
    document.getElementById('fReveal').onclick = function(){
      if(timerHandle){ clearInterval(timerHandle); timerHandle=null; }
      document.getElementById('fBody').classList.remove('hidden'); document.getElementById('fReveal').classList.add('hidden');
      document.getElementById('fRate').classList.remove('hidden');
    };
    function rate(v){ store.fall[p.id]=v; saveStore(); state.fallIdx=(state.fallIdx+1)%list.length; render(); }
    document.getElementById('fSure').onclick=function(){rate('sure');};
    document.getElementById('fWeak').onclick=function(){rate('weak');};
  }

  // ----- OFFLINE (Cache API, nur unter https) -----
  var AUDIO_CACHE = 'hmbsg-audio-v1';
  var OFFLINE_OK = (typeof window.caches !== 'undefined') && (location.protocol === 'https:' || location.hostname === 'localhost');
  function mediaUrl(rel){ return new URL(rel, location.href).href; }
  function audioUrl(tn){ return mediaUrl('audio/'+encodeURIComponent(AUDIO[tn].file)); }
  function cachedInfoUrl(url){
    if(!OFFLINE_OK) return Promise.resolve(null);
    return caches.open(AUDIO_CACHE).then(function(c){ return c.match(url); }).then(function(r){
      if(!r) return null; var len = parseInt(r.headers.get('Content-Length')||'0',10); return {size: len}; }).catch(function(){ return null; });
  }
  function downloadUrl(url, type, onProgress){
    return fetch(url).then(function(resp){
      if(!resp.ok) throw new Error('HTTP '+resp.status);
      var total = parseInt(resp.headers.get('Content-Length')||'0',10), loaded = 0, chunks = [], reader = resp.body.getReader();
      function pump(){ return reader.read().then(function(res){ if(res.done) return; chunks.push(res.value); loaded += res.value.length; onProgress(total? loaded/total : 0); return pump(); }); }
      return pump().then(function(){
        var blob = new Blob(chunks, {type:type});
        return caches.open(AUDIO_CACHE).then(function(c){ return c.put(url, new Response(blob, {headers:{'Content-Type':type,'Content-Length':String(blob.size),'Accept-Ranges':'bytes'}})); }).then(function(){ return blob.size; });
      });
    });
  }
  function mb(n){ return (n/1048576).toFixed(0)+' MB'; }
  function renderOfflineGeneric(el, url, type, label){
    if(!OFFLINE_OK){ el.innerHTML=''; return; }
    cachedInfoUrl(url).then(function(info){
      if(info){ el.innerHTML = '<span class="ok">✓ offline gespeichert ('+mb(info.size)+')</span><button class="btn" data-del="1">Löschen</button>'; }
      else { el.innerHTML = '<button class="btn" data-dl="1">'+esc(label)+'</button><span class="pbar hidden"><span></span></span><span class="pct"></span>'; }
      var dl = el.querySelector('[data-dl]'), del = el.querySelector('[data-del]');
      if(dl) dl.onclick = function(){ dl.disabled = true; dl.textContent = 'Lädt …'; var bar = el.querySelector('.pbar'); bar.classList.remove('hidden');
        downloadUrl(url, type, function(f){ bar.firstChild.style.width = Math.round(f*100)+'%'; el.querySelector('.pct').textContent = Math.round(f*100)+' %'; })
          .then(function(){ renderOfflineGeneric(el, url, type, label); }).catch(function(e){ el.innerHTML = '<span style="color:var(--warn)">Download fehlgeschlagen ('+esc(e.message)+'). Später noch einmal versuchen.</span>'; }); };
      if(del) del.onclick = function(){ caches.open(AUDIO_CACHE).then(function(c){ return c.delete(url); }).then(function(){ renderOfflineGeneric(el, url, type, label); }); };
    });
  }
  function renderOfflineRow(tn, el){
    if(!AUDIO[tn]){ el.innerHTML=''; return; }
    renderOfflineGeneric(el, audioUrl(tn), 'audio/mpeg', 'Offline speichern');
  }

  // ----- HÖREN -----
  var audioEl = null;
  function renderHoeren(){
    if(audioEl){ try{ store.pos[audioEl.getAttribute('data-teil')] = audioEl.currentTime; saveStore(); audioEl.pause(); }catch(e){} audioEl = null; }
    var tn = state.hoerTeil || (state.teil!=='all' ? state.teil : null);
    if(!tn || !AUDIO[tn]){
      var html = '<div class="panel"><p class="sub">Hörbuch: ein Teil des Gesetzes pro Datei, zusammen rund fünf Stunden. '+
        (OFFLINE_OK ? 'Mit „Offline speichern“ liegt ein Teil dauerhaft auf diesem Gerät und läuft auch ohne Netz. Auf dem iPhone die Seite dafür zum Home-Bildschirm hinzufügen, sonst räumt Safari den Speicher nach einer Woche ohne Nutzung wieder auf.' : 'Die MP3s müssen im Unterordner <b>audio</b> neben dieser Datei liegen.')+'</p>';
      TEILE.forEach(function(t){ var a = AUDIO[String(t.n)];
        html += '<button class="btn teilbtn" data-teil="'+t.n+'"'+(a?'':' disabled style="opacity:.45"')+'>'+esc(t.roman+' Teil: '+t.title)+(a?' <span style="color:var(--muted);font-weight:400">('+fmt(a.duration)+(store.pos[String(t.n)]?', zuletzt bei '+fmt(store.pos[String(t.n)]):'')+')</span>':' <span style="color:var(--muted);font-weight:400">(noch kein Audio)</span>')+'</button>';
        if(a) html += '<div class="offl" data-offl="'+t.n+'"></div><div class="offl" style="margin-top:-6px"><a href="audio/'+encodeURIComponent(a.file)+'" download style="color:var(--accent)">MP3</a><span>·</span><a href="audio/'+encodeURIComponent(a.file.replace(/\.mp3$/,'.txt'))+'" style="color:var(--accent)">Skript</a></div>'; });
      html += '</div>';
      if(VIDEOS.length) html += '<div class="panel"><p class="sub" style="margin:0 0 4px">Erklärvideos zum Einstieg</p>'+VIDEOS.map(function(v){ return videoCard(v.id, false); }).join('')+'</div>';
      view.innerHTML = html;
      Array.prototype.forEach.call(view.querySelectorAll('[data-teil]'), function(b){ b.onclick = function(){ state.hoerTeil = b.getAttribute('data-teil'); renderHoeren(); }; });
      bindVideoRows();
      Array.prototype.forEach.call(view.querySelectorAll('[data-offl]'), function(el){ renderOfflineRow(el.getAttribute('data-offl'), el); });
      return;
    }
    var a = AUDIO[tn], t = TEILE[parseInt(tn,10)-1];
    var html = '<div class="panel"><div class="navbar"><button class="btn small" id="hBack">‹ Alle Teile</button><span class="pos">'+esc(t.roman+' Teil')+'</span><span></span></div>';
    html += '<div class="ptitle" style="font-size:1rem">'+esc(t.title)+'</div>';
    html += '<audio id="player" controls preload="metadata" data-teil="'+tn+'" src="audio/'+encodeURIComponent(a.file)+'"></audio>';
    html += '<div id="hErr" class="cover hidden">MP3 nicht gefunden. Liegt „'+esc(a.file)+'“ im Ordner audio neben dieser HTML-Datei?</div>';
    html += '<div class="row speed" style="margin:4px 0 8px"><span class="sub" style="margin:0">Tempo:</span>'+[1,1.15,1.3,1.5].map(function(v){ return '<button class="btn'+(store.speed===v?' on':'')+'" data-speed="'+v+'">'+v+'×</button>'; }).join('')+
            '<button class="btn small" id="hPrev">‹ §</button><button class="btn small" id="hNext">§ ›</button></div>';
    html += '<div id="hLive" class="live"></div></div>';
    html += '<div class="panel"><div class="sub" style="margin-bottom:4px">Kapitel (tippen springt hin)</div><div id="hChaps">';
    a.chapters.forEach(function(c){ if(c.kind!=='law') return; var p = BY[c.id];
      html += '<div class="chap" data-start="'+c.start+'" data-id="'+c.id+'"><span class="t">'+fmt(c.start)+'</span><span><span class="nr">'+esc(p.label)+'</span> '+esc(p.title)+'</span></div>'; });
    html += '</div></div>';
    view.innerHTML = html;
    audioEl = document.getElementById('player');
    audioEl.playbackRate = store.speed;
    var startAt = state.seekTo!==null ? state.seekTo : (store.pos[tn] || 0); state.seekTo = null;
    audioEl.addEventListener('loadedmetadata', function(){ if(startAt>0 && startAt<audioEl.duration-2) audioEl.currentTime = startAt; });
    audioEl.addEventListener('error', function(){ document.getElementById('hErr').classList.remove('hidden'); });
    var lastKey = null;
    function current(){ var cur = null; for(var i=0;i<a.chapters.length;i++){ if(a.chapters[i].start <= audioEl.currentTime + 0.3) cur = a.chapters[i]; else break; } return cur; }
    function updateLive(){
      var c = current(); var key = c ? c.id+':'+c.kind : '';
      if(key===lastKey) return; lastKey = key;
      Array.prototype.forEach.call(view.querySelectorAll('.chap'), function(el){ el.classList.toggle('now', !!c && el.getAttribute('data-id')===c.id); });
      var live = document.getElementById('hLive');
      if(!c){ live.innerHTML = '<div class="cover">Ansage des Teils. Der Text erscheint, sobald der erste Paragraf beginnt.</div>'; return; }
      var p = BY[c.id];
      live.innerHTML = head(p) + '<div class="law'+(c.kind==='law'?' now':'')+'">'+lawHtml(p).replace(/^<div class="law">|<\/div>$/g,'')+'</div>' +
        (p.kurz?'<div class="kurz'+(c.kind==='kurz'?' now':'')+'"><b>Kurz gesagt</b>'+esc(p.kurz)+'</div>':'') +
        (p.fallSit?'<div class="fall'+(c.kind==='fall'?' now':'')+'"><b>Beispiel</b>'+esc(p.fallSit)+' '+esc(p.fallLoes)+'</div>':'');
    }
    audioEl.addEventListener('timeupdate', function(){ updateLive(); if(Math.floor(audioEl.currentTime)%10===0){ store.pos[tn]=audioEl.currentTime; saveStore(); } });
    audioEl.addEventListener('pause', function(){ store.pos[tn]=audioEl.currentTime; saveStore(); });
    audioEl.addEventListener('seeked', function(){ lastKey=null; updateLive(); });
    updateLive();
    Array.prototype.forEach.call(view.querySelectorAll('.chap'), function(el){ el.onclick = function(){ audioEl.currentTime = parseFloat(el.getAttribute('data-start')); audioEl.play(); }; });
    Array.prototype.forEach.call(view.querySelectorAll('[data-speed]'), function(b){ b.onclick = function(){ store.speed = parseFloat(b.getAttribute('data-speed')); saveStore(); audioEl.playbackRate = store.speed;
      Array.prototype.forEach.call(view.querySelectorAll('[data-speed]'), function(x){ x.classList.toggle('on', x===b); }); }; });
    function stepPara(dir){ var laws = a.chapters.filter(function(c){return c.kind==='law';}); var cur = -1;
      for(var i=0;i<laws.length;i++){ if(laws[i].start <= audioEl.currentTime - (dir<0?1.5:-0.3)) cur = i; }
      var n = Math.min(laws.length-1, Math.max(0, cur+dir)); audioEl.currentTime = laws[n].start; audioEl.play(); }
    document.getElementById('hPrev').onclick = function(){ stepPara(-1); };
    document.getElementById('hNext').onclick = function(){ stepPara(1); };
    document.getElementById('hBack').onclick = function(){ state.hoerTeil = null; renderHoeren(); };
  }

  // ----- STRUKTUR -----
  function renderStruktur(){
    var html = houseHtml() + (vid('schulhaus') ? '<div class="panel">'+videoCard('schulhaus', false)+'</div>' : '') +
      '<div class="panel tree"><p class="sub">Die Gliederung zum Einprägen. Tippen springt zum Paragrafen.</p>';
    TEILE.forEach(function(t){
      if(state.teil!=='all' && t.n!==parseInt(state.teil,10)) return;
      html += '<h3>'+esc(t.roman+' Teil: '+t.title)+'</h3>';
      t.abschnitte.forEach(function(s){
        if(s.title) html += '<div class="sec">'+esc(s.ord+' Abschnitt: '+s.title)+'</div>';
        s.ids.forEach(function(id){
          var p = BY[id]; var st = store.status[id]||'';
          html += '<a href="#" data-id="'+id+'" class="'+(p.aufgehoben?'off':'')+'"><span class="nr">'+esc(p.label)+'</span>'+esc(p.title)+(p.aufgehoben?'':'<span class="dot '+st+'"></span>')+'</a>';
        });
      });
    });
    html += '</div>';
    view.innerHTML = html;
    bindHouse();
    Array.prototype.forEach.call(view.querySelectorAll('a[data-id]'), function(a){
      a.onclick = function(ev){ ev.preventDefault(); state.jumpTo = a.getAttribute('data-id'); setMode('lesen'); };
    });
  }

  // ----- controls -----
  var teilSel = document.getElementById('teilSel');
  var opts = '<option value="all">Alle Teile</option>';
  TEILE.forEach(function(t){ opts += '<option value="'+t.n+'">'+esc(t.roman+' Teil: '+t.title)+'</option>'; });
  teilSel.innerHTML = opts;
  teilSel.onchange = function(){ state.teil=teilSel.value; state.hoerTeil=null; state.idx=0; state.fallIdx=0; state.order=null; state.fallOrder=null; state.werItem=null; state.werOrder=null; render(); };
  document.getElementById('weakOnly').onchange = function(e){ state.weakOnly=e.target.checked; state.idx=0; state.fallIdx=0; state.order=null; state.fallOrder=null; state.werOrder=null; state.werItem=null; state.eoOrder=null; render(); };
  document.getElementById('randomBtn').onclick = function(){
    if(state.mode==='faelle'){ state.fallOrder=null; state.fallIdx=0; }
    else if(state.mode==='wer'){ state.werOrder=null; state.werItem=null; }
    else if(state.mode==='eo'){ state.eoOrder=null; }
    else { state.order=null; state.idx=0; if(state.mode!=='recall'){ setMode('recall'); return; } }
    render();
  };
  function setMode(m){
    if(audioEl && m!=='hoeren'){ try{ store.pos[audioEl.getAttribute('data-teil')] = audioEl.currentTime; saveStore(); audioEl.pause(); }catch(e){} audioEl=null; }
    Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(x){ x.classList.toggle('active', x.getAttribute('data-mode')===m); });
    state.mode = m; render(); window.scrollTo(0,0);
  }
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(t){ t.onclick = function(){ setMode(t.getAttribute('data-mode')); }; });
  document.getElementById('resetBtn').onclick = function(){
    if(!window.confirm('Gesamten Fortschritt wirklich löschen?')) return;
    store = {status:{}, fall:{}, wer:{right:0,total:0}, werStatus:{}, eoStatus:{}, pos:{}, speed:1}; saveStore(); state.order=null; state.fallOrder=null; state.werOrder=null; state.werItem=null; state.eoOrder=null; render();
  };
  render();
  if('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')){
    navigator.serviceWorker.register('sw.js').catch(function(){});
  }
})();
</script>
</body>
</html>
'''
OUT.write_text(HTML.replace("PAYLOAD", payload.replace("</", "<\\/")).replace("STAND", data["stand"]), encoding="utf-8")
print(f"saved: {OUT}  ({OUT.stat().st_size/1024:.0f} KB, {len(paras)} Paragrafen, {sum(1 for p in paras if p['fallSit'])} Fälle)")
