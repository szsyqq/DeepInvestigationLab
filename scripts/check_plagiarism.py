#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度调查档案室 · 文章查重测试
================================
比对对象：每篇文章（底稿/<日期_公司>/index.html 原文） vs 其「原始资料/」下的网站出处
（HTML 网页快照 / MD / JSON），以及跨文章互抄检测。

输出：查重报告/ 下
  - 汇总.md / 汇总.csv        ：每篇查重率与来源清单
  - 方法说明.md               ：算法与口径
  - articles/<folder>/index.html ：单篇带高亮的可读报告 + 命中清单

用法：
  python3 scripts/check_plagiarism.py
  python3 scripts/check_plagiarism.py --only 宇树
"""

import os, re, html, sys, json, csv, argparse, html as _html
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# ---- 句级语义近重复（改写/观点相似）依赖（优雅降级）----
HAVE_JIEBA = False
HAVE_SK = False
try:
    import jieba
    jieba.setLogLevel(20)
    HAVE_JIEBA = True
except Exception:
    pass
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAVE_SK = True
except Exception:
    pass

ROOT = "/Users/panyp/WorkBuddy/#深度调查档案室"
DRAFT = os.path.join(ROOT, "底稿")
OUT = os.path.join(ROOT, "查重报告")

# ---- 可调参数 ----
DIRECT_LEN = 15      # 连续 N 字完全一致 => 直接复制
PARTIAL_CORE = 12    # 核心 N 字命中但无完整 DIRECT_LEN => 部分引用/观点雷同
CORE_MIN_CN = 6      # 核心中至少含 N 个汉字，过滤无意义短串
PARTIAL_OFF = 1      # 部分核心在 15 字窗口中的起始偏移
MERGE_GAP = 0        # 归一化位置上允许合并的间隙（0=不桥接间隙，避免虚高）

# ---- 句级语义近重复（改写/观点相似）参数 ----
T_PARA = 0.55        # 句级 TF-IDF 余弦相似度阈值（≥ 视为改写/观点相似）
MIN_PARA_ART = 14    # 文章句归一化最小长度（过短忽略）
MIN_PARA_SRC = 12    # 来源句归一化最小长度
MIN_SHARED_TOK = 2   # 文章句与来源句最少共享实词数（过滤纯实体巧合）
MAX_PARA_PER_ART = 60  # 单篇改写命中上限（防极端膨胀）

CN = re.compile(r'[\u4e00-\u9fff]')
KEEP = re.compile(r'[\u4e00-\u9fff0-9a-zA-Z]')

def normalize(s: str) -> str:
    """只保留中文/数字/字母，去除标点与空白。用于跨文档比对。"""
    return ''.join(KEEP.findall(s))

def n_cn(s: str) -> int:
    return len(CN.findall(s))

# ---------------- 文本提取 ----------------
def extract_prose_from_html(t: str):
    """抽取文章叙事正文（p/h1-6/li/blockquote），剔除脚注/consent/图表/导航。"""
    # 去脚本样式
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
    # 去脚注区与合规弹窗
    t = re.sub(r'<(div|section|ol|ul)[^>]*class="[^"]*footnotes[^"]*"[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<(div|section)[^>]*class="[^"]*consent[^"]*"[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
    # 去导航/目录抽屉（含 'nav' 'drawer' 'toc' 'top-bar' 'masthead' 'back-top' 'internal-banner' 'chapter-nav' 'menu'）
    t = re.sub(r'<(nav|div|aside|header|footer)[^>]*class="[^"]*(nav|drawer|toc|top-bar|masthead|back-top|internal-banner|chapter-nav|menu|sidebar)[^"]*"[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
    chunks = []
    for m in re.finditer(r'<(p|h[1-6]|li|blockquote)\b[^>]*>(.*?)</\1>', t, flags=re.S | re.I):
        txt = re.sub(r'<[^>]+>', ' ', m.group(2))
        txt = html.unescape(txt)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt:
            chunks.append((m.group(1).lower(), txt))
    return chunks

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        raw = open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return ''
    if ext in ('.html', '.htm'):
        raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
        raw = re.sub(r'<[^>]+>', ' ', raw)
        raw = html.unescape(raw)
    # md/json 直接当文本
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw

# ---------------- 索引构建 ----------------
def build_index(items):
    """items: list of (src_id, norm_text). 返回 (map15, map10, src_texts)
    map15: shingle15 -> set(src_idx)
    map10: shingle10 -> set(src_idx)
    src_texts: list of (src_id, norm_text, clean_text)  —— clean_text 保留标点用于展示
    """
    map15 = defaultdict(set)
    map10 = defaultdict(set)
    src_texts = []
    for idx, (sid, norm) in enumerate(items):
        src_texts.append((sid, norm, None))  # clean_text 稍后补
        L = len(norm)
        for i in range(0, L - DIRECT_LEN + 1):
            map15[norm[i:i+DIRECT_LEN]].add(idx)
        for i in range(0, L - PARTIAL_CORE + 1):
            sh = norm[i:i+PARTIAL_CORE]
            if n_cn(sh) >= CORE_MIN_CN:
                map10[sh].add(idx)
    return map15, map10, src_texts

def build_clean_texts(items, src_texts):
    for (sid, norm), rec in zip(items, src_texts):
        # 用原始抽取文本作为展示用 clean（保留标点）
        rec = list(rec)
        rec[2] = sid  # placeholder, replaced below
    # 直接重新读取 clean：从 items 拿原始
    out = []
    for (sid, norm), (_, _, _) in zip(items, src_texts):
        out.append((sid, norm, norm))  # 展示用直接用 norm（已去标点，稳定）
    return out

# ---------------- 扫描 ----------------
def scan(article_norm, map15, map10, exclude_idx=None):
    """返回 spans: list of dict(start, end, type, srcs(set), cores(list))。
    type: 'direct'|'partial'。exclude_idx 用于跨文章扫描排除自身。
    命中时标记整个 DIRECT_LEN 窗口（而非仅起点），确保 span 覆盖真实重合文本。"""
    N = len(article_norm)
    direct = [False]*N
    partial = [False]*N
    direct_src = [set() for _ in range(N)]
    partial_src = [set() for _ in range(N)]
    direct_cores = defaultdict(list)   # 起点 -> 命中的 15 字串
    partial_cores = defaultdict(list)  # 起点 -> 命中的核心串
    ex = {exclude_idx} if exclude_idx is not None else set()

    for i in range(0, N - DIRECT_LEN + 1):
        sh = article_norm[i:i+DIRECT_LEN]
        if sh in map15:
            s = map15[sh] - ex
            if s:
                for p in range(i, i+DIRECT_LEN):
                    direct[p] = True
                    direct_src[p] |= s
                direct_cores[i].append(sh)

    for i in range(0, N - DIRECT_LEN + 1):
        if direct[i]:
            continue
        c0 = i + PARTIAL_OFF
        core = article_norm[c0:c0+PARTIAL_CORE]
        if len(core) < PARTIAL_CORE:
            continue
        if n_cn(core) < CORE_MIN_CN:
            continue
        if core in map10:
            s = map10[core] - ex
            if s:
                for p in range(c0, c0+PARTIAL_CORE):
                    partial[p] = True
                    partial_src[p] |= s
                partial_cores[i].append(core)

    def merge(mask, srcmap, cores_map, typ):
        spans = []
        i = 0
        while i < N:
            if not mask[i]:
                i += 1; continue
            j = i
            while j < N:
                if mask[j]:
                    j += 1
                else:
                    k = j
                    while k < N and not mask[k]:
                        k += 1
                    if k - j <= MERGE_GAP and k < N:
                        j = k
                    else:
                        break
            srcs = set()
            cores = []
            for p in range(i, j):
                if mask[p]:
                    srcs |= srcmap[p]
                if p in cores_map:
                    cores.extend(cores_map[p])
            spans.append({'start': i, 'end': j, 'type': typ, 'srcs': srcs, 'cores': cores})
            i = j
        return spans

    spans = merge(direct, direct_src, direct_cores, 'direct')
    # 部分引用不与直接复制重叠，避免重复计数
    for p in range(N):
        partial[p] = partial[p] and not direct[p]
    spans += merge(partial, partial_src, partial_cores, 'partial')
    return spans

def sim_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_original_span(orig, core_norm):
    """在 orig 的「保留字符序列」(去标点空白) 中找 core_norm 的连续命中，
    返回对应原始区间 [s,e) 或 None。要求核心在保留序列中连续出现。"""
    kept_idx = [i for i, c in enumerate(orig) if KEEP.match(c)]
    ks = ''.join(orig[i] for i in kept_idx)
    p = ks.find(core_norm)
    if p < 0:
        return None
    s = kept_idx[p]
    e = kept_idx[p + len(core_norm) - 1] + 1
    return (s, e)

def make_excerpt(orig, core, radius=140):
    """在 orig 中以 core（归一化串）定位重合区间，返回带 <mark class='hl'> 的 HTML 片段。
    仅高亮真实命中核心（pre/post 为未高亮上下文），用于对比面板。"""
    if not orig:
        return ''
    core_find = normalize(core) if core else ''
    pos = find_original_span(orig, core_find) if core_find else None
    if pos is None:
        snippet = orig[:radius*2]
        return _html.escape(snippet) + ('…' if len(orig) > radius*2 else '')
    s, e = pos
    s2 = max(0, s - radius)
    e2 = min(len(orig), e + radius)
    pre = orig[s2:s]; mid = orig[s:e]; post = orig[e:e2]
    res = ''
    if s2 > 0:
        res += '…'
    res += _html.escape(pre) + '<mark class="hl">' + _html.escape(mid) + '</mark>' + _html.escape(post)
    if e2 < len(orig):
        res += '…'
    return res

# ---------------- 段落装配 ----------------
def assemble_paragraphs(chunks):
    """返回 (para_norm_list, para_orig_list, global_norm, para_of, para_tags)
    global_norm 为各段 norm 拼接（以 '\n' 分隔），para_of[i]=段落索引"""
    tags = [tg for tg, _ in chunks]
    texts = [tx for _, tx in chunks]
    para_norm = [normalize(c) for c in texts]
    para_orig = texts
    global_norm_parts = []
    para_of = []
    for pi, pn in enumerate(para_norm):
        if pi > 0:
            global_norm_parts.append('\n')
            para_of.append(pi)
        global_norm_parts.append(pn)
        para_of.extend([pi]*len(pn))
    global_norm = ''.join(global_norm_parts)
    return para_norm, para_orig, global_norm, para_of, tags

def render_paragraph_with_marks(orig, mark_int, hit_ids=None):
    """mark_int: 与 orig 中'保留字符'一一对应的 int 数组(0无/1直接/2部分)。
    hit_ids: 与 mark_int 等长，标记该字符归属的命中序号（用于 data-hit 联动），可省略。
    渲染 HTML，对连续同类型标记加 <mark class=...>。"""
    kept = [bool(KEEP.match(c)) for c in orig]
    out = []
    inside = 0  # 0 none,1 direct,2 partial
    cur_hit = -1
    i = 0; j = 0  # j 走 mark_int
    while i < len(orig):
        c = orig[i]
        if kept[i]:
            m = mark_int[j] if j < len(mark_int) else 0
            hid = hit_ids[j] if (hit_ids is not None and j < len(hit_ids)) else -1
            j += 1
        else:
            m = inside
            hid = cur_hit
        if m != inside:
            if inside:
                out.append('</mark>')
            if m:
                cls = {1: 'direct', 2: 'partial', 3: 'paraphrase'}.get(m, 'partial')
                attr = f' data-hit="{hid}"' if hid >= 0 else ''
                out.append(f'<mark class="{cls}"{attr}>')
            inside = m
            cur_hit = hid if m else -1
        out.append(_html.escape(c))
        i += 1
    if inside:
        out.append('</mark>')
    return ''.join(out)

# ---------------- 句级语义近重复（改写 / 观点相似） ----------------
STOP = set('的 了 和 与 及 在 是 对 为 以 等 也 都 而 或 其 该 这 那 我们 他们 公司 中国 表示 认为 指出 '
           '显示 通过 进行 方面 目前 已经 可能 可以 一个 一种 没有 不是 以及 关于 由于 因此 所以 但是 '
           '然而 同时 此外 其中 包括 称 据 日前 近日 截至 同比 环比 分别 达到 超过 突破 增至 降至 '
           '约为 约为 亿元 万元 一年 两年 三年 年度 上半年 下半年 一季度 三季度 表示称 相关 方面 而言'.split())

def _tok(s: str):
    """jieba 分词 + 去停用词 + 过滤：保留字母数字 token 与 ≥2 字中文实词。"""
    out = []
    for t in jieba.lcut(s):
        t = t.strip().lower()
        if not t or t in STOP:
            continue
        if re.fullmatch(r'[a-z0-9]+', t):
            out.append(t)
        elif re.search(r'[\u4e00-\u9fff]', t) and len(t) >= 2:
            out.append(t)
    return out

def _split_long(seg: str, base: int):
    """长句按 ，、 进一步切分为子句，返回 [(start,end)]（全局原文坐标）。"""
    if len(normalize(seg)) <= 45:
        return [(base, base + len(seg))]
    parts = []
    cur = 0
    for m in re.finditer(r'[，,、]', seg):
        end = m.start() + 1
        clause = seg[cur:end]
        if clause.strip():
            parts.append((base + cur, base + end))
        cur = end
    tail = seg[cur:]
    if tail.strip():
        parts.append((base + cur, base + len(seg)))
    return parts or [(base, base + len(seg))]

def seg_sentences(orig: str):
    """在原文上按句末标点切句（长句再按 ，、 细分），返回全局原文坐标 [(s,e)]。"""
    res = []
    cuts = [m.start() for m in re.finditer(r'[。！？；!?;\n]', orig)]
    prev = 0
    for c in cuts:
        seg = orig[prev:c+1]
        res.extend(_split_long(seg, prev))
        prev = c + 1
    tail = orig[prev:]
    if tail.strip():
        res.extend(_split_long(tail, prev))
    return [p for p in res if p[1] > p[0]]

def detect_paraphrase(para_orig, para_norm, article_norm, para_of, src_orig_map, occupied):
    """返回改写命中列表：每条 {g0,g1,rel,sim,art_norm,src_norm,art_orig,src_orig,core_disp}。
    occupied: 已判定为直接复制/部分引用的布尔数组（用于跳过已覆盖句）。"""
    if not (HAVE_JIEBA and HAVE_SK) or not src_orig_map or not para_orig:
        return []
    # 文章句（带全局归一化坐标）
    art_sents = []
    prefix = 0
    for pi, orig in enumerate(para_orig):
        pn_len = len(para_norm[pi])
        for (s, e) in seg_sentences(orig):
            ns = len(normalize(orig[:s])); ne = len(normalize(orig[:e]))
            g0 = prefix + ns; g1 = prefix + ne
            norm_sent = normalize(orig[s:e])
            if len(norm_sent) < MIN_PARA_ART:
                continue
            # 跳过已被逐字/核心命中的句
            if g1 > g0 and sum(occupied[g0:g1]) > 0.5 * (g1 - g0):
                continue
            art_sents.append({'g0': g0, 'g1': g1, 'norm': norm_sent, 'orig': orig[s:e]})
        prefix += pn_len + 1  # +1 为段落间 '\n'
    if not art_sents:
        return []
    # 来源句
    src_sents = []
    rel_list = []
    for rel, orig_src in src_orig_map.items():
        for (s, e) in seg_sentences(orig_src):
            norm_sent = normalize(orig_src[s:e])
            if len(norm_sent) < MIN_PARA_SRC:
                continue
            src_sents.append({'rel': rel, 'norm': norm_sent, 'orig': orig_src[s:e]})
    if not src_sents:
        return []
    # TF-IDF 余弦相似度
    all_txt = [a['norm'] for a in art_sents] + [s['norm'] for s in src_sents]
    try:
        vec = TfidfVectorizer(tokenizer=_tok, token_pattern=None).fit_transform(all_txt)
    except Exception:
        return []
    A = vec[:len(art_sents)]; S = vec[len(art_sents):]
    sims = cosine_similarity(A, S)
    hits = []
    for i, a in enumerate(art_sents):
        j = int(sims[i].argmax())
        best = float(sims[i][j])
        if best < T_PARA:
            continue
        s = src_sents[j]
        shared = len(set(_tok(a['norm'])) & set(_tok(s['norm'])))
        if shared < MIN_SHARED_TOK:
            continue
        core_disp = s['orig']
        if len(core_disp) > 60:
            core_disp = core_disp[:60] + '…'
        hits.append({
            'g0': a['g0'], 'g1': a['g1'], 'rel': s['rel'], 'sim': round(best, 3),
            'art_norm': a['norm'], 'src_norm': s['norm'],
            'art_orig': a['orig'], 'src_orig': s['orig'], 'core_disp': core_disp,
        })
        if len(hits) >= MAX_PARA_PER_ART:
            break
    return hits

# ---------------- 主流程 ----------------
def process_article(folder, cross_index=None, cross_items=None):
    fpath = os.path.join(DRAFT, folder, 'index.html')
    if not os.path.exists(fpath):
        return None
    t = open(fpath, encoding='utf-8', errors='ignore').read()
    # 提取真实标题（首个 h1）
    mtitle = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S | re.I)
    title = re.sub(r'<[^>]+>', '', mtitle.group(1)).strip() if mtitle else folder
    title = html.unescape(title)
    chunks = extract_prose_from_html(t)
    para_norm, para_orig, article_norm, para_of, para_tags = assemble_paragraphs(chunks)
    total = len(article_norm)
    if total == 0:
        return {'folder': folder, 'total': 0, 'direct': 0, 'partial': 0, 'paraphrase': 0,
                'rate': 0.0, 'rate_direct': 0.0, 'rate_partial': 0.0, 'rate_paraphrase': 0.0,
                'mark': [], 'src_hits': {}, 'spans': [], 'para_norm': [], 'para_orig': [],
                'para_of': [], 'article_norm': '', 'nosource': True}

    # 收集来源
    raw_dir = os.path.join(DRAFT, folder, '原始资料')
    src_items = []
    src_files = []
    src_orig_map = {}
    if os.path.isdir(raw_dir):
        for sub, _, fs in os.walk(raw_dir):
            for f in sorted(fs):
                if f.startswith('.'):
                    continue
                ext = os.path.splitext(f)[1].lower()
                if ext not in ('.html', '.htm', '.md', '.json', '.txt'):
                    continue
                fp = os.path.join(sub, f)
                txt = extract_text_from_file(fp)
                if not txt:
                    continue
                norm = normalize(txt)
                if len(norm) < PARTIAL_CORE:
                    continue
                rel = os.path.relpath(fp, DRAFT)
                src_items.append((rel, norm))
                src_files.append(rel)
                src_orig_map[rel] = txt
    nosource = (len(src_items) == 0)

    # 来源索引
    map15, map10, src_texts = build_index(src_items) if src_items else ({}, {}, [])
    src_clean = [(sid, norm, norm) for (sid, norm) in src_items]

    # 站内扫描
    spans = []
    if src_items:
        spans = scan(article_norm, map15, map10)

    # 跨文章扫描（若有），排除自身
    cross_spans = []
    if cross_index is not None:
        self_idx = cross_index['folders'].index(folder) if folder in cross_index['folders'] else None
        cross_spans = scan(article_norm, cross_index['map15'], cross_index['map10'], exclude_idx=self_idx)

    # 改写 / 观点相似（句级语义近重复）检测：先标记已逐字/核心命中的字符，避免重复计数
    para_spans = []
    if src_items and HAVE_JIEBA and HAVE_SK:
        occ = [False]*total
        for sp in spans:
            for p in range(sp['start'], sp['end']):
                if p < total:
                    occ[p] = True
        for h in detect_paraphrase(para_orig, para_norm, article_norm, para_of, src_orig_map, occ):
            para_spans.append({
                'start': h['g0'], 'end': h['g1'], 'type': 'paraphrase',
                'srcs': set(), 'cores': [],
                'rel': h['rel'], 'sim': h['sim'],
                'art_norm': h['art_norm'], 'src_norm': h['src_norm'],
                'art_orig': h['art_orig'], 'src_orig': h['src_orig'],
                'core_disp': h['core_disp'],
            })
    spans = spans + para_spans

    # 归类统计 & 归因 & 合并标记
    direct_chars = 0
    partial_chars = 0
    paraphrase_chars = 0
    src_hit_count = Counter()
    detailed = []  # 每条命中：type, src, core, sim, 摘录
    mark = [0]*total
    for sp in spans:
        typ = sp['type']
        length = sp['end'] - sp['start']
        if typ == 'direct':
            direct_chars += length; v = 1
        elif typ == 'partial':
            partial_chars += length; v = 2
        else:
            paraphrase_chars += length; v = 3
        # 合并标记（优先级 direct > partial > paraphrase，避免重复计数）
        for p in range(sp['start'], sp['end']):
            if p < total:
                if v == 1:
                    mark[p] = 1
                elif v == 2 and mark[p] != 1:
                    mark[p] = 2
                elif v == 3 and mark[p] == 0:
                    mark[p] = 3
        # 归因与明细
        if typ in ('direct', 'partial'):
            if sp['cores']:
                core = Counter(sp['cores']).most_common(1)[0][0]
            else:
                seg = article_norm[sp['start']:sp['end']]
                core = seg[:DIRECT_LEN] if typ == 'direct' else seg[:PARTIAL_CORE]
            top_src = sorted(sp['srcs'])[0] if sp['srcs'] else None
            p0 = para_of[sp['start']] if sp['start'] < len(para_of) else 0
            art_snip = para_orig[p0][:80]
            src_snip = ''
            sim = 1.0 if typ == 'direct' else 0.0
            sid = None
            if top_src is not None and src_clean:
                sid, snorm, _ = src_clean[top_src]
                src_hit_count[sid] += 1
                pos = snorm.find(core)
                if pos >= 0:
                    s_start = max(0, pos-15); s_end = min(len(snorm), pos+len(core)+25)
                    src_snip = snorm[s_start:s_end]
                    if typ == 'partial':
                        sim = round(sim_ratio(core, snorm[pos:pos+len(core)+8]), 3)
            detailed.append({'type': typ, 'src': sid, 'core': core,
                             'art_snip': art_snip, 'src_snip': src_snip, 'sim': sim,
                             'start': sp['start'], 'end': sp['end'], 'len': length})
        else:  # paraphrase
            rel = sp.get('rel')
            sim = sp.get('sim', 0)
            if rel:
                src_hit_count[rel] += 1
            art_exc = make_excerpt(sp['art_orig'], sp['art_norm'], radius=140)
            src_exc = make_excerpt(sp['src_orig'], sp['src_norm'], radius=140)
            detailed.append({'type': 'paraphrase', 'src': rel, 'core': sp.get('core_disp', ''),
                             'sim': sim, 'start': sp['start'], 'end': sp['end'], 'len': length,
                             'art_snip': sp['art_orig'][:60], 'src_snip': sp['src_orig'][:60],
                             'art': art_exc, 'srcexc': src_exc})

    c_direct = sum(1 for m in mark if m == 1)
    c_partial = sum(1 for m in mark if m == 2)
    c_para = sum(1 for m in mark if m == 3)
    rate_direct = c_direct/total if total else 0
    rate_partial = c_partial/total if total else 0
    rate_paraphrase = c_para/total if total else 0
    rate = (c_direct + c_partial + c_para)/total if total else 0

    # 跨文章重复率
    cross_direct = 0
    cross_top = Counter()
    if cross_spans:
        for sp in cross_spans:
            if sp['type'] == 'direct':
                cross_direct += (sp['end']-sp['start'])
                if sp['srcs']:
                    cross_top[sorted(sp['srcs'])[0]] += 1
    cross_rate = cross_direct/total if total else 0

    return {
        'folder': folder, 'total': total,
        'direct': direct_chars, 'partial': partial_chars, 'paraphrase': paraphrase_chars,
        'rate': rate, 'rate_direct': rate_direct, 'rate_partial': rate_partial,
        'rate_paraphrase': rate_paraphrase, 'mark': mark,
        'src_hits': dict(src_hit_count), 'src_files': src_files,
        'spans': spans, 'detailed': detailed,
        'para_norm': para_norm, 'para_orig': para_orig, 'para_of': para_of,
        'para_tags': para_tags, 'article_norm': article_norm, 'nosource': nosource,
        'cross_rate': cross_rate, 'cross_top': dict(cross_top),
        'n_src': len(src_items), 'title': title,
        'src_orig_map': src_orig_map,
        'company': folder.split('_', 1)[1] if '_' in folder else folder,
        'date': folder.split('_', 1)[0],
    }

def build_cross_index(results):
    """用各文章正文构建跨文章索引（仅 direct 用 15 字）。"""
    items = []
    for r in results:
        if r and r.get('article_norm'):
            items.append((r['folder'], r['article_norm']))
    map15 = defaultdict(set); map10 = defaultdict(set)
    for idx, (sid, norm) in enumerate(items):
        L = len(norm)
        for i in range(0, L - DIRECT_LEN + 1):
            map15[norm[i:i+DIRECT_LEN]].add(idx)
        for i in range(0, L - PARTIAL_CORE + 1):
            sh = norm[i:i+PARTIAL_CORE]
            if n_cn(sh) >= CORE_MIN_CN:
                map10[sh].add(idx)
    return {'map15': map15, 'map10': map10, 'folders': [s for s,_ in items]}

# ---------------- 输出 ----------------
def write_summary(results):
    os.makedirs(OUT, exist_ok=True)
    # 过滤有效
    valid = [r for r in results if r]
    valid.sort(key=lambda r: -r['rate'])
    # CSV
    csv_path = os.path.join(OUT, '汇总.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['文章', '正文总字符', '来源文件数', '直接复制字符', '部分引用字符', '改写字符',
                    '直接复制率', '含疑似部分引用率', '改写/观点相似率', '综合查重率', '跨文章重复率', '主要命中来源', '备注'])
        for r in valid:
            note = ''
            if r['nosource']:
                note = '无对照原始资料'
            elif r['n_src'] == 0:
                note = '来源无可比文本'
            top = '；'.join(f"{k}({v})" for k, v in sorted(r['src_hits'].items(), key=lambda x:-x[1])[:5])
            w.writerow([r['folder'], r['total'], r['n_src'], r['direct'], r['partial'], r.get('paraphrase', 0),
                        f"{r['rate_direct']*100:.1f}%", f"{r['rate_partial']*100:.1f}%",
                        f"{r['rate_paraphrase']*100:.1f}%", f"{r['rate']*100:.1f}%", f"{r['cross_rate']*100:.1f}%", top, note])
    # MD
    md = ['# 深度调查档案室 · 文章查重汇总\n']
    md.append(f'> 生成时间口径：正文 vs 原始资料（`底稿/<日期_公司>/原始资料/`）。检测三层：① ≥15 字连续一致判「直接复制」；② ≥12 字核心命中判「部分引用」；③ 句级 TF-IDF 余弦相似度 ≥{T_PARA} 且共享实词 ≥{MIN_SHARED_TOK} 判「改写/观点相似」（抓同义替换、调序、改写，字面不完全一致）。\n')
    md.append('| 文章 | 正文字符 | 来源数 | 直接复制率 | 含疑似部分引用率 | 改写/观点相似率 | 综合查重率 | 跨文章重复率 | 备注 |')
    md.append('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |')
    for r in valid:
        note = '无对照原始资料' if r['nosource'] else ('来源无可比文本' if r['n_src']==0 else '')
        md.append(f"| [{r['folder']}](articles/{r['folder']}/index.html) | {r['total']} | {r['n_src']} | "
                  f"{r['rate_direct']*100:.1f}% | {r['rate_partial']*100:.1f}% | {r['rate_paraphrase']*100:.1f}% | "
                  f"**{r['rate']*100:.1f}%** | {r['cross_rate']*100:.1f}% | {note} |")
    md.append('\n## 说明\n')
    md.append('- **直接复制率**：与来源存在 ≥15 字连续完全一致的正文占比。')
    md.append('- **含疑似部分引用率**：另有 ≥12 字核心命中但无完整 15 字一致的「部分引用」占比。')
    md.append(f'- **改写/观点相似率**：句级（jieba 分词 + TF-IDF 余弦）相似度 ≥{T_PARA}、且共享实词 ≥{MIN_SHARED_TOK} 的正文占比，专门捕捉**同义替换、调序、改写**等字面不完全一致但意思雷同的情况（蓝标）。')
    md.append('- **综合查重率** = 直接复制率 + 含疑似部分引用率 + 改写/观点相似率（三者按字符优先级合并，不重复计数）。')
    md.append('- **跨文章重复率**：该文章与其他已发布文章存在 ≥15 字连续一致的正文占比（检测站内互抄）。')
    md.append('- 「无对照原始资料」表示该篇 `原始资料/` 为空，无法做来源查重；其跨文章重复率仍可参考。')
    md.append('\n## 重点提示（自动生成）\n')
    high = [r for r in valid if r['rate'] >= 0.05 and not r['nosource']]
    if high:
        md.append('**一、综合查重率 ≥ 5% 的篇目（建议优先人工核查来源标注与引用合规性）：**')
        for r in sorted(high, key=lambda x:-x['rate']):
            top = '；'.join(f"{k}({v})" for k,v in sorted(r['src_hits'].items(), key=lambda x:-x[1])[:3])
            md.append(f"- **{r['folder']}**：综合 {r['rate']*100:.1f}%（直接 {r['rate_direct']*100:.1f}% / 部分 {r['rate_partial']*100:.1f}%），主要来源 {top}")
    else:
        md.append('一、本次无综合查重率 ≥ 5% 的篇目。')
    nosrc = [r for r in valid if r['nosource']]
    if nosrc:
        md.append('\n**二、无对照原始资料、未做来源查重的篇目（建议回补存档后重测）：**')
        for r in nosrc:
            md.append(f"- {r['folder']}")
    cross = [r for r in valid if r['cross_rate'] >= 0.01]
    if cross:
        md.append('\n**三、跨文章重复率 ≥ 1% 的篇目（提示站内可能存在互抄或共用模板/口径）：**')
        for r in sorted(cross, key=lambda x:-x['cross_rate']):
            md.append(f"- {r['folder']}：{r['cross_rate']*100:.1f}%")
    md.append('\n> 判定原则：红色「直接复制」与黄色「部分引用」均已在单篇报告中标注具体来源文件与重合片段；'
              '是否构成「未规范标注的复制」由人工结合脚注/引文核查。合理引用（已加脚注的引文）也会被标红，属正常。')
    open(os.path.join(OUT, '汇总.md'), 'w', encoding='utf-8').write('\n'.join(md))
    return csv_path

def write_article_report(r):
    d = os.path.join(OUT, 'articles', r['folder'])
    os.makedirs(d, exist_ok=True)
    # 渲染正文带高亮
    # 合并标记数组（直接复制/部分引用/改写）已由 process_article 计算
    N = len(r['article_norm'])
    mark = r.get('mark') or [0]*N
    if len(mark) != N:
        mark = [0]*N
    # 逐段渲染
    body_html = []
    for pi, (orig, pn, tag) in enumerate(zip(r['para_orig'], r['para_norm'], r['para_tags'])):
        idxs = [k for k in range(N) if r['para_of'][k]==pi]
        seg_mark = [mark[k] for k in idxs if r['article_norm'][k] != '\n']
        if len(seg_mark) != len(pn):
            seg_mark = [0]*len(pn)
        rendered = render_paragraph_with_marks(orig, seg_mark)
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            lvl = min(int(tag[1]), 4)
            body_html.append(f'<h{lvl} class="rh">{rendered}</h{lvl}>')
        elif tag == 'blockquote':
            body_html.append(f'<blockquote>{rendered}</blockquote>')
        elif tag == 'li':
            body_html.append(f'<p class="rli">{rendered}</p>')
        else:
            body_html.append(f'<p>{rendered}</p>')
    body = '\n'.join(body_html)

    # 命中清单表
    rows = []
    for i, det in enumerate(r['detailed'], 1):
        if det['type'] == 'direct':
            typ, cls = '直接复制', 'direct'
        elif det['type'] == 'partial':
            typ, cls = '部分引用', 'partial'
        else:
            typ, cls = '改写/观点相似', 'paraphrase'
        src = det['src'] if det['src'] is not None else '（未定位来源）'
        sim = f"{det['sim']*100:.0f}%" if det.get('sim') else '-'
        rows.append(f"""<tr class="{cls}">
