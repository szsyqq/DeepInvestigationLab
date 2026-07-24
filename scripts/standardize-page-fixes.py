#!/usr/bin/env python3
"""
统一修复所有文章页的两个问题：
1. 移除 .reading-time-fab 残留CSS（源头已在global.js中删除注入）
2. 在所有页面添加 html{overflow-x:hidden} 防止水平滑动
"""
import re, os, glob

REPORTS_DIR = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    changes = []

    # 1. Remove .reading-time-fab CSS block
    fab_pattern = r'/\*.*?阅读时间.*?\*/\s*\.reading-time-fab\{[^}]+\}\s*(@media[^\{]*\{[^}]*\.reading-time-fab\{[^}]+\}\})?\s*'
    html, n = re.subn(fab_pattern, '\n', html)
    if n > 0:
        changes.append(f"removed .reading-time-fab CSS ({n} match)")

    # Simpler fallback: remove .reading-time-fab CSS by line
    lines = html.split('\n')
    new_lines = []
    skip = False
    in_fab_block = False
    fab_end = 0
    for i, line in enumerate(lines):
        if '.reading-time-fab{' in line:
            in_fab_block = True
            fab_end = 1
            continue
        if in_fab_block:
            if '}' in line:
                in_fab_block = False
                if fab_end == 1:
                    # Skip @media block too
                    continue
            fab_end += 1
            continue
        new_lines.append(line)
    html = '\n'.join(new_lines)

    # 2. Add html{overflow-x:hidden} if not present
    if 'html{overflow-x:hidden}' not in html and 'html {\n  overflow-x: hidden' not in html:
        # Add right after body{...overflow-x:hidden}
        html = html.replace(
            'overflow-x:hidden}',
            'overflow-x:hidden}\nhtml{overflow-x:hidden}',
            1  # only first occurrence
        )
        if 'overflow-x:hidden}' in html:  # check if replacement happened
            changes.append("added html{overflow-x:hidden}")

    # 3. Also check for the no-space CSS pattern
    pat = r'(body\{[^}]*overflow-x:hidden[^}]*\})'
    if not re.search(r'html\{overflow-x:hidden', html):
        html = re.sub(pat, r'\1\nhtml{overflow-x:hidden}', html, count=1)
        if 'html{overflow-x:hidden}' in html and not any('added' in c for c in changes):
            changes.append("added html{overflow-x:hidden} (alt method)")

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ {os.path.basename(os.path.dirname(filepath))}: {', '.join(changes)}")
    else:
        print(f"  - {os.path.basename(os.path.dirname(filepath))}: no changes needed")

# Process all reports
reports = sorted(glob.glob(f"{REPORTS_DIR}/*/index.html"))
print(f"Processing {len(reports)} report pages...")
for rp in reports:
    fix_file(rp)
print("Done.")
