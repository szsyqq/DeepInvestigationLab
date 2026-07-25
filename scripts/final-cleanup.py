#!/usr/bin/env python3
"""
最终清理：移除 masthead 关闭后可能残留的孤立 </div>。
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"
PAGES = ["bmw", "seres", "jiantao", "suiyuan", "changxin", "deepseek", "chowsangsang", "yushu", "zhipu", "xiaohongshu", "wuliangye"]

for page in PAGES:
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove orphan </div> lines between masthead close and the next meaningful element
    # Pattern: </div>\n\n</div>\n (masthead close followed by orphan close)
    pattern = re.compile(
        r'(</div><!-- masthead close -->)?\s*</div>\s*</div>\s*\n\s*(<(p|div|h2|ul|ol|blockquote|table))',
        re.DOTALL
    )
    
    # Simpler approach: remove any </div> that appears alone between masthead close and content
    # Find the masthead close position, then check for orphan </div> in next few lines
    mh_close = content.find('class="masthead">')
    if mh_close < 0:
        continue
    
    # Find the LAST </div> that closes the masthead (4th </div> after "masthead">)
    # Actually just find the position after "档案室</a></div>"
    mh_end_marker = '档案室</a></div>'
    mh_end_pos = content.find(mh_end_marker)
    if mh_end_pos < 0:
        continue
    
    # After the marker, we expect </div> to close .masthead, then content
    # Check if there's an extra </div> before the next real element
    after_mh = content[mh_end_pos + len(mh_end_marker):]
    
    # Remove any single </div> that appears before the next meaningful element
    cleaned = re.sub(r'^\s*</div>\s*\n', '\n', after_mh)
    
    if cleaned != after_mh:
        content = content[:mh_end_pos + len(mh_end_marker)] + cleaned
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[DONE] {page} - removed orphan </div>")
    else:
        print(f"[SKIP] {page} - clean")

print("✅ Done")
