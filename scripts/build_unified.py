# -*- coding: utf-8 -*-
"""统一查重站点生成器（重写版）。

主 tab = 「来源抄袭检测」：每篇文章（底稿/<日期_公司>/index.html）vs 其「原始资料/」
下的外部源文件（网站快照/招股书/研报/舆情），逐条标示「抄自哪份文件、抄了哪段」。
来源重复率 = 直接复制率 + 部分引用率 + 改写/观点相似率（三者按字符优先级合并，不重复计数）。

次 tab = 「观点层查重」：由 观点查重报告/index.html 的 VPDATA 提供（角度档案/共享框架/原创性）。

用法：python3 scripts/build_unified.py   （建议用带 jieba+sklearn 的 venv 运行）
输出：查重报告/index.html
"""
import os, re, json, importlib.util

_TAGRE = re.compile(r"<[^>]+>")


def _clean(s):
    return _TAGRE.sub("", s or "")

ROOT = "/Users/panyp/WorkBuddy/#深度调查档案室"
DRAFT = os.path.join(ROOT, "底稿")
SCRIPT = os.path.join(ROOT, "scripts", "check_plagiarism.py")
VP_HTML = os.path.join(ROOT, "观点查重报告", "index.html")
OUT = os.path.join(ROOT, "查重报告", "index.html")

