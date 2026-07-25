#!/usr/bin/env python3
"""
同步 portal/index.html 中各卡片描述与各文章页的 hero dek 一致。
"""
import os, re

PORTAL = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/index.html"
REPORTS = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

# Read portal
with open(PORTAL, "r", encoding="utf-8") as f:
    portal = f.read()

# Extract cards: find each card block's <p class="desc">...</p>
cards = re.findall(
    r'<a class="card reveal" id="r-([^"]+)"[^>]*>.*?<h3>(.*?)</h3>',
    portal, re.DOTALL
)

print("=" * 70)
print(f"{'Key':<16} {'Title Match':<12} {'Desc Sync':<12}")
print("=" * 70)

for key, card_title in cards:
    article_path = os.path.join(REPORTS, key, "index.html")
    if not os.path.exists(article_path):
        print(f"{key:<16} {'[NO FILE]':<12}")
        continue
    
    with open(article_path, "r", encoding="utf-8") as f:
        article = f.read()
    
    # Get article title
    title_m = re.search(r'<h1>(.*?)</h1>', article, re.DOTALL)
    article_title = title_m.group(1).replace('<br>', '').replace('<br/>', '').strip() if title_m else ""
    
    # Get article dek: either <p class="dek"> or <div class="dek">
    dek_m = re.search(r'<(p|div)\s+class="dek"[^>]*>(.*?)</\1>', article, re.DOTALL)
    if not dek_m:
        # Try text after byline/before first h2 as fallback
        print(f"{key:<16} {'[NO DEK]':<12}")
        continue
    
    article_dek = dek_m.group(2).replace('\n', ' ').strip()
    
    # Remove <br> tags from article_dek for consistency
    article_dek = article_dek.replace('<br>', '').replace('<br/>', '').replace('  ', ' ').strip()
    
    # Now find the <p class="desc"> in portal and replace its content
    # The card is identified by id="r-{key}"
    card_pattern = re.compile(
        r'(<a class="card reveal" id="r-' + re.escape(key) + r'"[^>]*>.*?<h3>.*?</h3>\s*)<p class="desc">.*?</p>',
        re.DOTALL
    )
    
    m = card_pattern.search(portal)
    if not m:
        print(f"{key:<16} {'[CARD NOT FOUND]':<12}")
        continue
    
    old_block = m.group(0)
    new_block = m.group(1) + f'<p class="desc">{article_dek}</p>'
    
    portal = portal.replace(old_block, new_block)
    
    title_ok = "✅" if card_title == article_title else "❌"
    print(f"{key:<16} {title_ok:<12} ✅")

# Write updated portal
with open(PORTAL, "w", encoding="utf-8") as f:
    f.write(portal)

print(f"\n✅ Portal index.html updated with {len(cards)} card descriptions synced")
