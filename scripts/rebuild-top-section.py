#!/usr/bin/env python3
"""
重写每页的 body 顶部结构（internal-banner → top-bar → progress → back-top → masthead）。
不依赖 regex 替换已有内容，而是精确定位并重建整个顶部区块。
"""
import os

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

PAGE_CITIES = {
    "bmw": "慕尼黑", "seres": "重庆 / 深圳", "jiantao": "香港",
    "suiyuan": "上海", "changxin": "合肥", "deepseek": "杭州",
    "chowsangsang": "香港", "yushu": "深圳", "zhipu": "香港",
    "xiaohongshu": "上海", "wuliangye": "宜宾",
}

PAGE_READING = {
    "bmw": "约 12 分钟阅读", "seres": "约 13 分钟阅读", "jiantao": "约 13 分钟阅读",
    "suiyuan": "约 18 分钟阅读", "changxin": "约 21 分钟阅读", "deepseek": "约 14 分钟阅读",
    "chowsangsang": "约 28 分钟阅读", "yushu": "约 54 分钟阅读", "zhipu": "约 20 分钟阅读",
    "xiaohongshu": "约 14 分钟阅读", "wuliangye": "约 8 分钟阅读",
}

H = "../../index.html"  # home href

def canonical_top(city, reading):
    """生成标准顶部 HTML 块"""
    return f'''<div class="internal-banner"><span>●</span>内部资料 · 仅供研究参考 · 请勿外传</div>
<div class="top-bar">
  <div class="top-bar-inner">
    <div class="top-bar-left">
      <a class="home" href="{H}">返回首页</a>
      <span class="sep"></span>
      <span class="time" id="readTime">{reading}</span>
    </div>
    <div class="top-bar-right">
      <span class="pos" id="tracker">导语</span>
      <span class="sep"></span>
      <button class="toc nav-toggle" onclick="toggleNav()">≡ 目录</button>
    </div>
  </div>
</div>
<div class="progress-bar" id="progress"></div>
<button class="back-top" id="backTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="回到顶部">↑</button>
<div class="masthead">
<div class="brand"><a href="{H}">调查团队 &nbsp;|&nbsp; <span class="accent">THE INVESTIGATION</span></a></div>
<div class="date">2026年7月 · {city} <a class="home-link" href="{H}">档案室</a></div>
</div>'''

for page in PAGE_CITIES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find <body> start
    body_start = content.find('<body>')
    if body_start < 0:
        body_start = content.find('<body ')
    if body_start < 0:
        print(f"[FAIL] {page} - no <body> found")
        continue
    
    # Find the masthead close (</div>) after <div class="masthead">
    masthead_start = content.find('<div class="masthead">', body_start)
    if masthead_start < 0:
        print(f"[FAIL] {page} - no masthead found")
        continue
    
    # Find the masthead close - </div> after the masthead content
    masthead_close = content.find('</div>', masthead_start + 20)
    # The masthead has 2 inner divs, so we need the 2nd </div> which closes .masthead
    # First </div> closes .brand, second </div> closes .date, third </div> closes .masthead
    # Actually, let's just find the FULL masthead block
    # Structure: <div class="masthead">\n<div class="brand">...</div>\n<div class="date">...</div>\n</div>
    # The closing </div> of .masthead is the 3rd </div> after the opening
    mh_first_close = content.find('</div>', masthead_start + 20)  # closes .brand
    mh_second_close = content.find('</div>', mh_first_close + 6)  # closes .date
    mh_third_close = content.find('</div>', mh_second_close + 6)  # closes .masthead
    
    masthead_end = mh_third_close + 6  # length of '</div>'
    
    # Now we know: body_start to masthead_end should be replaced
    # But we want to keep the </body> closing tag and everything after it
    
    body_end_open = content.find('</body>', masthead_end)
    
    # Build replacement
    canonical = canonical_top(PAGE_CITIES[page], PAGE_READING[page])
    
    # Everything after masthead stays
    after_masthead = content[masthead_end:]
    
    new_content = content[:body_start] + '<body>\n' + canonical + '\n' + after_masthead
    
    # Verify: count open and close body tags
    open_body = new_content.count('<body>') + new_content.count('<body ')
    close_body = new_content.count('</body>')
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"[DONE] {page} (body tags: {open_body} open, {close_body} close)")

print("\n✅ 全部重建完成")
