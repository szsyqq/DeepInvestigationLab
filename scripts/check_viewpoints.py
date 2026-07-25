# -*- coding: utf-8 -*-
"""
观点层级查重（第四层）：角度 taxonomy + 跨篇角度重合 + 二手观点密度

与第一~三层（逐字复制 / 部分引用 / 句级改写）不同，本层不比较"字"或"句"，
而是比较"观点/论证结构"：
  1) 角度档案：每篇文章拷问了哪些分析角度（国产替代、地缘、烧钱可持续、收入质量…）
  2) 跨篇角度重合：哪些文章"都拷问了这些点"（共享分析框架）
  3) 二手观点密度：文章多少比例的论断是"据/称/认为/券商指出"式的转述，而非原创分析

依赖：纯标准库，受管/系统 Python 均可运行。
输出：观点查重/角度档案.json、观点查重/汇总.md
"""
import os, re, json, glob, html
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(BASE, "底稿")
OUT = os.path.join(BASE, "观点查重")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. 角度 taxonomy：深度报道常见分析维度 + 关键词
# ---------------------------------------------------------------------------
ANGLES = [
    ("收入质量", ["收入", "营收", "营收增速", "收入结构", "收入确认", "营收下滑", "收入增长", "营收增长"]),
    ("利润与盈利", ["利润", "毛利率", "净利率", "盈利能力", "盈利质量", "净利", "亏损", "扭亏"]),
    ("现金流", ["现金流", "经营性现金流", "自由现金流", "造血", "现金流转"]),
    ("烧钱与可持续", ["烧钱", "研发投入", "研发烧钱", "盈亏平衡", "可持续", "现金流断裂", "现金储备", "烧钱速度"]),
    ("估值合理性", ["估值", "市盈率", "市净率", "市销率", "市值", "估值泡沫", "估值高", "贵不贵", "估值逻辑"]),
    ("国产替代", ["国产替代", "自主可控", "进口替代", "国产化", "国产"]),
    ("地缘博弈", ["地缘", "制裁", "出口管制", "中美", "博弈", "供应链安全", "卡脖子", "实体清单", "关税"]),
    ("行业周期", ["周期", "行业周期", "下行周期", "周期退潮", "产能过剩", "供需错配", "景气下行"]),
    ("客户集中", ["客户集中", "大客户", "单一客户", "前五大客户", "依赖客户", "最大客户"]),
    ("供应链依赖", ["供应链", "供应商", "断供", "上游依赖", "原材料依赖", "备货"]),
    ("政策与监管", ["政策", "补贴", "政府补助", "监管", "牌照", "合规风险", "处罚", "政策依赖"]),
    ("技术自主", ["自研", "核心技术", "专利", "知识产权", "技术路线", "架构", "自研芯片"]),
    ("竞争格局", ["竞争", "市场份额", "市占率", "对手", "内卷", "价格战", "集中度", "竞争格局"]),
    ("治理与股权", ["股权", "实控人", "治理", "关联交易", "控制权", "管理层", "股权结构"]),
    ("债务与杠杆", ["债务", "杠杆", "负债率", "偿债能力", "借款", "短债", "现金流偿债", "资产负债率"]),
    ("增长天花板", ["天花板", "增长瓶颈", "市场空间", "渗透率", "见顶", "放缓", "增长放缓"]),
    ("商业化落地", ["商业化", "变现", "落地", "规模化", "量产", "订单", "商业化落地"]),
    ("人才与组织", ["人才", "团队", "流失", "组织", "裁员", "招聘", "核心团队"]),
    ("数据真实性", ["数据", "统计口径", "披露", "粉饰", "水分", "真实性", "审计", "财务数据"]),
    ("需求与景气", ["需求", "景气", "订单下滑", "终端需求", "下游", "需求疲软", "需求旺盛"]),
    ("安全与风险", ["风险", "隐患", "暴雷", "危机", "脆弱性", "风险点", "不确定性"]),
]

