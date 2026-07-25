#!/usr/bin/env python3
"""
为缺少 sidenav HTML 的页面注入目录面板。
根据每页的 h2 章节结构自动生成正确的 sidenav。
"""
import os, re

BASE = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports"

# 各页章节结构定义 (anchor_id, data_ch, short_title)
PAGE_CHAPTERS = {
    "bmw": {
        "hero_id": "hero",  # will add id="hero" to hero div
        "chapters": [
            ("ch1", 1, "一条制动系统，让百年宝马发了利润预警"),
            ("ch2", 2, "1,400 亿欧元的营收，与消失的利润"),
            ("ch3", 3, "中国，它最大的市场和最硬的骨头"),
            ("ch4", 4, "新世代，一次千亿欧元的赌注"),
            ("ch5", 5, "终极驾驶机器的软件短板"),
            ("ch6", 6, "关税、供应链、与一道跨不过的坎"),
        ],
        "epilogue": ("ch7", 7, "尾声：踩不稳的电门，与下一个百年"),
    },
    "seres": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "面包车厂的翻身"),
            ("c2", 2, "华为这台印钞机"),
            ("c3", 3, "一笔流向华为的账"),
            ("c4", 4, "赎回灵魂的三笔钱"),
            ("c5", 5, "五界分流，含华量被稀释"),
            ("c6", 6, "增长的悬崖"),
            ("c7", 7, "赎回自我的赌注"),
        ],
        "epilogue": ("c8", 8, "灵魂的去向"),
    },
    "jiantao": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "从深圳农民到全球第一"),
            ("c2", 2, "追问收入：AI的蛋糕"),
            ("c3", 3, "追问利润：涨价函就是印钞机"),
            ("c4", 4, "追问技术：M9的牌桌"),
            ("c5", 5, "追问资本：家族在周期顶端套现"),
            ("c6", 6, "追问风险：地产旧伤与周期退潮"),
            ("c7", 7, "招股书之外：原材料的咽喉"),
        ],
        "epilogue": ("c8", 8, "AI 叙事之外的真实引擎"),
    },
    "suiyuan": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "起个大早，赶个晚集"),
            ("c2", 2, "追问收入：11倍增长从哪来"),
            ("c3", 3, "追问客户：腾讯的干儿子"),
            ("c4", 4, "追问利润：三年烧掉51.79亿"),
            ("c5", 5, "追问技术：不抄CUDA的那条窄路"),
            ("c6", 6, "追问份额：1.4%的现实"),
            ("c7", 7, "追问治理：不足30%的方向盘"),
            ("c8", 8, "招股书之外：四小龙的终局"),
        ],
        "epilogue": ("c9", 9, "没有腾讯，也能活吗"),
    },
    "changxin": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "148天：预先审阅的速度"),
            ("c2", 2, "追问收入：谁在买这些内存"),
            ("c3", 3, "追问利润：330亿是怎么赚到的"),
            ("c4", 4, "追问技术：17nm与10nm之间"),
            ("c5", 5, "追问壁垒：研发33%的绕路"),
            ("c6", 6, "追问资本：295亿与耐心钱"),
            ("c7", 7, "追问风险：三道关"),
            ("c8", 8, "招股书之外"),
        ],
        "epilogue": ("c9", 9, "周期退潮，才是真的开始"),
    },
    "deepseek": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "从 558 万到 R3"),
            ("c2", 2, "算力的真相"),
            ("c3", 3, "不透明的财务"),
            ("c4", 4, "开源的账单"),
            ("c5", 5, "被芯片卡住的下一程"),
            ("c6", 6, "全球封禁的墙"),
            ("c7", 7, "私募孵化出的国运符号"),
        ],
        "epilogue": ("c8", 8, "开源给世界，捂紧给自己"),
    },
    "chowsangsang": {
        "hero_id": "c0",
        "chapters": [
            ("c_intro", 1, "黄金珠宝行业 2026"),
            ("c1", 2, "广州的金铺，香港的牌子"),
            ("c2", 3, "金价牛，它却在2024过了个冬"),
            ("c3", 4, "关掉的74家店"),
            ("c4", 5, "金价越高，消费者越冷"),
            ("c5", 6, "一克黄金，从矿山到你手上"),
            ("c6", 7, "周氏江湖，老二的位子"),
            ("c7", 8, "90年，怎么让25岁的人进门"),
            ("c8", 9, "2025大反转"),
            ("c9", 10, "与金价解绑的长跑"),
            ("c_10", 11, "金价、同店与股价的密码"),
        ],
        "epilogue": ("c11", 12, "金价跌了25%，它反而暖了"),
    },
    "yushu": {
        "hero_id": "c0",
        "chapters": [
            ("c1", 1, "73天：一场考试提前结束"),
            ("c2", 2, "卖机器人，还是卖科研玩具"),
            ("c3", 3, "一个没有大脑的智能机器人"),
            ("c4", 4, "90%自研率的14%到18%"),
            ("c5", 5, "估值的斜率与门外的队伍"),
            ("c6", 6, "四条同向运动的曲线"),
            ("c7", 7, "三个没有答案的问题"),
            ("c8", 8, "819页里写得最轻的一页"),
        ],
        "epilogue": ("c9", 9, "翻不过去的那道坎"),
    },
}