# ---------- import 已有匹配逻辑 ----------
spec = importlib.util.spec_from_file_location("cp", SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

# ---------- 观点层数据 ----------
vp_html = open(VP_HTML, encoding="utf-8").read()
_vp_marker = "const DATA = "
i = vp_html.index(_vp_marker) + len(_vp_marker)
_vp_obj, _vp_end = json.JSONDecoder().raw_decode(vp_html[i:])
VPDATA = vp_html[i:i + _vp_end]

# ---------- 计算来源抄袭层（文字层） ----------
folders = sorted([d for d in os.listdir(DRAFT)
                 if os.path.isdir(os.path.join(DRAFT, d))])
textdata = []
for folder in folders:
    r = cp.process_article(folder)
    if not r:
        continue
    N = len(r["article_norm"])
    mark = r.get("mark") or [0] * N
    if len(mark) != N:
        mark = [0] * N
    # 命中归属数组（字符 -> 命中序号），用于 data-hit 联动
    hit_of = [-1] * N
    for si, sp in enumerate(r["spans"]):
        for p in range(sp["start"], sp["end"]):
            if p < N:
                hit_of[p] = si
    # 正文高亮
    body_parts = []
    for pi, (orig, pn, tag) in enumerate(zip(r["para_orig"], r["para_norm"], r["para_tags"])):
        idxs = [k for k in range(N) if r["para_of"][k] == pi]
        seg_mark = [mark[k] for k in idxs if r["article_norm"][k] != "\n"]
        seg_hit = [hit_of[k] for k in idxs if r["article_norm"][k] != "\n"]
        if len(seg_mark) != len(pn):
            seg_mark = [0] * len(pn)
            seg_hit = [-1] * len(pn)
        rendered = cp.render_paragraph_with_marks(orig, seg_mark, seg_hit)
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = min(int(tag[1]), 4)
            body_parts.append(f"<h{lvl} class=\"rh\">{rendered}</h{lvl}>")
        elif tag == "blockquote":
            body_parts.append(f"<blockquote>{rendered}</blockquote>")
        elif tag == "li":
            body_parts.append(f"<p class=\"rli\">{rendered}</p>")
        else:
            body_parts.append(f"<p>{rendered}</p>")
    body = "\n".join(body_parts)
    # 命中清单（含来源文件归属）
    hits = []
    for det in r["detailed"]:
        hits.append({
            "type": det["type"],
            "src": det["src"],
            "core": (det.get("core") or "")[:40],
            "art": _clean(det.get("art") or det.get("art_snip") or "")[:160],
            "srcc": _clean(det.get("srcexc") or det.get("src_snip") or "")[:160],
            "sim": det.get("sim") or 0,
            "len": det.get("len", 0),
        })
    textdata.append({
        "key": folder,
        "title": r["title"],
        "company": folder.split("_", 1)[1] if "_" in folder else folder,
        "date": folder.split("_", 1)[0],
        "n_src": r["n_src"],
        "nosource": r["nosource"],
        "rate": round(r["rate"] * 100, 1),
        "rate_direct": round(r["rate_direct"] * 100, 1),
        "rate_partial": round(r["rate_partial"] * 100, 1),
        "rate_paraphrase": round(r["rate_paraphrase"] * 100, 1),
        "src_files": r["src_files"],
        "src_hits": r["src_hits"],
        "body_html": body,
        "hits": hits,
    })

TEXTDATA = json.dumps(textdata, ensure_ascii=False)

# =====================================================================
#  CSS（自包含，大理红主题）
# =====================================================================
CSS = """
:root{--maroon:#7a1f1f;--maroon2:#9a2c2c;--red:#c0392b;--amber:#c9961a;--blue:#2c5fb3;--green:#2e7d32;--ink:#211c16;--muted:#8a8178;--line:#e7e0d6;--bg:#faf8f4;--card:#fff}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg)}
.topbar{display:flex;align-items:center;gap:14px;padding:11px 20px;background:linear-gradient(100deg,var(--maroon),var(--maroon2));color:#fff;position:sticky;top:0;z-index:20}
.brand{font-weight:700;font-size:16px;letter-spacing:.5px;white-space:nowrap}
.tabs{display:flex;gap:6px}
.tab{padding:7px 16px;border-radius:8px;background:rgba(255,255,255,.16);color:#fff;cursor:pointer;font-size:13px;border:1px solid rgba(255,255,255,.28);font-weight:600;transition:.15s}
.tab:hover{background:rgba(255,255,255,.30)}
.tab.active{background:#fff;color:var(--maroon)}
.links{margin-left:auto;display:flex;gap:14px;font-size:13px}
.links a{color:#ffe;border-bottom:1px dashed rgba(255,255,255,.5);text-decoration:none}
.links a:hover{color:#fff}
.main{flex:1;display:flex;height:calc(100vh - 57px);overflow:hidden}
.sidebar{width:300px;min-width:300px;border-right:1px solid var(--line);background:#fff;display:flex;flex-direction:column;overflow:hidden}
.controls{padding:12px 14px;border-bottom:1px solid var(--line)}
.controls input{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px}
.legend{font-size:11px;color:var(--muted);margin-top:7px;line-height:1.5}
.list{overflow:auto;padding:8px}
.item{padding:11px 12px;border:1px solid var(--line);border-radius:10px;margin-bottom:9px;cursor:pointer;background:#fff;transition:.12s}
.item:hover{border-color:var(--maroon);box-shadow:0 2px 8px rgba(122,31,31,.08)}
.item.active{border-color:var(--maroon);background:#fbf3ef}
.item-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.item-title{font-size:14px;font-weight:700;line-height:1.3}
.rate-badge{font-size:18px;font-weight:800;white-space:nowrap;line-height:1}
.rate-sub{font-size:11px;color:var(--muted);margin-top:5px}
.nosrc{font-size:11px;color:var(--amber);margin-top:4px}
.content{flex:1;overflow:auto;padding:26px 34px;line-height:1.95;font-size:15.5px;max-width:860px}
.content .c-head{border-bottom:2px solid var(--maroon);padding-bottom:12px;margin-bottom:18px}
.content .c-title{font-size:22px;font-weight:800;margin:0 0 6px}
.content .c-meta{font-size:13px;color:var(--muted)}
.chips{display:flex;gap:9px;flex-wrap:wrap;margin:12px 0 4px}
.chip{font-size:12px;padding:4px 10px;border-radius:20px;border:1px solid var(--line);background:#fff}
.chip b{font-size:14px}
.c-direct b{color:var(--red)}.c-partial b{color:var(--amber)}.c-para b{color:var(--blue)}.c-tot b{color:var(--maroon)}
.rh{color:var(--maroon);margin:22px 0 8px;line-height:1.4}
.content p{margin:11px 0}
.rli{margin:7px 0 7px 22px}
blockquote{margin:14px 0;padding:8px 16px;border-left:3px solid var(--line);color:#555;background:#fafafa}
.empty{color:var(--muted);padding:60px 20px;text-align:center}
.right{width:430px;min-width:430px;border-left:1px solid var(--line);background:#faf8f4;display:flex;flex-direction:column;overflow:hidden}
.r-head{padding:13px 16px;font-weight:700;color:var(--maroon);border-bottom:2px solid var(--maroon);font-size:14px}
#rbody{overflow:auto;padding:12px 14px 60px}
.src-sum{font-size:12.5px;color:var(--muted);background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 11px;margin:10px 0;line-height:1.6}
.src-sec{font-size:13px;font-weight:700;color:var(--maroon);border-left:4px solid var(--maroon);padding-left:9px;margin:18px 0 8px}
.src-group{margin-bottom:14px}
.src-name{font-size:12.5px;font-weight:700;word-break:break-all;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:7px 7px 0 0;padding:7px 10px;border-bottom:none}
.src-meta{font-size:11px;color:var(--muted);background:#f3efe7;border:1px solid var(--line);border-top:none;border-radius:0 0 7px 7px;padding:4px 10px}
.hit{border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:8px 0;background:#fff;cursor:pointer;transition:.12s}
.hit:hover{border-color:var(--maroon)}
.hit.flash{box-shadow:0 0 0 2px var(--maroon);background:#fbf3ef}
.ht{display:inline-block;font-size:10.5px;font-weight:700;color:#fff;padding:1px 7px;border-radius:10px;margin-bottom:5px}
.ht.direct{background:var(--red)}.ht.partial{background:var(--amber)}.ht.paraphrase{background:var(--blue)}
.h-art{font-size:12.5px;line-height:1.6;margin:3px 0}
.h-art b{color:var(--red)}
.h-src{font-size:12px;line-height:1.6;color:#3a4a6b;background:#eef3fb;border-left:2px solid var(--blue);padding:5px 8px;border-radius:0 4px 4px 0;margin-top:4px}
.warn{background:#fff4e0;border:1px solid #e0b070;padding:10px;border-radius:7px;font-size:12.5px;color:#7a5a10;margin:10px 0}
.r-legend{font-size:11px;color:var(--muted);margin-top:10px;line-height:1.6}
mark.direct{background:#ffd6d6;color:#7a0000;text-decoration:underline;cursor:pointer;padding:0 1px}
mark.partial{background:#fff2b8;color:#6b5200;cursor:pointer;padding:0 1px}
mark.paraphrase{background:#d6e4ff;color:#1a3a8a;cursor:pointer;padding:0 1px}
/* 观点层 */
.vp-right{width:380px;min-width:380px;border-left:1px solid var(--line);background:#faf8f4;display:flex;flex-direction:column;overflow:auto;padding:14px 16px 50px}
.vp-sec{font-size:13px;font-weight:700;color:var(--maroon);border-left:4px solid var(--maroon);padding-left:9px;margin:20px 0 8px}
.vp-sec:first-child{margin-top:0}
.vp-chip{display:inline-block;background:#f1ece3;border:1px solid var(--line);color:var(--ink);font-size:12px;padding:2px 9px;border-radius:12px;margin:3px 4px 0 0}
.vp-k{font-size:13.5px;margin:5px 0 0;padding-left:14px;position:relative;line-height:1.6}
.vp-k:before{content:"•";position:absolute;left:2px;color:var(--maroon)}
.vp-frame{background:#fff3c4;border-left:3px solid var(--amber);padding:7px 11px;margin:6px 0;font-size:13px;border-radius:0 4px 4px 0;line-height:1.6}
.vp-orig{font-size:13px;background:#eef6ef;border-left:3px solid var(--green);padding:9px 12px;border-radius:0 4px 4px 0;line-height:1.65}
.vp-sh{margin:11px 0;padding:11px 13px;border:1px solid var(--line);border-radius:8px;background:#fff}
.vp-sh .sn{font-weight:700;font-size:13.5px;color:var(--red)}
.vp-sh .sa{font-size:12px;color:var(--muted);margin:4px 0}
.vp-sh .sd{font-size:12.5px;line-height:1.6}
.vp-flag{background:#fdecea;border-left:3px solid var(--red);padding:9px 12px;margin:9px 0;font-size:12.5px;border-radius:0 4px 4px 0;line-height:1.6}
.vp-badge{font-size:10px;padding:1px 6px;border-radius:10px;color:#fff;font-weight:700;white-space:nowrap}
.vp-bartrack{height:4px;background:#eee;border-radius:2px;margin-top:6px;overflow:hidden}
.vp-bartrack>i{display:block;height:100%}
.vp-detail-head{border-bottom:2px solid var(--maroon);padding-bottom:10px;margin-bottom:6px}
.vp-detail-title{font-size:19px;font-weight:700;line-height:1.3}
.vp-detail-sub{font-size:13px;color:var(--muted);margin-top:4px}
.vp-legend{font-size:11px;color:var(--muted);margin-top:8px;line-height:1.5}
@media(max-width:1180px){.right{width:360px;min-width:360px}.sidebar{width:270px;min-width:270px}.vp-right{width:330px;min-width:330px}}
"""

# =====================================================================
#  HTML 骨架
# =====================================================================
BODY = (
'<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">\n'
'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
'<title>深度调查档案室 · 来源抄袭检测</title>\n'
'<style>\n' + CSS + '</style></head><body>\n'
'<header class="topbar">\n'
'  <div class="brand">深度调查档案室 · 来源抄袭检测</div>\n'
'  <div class="tabs">\n'
'    <button class="tab active" data-view="text">来源抄袭检测</button>\n'
'    <button class="tab" data-view="view">观点层查重</button>\n'
'  </div>\n'
'  <div class="links"><a href="汇总.md" target="_blank">汇总表</a>'
'<a href="方法说明.md" target="_blank">方法说明</a>'
'<a href="../观点查重/汇总.md" target="_blank">观点层分析</a></div>\n'
'</header>\n'
'<div class="main" id="viewText">\n'
'  <aside class="sidebar">\n'
'    <div class="controls">\n'
'      <input id="q" placeholder="搜索文章…">\n'
'      <div class="legend">主指标=来源重复率（文章 vs 其原始资料）。红≥5% 直接复制 · 黄=部分引用 · 蓝=改写观点相似</div>\n'
'    </div>\n'
'    <div class="list" id="list"></div>\n'
'  </aside>\n'
'  <section class="content" id="content"><div class="empty">← 从左侧选择一篇文章，查看其来源抄袭高亮与归属</div></section>\n'
'  <aside class="right">\n'
'    <div class="r-head">来源归属 · 抄自哪份文件</div>\n'
'    <div id="rbody"><div class="empty" style="padding:40px 10px">选择文章后，这里按来源文件列出每一处抄袭/雷同的原文与来源片段</div></div>\n'
'  </aside>\n'
'</div>\n'
'<div class="main" id="viewView" style="display:none">\n'
'  <aside class="sidebar">\n'
'    <div class="controls">\n'
'      <input id="vpq" placeholder="搜索文章…">\n'
'      <div class="legend">徽标：<b>角</b>=角度数 · <b>二手</b>=定性二手观点评估（高红 / 中橙 / 低绿）</div>\n'
'    </div>\n'
'    <div class="list" id="vplist"></div>\n'
'  </aside>\n'
'  <section class="content" id="vpdetail"><div class="empty">← 从左侧选择一篇文章，查看其观点档案</div></section>\n'
'  <aside class="vp-right">\n'
'    <div class="vp-sec" style="margin-top:0">跨篇共享框架（他们都拷问了这些点）</div>\n'
'    <div id="vpshared"></div>\n'
'    <div class="vp-sec">需重点核查</div>\n'
'    <div id="vpflags"></div>\n'
'  </aside>\n'
'</div>\n'
)

# =====================================================================
#  JS：来源抄袭层
# =====================================================================
TEXT_JS = """
const TEXT = TEXTDATA;
function rateColor(r){ return r>=5?'var(--red)':(r>=2?'var(--amber)':'var(--green)'); }
function shortName(a){ return a.replace(/^\\d+-\\d+-\\d+_/, ''); }
function esc(s){ return (s||'').replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function renderList(){
  const q=(document.getElementById('q').value||'').trim();
  const box=document.getElementById('list'); box.innerHTML='';
  TEXT.filter(d=>!q||d.company.indexOf(q)>=0||d.title.indexOf(q)>=0).forEach(d=>{
    const el=document.createElement('div'); el.className='item'; el.dataset.k=d.key;
    const col=rateColor(d.rate);
    let sub='来源重复 '+d.rate+'% · 抄自 '+d.n_src+' 份来源';
    let nos='';
    if(d.nosource){ sub='未存档原始资料，无法做来源判定'; nos='<div class="nosrc">⚠ 无对照原始资料</div>'; }
    el.innerHTML='<div class="item-top"><div class="item-title">'+esc(shortName(d.key))+'</div>'
      +'<div class="rate-badge" style="color:'+col+'">'+d.rate+'%</div></div>'
      +'<div class="rate-sub">'+esc(sub)+'</div>'+nos;
    el.onclick=function(){ document.querySelectorAll('#list .item').forEach(x=>x.classList.remove('active')); el.classList.add('active'); selectText(d.key); };
    box.appendChild(el);
  });
}
function selectText(key){
  const d=TEXT.find(x=>x.key===key); if(!d) return;
  const c=document.getElementById('content');
  const chips='<div class="chips">'
    +'<span class="chip c-tot">综合 <b>'+d.rate+'%</b></span>'
    +'<span class="chip c-direct">直接复制 <b>'+d.rate_direct+'%</b></span>'
    +'<span class="chip c-partial">部分引用 <b>'+d.rate_partial+'%</b></span>'
    +'<span class="chip c-para">改写/观点相似 <b>'+d.rate_paraphrase+'%</b></span>'
    +'<span class="chip">来源文件 <b>'+d.n_src+'</b> 份</span></div>';
  c.innerHTML='<div class="c-head"><h1 class="c-title">'+esc(d.title)+'</h1>'
    +'<div class="c-meta">'+esc(d.key)+' · 比对对象：本篇「原始资料/」下的外部源文件（网页快照/招股书/研报/舆情）</div>'+chips+'</div>'
    + (d.nosource?'<div class="warn">⚠ 本篇未存档「原始资料/」，无法做来源抄袭判定。若当时撰写参考了外部文件，请回补存档后重测。</div>':'')
    + d.body_html;
  c.scrollTop=0;
  renderRight(d);
  // 高亮点击 -> 右侧命中
  c.querySelectorAll('mark[data-hit]').forEach(m=>{
    m.addEventListener('click',()=>{
      const id='hit-'+d.key+'-'+m.getAttribute('data-hit');
      const t=document.getElementById(id);
      if(t){ t.scrollIntoView({block:'center'}); t.classList.add('flash'); setTimeout(()=>t.classList.remove('flash'),1200); }
    });
  });
}
function renderRight(d){
  const box=document.getElementById('rbody');
  if(d.nosource){ box.innerHTML='<div class="warn">本篇无对照原始资料，未做来源抄袭判定。</div>'; return; }
  if(!d.hits.length){ box.innerHTML='<div class="src-sum">本篇来源重复率 '+d.rate+'%，未在正文中定位到与原始资料的逐字/改写重合片段（主要为原创转述）。</div>'; return; }
  // 按来源文件分组
  const groups={};
  d.hits.forEach((h,idx)=>{ const s=h.src||'（未定位来源）'; (groups[s]=groups[s]||[]).push([idx,h]); });
  let h='<div class="src-sum"><b>来源重复率 '+d.rate+'%</b>（直接 '+d.rate_direct+'% / 部分 '+d.rate_partial+'% / 改写 '+d.rate_paraphrase+'%）。'
    +' 下方按来源文件分组，共 '+d.hits.length+' 处命中，抄自 '+Object.keys(groups).length+' 份来源文件。</div>';
  h+='<div class="src-sec">逐条命中（按来源文件分组）</div>';
  for(const s of Object.keys(groups)){
    const arr=groups[s];
    const chars=arr.reduce((a,x)=>a+x[1].len,0);
    h+='<div class="src-group"><div class="src-name">📄 '+esc(s)+'</div>'
      +'<div class="src-meta">'+arr.length+' 处 · 约 '+chars+' 字重合</div>';
    arr.forEach(([idx,h])=>{
      const tl=h.type==='direct'?'直接复制':(h.type==='partial'?'部分引用':'改写/观点相似');
      const sim=h.sim?(' 相似 '+Math.round(h.sim*100)+'%'):'';
      h+='<div class="hit" id="hit-'+d.key+'-'+idx+'">'
        +'<span class="ht '+h.type+'">'+tl+sim+'</span>'
        +'<div class="h-art"><b>文章：</b>'+esc(h.art)+'</div>'
        + (h.srcc?'<div class="h-src"><b>来源：</b>'+esc(h.srcc)+'</div>':'')
        +'</div>';
    });
    h+='</div>';
  }
  h+='<div class="r-legend">红=与来源≥15字连续一致（直接复制）；黄=与来源≥12字核心命中（部分引用）；蓝=句级语义近重复（同义替换/改写）。点击正文高亮可定位到此处；点击此处可回到正文。</div>';
  box.innerHTML=h;
  // 命中点击 -> 正文高亮
  box.querySelectorAll('.hit').forEach(t=>{
    t.addEventListener('click',()=>{
      const id=t.id.replace('hit-'+d.key+'-','');
      const m=document.querySelector('#content mark[data-hit="'+id+'"]');
      if(m){ m.scrollIntoView({block:'center'}); m.style.outline='2px solid var(--maroon)'; setTimeout(()=>m.style.outline='',1200); }
    });
  });
}
document.getElementById('q').addEventListener('input', renderList);
renderList();
if(TEXT[0]){ const first=document.querySelector('#list .item'); if(first){ first.classList.add('active'); selectText(TEXT[0].key); } }
"""

# =====================================================================
#  JS：tab 切换 + 观点层（来自 观点查重报告）
# =====================================================================
TAB_JS = """
function switchView(v){
  document.getElementById('viewText').style.display=(v==='text')?'flex':'none';
  document.getElementById('viewView').style.display=(v==='view')?'flex':'none';
  document.querySelectorAll('.tab').forEach(function(t){ t.classList.toggle('active', t.getAttribute('data-view')===v); });
}
document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click', function(){ switchView(t.getAttribute('data-view')); });
});
"""

VP_JS = """
const $ = s => document.querySelector(s);
const VP = VPDATA;
const arts = Object.keys(VP.qual);
function secColor(v){ return (VP.secColor && VP.secColor[v]) || '#999'; }
function esc(s){ return (s||'').replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function shortName(a){ return a.replace(/^\\d+-\\d+_/, ''); }
function renderVpList(){
  const q=($('#vpq').value||'').trim();
  const box=$('#vplist'); box.innerHTML='';
  arts.filter(a=>!q||a.indexOf(q)>=0).forEach(a=>{
    const qd=VP.qual[a], sr=VP.sys[a]||{};
    const sec=sr.second_hand_ratio?(sr.second_hand_ratio*100).toFixed(0)+'%':'-';
    const el=document.createElement('div'); el.className='item'; el.dataset.a=a;
    el.innerHTML='<div class="item-top"><div><div class="item-title">'+esc(shortName(a))+'</div></div>'
      +'<div style="display:flex;gap:5px"><span class="vp-badge" style="background:var(--maroon)">角 '+(sr.angle_count||'-')+'</span>'
      +'<span class="vp-badge" style="background:'+secColor(qd.second)+'">二手 '+qd.second+'</span></div></div>'
      +'<div class="vp-bartrack"><i style="width:'+sec+';background:'+secColor(qd.second)+'"></i></div>';
    el.onclick=function(){ document.querySelectorAll('#vplist .item').forEach(x=>x.classList.remove('active')); el.classList.add('active'); renderVpDetail(a); };
    box.appendChild(el);
  });
}
function renderVpDetail(a){
  const qd=VP.qual[a], sr=VP.sys[a]||{}; const ang=sr.angles||{};
  let h='<div class="vp-detail-head"><div class="vp-detail-title">'+esc(shortName(a))+'</div>'
    +'<div class="vp-detail-sub">'+esc(a)+' · 系统层角度数 '+(sr.angle_count||'-')+' · 算法二手密度 '+((sr.second_hand_ratio*100)||0).toFixed(1)+'% · 定性二手评估 <b style="color:'+secColor(qd.second)+'">'+qd.second+'</b></div></div>';
  h+='<div class="vp-sec">角度档案（拷问了哪些点）</div>';
  h+='<div>'+(Object.keys(ang).map(k=>'<span class="vp-chip">'+esc(k)+'</span>').join('')||'—')+'</div>';
  h+='<div class="vp-sec">拷问点</div>'+qd.kao.map(k=>'<div class="vp-k">'+esc(k)+'</div>').join('');
  h+='<div class="vp-sec">叙事框架 / 比喻</div>'+qd.frame.map(f=>'<div class="vp-frame">'+esc(f)+'</div>').join('');
  h+='<div class="vp-sec">原创性判断</div><div class="vp-orig">'+esc(qd.orig)+'</div>';
  h+='<div class="vp-sec">与其他篇共享的框架</div>'+(qd.shared&&qd.shared.length?qd.shared.map(s=>'<span class="vp-chip">'+esc(s)+'</span>').join(''):'<span style="color:var(--muted);font-size:12px">—</span>');
  $('#vpdetail').innerHTML=h; $('#vpdetail').scrollTop=0;
}
function renderVpShared(){
  $('#vpshared').innerHTML=VP.shared.map(s=>'<div class="vp-sh"><div class="sn">'+esc(s.name)+'</div><div class="sa">涉及：'+esc(s.arts.join('、'))+'</div><div class="sd">'+esc(s.note)+'</div></div>').join('');
  $('#vpflags').innerHTML=VP.flags.map(f=>'<div class="vp-flag"><b>'+esc(f.a)+'</b><br>'+esc(f.issue)+'</div>').join('');
}
$('#vpq').addEventListener('input', renderVpList);
renderVpList(); renderVpShared();
if(arts[0]){ const first=document.querySelector('#vplist .item'); if(first){ first.classList.add('active'); renderVpDetail(arts[0]); } }
"""

# =====================================================================
#  组装
# =====================================================================
UNI = (
    BODY
    + "\n<script>\n" + TAB_JS + "</script>\n"
    + "\n<script>\nconst TEXTDATA = " + TEXTDATA + ";\n" + TEXT_JS + "\n</script>\n"
    + "\n<script>\nconst VPDATA = " + VPDATA + ";\n" + VP_JS + "\n</script>\n"
    + "</body></html>"
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(UNI)

print("written:", OUT, len(UNI), "bytes")
print("text articles:", len(textdata))
print("with sources:", sum(1 for d in textdata if not d["nosource"]))
print("nosource:", [d["key"] for d in textdata if d["nosource"]])
print("total hits:", sum(len(d["hits"]) for d in textdata))
