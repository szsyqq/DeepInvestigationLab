#!/usr/bin/env python3
"""Generate correct pie chart, bar charts, and insert into 平安证券 article."""
import math
import re

# ============================================================
# 1. FIXED PIE CHART - 方正证券2025年业务收入结构
# ============================================================
def pie_sector(cx, cy, r1, r2, start_deg, sweep_deg, color):
    """Generate SVG path for a donut sector."""
    # Convert degrees to radians (SVG y-axis points down)
    start_rad = math.radians(start_deg)
    end_deg = start_deg + sweep_deg
    end_rad = math.radians(end_deg)
    
    # Inner arc endpoints
    x_in_start = cx + r1 * math.cos(start_rad)
    y_in_start = cy + r1 * math.sin(start_rad)
    x_in_end = cx + r1 * math.cos(end_rad)
    y_in_end = cy + r1 * math.sin(end_rad)
    
    # Outer arc endpoints
    x_out_start = cx + r2 * math.cos(start_rad)
    y_out_start = cy + r2 * math.sin(start_rad)
    x_out_end = cx + r2 * math.cos(end_rad)
    y_out_end = cy + r2 * math.sin(end_rad)
    
    large_arc = 1 if sweep_deg > 180 else 0
    
    d = (f"M {cx},{cy} "
         f"L {x_in_start:.1f},{y_in_start:.1f} "
         f"A {r1},{r1} 0 {large_arc},1 {x_in_end:.1f},{y_in_end:.1f} "
         f"L {x_out_end:.1f},{y_out_end:.1f} "
         f"A {r2},{r2} 0 {large_arc},0 {x_out_start:.1f},{y_out_start:.1f} "
         f"Z")
    return d