# 二手观点（转述/归因）标记
SECOND_HAND_PATTERNS = [
    re.compile(r"据.{0,18}(称|表示|报道|透露|指出|称[，。])"),
    re.compile(r"(援引|引述)"),
    re.compile(r"(业内人士|市场人士|券商|机构|分析师|专家|有分析|知情人士|业内人士称)"),
    re.compile(r"[一-龥]{2,10}(称|表示|认为|指出|透露|分析|坦言|坦言)"),
    re.compile(r"[一-龥]{2,12}(在|发布的|研报|报告)(其|中|称|表示|指出|认为)"),
    re.compile(r"(数据显示|统计显示|据计算|据测算)"),
]

SKIP_CLASS = re.compile(r"(nav|header|footer|footnote|consent|chart|sidebar|toc|disclaimer|toolbar|menu|breadcrumb)", re.I)
BODY_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "td", "caption"}


def extract_prose(path):
    """抽取正文散文（剔除导航/页脚/脚注/图表/弹窗），返回纯净文本。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    # 移除 script / style
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)

    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
            self.skip = 0
            self.cur = []

        def handle_starttag(self, tag, attrs):
            cls = " ".join(v for k, v in attrs if k == "class")
            if SKIP_CLASS.search(cls):
                self.skip += 1
            if tag in BODY_TAGS and self.skip == 0:
                self.cur = []

        def handle_endtag(self, tag):
            if SKIP_CLASS.search(""):
                pass
            if tag in BODY_TAGS and self.skip == 0:
                if self.cur:
                    self.parts.append("".join(self.cur))
                    self.cur = []
            # 简化处理：根据 class 栈深度粗略恢复（不完美但够用）
            if self.skip > 0 and tag not in BODY_TAGS:
                # 无法精确配对，仅当遇到明显的 footer/nav 容器结束减少
                pass

        def handle_data(self, data):
            if self.skip == 0:
                self.cur.append(data)

    # 简化：用更稳妥的方式——基于标签配对
    p = P()
    # 由于 HTMLParser 难以精确配对嵌套 skip，改用正则分块：
    # 先把带 skip class 的容器整体挖掉
    def strip_block(m):
        return " "
    # 移除注释
    raw = re.sub(r"<!--[\s\S]*?-->", " ", raw)
    # 移除已知 skip 容器：<tag ... class="...skip...">...</tag>
    for cls_kw in ["footnotes", "consent", "nav", "top-bar", "masthead", "site-foot",
                   "footer", "chart", "sidebar", "toc", "disclaimer", "toolbar",
                   "breadcrumb", "back-top", "internal-banner"]:
        raw = re.sub(r"<([a-zA-Z0-9]+)(\s[^>]*class=\"[^\"]*%s[^\"]*\"[\s\S]*?)</\1>" % cls_kw,
                     " ", raw, flags=re.I)
    # 抽取正文标签文本
    texts = []
    for tag in BODY_TAGS:
        for m in re.finditer(r"<%s[\s>][\s\S]*?</%s>" % (tag, tag), raw, flags=re.I):
            t = re.sub(r"<[^>]+>", "", m.group(0))
            t = html.unescape(t).strip()
            if len(t) >= 4:
                texts.append(t)
    return "\n".join(texts)


def normalize(text):
    return re.sub(r"[^\u4e00-\u9fff0-9a-zA-Z]", "", text)


def angle_profile(prose):
    norm = normalize(prose)
    prof = {}
    for name, kws in ANGLES:
        occ = 0
        distinct = 0
        for kw in kws:
            c = norm.count(normalize(kw))
            if c:
                occ += c
                distinct += 1
        if occ >= 3 or distinct >= 2:
            prof[name] = occ
    return prof


def second_hand_ratio(prose):
    # 按句切分
    sents = re.split(r"[。！？!?；;\n]+", prose)
    sents = [s.strip() for s in sents if len(s.strip()) >= 6]
    if not sents:
        return 0.0, 0, 0, []
    relayed = []
    for s in sents:
        for pat in SECOND_HAND_PATTERNS:
            if pat.search(s):
                relayed.append(s)
                break
    total = len(sents)
    return (len(relayed) / total, len(relayed), total, relayed[:8])


def main():
    files = sorted(glob.glob(os.path.join(DRAFT, "*", "index.html")))
    results = {}
    for path in files:
        folder = os.path.basename(os.path.dirname(path))
        prose = extract_prose(path)
        prof = angle_profile(prose)
        ratio, n_rel, n_tot, samples = second_hand_ratio(prose)
        results[folder] = {
            "angles": prof,
            "angle_count": len(prof),
            "second_hand_ratio": round(ratio, 3),
            "relayed_sentences": n_rel,
            "total_sentences": n_tot,
            "relayed_samples": samples,
            "prose_chars": len(prose),
        }
        print(f"[ok] {folder}: angles={len(prof)} 2nd={ratio:.1%} ({n_rel}/{n_tot})")

    # 跨篇角度重合
    folders = list(results.keys())
    overlaps = []
    for i in range(len(folders)):
        for j in range(i + 1, len(folders)):
            a, b = folders[i], folders[j]
            sa, sb = set(results[a]["angles"]), set(results[b]["angles"])
            if not sa or not sb:
                continue
            inter = sa & sb
            union = sa | sb
            jac = len(inter) / len(union)
            if len(inter) >= 5 or jac >= 0.4:
                overlaps.append({
                    "a": a, "b": b, "jaccard": round(jac, 2),
                    "shared": sorted(inter), "shared_count": len(inter)
                })
    overlaps.sort(key=lambda x: (-x["shared_count"], -x["jaccard"]))

    # 角度共现频次（哪些角度被多篇文章共同拷问）
    angle_articles = defaultdict(list)
    for f, r in results.items():
        for ang in r["angles"]:
            angle_articles[ang].append(f)
    angle_freq = {ang: sorted(fs) for ang, fs in angle_articles.items()}
    angle_freq = dict(sorted(angle_freq.items(), key=lambda x: -len(x[1])))

    out = {
        "results": results,
        "overlaps": overlaps,
        "angle_frequency": angle_freq,
    }
    with open(os.path.join(OUT, "角度档案.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ---- 汇总 md ----
    lines = []
    lines.append("# 观点层级查重 · 系统层汇总\n")
    lines.append("> 方法：对每篇正文抽取散文，按 21 个常见分析角度做关键词命中（角度档案），"
                 "再算跨篇角度重合（Jaccard + 共享角度清单 = \"他们都拷问了这些点\"）；"
                 "另统计二手观点密度（据/称/认为/券商指出等归因标记句占比）。\n")
    lines.append("\n## 一、各篇角度档案（拷问了哪些点）\n")
    for f in sorted(results, key=lambda x: -results[x]["angle_count"]):
        r = results[f]
        angs = "、".join(f"{k}({v})" for k, v in sorted(r["angles"].items(), key=lambda x: -x[1]))
        lines.append(f"- **{f}** — 角度数 {r['angle_count']}；二手观点 {r['second_hand_ratio']:.1%}（{r['relayed_sentences']}/{r['total_sentences']} 句）\n  - {angs}")
    lines.append("\n## 二、跨篇角度重合（“他们都拷问了这些点”）\n")
    for o in overlaps[:40]:
        lines.append(f"- **{o['a']}** ⇄ **{o['b']}** — 共享 {o['shared_count']} 个角度（Jaccard {o['jaccard']}）\n  - {('、'.join(o['shared']))}")
    if not overlaps:
        lines.append("（无达到阈值的跨篇重合）")
    lines.append("\n## 三、角度共现频次（被多少篇共同拷问）\n")
    for ang, fs in angle_freq.items():
        if len(fs) >= 3:
            lines.append(f"- **{ang}**：{len(fs)} 篇 — {('、'.join(fs))}")
    lines.append("\n## 四、二手观点密度排序（转述占比高 = 越可能是“抄别人观点”）\n")
    for f in sorted(results, key=lambda x: -results[x]["second_hand_ratio"]):
        r = results[f]
        if r["second_hand_ratio"] >= 0.10:
            lines.append(f"- **{f}** — {r['second_hand_ratio']:.1%}（{r['relayed_sentences']}/{r['total_sentences']}）")
            for s in r["relayed_samples"][:3]:
                lines.append(f"  - 例：{s[:60]}")
    lines.append("\n---\n*系统层为确定性算法输出；定性“共享叙事框架/原创性评估”见 LLM 提取层。*")

    with open(os.path.join(OUT, "汇总.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[done] 输出 -> 观点查重/角度档案.json, 观点查重/汇总.md")
    print(f"       文章 {len(results)} 篇，跨篇重合 {len(overlaps)} 对")


if __name__ == "__main__":
    main()