<td>{i}</td><td>{typ}</td><td class="src">{_html.escape(str(src))}</td>
<td>{_html.escape(det['core'][:30])}</td>
<td>{_html.escape(det.get('art_snip', '')[:60])}</td>
<td>{_html.escape(det.get('src_snip', '')[:60])}</td>
<td>{sim}</td></tr>""")
    table = '\n'.join(rows) if rows else '<p class="empty">未发现与原始资料的文字重复。</p>'

    src_list = '\n'.join(f'<li>{_html.escape(s)}</li>' for s in r['src_files']) or '<li>（无）</li>'
    cross = ''
    if r['cross_rate'] > 0:
        ct = '；'.join(f"{k}({v})" for k,v in sorted(r['cross_top'].items(), key=lambda x:-x[1])[:5])
        cross = f'<p>跨文章重复率 <b>{r["cross_rate"]*100:.1f}%</b>，主要重合文章：{_html.escape(ct)}</p>'

    note = ''
    if r['nosource']:
        note = '<p class="warn">⚠️ 本篇原始资料目录为空，未做来源查重；以下仅含跨文章重复检测。</p>'

    html_doc = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>查重报告 · {_html.escape(r['folder'])}</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",serif;max-width:920px;margin:24px auto;padding:0 18px;color:#222;line-height:1.8}}
h1{{font-size:22px;border-bottom:2px solid #333;padding-bottom:8px}}
h2{{font-size:17px;margin-top:32px;border-left:4px solid #8a1f1f;padding-left:10px}}
.metrics{{display:flex;gap:14px;flex-wrap:wrap;margin:16px 0}}
.metric{{flex:1;min-width:140px;background:#f7f4ee;border:1px solid #e3ddd0;border-radius:8px;padding:12px}}
.metric .v{{font-size:24px;font-weight:700}}
.metric .l{{font-size:12px;color:#666}}
mark.direct{{background:#ffd6d6;color:#7a0000;text-decoration:underline}}
mark.partial{{background:#fff2b8;color:#6b5200}}
mark.paraphrase{{background:#d6e4ff;color:#1a3a8a}}
p{{margin:10px 0}}
.src{{font-size:12px;color:#555;word-break:break-all}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px}}
th,td{{border:1px solid #ddd;padding:6px 8px;vertical-align:top;text-align:left}}
th{{background:#f0ece2}}
tr.direct td{{background:#fff6f6}}
tr.partial td{{background:#fffdf2}}
tr.paraphrase td{{background:#f2f7ff}}
.empty{{color:#888}}
.warn{{background:#fff4e0;border:1px solid #e0b070;padding:10px;border-radius:6px}}
.legend{{font-size:13px;color:#555;margin:8px 0}}
ul{{font-size:13px;color:#555}}
</style></head><body>
<h1>查重报告 · {_html.escape(r['folder'])}</h1>
<div class="metrics">
<div class="metric"><div class="v">{r['rate']*100:.1f}%</div><div class="l">综合查重率（来源）</div></div>
<div class="metric"><div class="v">{r['rate_direct']*100:.1f}%</div><div class="l">直接复制率</div></div>
<div class="metric"><div class="v">{r['rate_partial']*100:.1f}%</div><div class="l">含疑似部分引用率</div></div>
<div class="metric"><div class="v">{r['rate_paraphrase']*100:.1f}%</div><div class="l">改写/观点相似率</div></div>
<div class="metric"><div class="v">{r['cross_rate']*100:.1f}%</div><div class="l">跨文章重复率</div></div>
</div>
{note}
<div class="legend">图例：<mark class="direct">红底</mark> = 与来源 ≥15 字连续一致（直接复制）；<mark class="partial">黄底</mark> = 与来源 ≥12 字核心命中（部分引用）；<mark class="paraphrase">蓝底</mark> = 句级语义近重复（同义替换/改写/观点相似）。</div>
{cross}
<h2>一、正文高亮（红=直接复制 / 黄=部分引用 / 蓝=改写观点相似）</h2>
{body}
<h2>二、命中清单（标注出处来源，供人工判断重复程度）</h2>
<table><thead><tr><th>#</th><th>类型</th><th>来源文件</th><th>命中核心串</th><th>文章片段</th><th>来源片段</th><th>相似度</th></tr></thead>
<tbody>{table}</tbody></table>
<h2>三、本篇对照的来源文件</h2>
<ul>{src_list}</ul>
<p style="margin-top:30px;color:#999;font-size:12px">方法：正文仅取 p/h1-6/li/blockquote 叙事文本（剔除导航/页脚/图表/脚注）；来源取原始资料 HTML/MD/JSON 纯文本；双方归一化（保留中文+字母数字）后做子串匹配。相似度为局部序列比对比值，仅供人工参考。</p>
</body></html>"""
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html_doc)

