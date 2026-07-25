#!/usr/bin/env python3
"""
==========================
导航栏 UI 范式抽离工具
==========================
定义所有页面顶部结构的【权威模板】。
运行此脚本 = 将模板同步到所有报告页。
以后改导航栏只需改这里的模板定义再跑一次。
==========================
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu", "wuliangye"]

# ========== 权威模板定义 ========== #

def top_bar_html(home_href="../../index.html", reading_time=""):
    """统一顶栏模板"""
    time_html = f'\n      <span class="sep"></span>\n      <span class="time" id="readTime">{reading_time}</span>' if reading_time else ''
    return f'''<div class="top-bar">
  <div class="top-bar-inner">
    <div class="top-bar-left">
      <a class="home" href="{home_href}">返回首页</a>{time_html}
    </div>
    <div class="top-bar-right">
      <span class="pos" id="tracker">导语</span>
      <span class="sep"></span>
      <button class="toc nav-toggle" onclick="toggleNav()">≡ 目录</button>
    </div>
  </div>
</div>'''

def masthead_html(home_href="../../index.html", city=""):
    """统一报头栏模板"""
    city_html = f" · {city}" if city else ""
    return f'''<div class="masthead">
<div class="brand"><a href="{home_href}">调查团队 &nbsp;|&nbsp; <span class="accent">THE INVESTIGATION</span></a></div>
<div class="date">2026年7月{city_html} <a class="home-link" href="{home_href}">档案室</a></div>
</div>'''

BACKTOP_HTML = '<button class="back-top" id="backTop" onclick="window.scrollTo({top:0,behavior:\'smooth\'})" title="回到顶部">↑</button>'

# ========== 页面专属数据 ========== #

PAGE_DATA = {
    "bmw":        {"reading_time": "约 12 分钟阅读", "city": "慕尼黑",      "home": "../../index.html"},
    "seres":      {"reading_time": "约 13 分钟阅读", "city": "重庆 / 深圳", "home": "../../index.html"},
    "jiantao":    {"reading_time": "约 13 分钟阅读", "city": "香港",        "home": "../../index.html"},
    "suiyuan":    {"reading_time": "约 18 分钟阅读", "city": "上海",        "home": "../../index.html"},
    "changxin":   {"reading_time": "约 21 分钟阅读", "city": "合肥",        "home": "../../index.html"},
    "deepseek":   {"reading_time": "约 14 分钟阅读", "city": "杭州",        "home": "../../index.html"},
    "chowsangsang":{"reading_time": "约 28 分钟阅读", "city": "香港",       "home": "../../index.html"},
    "yushu":      {"reading_time": "约 54 分钟阅读", "city": "深圳",        "home": "../../index.html"},
    "zhipu":      {"reading_time": "约 20 分钟阅读", "city": "香港",        "home": "../../index.html"},
    "xiaohongshu":{"reading_time": "约 14 分钟阅读", "city": "上海",        "home": "../../index.html"},
    "wuliangye":  {"reading_time": "约 8 分钟阅读",  "city": "宜宾",        "home": "../../index.html"},
}

# ========== 处理 ========== #

def replace_topbar(content, page):
    """替换页面中的 top-bar HTML。匹配完整的 3 层 closing div。"""
    data = PAGE_DATA[page]
    new_top = top_bar_html(data["home"], data["reading_time"])
    
    # Match: <div class="top-bar">\n  <div class="top-bar-inner">...3层关闭...
    pattern = r'<div class="top-bar">\s*<div class="top-bar-inner">.*?</div>\s*</div>\s*</div>'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        content = content[:m.start()] + new_top + content[m.end():]
        return content, True
    return content, False

def replace_masthead(content, page):
    """替换或添加 masthead HTML"""
    data = PAGE_DATA[page]
    new_mast = masthead_html(data["home"], data["city"])
    
    # Match: <div class="masthead"> ... </div> (with exactly 2 inner divs)
    pattern = r'<div class="masthead">.*?</div>\s*</div>\s*</div>'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        # Replace existing masthead
        content = content[:m.start()] + new_mast + content[m.end():]
    else:
        # Insert after progress bar or back-top
        # Find a good insertion point: after back-top or before sidenav/container
        insert = re.search(r'id="backTop".*?</button>', content)
        if insert:
            pos = insert.end()
            content = content[:pos] + '\n' + new_mast + content[pos:]
        else:
            # Fallback: before container
            insert = re.search(r'<div class="sidenav"', content)
            if not insert:
                insert = re.search(r'<div class="container"', content)
            if insert:
                pos = insert.start()
                content = content[:pos] + new_mast + '\n' + content[pos:]
            else:
                return content, False
    return content, True

def replace_backtop(content):
    """统一 back-top HTML"""
    m = re.search(r'<button class="back-top".*?</button>', content)
    if m:
        content = content[:m.start()] + BACKTOP_HTML + content[m.end():]
        return content, True
    return content, False

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    changes = []
    
    # 1. Top-bar
    content, ok = replace_topbar(content, page)
    if ok: changes.append("top-bar")
    
    # 2. Masthead
    content, ok = replace_masthead(content, page)
    if ok: changes.append("masthead")
    
    # 3. Back-top
    content, ok = replace_backtop(content)
    if ok: changes.append("back-top")
    
    if changes:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[DONE] {page}: {', '.join(changes)}")
    else:
        print(f"[SKIP] {page} - no changes")

print("\n✅ 范式同步完成")