def build_sidenav_html(hero_id, chapters, epilogue):
    """Generate the side navigation HTML."""
    html = '<div class="sidenav" id="sidenav">\n'
    html += '<button class="close" onclick="toggleNav()">×</button>\n'
    html += '<h4>章节导航</h4>\n'
    
    # Hero/导语 link
    if hero_id:
        href = "#" + hero_id
    else:
        href = "#"  # no hero id, scroll to top
    html += f'<a href="{href}" data-ch="0"><span class="num">导语</span>开篇</a>\n'
    
    # Chapter links
    for i, (anchor_id, ch_num, title) in enumerate(chapters):
        html += f'<a href="#{anchor_id}" data-ch="{ch_num}"><span class="num">第{ch_num}章</span>{title}</a>\n'
    
    # Epilogue link
    if epilogue:
        href = "#" + epilogue[0]
        ch_num = epilogue[1]
        # Shorten epilogue title
        short_title = epilogue[2]
        if "：急" in short_title:
            short_title = short_title.split("：")[-1]
        html += f'<a href="{href}" data-ch="{ch_num}"><span class="num">尾声</span>{short_title}</a>\n'
    
    html += '</div>\n'
    return html

def get_sidenav_insert_position(content):
    """Find where to insert the sidenav - before the container div."""
    # Insert right before <div class="container">
    m = re.search(r'<div class="container">', content)
    if m:
        return m.start()
    # Fallback: before the main content script
    m = re.search(r'<script>\s*var\s+(obs|progress|reveals)', content)
    if m:
        return m.start()
    return -1

for page, data in PAGE_CHAPTERS.items():
    path = os.path.join(BASE, page, "index.html")
    if not os.path.exists(path):
        print(f"[SKIP] {page} - not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if sidenav already exists
    if '<div class="sidenav"' in content:
        print(f"[SKIP] {page} - already has sidenav")
        continue
    
    # BMW special: add id="hero" to the hero div
    if page == "bmw":
        content = content.replace(
            '<div class="hero reveal">',
            '<div class="hero reveal" id="hero">'
        )
    
    # Generate sidenav HTML
    sidenav_html = build_sidenav_html(
        data["hero_id"],
        data["chapters"],
        data["epilogue"]
    )
    
    # Find insertion point
    pos = get_sidenav_insert_position(content)
    if pos < 0:
        print(f"[FAIL] {page} - could not find insertion point")
        continue
    
    # Insert before the container
    content = content[:pos] + sidenav_html + content[pos:]
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[DONE] {page} - sidenav injected")

print("\n✅ All sidenavs injected")
