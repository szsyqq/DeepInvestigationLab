#!/usr/bin/env python3
"""
统一修复9篇报告页面的CSS/JS问题：
1. .reveal → .js 降级模式
2. 添加 document.documentElement.classList.add('js')
3. 标记是否已有 sidenav
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu"]

OLD_REVEAL = ".reveal{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}"
NEW_REVEAL = ".reveal{opacity:1;transform:none}.js .reveal{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}"

OLD_REVEAL_VISIBLE = ".reveal.visible{opacity:1;transform:translateY(0)}"
NEW_REVEAL_VISIBLE = ".js .reveal.visible{opacity:1;transform:translateY(0)}"

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    changed = []
    
    # 1. Replace .reveal CSS
    if OLD_REVEAL in content:
        content = content.replace(OLD_REVEAL, NEW_REVEAL)
        changed.append("reveal CSS")
    else:
        print(f"[WARN] {page} - .reveal pattern not found (may already be updated)")
    
    # 2. Replace .reveal.visible CSS
    if OLD_REVEAL_VISIBLE in content:
        content = content.replace(OLD_REVEAL_VISIBLE, NEW_REVEAL_VISIBLE)
        changed.append("reveal.visible CSS")
    
    # 3. Check/add document.documentElement.classList.add('js')
    if "document.documentElement.classList.add('js')" not in content:
        # Find the first <script> block that contains var obs= or var reveals=
        # and add the js class line right after it
        script_patterns = [
            r'(<script>\s*)var\s+obs\s*=\s*new\s+IntersectionObserver',
            r'(<script>\s*)var\s+reveals\s*=\s*document\.querySelectorAll',
            r'(<script>\s*)var\s+progress\s*=\s*document\.getElementById',
        ]
        for pat in script_patterns:
            m = re.search(pat, content)
            if m:
                insert_pos = m.start(1) + len(m.group(1))
                js_line = "document.documentElement.classList.add('js');\n"
                content = content[:insert_pos] + js_line + content[insert_pos:]
                changed.append("classList.add('js')")
                break
        else:
            print(f"[WARN] {page} - could not find script block to inject js class")
    
    # 4. Check for sidenav
    has_sidenav = '<div class="sidenav"' in content
    if has_sidenav:
        changed.append(f"already has sidenav ✅")
    else:
        changed.append(f"MISSING sidenav ❌")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[DONE] {page}: {', '.join(changed)}")

print("\n✅ All pages processed")
