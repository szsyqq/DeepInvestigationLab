#!/usr/bin/env python3
"""
移除所有页面中 .nav-toggle 的视觉样式（position:fixed 等），
该 class 应只作为 JS 事件代理钩子使用，不附带任何 CSS 样式。
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu", "wuliangye"]

# 匹配完整的 .nav-toggle{...} 规则（含 position:fixed）
NAV_TOGGLE_FULL = re.compile(
    r'\.nav-toggle\{position:fixed;[^}]*\}'
)

# 匹配 @media 中的 .nav-toggle{top:...;right:...} 覆盖规则
NAV_TOGGLE_MEDIA = re.compile(
    r'\.nav-toggle\{top:[^;]*;right:[^;]*[^}]*\}'
)

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    changes = 0
    
    # Remove full .nav-toggle{position:fixed...} rules
    new_content, n1 = NAV_TOGGLE_FULL.subn('', content)
    changes += n1
    
    # Remove media query overrides (top:12px;right:12px...)
    new_content, n2 = NAV_TOGGLE_MEDIA.subn('', new_content)
    changes += n2
    
    # Also remove standalone .nav-toggle:hover rule (keep only if .nav-toggle is still used)
    # But .nav-toggle:hover is harmless without .nav-toggle, but let's clean it
    new_content, n3 = re.subn(r'\.nav-toggle:hover\{[^}]*\}', '', new_content)
    changes += n3
    
    if changes > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[DONE] {page} - removed {changes} .nav-toggle CSS rules")
    else:
        print(f"[SKIP] {page} - no .nav-toggle CSS found")

print("\n✅ All pages cleaned")