def generate_pie_svg():
    cx, cy = 245, 150
    r1, r2 = 65, 110
    # Start at 180 degrees (9 o'clock), go clockwise
    start_deg = 180.0
    
    sectors = [
        (73.72, "#5a5045", "\u8d22\u5bcc\u7ba1\u7406 73.72%"),      # 财富管理
        (20.37, "#8b7355", "\u6295\u8d44\u4e0e\u4ea4\u6613 20.37%"),  # ���资与交易
        (5.20, "#c4a882", "\u8d44\u4ea7\u7ba1\u7406 5.20%"),          # 资产管理
        (1.22, "#e0d0b8", "\u6295\u8d44\u94f6\u884c 1.22%"),          # 投���银行
    ]
    
    paths = []
    current_deg = start_deg
    
    colors = ["#5a5045", "#8b7355", "#c4a882", "#e0d0b8"]
    for i, (pct, color, label) in enumerate(sectors):
        sweep_deg = pct * 360.0 / 100.0
        d = pie_sector(cx, cy, r1, r2, current_deg, sweep_deg, color)
        paths.append(f'<path d="{d}" fill="{color}" stroke="#fff" stroke-width="2"/>')
        current_deg += sweep_deg
    
    # Calculate label line endpoints (use midpoint angles at outer radius + offset)
    current_deg = start_deg
    label_positions = []
    for i, (pct, color, label) in enumerate(sectors):
        mid_deg = current_deg + pct * 360.0 / 200.0  # midpoint of sector
        mid_rad = math.radians(mid_deg)
        # Label line starts at outer radius + small gap
        lx = cx + (r2 + 10) * math.cos(mid_rad)
        ly = cy + (r2 + 10) * math.sin(mid_rad)
        # Extend outward
        ex = cx + (r2 + 55) * math.cos(mid_rad)
        ey = cy + (r2 + 55) * math.sin(mid_rad)
        label_positions.append((lx, ly, ex, ey, label, color))
        current_deg += pct * 360.0 / 100.0
    
    lines = []
    for lx, ly, ex, ey, label, color in label_positions:
        # Line from sector edge to label
        lines.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="1"/>')
        # Horizontal extension for text
        if ex >= cx:
            hx = ex + 60
            lines.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{hx:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="1"/>')
            lines.append(f'<text x="{hx+4:.1f}" y="{ey+4:.1f}" font-size="11" fill="{color}">{label}</text>')
        else:
            hx = ex - 60
            lines.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{hx:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="1"/>')
            lines.append(f'<text x="{hx:.1f}" y="{ey+4:.1f}" font-size="11" fill="{color}" text-anchor="end">{label}</text>')
    
    svg_lines = [
        '<svg viewBox="0 0 460 340" style="width:100%;max-width:460px;height:auto;display:block;margin:0 auto">',
        *paths,
        *lines,
        '<text x="230" y="146" text-anchor="middle" font-size="13" font-weight="700" fill="#5a5045">2025</text>',
        '<text x="230" y="163" text-anchor="middle" font-size="11" fill="#8b7355">\u8425\u6536\u6784\u6210</text>',  # 营收构成
        '</svg>'
    ]
    return '\n'.join(svg_lines)

# ============================================================
# 2. BAR CHART - Top 10 Broker Revenue Comparison (Chapter 3)
# ============================================================
def generate_bar_chart_svg():
    """Generate horizontal bar chart for 2025 top brokers revenue comparison."""
    brokers = [
        ("\u4e2d\u4fe1\u8bc1\u5238", 748.5, "#5a5045"),      # 中信证券
        ("\u56fd\u6cf0\u6d77\u901a", 631.1, "#6b5f55"),     # 国泰海通
        ("\u534e\u6cf0\u8bc1\u5238", 358.1, "#7b6f65"),      # 华泰证券
        ("\u5e7f\u53d1\u8bc1\u5238", 354.9, "#8b7f75"),      # 广发证券
        ("\u4e2d\u91d1\u516c\u53f8", 284.8, "#9b8f85"),      # 中金公司
        ("\u4e2d\u56fd\u94f6\u6cb3", 283.0, "#ab9f95"),      # 中国银河
        ("\u62db\u5546\u8bc1\u5238", 249.7, "#bbafa5"),      # 招商证券
        ("\u7533\u4e07\u5b8f\u6e90", 242.6, "#cbbfb5"),      # 申万宏源
        ("\u4e2d\u4fe1\u5efa\u6295", 233.2, "#dbcfc5"),      # 中信建投
        ("\u65b0\u5e73\u5b89(\u4f30)", 220.0, "#c0392b"),     # 新平安(估) - highlighted in red
    ]
    
    max_rev = 800.0
    bar_height = 28
    gap = 8
    start_y = 30
    label_x = 10
    bar_start = 90
    bar_max_w = 380
    chart_h = start_y + len(brokers) * (bar_height + gap) + 20
    
    lines = [f'<svg viewBox="0 0 500 {chart_h}" style="width:100%;max-width:500px;height:auto;display:block;margin:12px auto">']
    # Title
    lines.append(f'<text x="250" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#5a5045">2025\u5e74\u4e3b\u8981\u5238\u5546\u8425\u6536\u6392\u540d</text>')  # 主要券商营收排名
    lines.append(f'<text x="250" y="28" text-anchor="middle" font-size="10" fill="#8b7355">\u5355\u4f4d\uff1a\u4ebf\u5143</text>')  # 单位：亿元
    
    for i, (name, rev, color) in enumerate(brokers):
        y = start_y + i * (bar_height + gap)
        bar_w = (rev / max_rev) * bar_max_w
        # Label
        lines.append(f'<text x="{label_x}" y="{y+bar_height-6}" font-size="11" fill="#5a5045" font-weight="{"700" if i==len(brokers)-1 else "400"}">{name}</text>')
        # Bar
        lines.append(f'<rect x="{bar_start}" y="{y+2}" width="{bar_w:.1f}" height="{bar_height-4}" rx="3" fill="{color}" opacity="{"0.9" if i<len(brokers)-1 else "0.95"}"/>')
        # Value label
        if rev >= 100:
            val_str = f"{rev:.0f}"
        else:
            val_str = f"{rev:.1f}"
        lines.append(f'<text x="{bar_start+bar_w+6}" y="{y+bar_height-6}" font-size="10" fill="{color}" font-weight="700">{val_str}</text>')
    
    # Grid lines (background)
    for v in [200, 400, 600, 800]:
        gx = bar_start + (v/max_rev)*bar_max_w
        lines.append(f'<line x1="{gx:.1f}" y1="{start_y}" x2="{gx:.1f}" y2="{y+bar_height+4}" stroke="#e0dcd0" stroke-width="1"/>')
        lines.append(f'<text x="{gx:.1f}" y="{start_y-5}" text-anchor="middle" font-size="9" fill="#c0b8a8">{v}</text>')
    
    lines.append('</svg>')
    return '\n'.join(lines)

# ============================================================
# 3. NET PROFIT BAR CHART - Bonus chart for Chapter 3
# ============================================================
def generate_profit_bar_chart_svg():
    """Generate horizontal bar chart for 2025 top brokers net profit."""
    brokers = [
        ("\u4e2d\u4fe1\u8bc1\u5238", 300.8, "#5a5045"),
        ("\u56fd\u6cf0\u6d77\u901a", 278.1, "#6b5f55"),
        ("\u534e\u6cf0\u8bc1\u5238", 163.8, "#7b6f65"),
        ("\u5e7f\u53d1\u8bc1\u5238", 137.0, "#8b7f75"),
        ("\u4e2d\u56fd\u94f6\u6cb3", 125.2, "#9b8f85"),
        ("\u62db\u5546\u8bc1\u5238", 123.5, "#ab9f95"),
        ("\u4e2d\u91d1\u516c\u53f8", 97.9, "#bbafa5"),
        ("\u7533\u4e07\u5b8f\u6e90", 95.1, "#cbbfb5"),
        ("\u4e2d\u4fe1\u5efa\u6295", 94.4, "#dbcfc5"),
        ("\u65b0\u5e73\u5b89(\u4f30)", 70.0, "#c0392b"),
    ]
    
    max_val = 320.0
    bar_height = 28
    gap = 8
    start_y = 30
    label_x = 10
    bar_start = 90
    bar_max_w = 380
    chart_h = start_y + len(brokers) * (bar_height + gap) + 20
    
    lines = [f'<svg viewBox="0 0 500 {chart_h}" style="width:100%;max-width:500px;height:auto;display:block;margin:12px auto">']
    lines.append(f'<text x="250" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#5a5045">2025\u5e74\u4e3b\u8981\u5238\u5546\u51c0\u5229\u6da6\u6392\u540d</text>')  # ���要券商净利润排名
    lines.append(f'<text x="250" y="28" text-anchor="middle" font-size="10" fill="#8b7355">\u5355\u4f4d\uff1a\u4ebf\u5143</text>')
    
    for i, (name, val, color) in enumerate(brokers):
        y = start_y + i * (bar_height + gap)
        bar_w = (val / max_val) * bar_max_w
        lines.append(f'<text x="{label_x}" y="{y+bar_height-6}" font-size="11" fill="#5a5045" font-weight="{"700" if i==len(brokers)-1 else "400"}">{name}</text>')
        lines.append(f'<rect x="{bar_start}" y="{y+2}" width="{bar_w:.1f}" height="{bar_height-4}" rx="3" fill="{color}" opacity="0.9"/>')
        lines.append(f'<text x="{bar_start+bar_w+6}" y="{y+bar_height-6}" font-size="10" fill="{color}" font-weight="700">{val:.1f}</text>')
    
    for v in [100, 200, 300]:
        gx = bar_start + (v/max_val)*bar_max_w
        lines.append(f'<line x1="{gx:.1f}" y1="{start_y}" x2="{gx:.1f}" y2="{y+bar_height+4}" stroke="#e0dcd0" stroke-width="1"/>')
        lines.append(f'<text x="{gx:.1f}" y="{start_y-5}" text-anchor="middle" font-size="9" fill="#c0b8a8">{v}</text>')
    
    lines.append('</svg>')
    return '\n'.join(lines)

# ============================================================
# 4. CHAPTER 1 - 平安集团内部营收对比 bubble/bar chart
# ============================================================
def generate_group_revenue_chart():
    """Horizontal bar chart showing 平��集团 vs 平安银行 vs 平安证券."""
    items = [
        ("\u5e73\u5b89\u96c6\u56e2(\u603b\u6536)", 10505, "#1a1a2e"),
        ("\u5e73\u5b89\u94f6\u884c", 1300, "#5a5045"),
        ("\u5e73\u5b89\u4fdd\u9669(\u5bff\u9669)", 4800, "#7b6f65"),
        ("\u5e73\u5b89\u4fdd\u9669(\u8d22\u9669)", 2800, "#9b8f95"),
        ("\u5e73\u5b89\u79d1\u6280", 1200, "#bba080"),
        ("\u5e73\u5b89\u5065\u5eb7", 350, "#c4a882"),
        ("\u5e73\u5b89\u8bc1\u5238", 200, "#c0392b"),
    ]
    
    max_val = 11000
    bar_height = 24
    gap = 6
    start_y = 30
    label_x = 8
    bar_start = 100
    bar_max_w = 370
    chart_h = start_y + len(items) * (bar_height + gap) + 10
    
    lines = [f'<svg viewBox="0 0 500 {chart_h}" style="width:100%;max-width:500px;height:auto;display:block;margin:12px auto">']
    lines.append(f'<text x="250" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#5a5045">\u5e73\u5b89\u96c6\u56e2\u5404\u4e1a\u52a1\u7ebf\u8425\u6536\u5bf9\u6bd4(2025)</text>')  # 平安集团各业务线营收对比
    lines.append(f'<text x="250" y="28" text-anchor="middle" font-size="10" fill="#8b7355">\u5355\u4f4d\uff1a\u4ebf\u5143</text>')
    
    for i, (name, val, color) in enumerate(items):
        y = start_y + i * (bar_height + gap)
        bar_w = (val / max_val) * bar_max_w
        lines.append(f'<text x="{label_x}" y="{y+bar_height-6}" font-size="10" fill="#5a5045">{name}</text>')
        lines.append(f'<rect x="{bar_start}" y="{y+2}" width="{bar_w:.1f}" height="{bar_height-4}" rx="2" fill="{color}" opacity="0.85"/>')
        # Value on right of bar
        lines.append(f'<text x="{bar_start+bar_w+4}" y="{y+bar_height-6}" font-size="9" fill="{color}">{val}</text>')
    
    lines.append('</svg>')
    return '\n'.join(lines)

# ============================================================
# 5. CHAPTER 7 - 投行收入集中度 trend chart
# ============================================================
def generate_concentration_chart():
    """Line chart showing 前五大券商投行收入占比 from 2020 to 2025."""
    data = [
        (2020, 40),
        (2021, 42),
        (2022, 44),
        (2023, 47),
        (2024, 51),
        (2025, 55),
    ]
    
    w, h = 460, 200
    margin_l, margin_r, margin_t, margin_b = 50, 20, 30, 35
    plot_w = w - margin_l - margin_r
    plot_h = h - margin_t - margin_b
    
    min_y, max_y = 35, 60
    x_step = plot_w / (len(data) - 1)
    
    lines_svg = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:460px;height:auto;display:block;margin:12px auto">']
    lines_svg.append(f'<text x="{w//2}" y="16" text-anchor="middle" font-size="12" font-weight="700" fill="#5a5045">\u524d\u4e94\u5927\u5238\u5546\u6295\u884c\u6536\u5165\u96c6\u4e2d\u5ea6\u8d8b\u52bf</text>')  # 前五��券商投行收入集中度趋势
    
    # Grid
    for val in [35, 40, 45, 50, 55, 60]:
        gy = margin_t + (max_y - val) / (max_y - min_y) * plot_h
        lines_svg.append(f'<line x1="{margin_l}" y1="{gy:.1f}" x2="{w-margin_r}" y2="{gy:.1f}" stroke="#e0dcd0" stroke-width="1"/>')
        lines_svg.append(f'<text x="{margin_l-5}" y="{gy+4:.1f}" text-anchor="end" font-size="9" fill="#8b7355">{val}%</text>')
    
    # Area fill
    points = []
    for i, (year, val) in enumerate(data):
        x = margin_l + i * x_step
        y = margin_t + (max_y - val) / (max_y - min_y) * plot_h
        points.append(f"{x},{y:.1f}")
    
    # Bottom edge for polygon
    polygon_pts = f"{margin_l},{margin_t+plot_h} " + " ".join(points) + f" {margin_l+(len(data)-1)*x_step},{margin_t+plot_h}"
    lines_svg.append(f'<polygon fill="rgba(192,57,43,0.10)" points="{polygon_pts}"/>')
    
    # Line
    lines_svg.append(f'<polyline fill="none" stroke="#c0392b" stroke-width="2.5" stroke-linejoin="round" points="{" ".join(points)}"/>')
    
    # Points + labels
    for i, (year, val) in enumerate(data):
        x = margin_l + i * x_step
        y = margin_t + (max_y - val) / (max_y - min_y) * plot_h
        lines_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#c0392b" stroke="#fff" stroke-width="2"/>')
        lines_svg.append(f'<text x="{x:.1f}" y="{y-10:.1f}" text-anchor="middle" font-size="10" fill="#c0392b" font-weight="700">{val}%</text>')
        # Year labels
        lines_svg.append(f'<text x="{x:.1f}" y="{margin_t+plot_h+15}" text-anchor="middle" font-size="9" fill="#8b7355">{year}</text>')
    
    lines_svg.append(f'<line x1="{margin_l}" y1="{margin_t+plot_h}" x2="{w-margin_r}" y2="{margin_t+plot_h}" stroke="#8b7355" stroke-width="1.5"/>')
    lines_svg.append('</svg>')
    return '\n'.join(lines_svg)


if __name__ == "__main__":
    # Print all generated SVGs for verification
    print("=== PIE CHART ===")
    print(generate_pie_svg())
    print()
    print("=== BAR CHART (Revenue) ===")
    print(generate_bar_chart_svg())
    print()
    print("=== BAR CHART (Profit) ===")
    print(generate_profit_bar_chart_svg())
    print()
    print("=== GROUP REVENUE ===")
    print(generate_group_revenue_chart())
    print()
    print("=== CONCENTRATION ===")
    print(generate_concentration_chart())