def build_site(results):
    """生成整合站点 查重报告/index.html（两栏：左列表 / 右正文高亮 + 对比）。
    数据内联进 HTML（避免 file:// 下 fetch 跨域），正文红/黄高亮可点击联动对比卡片。"""
    os.makedirs(OUT, exist_ok=True)
    valid = [r for r in results if r]
    data = []
    for r in valid:
        N = len(r['article_norm'])
        note = ''
        if r['nosource']:
            note = '本篇「原始资料/」为空，未做来源查重；下方仅展示跨文章重复率。'
        elif r['n_src'] == 0:
            note = '来源无可比文本，未做来源查重。'
        # 命中归属数组
        hit_of = [-1]*N
        for si, sp in enumerate(r['spans']):
            for p in range(sp['start'], sp['end']):
                if p < N:
                    hit_of[p] = si
        # 正文高亮（带 data-hit）—— 合并标记数组由 process_article 计算（含改写层）
        mark = r.get('mark') or [0]*N
        if len(mark) != N:
            mark = [0]*N
        body_parts = []
        for pi in range(len(r['para_orig'])):
            orig = r['para_orig'][pi]; pn = r['para_norm'][pi]; tag = r['para_tags'][pi]
            idxs = [k for k in range(N) if r['para_of'][k] == pi]
            seg_mark = [mark[k] for k in idxs if r['article_norm'][k] != '\n']
            seg_hit = [hit_of[k] for k in idxs if r['article_norm'][k] != '\n']
            if len(seg_mark) != len(pn):
                seg_mark = [0]*len(pn); seg_hit = [-1]*len(pn)
            rendered = render_paragraph_with_marks(orig, seg_mark, seg_hit)
            if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                lvl = min(int(tag[1]), 4)
                body_parts.append(f'<h{lvl} class="rh">{rendered}</h{lvl}>')
            elif tag == 'blockquote':
                body_parts.append(f'<blockquote>{rendered}</blockquote>')
            elif tag == 'li':
                body_parts.append(f'<p class="rli">{rendered}</p>')
            else:
                body_parts.append(f'<p>{rendered}</p>')
        body_html = '\n'.join(body_parts)
        # 命中明细（含对比摘录）
        hits = []
        for si, det in enumerate(r['detailed']):
            typ = det['type']
            p0 = r['para_of'][det['start']] if det['start'] < len(r['para_of']) else 0
            # 改写层已预存 art/srcexc；其余类型用 core 现场定位
            art_exc = det.get('art')
            if art_exc is None:
                art_exc = make_excerpt(r['para_orig'][p0], det['core'], radius=150)
            src_exc = det.get('srcexc')
            if src_exc is None and det['src'] and det['src'] in r.get('src_orig_map', {}):
                src_exc = make_excerpt(r['src_orig_map'][det['src']], det['core'], radius=90)
            hits.append({
                'id': si, 'type': typ,
                'src': det['src'] or '',
                'core': det['core'],
                'sim': det['sim'],
                'art': art_exc,
                'srcexc': src_exc,
            })
        top = '；'.join(f"{k}({v})" for k, v in sorted(r['src_hits'].items(), key=lambda x:-x[1])[:5])
        data.append({
            'key': r['folder'], 'company': r['company'], 'title': r['title'], 'date': r['date'],
            'total': r['total'], 'n_src': r['n_src'],
            'rate': round(r['rate']*100, 1), 'rate_direct': round(r['rate_direct']*100, 1),
            'rate_partial': round(r['rate_partial']*100, 1), 'rate_paraphrase': round(r['rate_paraphrase']*100, 1),
            'cross_rate': round(r['cross_rate']*100, 1),
            'nosource': r['nosource'], 'note': note, 'top_sources': top,
            'body_html': body_html, 'hits': hits,
        })

    json_str = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    html_doc = TEMPLATE.replace('__DATA__', json_str)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html_doc)
    print(f"  整合站点已生成：{os.path.join(OUT, 'index.html')}（{len(data)} 篇）")

