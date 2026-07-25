#!/usr/bin/env python3
"""
将 .bar-fill 的 inline style="width:XX%" 转换为 data-w="XX"，
让 IntersectionObserver 驱动的入场动效生效。
处理两种情形：
  a) style="width:70%"            → data-w="70"
  b) style="width:75%;height:100%;..."  → style="height:100%;..." data-w="75"
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu"]

def convert_style(m):
    """Convert bar-fill inline style with width to data-w."""
    full = m.group(0)
    style_attr = m.group(1)  # the value of style="..."
    
    # Extract width percentage
    wm = re.search(r'width:\s*([\d.]+)%', style_attr)
    if not wm:
        return full  # no width, skip
    
    pct = wm.group(1)
    
    # Remove width:XX%; from the style (with semicolon or end)
    cleaned = re.sub(r'width:\s*[\d.]+%;?\s*', '', style_attr).strip()
    # Also handle ";width:XX%" (semicolon before width)
    cleaned = re.sub(r';\s*width:\s*[\d.]+%', '', cleaned).strip()
    
    if cleaned:
        # Has remaining styles: keep style="" and add data-w
        result = full.replace(f'style="{style_attr}"', f'style="{cleaned}"')
        result = result.replace('class="', f'data-w="{pct}" class="')
    else:
        # Only width: remove style attr entirely, add data-w
        result = full.replace(f' style="{style_attr}"', '')
        result = result.replace('class="', f'data-w="{pct}" class="')
    
    return result

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Match .bar-fill elements with style attributes containing width
    # Pattern: <div class="bar-fill ..." style="...width:XX%..."> 
    pattern = r'<div class="bar-fill[^"]*"[^>]*style="([^"]*)"[^>]*>'
    new_content = re.sub(pattern, convert_style, content)
    
    count = content.count('<div class="bar-fill') - new_content.count('<div class="bar-fill')
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"[DONE] {page} - bar-fill width→data-w converted")

print("\n✅ All bar animations fixed")
