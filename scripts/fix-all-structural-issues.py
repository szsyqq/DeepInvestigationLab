#!/usr/bin/env python3
"""
全面修复所有页面在 standardization 过程中产生的结构性损坏。
移除: 孤立的 </div>、冗余 <div class="toolbar">、确保 top-bar/masthead/back-top 结构正确。
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

def clean_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # 1. Remove orphan </div> that appear right before <div class="masthead">
    # Pattern: back-top close followed by blank lines + </div>\n</div> + blank lines + masthead
    # Or: progress-bar followed by blank lines + </div>\n</div> + blank lines + masthead
    patterns = [
        # After back-top button: remove extra </div>\n</div> before masthead
        (r'(<button class="back-top"[^>]*></button>)\s*\n\s*</div>\s*\n\s*</div>\s*\n\s*(<div class="masthead">)', 
         r'\1\n\n\2'),
        # After progress bar (no back-top): remove extra </div> before masthead  
        (r'(<div class="progress-bar"[^>]*></div>)\s*\n\s*</div>\s*\n\s*(<div class="masthead">)',
         r'\1\n\2'),
        # After progress bar: remove extra </div>\n</div> before masthead
        (r'(<div class="progress-bar"[^>]*></div>)\s*\n\s*</div>\s*\n\s*</div>\s*\n\s*(<div class="masthead">)',
         r'\1\n\n\2'),
        # Remove <div class="toolbar">...</div> before masthead
        (r'\s*\n\s*<div class="toolbar">\s*\n\s*</div>', ''),
        # Remove isolated </div> right before <div class="masthead"
        (r'\s*\n\s*</div>\s*\n\s*<div class="masthead">', '\n\n<div class="masthead">'),
        # Remove isolated </div> right after <div class="masthead"> close
        (r'</div>\s*\n\s*</div>\s*\n\s*(<div class="sidenav"|<div class="container")', 
         r'</div>\n\n\1'),
    ]
    
    for pat, repl in patterns:
        content = re.sub(pat, repl, content, flags=re.DOTALL)
    
    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

for page in ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu", "wuliangye"]:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        continue
    if clean_file(path):
        print(f"[DONE] {page}")
    else:
        print(f"[SKIP] {page}")

print("✅ All fixed")
