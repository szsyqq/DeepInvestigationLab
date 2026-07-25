#!/usr/bin/env python3
"""
统一 consent-overlay 改造脚本 v2：
- 移除各页 inline consent HTML 块
- 移除 inline consent JS（行级定位，不依赖括号计数）
- 修正 global.js script 路径
- 补上缺失的 global.js 引用
"""
import re, os

PORTAL = "/Users/panyp/WorkBuddy/#深度调查档案室/portal"

ALL_FILES = [
    ("reports/bmw/index.html",         "../../global.js"),
    ("reports/changxin/index.html",    "../../global.js"),
    ("reports/zhipu/index.html",       "../../global.js"),
    ("reports/jiantao/index.html",     "../../global.js"),
    ("reports/yushu/index.html",       "../../global.js"),
    ("reports/xiaohongshu/index.html", "../../global.js"),
    ("reports/suiyuan/index.html",     "../../global.js"),
    ("reports/rongtong/index.html",    "../../global.js"),
    ("reports/seres/index.html",       "../../global.js"),
    ("reports/deepseek/index.html",    "../../global.js"),
    ("reports/fund-gray/index.html",   "../../global.js"),
    ("reports/hilton/index.html",           "../../global.js"),
    ("reports/shenzhen-air/index.html",     "../../global.js"),
    ("reports/airbus/index.html",           "../../global.js"),
    ("reports/wuliangye/index.html",        "../../global.js"),
    ("reports/pingansec/index.html",        "../../global.js"),
    ("reports/chowsangsang/index.html",     "../../global.js"),
    ("reports/invesco-greatwall/index.html","../../global.js"),
    ("reports/copper/index.html",           "../../global.js"),
    ("index.html",     "global.js"),
    ("changelog.html", "global.js"),
]

# ============================================================
# Helper: 移除匹配的 <script>..</script> 块
# ============================================================
def remove_script_blocks(text, keyword):
    """
    找到包含 keyword 的 <script>..</script> 块并移除。
    返回 (新文本, 是否改动)
    """
    changed = False
    while True:
        # 找 keyword
        idx = text.find(keyword)
        if idx == -1:
            break
        # 往回找最近的 <script
        script_start = text.rfind('<script', 0, idx)
        if script_start == -1:
            break
        # 找闭合 </script>
        script_end = text.find('</script>', idx)
        if script_end == -1:
            break
        script_end += 9  # len('</script>')
        # 清掉前面的空行
        while script_start > 0 and text[script_start-1] in ' \t\r\n':
            script_start -= 1
        text = text[:script_start] + text[script_end:]
        changed = True
    return text, changed


def remove_consent_html(text):
    """移除 inline consent HTML 块"""
    start_marker = '<div class="consent-overlay" id="consentOverlay">'
    idx = text.find(start_marker)
    if idx == -1:
        return text, False
    
    # 数 div 层级到匹配闭合
    pos = idx + len(start_marker)
    depth = 1
    i = pos
    while i < len(text) and depth > 0:
        next_open = text.find('<div ', i)
        next_close = text.find('</div>', i)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 5
        else:
            depth -= 1
            i = next_close + 6
    
    # 去掉前面空行
    start = idx
    while start > 0 and text[start-1] in ' \t\r\n':
        start -= 1
    text = text[:start] + text[i:]
    return text, True


def remove_consent_css(text):
    """移除 .consent-* CSS 规则（在 <style> 块内）"""
    # 找 <style> 块
    pat = re.compile(r'<style>(.*?)</style>', re.DOTALL)
    def clean_css(m):
        css = m.group(1)
        # 移除 .consent-overlay 相关规则（从 .consent- 到下一个 } ）
        cleaned = re.sub(r'\s*\n?\s*/\*.*?法律合规弹窗.*?\*/\s*\n?', '', css)
        cleaned = re.sub(r'\s*\n?\s*/\*.*?legal.*?\*/\s*\n?', '', cleaned, flags=re.IGNORECASE)
        # 移除 body.locked 规则
        cleaned = re.sub(r'body\.locked\{[^}]*\}', '', cleaned)
        # 移除 .consent-overlay 完整块（包括后续所有 .consent-* 规则直到非 .consent- 的 }
        lines = cleaned.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('.consent-') or stripped.startswith('body.locked'):
                skip = True
                # 如果这一行自身包含 }，可能就结束了
                if '}' in stripped and not stripped.startswith('@media'):
                    skip = False
                continue
            if skip:
                if '}' in stripped:
                    skip = False
                    # 检查下一行是否又是 .consent-*
                    continue
                continue
            new_lines.append(line)
        return '<style>' + '\n'.join(new_lines) + '</style>'
    
    new_text = pat.sub(clean_css, text)
    if new_text != text:
        return new_text, True
    return text, False


def fix_global_js_src(text, correct_path):
    """修正错误的 global.js script 路径"""
    if correct_path == "../global.js":
        return text  # 不可能用这个路径，留着后续逻辑
    text = text.replace('<script src="../global.js"', f'<script src="{correct_path}"')
    text = text.replace("<script src='../global.js'", f"<script src='{correct_path}'")
    return text


def ensure_global_js(text, correct_path):
    """确保页面在 </body> 前加载 global.js"""
    # 检查所有写法
    patterns = [
        f'<script src="{correct_path}"',
        f"<script src='{correct_path}'",
    ]
    for p in patterns:
        if p in text:
            return text
    # 还有没有其他写法？检查 ../global.js 和 ../../global.js 和 global.js
    for variant in ['../global.js', '../../global.js', 'global.js']:
        if variant in text:
            return text  # 已有某种引用
    # 还没有，在 </body> 前插入
    text = text.replace('</body>', f'<script src="{correct_path}" defer></script>\n</body>')
    return text


def process(rel_path, correct_js_path):
    full = os.path.join(PORTAL, rel_path)
    if not os.path.isfile(full):
        print(f"  ⚠ 不存在: {rel_path}")
        return

    with open(full, 'r', encoding='utf-8') as f:
        text = f.read()
    original = text
    log = []

    # 1. 移除 consent HTML 块
    text, changed = remove_consent_html(text)
    if changed:
        log.append("移除consent HTML")

    # 2. 移除 inline consent JS 块（各种模式）
    keywords = [
        'document.getElementById("consentOverlay")',
        "document.getElementById('consentOverlay')",
        'consentOverlay',
        '// 合规弹窗',
        '// Consent overlay',
        '// consent overlay',
    ]
    for kw in keywords:
        text, changed = remove_script_blocks(text, kw)
        if changed:
            log.append(f"移除consent JS")
            break

    # 3. 移除 consent CSS（仅在 <style> 块内）
    text, changed = remove_consent_css(text)
    if changed:
        log.append("移除consent CSS")

    # 4. 修正 global.js 路径
    text = fix_global_js_src(text, correct_js_path)

    # 5. 确保有 global.js
    text = ensure_global_js(text, correct_js_path)

    if text == original:
        print(f"  - {rel_path} — 无变化")
        return

    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  ✓ {rel_path} — {'; '.join(log)}")


def main():
    print("=== consent-overlay 统一改造 v2 ===\n")
    for rel_path, js_path in ALL_FILES:
        process(rel_path, js_path)
    print("\n=== 完成 ===")

if __name__ == '__main__':
    main()
