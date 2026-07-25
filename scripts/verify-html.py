#!/usr/bin/env python3
"""Verify the modified HTML file."""
import re
import os

base = '/Users/panyp/WorkBuddy/#深度调查档案���/底稿'
for d in os.listdir(base):
    if '平安' in d:
        path = os.path.join(base, d, 'index.html')
        break

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Check basic structure
print(f"File size: {len(html)} chars")
print(f"Has DOCTYPE: {html.startswith('<!DOCTYPE')}")
print(f"Has </html>: {'</html>' in html}")

# Extract script blocks
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
if scripts:
    for i, s in enumerate(scripts):
        with open(f'/tmp/check-pingan-{i}.js', 'w') as f:
            f.write(s)
        print(f"Script block {i}: {len(s)} chars, starts with: {s[:50]}")

# Check sup tags match footnote count
sup_count = html.count('<sup>')
print(f"Sup tags: {sup_count}")

# Check footnotes
fn_items = re.findall(r'<li>.*?</li>', html[html.find('<div class="footnotes">'):html.find('</ol></div>', html.find('<div class="footnotes">'))])
print(f"Footnotes: {len(fn_items)}")

# Print new chapter content summary
c2_start = html.find('<h2 class="reveal" id="c2"')
c3_start = html.find('<h2 class="reveal" id="c3"')
ch2 = html[c2_start:c3_start]
print(f"\nChapter 2 content length: {len(ch2)}")

# Check for chart content
for marker in ['chart-box', 'line_svg', 'pie_svg', '��正证券营收轨迹', '方正证券2025���业务收入结构', '[12]', '[13]']:
    print(f"Contains '{marker}': {marker in html}")
