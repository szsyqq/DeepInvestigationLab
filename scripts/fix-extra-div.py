#!/usr/bin/env python3
"""修复 standardize-chrome.py 导致的额外 </div> 问题"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu", "wuliangye"]

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Bug: extra </div> after top-bar close, before progress-bar
    # Pattern: </div>\n</div>\n</div>\n<div class="progress-bar"
    # Fix:   </div>\n</div>\n<div class="progress-bar"
    old = '</div>\n</div>\n</div>\n<div class="progress-bar"'
    new = '</div>\n</div>\n<div class="progress-bar"'
    new_content = content.replace(old, new)
    
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[DONE] {page} - removed extra </div>")
    else:
        print(f"[SKIP] {page} - no extra </div> found")

print("✅ Done")
