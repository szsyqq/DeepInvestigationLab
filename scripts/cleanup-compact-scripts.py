#!/usr/bin/env python3
"""
移除所有页面末尾冗余的 inline compact toggle 脚本，
这些功能已由 global.js 统一接管。
同时修复旧页面中已经变黄字（red变灰）的冗余段。
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu"]

# 匹配标准 inline compact 脚本（含 ct() + tracker 点击）
CT_PATTERN = re.compile(
    r'<script>function\s+ct\(\)\{document\.body\.classList\.toggle\("compact",window\.scrollY>80\)\}'
    r'window\.addEventListener\("scroll",ct,\{passive:true\}\);ct\(\);'
    r'var\s+tr=document\.getElementById\("tracker"\);'
    r'if\(tr\)\{tr\.classList\.add\("nav-toggle"\);tr\.style\.cursor="pointer";'
    r'tr\.onclick=function\(e\)\{e\.stopPropagation\(\);var\s+n=document\.querySelector\("\.sidenav"\);'
    r'if\(n\)n\.classList\.toggle\("open"\)\}\}</script>'
)

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove CT pattern
    new_content = CT_PATTERN.sub('', content)
    
    # Also handle wuliangye-style compact scripts
    wly_pattern = re.compile(
        r'<script>if\(window\.scrollY>80\)\{document\.body\.classList\.add\(\'compact\'\)\}else\{document\.body\.classList\.remove\(\'compact\'\)\}</script>'
    )
    new_content = wly_pattern.sub('', new_content)
    
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[DONE] {page} - removed inline compact script")
    else:
        print(f"[SKIP] {page} - no inline compact script found")

print("\n✅ All pages cleaned")
