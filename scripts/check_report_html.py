#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度调查报道单文件 HTML 页面体检脚本
=====================================

用途：
  一键检查单文件 HTML 调查报告的常见布局 Bug：
  1. <div class="container"> 是否被多余的 </div> 提前关闭（导致正文失去 680px 宽度约束）
  2. body 内 <div> 开/闭是否平衡
  3. 正文中用到的 bar-fill / bar-label 等 class 是否在 <style> 中定义

用法：
  python3 scripts/check_report_html.py <html文件路径> [第二个文件...]

退出码：
  0 = 无问题
  1 = 发现问题

依赖：仅标准库
"""
import re
import sys


def find_container_close(lines):
    """逐行追踪 <div class="container"> 的深度，返回其关闭行号（1-based）。"""
    in_container = False
    depth = 0
    open_line = 0
    close_line = 0
    for i, line in enumerate(lines, 1):
        if '<div class="container">' in line:
            in_container = True
            open_line = i
            depth = 1
            continue
        if not in_container:
            continue
        opens = len(re.findall(r'<div[\s>]', line))
        closes = len(re.findall(r'</div>', line))
        depth += opens - closes
        if depth <= 0:
            close_line = i
            break
    return open_line, close_line, depth


def count_div_balance(body_html):
    """统计 body 内（排除 script/style/svg/注释）的 div 开闭数。"""
    clean = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', '', body_html, flags=re.DOTALL)
    clean = re.sub(r'<!--.*?-->', '', clean, flags=re.DOTALL)
    opens = len(re.findall(r'<div[\s>]', clean))
    closes = len(re.findall(r'</div>', clean))
    return opens, closes


def check_css_classes(html):
    """检查正文中用到的常见 class 是否在 style 中有定义。"""
    style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    style_css = style_match.group(1) if style_match else ''

    # 正文中实际用到的 class（从 <div class="..."> 提取）
    used = set()
    for m in re.finditer(r'class="([^"]+)"', html):
        for c in m.group(1).split():
            used.add(c)

    # 需要关注的派生类（bar-fill.*, bar-label.*）
    needed_prefixes = ('bar-fill.', 'bar-label.')
    missing = []
    for cls in sorted(used):
        for prefix in needed_prefixes:
            if cls.startswith(prefix.replace('.', '')) and ('.' + cls) not in style_css and (cls) not in style_css:
                missing.append(cls)
                break
    return missing


def inspect(path):
    print(f"\n{'='*60}\n检查文件: {path}\n{'='*60}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"  无法读取文件: {e}")
        return 1

    lines = html.split('\n')
    problems = []

    # 1. container 提前关闭
    open_line, close_line, final_depth = find_container_close(lines)
    if open_line == 0:
        print("  [WARN] 未找到 <div class=\"container\">")
    else:
        total_lines = len(lines)
        span = close_line - open_line if close_line else (total_lines - open_line)
        print(f"  container: 打开于 line {open_line}，关闭于 line {close_line}（跨度 {span} 行）")
        # 启发式：若 container 关闭位置远早于文件末尾（< 60%），认为异常
        if close_line and close_line < total_lines * 0.6:
            print(f"  [BUG] container 在 line {close_line} 提前关闭！其后的正文/图表将失去宽度约束。")
            problems.append('container_early_close')
        elif close_line == 0:
            print(f"  [BUG] container 从未关闭（深度残留 {final_depth}），结构未闭合。")
            problems.append('container_unclosed')
        else:
            print("  [OK] container 覆盖到接近文末，结构正常。")

    # 2. div 平衡
    body_start = html.find('<body>')
    body_end = html.find('</body>')
    body_html = html[body_start:body_end + 7] if body_start >= 0 and body_end >= 0 else html
    opens, closes = count_div_balance(body_html)
    print(f"  div 平衡: <div>={opens}, </div>={closes}, diff={closes - opens}")
    if opens != closes:
        print(f"  [BUG] 存在 {abs(closes - opens)} 个不平衡的 div 标签（多余或缺失）。")
        problems.append('div_unbalanced')
    else:
        print("  [OK] div 标签平衡。")

    # 3. 缺失 CSS 类
    missing = check_css_classes(html)
    if missing:
        print(f"  [WARN] 以下 bar 类在 <style> 中未定义（可能导致柱状图无色）: {missing}")
        problems.append('missing_css')
    else:
        print("  [OK] 正文中用到的 bar-fill/bar-label 类均有 CSS 定义。")

    return 1 if problems else 0


def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_report_html.py <html文件> [更多文件...]")
        sys.exit(2)
    rc = 0
    for p in sys.argv[1:]:
        rc |= inspect(p)
    print(f"\n{'='*60}")
    if rc == 0:
        print("✅ 全部文件体检通过，未发现布局 Bug。")
    else:
        print("⚠️  发现问题，详见上方 [BUG]/[WARN] 标记。")
    sys.exit(rc)


if __name__ == '__main__':
    main()
