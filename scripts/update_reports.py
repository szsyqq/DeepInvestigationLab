#!/usr/bin/env python3
"""
更新所有报道页面，移除内联全局 UI，改用 portal/global.css + portal/global.js。

策略：
1. 从 <style> 中移除全局 UI CSS 规则（按类名匹配）
2. 移除 body 中的全局 HTML 元素
3. 提取 readingTime 和 title，写入 window.__REPORT_CONFIG__
4. 在 head 末尾插入 <link> 和配置脚本，在 body 末尾插入 global.js
"""

import re
import os
import json

BASE = os.path.dirname(__file__)
REPORTS_DIR = os.path.join(BASE, "..", "portal", "reports")

# 全局 CSS 选择器前缀（匹配 CSS 规则行开头）
GLOBAL_CSS_PREFIXES = [
    ".internal-banner", ".top-bar", ".top-bar-inner", ".top-bar-left",
    ".top-bar-right", ".progress-bar", ".consent-overlay",
    ".consent-box", ".consent-header", ".consent-body",
    ".consent-footer", ".consent-btn", ".consent-close",
    ".back-top", ".sidenav", ".reading-time", ".reading-time-fab",
    ".home-fab", ".home-link", ".tracker",
]


def remove_global_css_rules(css_text):
    """从 CSS 文本中移除匹配全局 UI 类名的规则"""
    lines = css_text.split('\n')
    new_lines = []
    skip_block = False
    brace_count = 0

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith('/*'):
            new_lines.append(line)
            continue

        if skip_block:
            brace_count += stripped.count('{') - stripped.count('}')
            if brace_count <= 0:
                skip_block = False
                brace_count = 0
            continue

        # 检查是否匹配要移除的选择器
        should_skip = False
        for prefix in GLOBAL_CSS_PREFIXES:
            # 匹配以该前缀开头的行（允许前面有空格）
            if stripped.startswith(prefix) or re.match(r'\s*' + re.escape(prefix) + r'[\s,.\[:{]', stripped):
                should_skip = True
                break

        # 也移除 footer .disc max-width
        if re.match(r'\s*footer\s+\.disc\s*\{', stripped):
            should_skip = True

        if should_skip:
            # 如果这行有 { 但没有 }，说明是多行块，需要跳过后续行
            if '{' in stripped and '}' not in stripped:
                skip_block = True
                brace_count = stripped.count('{') - stripped.count('}')
            continue

        new_lines.append(line)

    return '\n'.join(new_lines)


def process_page(filepath):
    """处理单个报道页面"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # ===== 1. 从 <style> 中移除全局 CSS =====
    style_match = re.search(r'(<style>)(.*?)(</style>)', html, re.DOTALL)
    if style_match:
        css = style_match.group(2)
        new_css = remove_global_css_rules(css)
        html = html[:style_match.start()] + style_match.group(1) + new_css + style_match.group(3) + html[style_match.end():]

    # ===== 2. 提取配置信息 =====
    reading_time = re.search(r'id="readTime"[^>]*>([^<]+)', html)
    reading_time = reading_time.group(1).strip() if reading_time else ""

    title_match = re.search(r'<title>([^<]+)</title>', html)
    report_title = re.sub(r'\s*\|\s*调查团队\s*$', '', title_match.group(1)).strip() if title_match else ""

    # ===== 3. 移除全局 HTML 元素 =====
    # banner
    html = re.sub(r'<div class="internal-banner">[^<]*(?:<[^/][^>]*>[^<]*</[^>]+>)*\s*</div>', '', html)

    # progress-bar
    html = re.sub(r'<div class="progress-bar"[^>]*>\s*</div>', '', html)

    # top-bar
    html = re.sub(r'<div class="top-bar">.*?</div>\s*$', '', html, flags=re.DOTALL | re.MULTILINE)

    # consent-overlay
    html = re.sub(r'<div class="consent-overlay"[^>]*>.*?</div>\s*$', '', html, flags=re.DOTALL | re.MULTILINE)

    # footer
    html = re.sub(r'<footer>.*?</footer>', '', html, flags=re.DOTALL)

    # sidenav
    html = re.sub(r'<div class="sidenav"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # back-top
    html = re.sub(r'<button class="back-top"[^>]*>\s*[^<]*\s*</button>', '', html)

    # reading-time badge
    html = re.sub(r'<div class="reading-time"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # 清理多余空行
    html = re.sub(r'\n{4,}', '\n\n', html).strip()

    # ===== 4. 构建配置 JSON =====
    config_json = json.dumps({
        "readingTime": reading_time,
        "reportTitle": report_title,
    }, ensure_ascii=False)

    # ===== 5. 在 head 末尾添加 link 和配置脚本 =====
    html = html.replace('</head>',
        '<link rel="stylesheet" href="../global.css">\n'
        f'<script>window.__REPORT_CONFIG__ = {config_json};</script>\n</head>')

    # ===== 6. 在 body 末尾添加 global.js =====
    html = html.replace('</body>', '\n<script src="../global.js" defer></script>\n</body>')

    # ===== 7. 写入 =====
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    changed = html != original
    return changed, reading_time, report_title


def main():
    reports = sorted(os.listdir(REPORTS_DIR))
    updated = 0
    for name in reports:
        filepath = os.path.join(REPORTS_DIR, name, "index.html")
        if os.path.isfile(filepath):
            changed, rt, title = process_page(filepath)
            status = '✓' if changed else ' '
            print(f"{status} {name}: readingTime={rt or '(none)'}, title={title}")
            if changed:
                updated += 1

    print(f"\n共处理 {len(reports)} 个页面，更新了 {updated} 个。")


if __name__ == "__main__":
    main()
