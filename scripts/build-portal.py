#!/usr/bin/env python3
"""数据驱动门户生成系统 —— 从 reports.json + template.html 生成 portal/index.html"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "portal", "reports.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "portal", "template.html")
OUTPUT_PATH = os.path.join(BASE_DIR, "portal", "index.html")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_card(report):
    """生成单张卡片 HTML"""
    href = report.get("href", f"reports/{report['id']}/index.html")
    parts = [
        f'<a class="card reveal" id="r-{report["id"]}" href="{href}">',
        '<div class="row">',
        f'<span class="date">{report["date"]}</span>',
    ]
    if report.get("trial"):
        parts.append('<span class="tag">试读</span>')
    parts.append(f'<span class="co">{report["co"]}</span>')
    parts.extend(f'<span class="tag">{tag}</span>' for tag in report["tags"])
    parts.append("</div>")
    parts.append(f'<h3>{report["title"]}</h3>')
    parts.append(f'<p class="desc">{report["desc"]}</p>')
    parts.append(f'<div class="foot"><span>{report["readingTime"]}</span><span class="more">阅读全文</span></div>')
    parts.append("</a>")
    return "\n".join(parts)


def generate_cards(reports):
    """生成所有卡片 HTML"""
    return "\n\n".join(generate_card(r) for r in reports) + "\n"


def generate_sidenav(reports):
    """生成侧边目录 HTML"""
    links = []
    for i, r in enumerate(reports, start=1):
        num = f"{i:02d}"
        links.append(f'<a href="#r-{r["id"]}"><span class="num">{num}</span>{r["navShort"]}</a>')
    return "\n".join(links) + "\n"


def validate_order(reports):
    """验证卡片按日期降序排列且 sidenav 编号连续"""
    errors = []
    for i in range(len(reports) - 1):
        if reports[i]["date"] < reports[i + 1]["date"]:
            errors.append(
                f"排序错误: '{reports[i]['id']}' ({reports[i]['date']}) "
                f"在 '{reports[i+1]['id']}' ({reports[i+1]['date']}) 之前"
            )
    if len(reports) < 1:
        errors.append(f"卡片数量错误: 至少需要 1 张卡片, 实际 {len(reports)} 张")
    for i, r in enumerate(reports):
        if r.get("trial"):
            expected_tag = '<span class="tag">试读</span>'
            card = generate_card(r)
            if expected_tag not in card:
                errors.append(f"试读标签缺失: {r['id']}")
    return errors


def build():
    print(f"[build-portal] 读取 {JSON_PATH}")
    reports = load_json(JSON_PATH)

    print(f"[build-portal] 读取 {TEMPLATE_PATH}")
    template = load_template(TEMPLATE_PATH)

    # 验证数据
    errors = validate_order(reports)
    if errors:
        for e in errors:
            print(f"  [错误] {e}")
        sys.exit(1)
    print(f"[build-portal] 数据验证通过 ({len(reports)} 张卡片)")

    # 生成卡片 HTML
    cards_html = generate_cards(reports)
    # 生成侧边栏 HTML
    sidenav_html = generate_sidenav(reports)

    # 替换标记
    result = template.replace("<!-- CARDS -->", cards_html)
    result = result.replace("<!-- SIDENAV -->", sidenav_html)

    # 验证替换结果
    if "<!-- CARDS -->" in result:
        print("[错误] CARDS 标记未被替换")
        sys.exit(1)
    if "<!-- SIDENAV -->" in result:
        print("[错误] SIDENAV 标记未被替换")
        sys.exit(1)

    # 写入输出文件
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(result)

    # 统计结果
    card_count = result.count('class="card reveal"')
    nav_count = result.count('class="num"')
    print(f"[build-portal] 写入 {OUTPUT_PATH}")
    print(f"[build-portal] 生成 {card_count} 张卡片, {nav_count} 个目录链接")

    # 基本结构验证
    if card_count != len(reports):
        print(f"[警告] 卡片数量异常: 期望 {len(reports)}, 实际 {card_count}")
    if nav_count != len(reports):
        print(f"[警告] 目录链接数量异常: 期望 {len(reports)}, 实际 {nav_count}")

    print("[build-portal] 完成")


if __name__ == "__main__":
    build()
