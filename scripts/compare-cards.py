#!/usr/bin/env python3
"""比较 portal/index.html 卡片与各文章页的标题/描述一致性"""
import os, re

PORTAL = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/index.html"
REPORTS = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

# Read portal to extract cards
with open(PORTAL) as f:
    portal = f.read()

# Extract card blocks
card_pattern = re.compile(
    r'<a class="card reveal" id="r-([^"]+)"[^>]*>.*?<h3>(.*?)</h3>\s*<p class="desc">(.*?)</p>',
    re.DOTALL
)

print("=" * 80)
print(f"{'文章':<20} {'卡片标题':<40} {'文章标题':<40} {'标题一致?'}")
print("=" * 80)

for m in card_pattern.finditer(portal):
    key = m.group(1)
    card_title = m.group(2)
    card_desc = m.group(3).replace('\n', ' ').strip()
    
    # Read article
    article_path = os.path.join(REPORTS, key, "index.html")
    if not os.path.exists(article_path):
        print(f"{key:<20} [文章不存在: {article_path}]")
        continue
    
    with open(article_path) as f:
        article = f.read()
    
    # Get article title
    title_m = re.search(r'<h1>(.*?)</h1>', article, re.DOTALL)
    article_title = title_m.group(1).replace('<br>', '').replace('<br/>', '').replace('\n', ' ').strip() if title_m else "[NOT FOUND]"
    
    # Get article dek
    dek_m = re.search(r'<p class="dek">(.*?)</p>', article, re.DOTALL)
    article_dek = dek_m.group(1).replace('\n', ' ').strip() if dek_m else "[NOT FOUND]"
    
    # Compare
    title_ok = "✅" if card_title == article_title else "❌"
    desc_ok = "✅" if card_desc == article_dek else "❌"
    
    print(f"\n--- {key} ---")
    print(f"卡片标题: {card_title}")
    print(f"文章标题: {article_title}  {title_ok}")
    if card_title != article_title:
        print(f"  差异: '{card_title}' vs '{article_title}'")
    print(f"\n卡片描述: {card_desc[:80]}...")
    print(f"文章描述: {article_dek[:80]}...  {desc_ok}")
    if card_desc != article_dek:
        # Show which is longer or where they differ
        if len(card_desc) != len(article_dek):
            print(f"  长度差异: card={len(card_desc)}, article={len(article_dek)}")
        # Check first difference
        for i in range(min(len(card_desc), len(article_dek))):
            if card_desc[i] != article_dek[i]:
                print(f"  首处差异位置 {i}: card='{card_desc[i:i+30]}' vs article='{article_dek[i:i+30]}'")
                break
    print()