TEMPLATE = r"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>深度调查档案室 · 查重检测中心</title>
<style>
:root{--maroon:#7a1f1f;--maroon2:#9c2b2b;--ink:#23211e;--muted:#7a736a;--line:#e7e0d6;--bg:#faf8f4;--panel:#fff;
--red:#c0392b;--redbg:#ffe3e3;--redink:#8a0000;--amber:#b8860b;--amberbg:#fff3c4;--amberink:#6b5200;--green:#2f7d4f;--blue:#2f6db5;--bluebg:#dbeafe;--blueink:#1a4fa0;}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg);font-size:14px}
.topbar{display:flex;align-items:center;gap:18px;padding:0 22px;height:58px;background:linear-gradient(90deg,var(--maroon),var(--maroon2));color:#fff;position:sticky;top:0;z-index:20;box-shadow:0 2px 8px rgba(0,0,0,.12)}
.brand{font-weight:700;font-size:16px;letter-spacing:.5px;white-space:nowrap}
.stats{display:flex;gap:16px;flex:1;flex-wrap:wrap;font-size:12px;opacity:.95}
.stats b{font-size:15px;margin-right:3px}
.links a{color:#ffe;opacity:.85;text-decoration:none;font-size:12px;margin-left:12px}
.links a:hover{opacity:1;text-decoration:underline}
.main{display:flex;height:calc(100vh - 58px)}
.sidebar{width:320px;min-width:320px;border-right:1px solid var(--line);background:#f4f0e9;display:flex;flex-direction:column}
.controls{padding:12px 14px;border-bottom:1px solid var(--line);background:#efe9df}
.controls input{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;outline:none}
.controls input:focus{border-color:var(--maroon)}
.filters,.sorts{display:flex;gap:6px;margin-top:8px}
.filters button,.sorts button{flex:1;padding:6px 4px;border:1px solid var(--line);background:#fff;border-radius:7px;cursor:pointer;font-size:12px;color:var(--muted)}
.filters button.active,.sorts button.active{background:var(--maroon);color:#fff;border-color:var(--maroon)}
.list{flex:1;overflow:auto;padding:8px}
.item{padding:10px 12px;margin-bottom:8px;background:var(--panel);border:1px solid var(--line);border-radius:10px;cursor:pointer;transition:.15s}
.item:hover{border-color:#cdbfae;box-shadow:0 2px 6px rgba(0,0,0,.05)}
.item.active{border-color:var(--maroon);box-shadow:0 0 0 2px rgba(122,31,31,.12)}
.item-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.item-title{font-weight:600;font-size:14px;line-height:1.35}
.item-sub{font-size:11px;color:var(--muted);margin-top:2px}
.badge{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap}
.badge.high{background:var(--redbg);color:var(--redink)}
.badge.mid{background:var(--amberbg);color:var(--amberink)}
.badge.low{background:#e8f3ec;color:var(--green)}
.badge.none{background:#ececec;color:#888}
.badge.para{background:var(--bluebg);color:var(--blueink)}
.item-meta{font-size:11px;color:var(--muted);margin-top:6px}
.bar{height:5px;background:#eee;border-radius:4px;margin-top:7px;overflow:hidden}
.bar span{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--amber),var(--red))}
.content{flex:1;overflow:auto;padding:24px 34px 60px}
.art-head{border-bottom:2px solid var(--maroon);padding-bottom:12px;margin-bottom:6px}
.art-title{font-size:21px;font-weight:700;line-height:1.3}
.art-sub{font-size:13px;color:var(--muted);margin-top:4px}
.chips{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.chip{background:#f1ece3;border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-size:12px}
.chip b{font-size:16px;display:block}
.chip.c-rate b{color:var(--maroon)}.chip.c-direct b{color:var(--red)}.chip.c-partial b{color:var(--amber)}.chip.c-para b{color:var(--blue)}.chip.c-cross b{color:#555}
.note{margin-top:12px;background:#fff4e0;border:1px solid #e0b070;color:#7a5a18;padding:9px 12px;border-radius:8px;font-size:12.5px}
.legend{font-size:12.5px;color:var(--muted);margin:14px 0 6px;display:flex;gap:16px;align-items:center}
.legend mark{font-style:normal;padding:1px 7px;border-radius:4px}
.body{line-height:1.95;font-size:15px;max-width:860px}
.body p{margin:11px 0}
.body .rh{margin:22px 0 8px;color:var(--maroon);border-left:4px solid var(--maroon);padding-left:10px}
.body .rli{padding-left:18px;position:relative}
.body .rli:before{content:"•";position:absolute;left:4px;color:var(--maroon)}
.body blockquote{margin:12px 0;padding:8px 16px;border-left:3px solid #ccc;color:#555;background:#fafafa}
mark.direct{background:var(--redbg);color:var(--redink);border-radius:3px;cursor:pointer;padding:0 1px}
mark.partial{background:var(--amberbg);color:var(--amberink);border-radius:3px;cursor:pointer;padding:0 1px}
mark.paraphrase{background:var(--bluebg);color:var(--blueink);border-radius:3px;cursor:pointer;padding:0 1px}
mark.hl{background:var(--amberbg);color:var(--amberink);border-radius:3px;font-style:normal}
mark.flash{animation:fl .9s ease}
@keyframes fl{0%{background:#ffb3b3}100%{}}
.hitfilter button{font-size:12px;padding:5px 10px;border:1px solid var(--line);background:#fff;border-radius:7px;cursor:pointer;color:var(--muted);margin-left:6px}
.hitfilter button.active{background:var(--maroon);color:#fff;border-color:var(--maroon)}
.hbadge{font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px}
.hbadge.direct{background:var(--redbg);color:var(--redink)}
.hbadge.partial{background:var(--amberbg);color:var(--amberink)}
.hbadge.paraphrase{background:var(--bluebg);color:var(--blueink)}
.hsrc{font-size:11.5px;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all;flex:1}
.hsim{font-size:12px;color:#555;white-space:nowrap}
.hcore{font-size:12px;color:var(--muted);margin:7px 0}
.hcore b{color:var(--ink)}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px}
.cmp-col{border:1px solid var(--line);border-radius:9px;overflow:hidden;display:flex;flex-direction:column;min-height:0}
.cmp-label{font-size:11.5px;font-weight:700;padding:8px 11px;background:#f1ece3;color:var(--muted);word-break:break-all;line-height:1.4}
.cmp-col.src .cmp-label{background:#f6efe2;color:var(--amberink)}
.cmp-body{padding:13px 15px;font-size:14px;line-height:1.9;flex:1;overflow:auto;min-height:140px}
.empty{padding:40px;text-align:center;color:var(--muted)}
.hl-mark{background:#ff9d9d!important}
.hl-mark.partial{background:#ffd95e!important}
.hl-mark.paraphrase{background:#9dc6ff!important}
.cmp-pane{width:480px;min-width:480px;border-left:1px solid var(--line);background:#faf8f4;display:flex;flex-direction:column}
.cmp-head{display:flex;align-items:center;justify-content:space-between;padding:11px 14px;border-bottom:1px solid var(--line);background:#efe9df}
.cmp-head h3{margin:0;font-size:15px}
.cmp-detail{flex:1 1 auto;min-height:0;overflow:auto;padding:16px;background:#fff}
.cmp-list{flex:0 0 34%;min-height:0;overflow:auto;padding:8px;border-top:2px solid var(--line);background:#f4f0e9}
.row{display:flex;gap:9px;align-items:flex-start;padding:9px 10px;margin-bottom:7px;background:var(--panel);border:1px solid var(--line);border-radius:9px;cursor:pointer;transition:.13s}
.row:hover{border-color:var(--maroon)}
.row.active{border-color:var(--maroon);box-shadow:0 0 0 2px rgba(122,31,31,.12)}
.row.hl-row{background:#fff6ec}
.rbadge{font-size:10px;font-weight:700;padding:2px 7px;border-radius:20px;white-space:nowrap;margin-top:1px}
.rbadge.direct{background:var(--redbg);color:var(--redink)}
.rbadge.partial{background:var(--amberbg);color:var(--amberink)}
.rbadge.paraphrase{background:var(--bluebg);color:var(--blueink)}
.rbody{flex:1;min-width:0}
.rcore{font-size:12.5px;color:var(--ink);line-height:1.45}
.rsrc{font-size:10.5px;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all;margin-top:2px}
@media(max-width:1180px){.cmp-pane{width:400px;min-width:400px}.sidebar{width:280px;min-width:280px}}
@media(max-width:920px){.cmp-pane{display:none}}
</style></head><body>
<header class="topbar">
  <div class="brand">深度调查档案室 · 查重检测中心</div>
  <div class="stats" id="topstats"></div>
  <div class="links"><a href="汇总.md" target="_blank">汇总表</a><a href="方法说明.md" target="_blank">方法说明</a></div>
</header>
<div class="main">
  <aside class="sidebar">
    <div class="controls">
      <input id="search" placeholder="搜索公司 / 标题…">
      <div class="filters">
        <button data-f="all" class="active">全部</button>
        <button data-f="dup">有重复</button>
        <button data-f="para">含改写</button>
        <button data-f="nosrc">无来源</button>
      </div>
      <div class="sorts">
        <button data-s="rate" class="active">按查重率</button>
        <button data-s="date">按日期</button>
      </div>
    </div>
    <div class="list" id="list"></div>
  </aside>
  <section class="content" id="content"></section>
  <aside class="cmp-pane" id="cmp"></aside>
</div>
<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
let state = { key:null, filter:'all', sort:'rate', search:'', hitFilter:'all', selHit:null };

function badgeClass(rate, nosource){
  if(nosource) return 'none';
  if(rate>=5) return 'high';
  if(rate>=1) return 'mid';
  return 'low';
}
function renderTopStats(){
  const total=DATA.length;
  const dup=DATA.filter(d=>d.rate>0).length;
  const para=DATA.filter(d=>!d.nosource&&d.rate_paraphrase>=1).length;
  const max=DATA.reduce((a,b)=>b.rate>a.rate?b:a,{rate:0});
  const review=DATA.filter(d=>!d.nosource&&d.rate>=5).length;
  const nosrc=DATA.filter(d=>d.nosource).length;
  $('#topstats').innerHTML =
    `<span><b>${total}</b>篇</span><span><b>${dup}</b>有重复</span>`+
    `<span><b>${para}</b>含改写</span>`+
    `<span><b>${max.rate}%</b>最高</span><span><b>${review}</b>需核查</span>`+
    `<span><b>${nosrc}</b>无来源</span>`;
}
function visibleList(){
  let arr=DATA.slice();
  if(state.filter==='dup') arr=arr.filter(d=>!d.nosource&&d.rate>0);
  if(state.filter==='para') arr=arr.filter(d=>!d.nosource&&d.rate_paraphrase>=1);
  if(state.filter==='nosrc') arr=arr.filter(d=>d.nosource);
  if(state.search){ const q=state.search.toLowerCase(); arr=arr.filter(d=>(d.company+d.title+d.date).toLowerCase().includes(q)); }
  if(state.sort==='rate') arr.sort((a,b)=>b.rate-a.rate);
  else arr.sort((a,b)=>b.date.localeCompare(a.date));
  return arr;
}
function renderList(){
  const arr=visibleList();
  const list=$('#list');
  if(!arr.length){ list.innerHTML='<div class="empty">无匹配文章</div>'; return; }
  list.innerHTML=arr.map(d=>{
    const bc=badgeClass(d.rate,d.nosource);
    const w=Math.min(d.rate,10)/10*100;
    const sub=d.nosource?'无对照原始资料':(d.n_src+' 个来源');
    const bcPara = (d.nosource||d.rate<1)&&d.rate_paraphrase>=1 ? 'para' : bc;
    return `<div class="item ${d.key===state.key?'active':''}" data-key="${d.key}">
      <div class="item-top">
        <div><div class="item-title">${esc(d.company)}</div><div class="item-sub">${esc(d.title)}</div></div>
        <div class="badge ${d.nosource?'none':bcPara}">${d.nosource?'—':d.rate+'%'}</div>
      </div>
      <div class="item-meta">${d.date} · ${sub} · 直接 ${d.rate_direct}% / 部分 ${d.rate_partial}% / 改写 ${d.rate_paraphrase}%</div>
      <div class="bar"><span style="width:${w}%"></span></div>
    </div>`;
  }).join('');
}
function esc(s){ return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function selectArticle(key){
  state.key=key;
  state.selHit=null;
  renderList();
  const d=DATA.find(x=>x.key===key);
  if(!d) return;
  const content=$('#content');
  const chips=`<div class="chips">
    <div class="chip c-rate"><b>${d.rate}%</b>综合查重率</div>
    <div class="chip c-direct"><b>${d.rate_direct}%</b>直接复制</div>
    <div class="chip c-partial"><b>${d.rate_partial}%</b>含疑似部分引用</div>
    <div class="chip c-para"><b>${d.rate_paraphrase}%</b>改写/观点相似</div>
    <div class="chip c-cross"><b>${d.cross_rate}%</b>跨文章重复</div>
    <div class="chip"><b>${d.n_src}</b>来源文件数</div></div>`;
  const note=d.note?`<div class="note">⚠️ ${esc(d.note)}</div>`:'';
  content.innerHTML=`
    <div class="art-head">
      <div class="art-title">${esc(d.title)}</div>
      <div class="art-sub">${esc(d.company)} · ${d.date}</div>
      ${chips}${note}
    </div>
    <div class="legend">图例：<mark class="direct">红底</mark> = 与来源 ≥15 字连续一致（直接复制）；<mark class="partial">黄底</mark> = ≥12 字核心命中（部分引用）；<mark class="paraphrase">蓝底</mark> = 句级语义近重复（同义替换/改写/观点相似，字面不完全一致）。点击正文高亮，右栏查看文章侧与来源侧对比。</div>
    <div class="body" id="artbody">${d.body_html}</div>`;
  renderCmpPane(d);
  bindContent();
}
function bindContent(){
  const content=$('#content');
  content.querySelectorAll('#artbody mark[data-hit]').forEach(m=>{
    const id=m.getAttribute('data-hit');
    m.addEventListener('click',()=>selectHit(id,true));
    m.addEventListener('mouseenter',()=>hlCard(id,true));
    m.addEventListener('mouseleave',()=>hlCard(id,false));
  });
}
function renderCmpPane(d){
  const pane=$('#cmp');
  if(!d.hits.length){
    pane.innerHTML=`<div class="cmp-head"><h3>疑似重复明细 / 对比</h3></div>
      <div class="empty" style="padding:50px 20px">未发现与原始资料的文字重复。<br>（无来源文章仅显示跨文章重复率）</div>`;
    return;
  }
  const head=`<div class="cmp-head"><h3>疑似重复明细 / 对比（${d.hits.length} 处）</h3>
    <div class="hitfilter">
      <button data-hf="all" class="${state.hitFilter==='all'?'active':''}">全部</button>
      <button data-hf="direct" class="${state.hitFilter==='direct'?'active':''}">直接复制</button>
      <button data-hf="partial" class="${state.hitFilter==='partial'?'active':''}">部分引用</button>
      <button data-hf="paraphrase" class="${state.hitFilter==='paraphrase'?'active':''}">改写/观点相似</button>
    </div></div>`;
  pane.innerHTML=head+`<div class="cmp-detail" id="cmpDetail"><div class="empty" style="padding:34px 18px">点击正文高亮或下方任一条目，<br>在此查看文章侧与来源侧对比。</div></div>`+
    `<div class="cmp-list" id="cmpList"></div>`;
  renderCmpList(d);
  pane.querySelectorAll('.hitfilter button').forEach(b=>{
    b.addEventListener('click',()=>{
      pane.querySelectorAll('.hitfilter button').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      state.hitFilter=b.getAttribute('data-hf');
      renderCmpList(d);
    });
  });
}
function renderCmpList(d){
  const list=$('#cmpList');
  if(!list) return;
  const arr=d.hits.filter(h=>state.hitFilter==='all'||state.hitFilter===h.type);
  if(!arr.length){ list.innerHTML='<div class="empty">无该类型命中</div>'; return; }
  list.innerHTML=arr.map(h=>{
    let bcls='partial', btxt='部分';
    if(h.type==='direct'){ bcls='direct'; btxt='直接'; }
    else if(h.type==='paraphrase'){ bcls='paraphrase'; btxt='改写'; }
    return `<div class="row ${h.id===state.selHit?'active':''}" data-id="${h.id}" data-type="${h.type}">
      <span class="rbadge ${bcls}">${btxt}</span>
      <div class="rbody"><div class="rcore">${esc(h.core)}</div><div class="rsrc">${esc(h.src.split('/').pop())}</div></div>
    </div>`;
  }).join('');
  list.querySelectorAll('.row').forEach(row=>{
    const id=row.getAttribute('data-id');
    row.addEventListener('click',()=>selectHit(id,false));
    row.addEventListener('mouseenter',()=>hlMark(id,true));
    row.addEventListener('mouseleave',()=>hlMark(id,false));
  });
}
function selectHit(id,fromMark){
  state.selHit=id;
  const d=DATA.find(x=>x.key===state.key);
  if(!d) return;
  const h=d.hits.find(x=>String(x.id)===String(id));
  if(!h) return;
  if(state.hitFilter!=='all' && state.hitFilter!==h.type){ state.hitFilter='all'; renderCmpList(d); }
  document.querySelectorAll('#cmpList .row').forEach(r=>r.classList.toggle('active',r.getAttribute('data-id')===id));
  let bcls='partial', btxt='部分引用 / 观点雷同';
  if(h.type==='direct'){ bcls='direct'; btxt='直接复制'; }
  else if(h.type==='paraphrase'){ bcls='paraphrase'; btxt='改写 / 观点相似'; }
  const sim=h.type==='direct'?'逐字一致':(h.sim?Math.round(h.sim*100)+'%':'—');
  const art=h.art||'';
  const src=h.srcexc?h.srcexc:'<span style="color:#aaa">（来源原文未定位）</span>';
  const srcName=h.src?h.src.split('/').pop():'未知来源';
  $('#cmpDetail').innerHTML=`<div class="hit-top">
      <span class="hbadge ${bcls}">${btxt}</span>
      <span class="hsrc" title="${esc(h.src)}">${esc(h.src)}</span>
      <span class="hsim">相似 ${sim}</span>
    </div>
    <div class="hcore">命中核心：<b>${esc(h.core)}</b></div>
    <div class="cmp">
      <div class="cmp-col art"><div class="cmp-label">📄 文章侧（本报告）</div><div class="cmp-body">${art}</div></div>
      <div class="cmp-col src"><div class="cmp-label">🔗 来源侧：${esc(srcName)}</div><div class="cmp-body">${src}</div></div>
    </div>`;
  const marks=document.querySelectorAll('#artbody mark[data-hit="'+id+'"]');
  marks.forEach(m=>{ m.classList.add('flash'); setTimeout(()=>m.classList.remove('flash'),1000); });
  if(marks.length && fromMark===false){ marks[0].scrollIntoView({behavior:'smooth',block:'center'}); }
  const row=document.querySelector('#cmpList .row[data-id="'+id+'"]');
  if(row) row.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function hlCard(id,on){ document.querySelectorAll('#cmpList .row[data-id="'+id+'"]').forEach(r=>r.classList.toggle('hl-row',on)); }
function hlMark(id,on){
  document.querySelectorAll('#artbody mark[data-hit="'+id+'"]').forEach(m=>m.classList.toggle('hl-mark',on));
}
$('#list').addEventListener('click',e=>{ const it=e.target.closest('.item'); if(it) selectArticle(it.getAttribute('data-key')); });
$('#search').addEventListener('input',e=>{ state.search=e.target.value; renderList(); });
document.querySelectorAll('.filters button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.filters button').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.filter=b.getAttribute('data-f'); renderList();
}));
document.querySelectorAll('.sorts button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.sorts button').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); state.sort=b.getAttribute('data-s'); renderList();
}));
renderTopStats();
renderList();
const def=visibleList().find(d=>!d.nosource&&d.rate>0)||visibleList()[0];
if(def) selectArticle(def.key);
</script>
</body></html>"""


def write_method():
    txt = """# 查重测试方法说明

## 一、目标
检测每篇调查报道（底稿中 `index.html` 原文）与其「原始资料/」下网站出处（网页快照、招股书、研报等）的文字重复，
并标注来源，方便人工判断观点/数据的来源与重复程度；同时计算查重率。

## 二、文本提取
- **文章正文**：仅抽取 `<p> <h1>-<h6> <li> <blockquote>` 的叙事文本；剔除 `<script>/<style>`、
  脚注区（`footnotes`）、合规弹窗（`consent`）、导航/目录抽屉（class 含 nav/drawer/toc 等）、图表（SVG/bar/timeline 等）。
- **来源文本**：`原始资料/` 下 `.html/.htm/.md/.json/.txt`，去标签/空白后取纯文本。

## 三、归一化
双方均做归一化：仅保留中文（\u4e00-\u9fff）、数字、字母，去除标点与空白。
目的是跨"标点/空格差异"仍能识别实质重复。

## 四、匹配规则（三层）
- **① 直接复制（红）**：文章归一化文本中出现与任一来源 **连续 ≥15 字完全一致** 的子串。
- **② 部分引用（黄）**：无完整 15 字一致，但存在 **≥12 字核心** 命中来源（且该核心含 ≥6 个汉字）；视为"疑似部分引用或观点同源"。
- **③ 改写 / 观点相似（蓝）**：**句级语义近重复检测**。把文章与每个来源按原文标点切成句子，
  用 jieba 分词 + TF-IDF 余弦计算句间相似度；当某文章句与某来源句 **余弦相似度 ≥ {T_PARA}** 且 **共享实词 ≥ {MIN_SHARED_TOK}** 时，
  判为"改写/观点相似"——专门捕捉**同义替换、调序、改写**等字面不完全一致但意思雷同的情况。
  - 已被①②覆盖的句子（≥50% 字符已命中）不再计入③，避免重复计数。
  - 句长过短（文章句 < {MIN_PARA_ART} 字、来源句 < {MIN_PARA_SRC} 字）忽略，减少噪声。
- 不做"间隙桥接"：①② 的命中窗口完整计入，命中之间不相连的间隙字符不计入查重，避免虚高。

## 五、查重率口径
- 正文总字符 = 文章归一化后总字符数。
- 直接复制字符 = 所有"直接复制"段长度之和；含疑似部分引用字符 = 所有"部分引用"段长度之和；改写字符 = 所有"改写/观点相似"句覆盖字符之和。
- 三层按字符优先级合并（直接 > 部分 > 改写），每个字符只计入最高一层，**不重复计数**。
- **直接复制率 / 含疑似部分引用率 / 改写观点相似率** 分别为对应字符 / 总字符。
- **综合查重率** =（直接 + 部分 + 改写）/ 总字符。
- **跨文章重复率**：该文章与其他已发布文章 ≥15 字连续一致的占比（站内互抄检测）。

## 六、输出
- `查重报告/汇总.md` / `汇总.csv`：各篇查重率与来源清单。
- `查重报告/articles/<文章>/index.html`：单篇正文高亮 + 命中清单（来源文件、命中核心串、文章/来源片段、相似度）。
- `查重报告/方法说明.md`：本文件。

## 七、局限
1. 第③层（改写/观点相似）基于**词面 TF-IDF 余弦**，能抓同义替换、调序、局部改写；但对"完全换种说法、措辞全然不同"的深度改写仍可能漏检（需句向量 embedding 模型，属后续可扩展项）。
2. ③ 层依赖 jieba + scikit-learn，若运行环境缺失则自动跳过该层（①② 仍正常）。
3. 相似度为统计近似值，仅供参考；最终是否构成"未标注复制"由人工判定。
4. 来源需已存档于 `原始资料/`；若某篇未存档来源，则仅能给出跨文章重复率。
5. 合理引用（已加脚注的引文）也会被标红/标蓝——这正是查重目的：请人工确认其是否已规范标注。
"""
    open(os.path.join(OUT, '方法说明.md'), 'w', encoding='utf-8').write(txt)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', help='只处理含该关键字的文章')
    args = ap.parse_args()
    folders = [d for d in sorted(os.listdir(DRAFT))
               if os.path.isdir(os.path.join(DRAFT, d)) and os.path.exists(os.path.join(DRAFT, d, 'index.html'))]
    if args.only:
        folders = [f for f in folders if args.only in f]
    os.makedirs(OUT, exist_ok=True)
    print(f"待处理文章：{len(folders)} 篇")

    # 第一轮：抽取各篇正文（用于跨文章索引）
    results = []
    for fo in folders:
        r = process_article(fo)
        if r:
            results.append(r)
        print(f"  [抽取] {fo}: 正文 {r['total']} 字, 来源 {r['n_src']} 个")

    # 构建跨文章索引
    cross_index = build_cross_index(results)
    print(f"跨文章索引建成，参与文章 {len(cross_index['folders'])} 篇")

    # 第二轮：补跨文章扫描
    # 重新扫描（带 cross）
    results2 = []
    for r in results:
        r2 = process_article(r['folder'], cross_index=cross_index)
        results2.append(r2)
    results = results2

    write_method()
    csvp = write_summary(results)
    for r in results:
        write_article_report(r)
    build_site(results)
    print(f"\n完成。汇总：{csvp}")
    print(f"报告目录：{OUT}")

if __name__ == '__main__':
    main()
