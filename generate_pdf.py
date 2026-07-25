#!/usr/bin/env python3
"""生成中文PDF报告：13篇文章质量评估"""

from fpdf import FPDF
import os

FONT_PATH = "/System/Library/Fonts/Supplemental/Songti.ttc"

class ReportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Songti", "", 7)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, "深度调查档案室 · 13 篇文章质量评估报告", align="L")
            self.ln(7)
            self.set_draw_color(180, 180, 180)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(4)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-20)
            self.set_draw_color(200, 200, 200)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.set_font("Songti", "", 7)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, f"— {self.page_no()} —", align="C")

    def section_title(self, text, size=16):
        self.set_font("Songti", "B", size)
        self.set_text_color(26, 26, 26)
        self.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(139, 26, 26)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_title(self, text, size=12):
        self.set_font("Songti", "B", size)
        self.set_text_color(26, 26, 26)
        self.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Songti", "", 9.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6.5, text, align="L")
        self.ln(1)

    def bold_body(self, text):
        self.set_font("Songti", "B", 9.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6.5, text, align="L")
        self.ln(1)

    def callout(self, text):
        self.set_fill_color(248, 244, 236)
        self.set_draw_color(139, 26, 26)
        x, y = self.get_x(), self.get_y()
        self.set_font("Songti", "", 9)
        self.set_text_color(70, 50, 50)
        # Draw background
        self.rect(x, y, self.w - self.l_margin - self.r_margin, 22, "F")
        # Draw accent bar
        self.set_fill_color(139, 26, 26)
        self.rect(x, y, 1.5, 22, "F")
        self.set_xy(x + 5, y + 2)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5.5, text)
        self.ln(4)

    def short_line(self):
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)


pdf = ReportPDF("P", "mm", "A4")
pdf.set_auto_page_break(auto=True, margin=22)
pdf.add_font("Songti", "", FONT_PATH, collection_font_number=1)
pdf.add_font("Songti", "B", FONT_PATH, collection_font_number=1)

# ── Cover page ──
pdf.add_page()
pdf.set_fill_color(26, 15, 15)
pdf.rect(0, 0, 210, 297, "F")

# Title area
pdf.set_y(80)
pdf.set_font("Songti", "B", 28)
pdf.set_text_color(235, 225, 215)
pdf.cell(0, 16, "深度调查档案室", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Songti", "", 14)
pdf.set_text_color(180, 160, 150)
pdf.cell(0, 12, "13 篇文章质量评估报告", align="C", new_x="LMARGIN", new_y="NEXT")

# Accent rule
pdf.set_y(130)
pdf.set_draw_color(139, 26, 26)
pdf.set_line_width(1.2)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())

# Author / date
pdf.set_y(145)
pdf.set_font("Songti", "", 11)
pdf.set_text_color(180, 160, 150)
pdf.cell(0, 8, "调查团队", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "2026 年 7 月 23 日", align="C", new_x="LMARGIN", new_y="NEXT")

# Description
pdf.set_y(180)
pdf.set_font("Songti", "", 9)
pdf.set_text_color(140, 130, 120)
pdf.multi_cell(0, 6, 
    "本报告从普通读者视角，对截至 2026 年 7 月 23 日已发布的全 13 篇调查报道\n"
    "进行逐篇阅读、打分、排名，并为每篇文章提出具体的分析增量方向。\n"
    "评估维度涵盖标题吸引力、导语力度、结构清晰度、数据可视化、\n"
    "叙事文笔、洞见深度与结语收束。",
    align="C")

# ══════════════════════════════ 正文 ══════════════════════════════

pdf.add_page()
pdf.section_title("评估方法说明", 14)
pdf.body_text(
    "本次评估基于普通读者视角，从以下七个维度对全部 13 篇已发布文章进行综合打分："
    "标题吸引力、导语力度、结构清晰度、数据可视化、叙事文笔、洞见深度、结语收束。"
    "每项维度加权后得出百分制总分，满分 100 分。"
)

# ── Ranking table ──
pdf.ln(2)
pdf.section_title("完整排序", 14)

# Table
col_w = [14, 100, 14, 132]  # Adjust based on A4 width (190 usable)
table_data = [
    ["排名", "文章", "评分", "关键词"],
    ["1st", "希尔顿：卖钥匙的酒店帝国", "92", "最好的隐喻贯穿 + 最佳数据可视化"],
    ["2nd", "五粮液：半瓶酒的回响", "90", "最锐利的分析——为什么老二跌得最惨"],
    ["3rd", "周生生：金价跌了反而暖了", "88", "最佳反直觉叙事 + 历史纵深感"],
    ["4th", "DeepSeek：把模型开源把账本捂紧", "85", "核弹级开篇 hook，核心悖论精准"],
    ["5th", "宇树：会翻跟头的机器人", "84", "最深入的研究工程，但对读者太密"],
    ["6th", "小红书：种草的帝国信任的裂缝", "82", "\"帝国 vs 裂缝\"角度好，缺硬数据"],
    ["7th", "赛力斯：灵魂交给华为的车厂", "81", "最完整的灵魂叙事弧线，donut 图"],
    ["8th", "建滔系：铜箔帝国与AI叙事", "80", "家族套现 145 亿是全文最好细节"],
    ["9th", "长鑫：存储涨价周期顶端", "79", "周期分析教科书，技术节太硬"],
    ["10th", "宝马：百年驾驶乐趣", "78", "专业但可预期，无惊喜"],
    ["11th", "燧原：一家AI芯片独角兽", "76", "核心发现尖锐，但结构太机械"],
    ["12th", "智谱：学霸下海", "75", "话题大深度浅，值得更深入"],
    ["13th", "平安证券：平安的棋子", "73", "输在选题——公司太\"正常\""],
]

# Table header
pdf.set_font("Songti", "B", 8)
pdf.set_fill_color(139, 26, 26)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(table_data[0]):
    pdf.cell(col_w[i], 7, h, border=1, align="C", fill=True)
pdf.ln()

# Table body
pdf.set_font("Songti", "", 7.5)
for row_idx, row in enumerate(table_data[1:]):
    if row_idx % 2 == 0:
        pdf.set_fill_color(247, 244, 238)
    else:
        pdf.set_fill_color(255, 255, 255)
    
    if row_idx < 3:
        pdf.set_text_color(26, 26, 26)
    else:
        pdf.set_text_color(60, 60, 60)

    for i, cell in enumerate(row):
        align = "C" if i in [0, 2] else "L"
        pdf.cell(col_w[i], 6.5, cell, border=1, align=align, fill=True)
    pdf.ln()

pdf.ln(3)

# ── Color key ──
pdf.body_text("评分区间：90-92 为卓越，85-89 为优秀，80-84 为良好，75-79 为一般，73-74 为及格。前三名与后三名差距约 20 分，反映选题和叙事张力的显著差异。")

# ══════════════════════════════ 分篇评估 ══════════════════════════════

articles = [
    ("1. 希尔顿（92 分）：唯一一篇无懈可击",
     "【最强之处】全系列执行最完美的核心隐喻——\"卖钥匙\"三字贯穿全文，"
     "从 99.4% 不拥有酒店的惊人事实，到 Hampton 税费逐层拆解，到尾声\"钥匙生意最妙的地方\"，"
     "每章都在深化。数据可视化的天花板——Hampton Inn \"希尔顿税费\"拆解表，一个表格讲清了轻资产商业模式的全部底层逻辑。"
     "叙事弧线完整：黑石杠杆收购、金融危机亏 70%、转型钥匙模式、140 亿退出——有戏剧性，也有解释力。",
     "【可增加的分析】品牌稀释的量化推演——50 万间在建客房集中入市后对存量入住率的冲击；"
     "忠诚度积分的\"隐形负债\"——breakage 率每下降 10% 对利润的实际影响；"
     "与万豪的竞争策略对比——做中高端（Hampton 占 27%）在消费降级时的优势，在消费升级时的风险。"),
    
    ("2. 五粮液（90 分）：全系列最锐利的一次分析",
     "【最强之处】核心问题\"茅台没倒，为什么五粮液倒了\"的答案——"
     "\"经销商卖茅台赚 500，卖五粮液亏 50，砍单先砍亏钱的\"——是对老二困境最简单也最深刻的拆解。"
     "五大酒企营收增速对比图、出厂价与批价倒挂图、2026Q1 反弹对比图——每一张都在叙事。"
     "\"半瓶酒的回响\"这个标题是系列中少数有诗意的。",
     "【可增加的分析】重返千亿的路径推演——普五销量恢复到 X 万瓶、提价到 Y 元、系列酒做到 Z 亿，每条路径的可行性；"
     "直销与经销比例对比——茅台直销从个位数升到 40%+ 而五粮液做不到的原因（渠道利益绑定的历史包袱）；"
     "出海潜力分析——浓香型真的比酱香型更难出海吗。"),
    
    ("3. 周生生（88 分）：最好的反直觉叙事",
     "【最强之处】金价暴涨反而关了 74 家店；金价暴跌 25% 同店增长 17%。这个反转本身就是最佳 hook。"
     "90 年家族企业的\"脱钩之路\"提供了历史重量。独特的\"数据深挖\"章节把最硬核的量化分析独立成章，"
     "既满足深度读者又不干扰叙事流。",
     "【可增加的分析】金价弹性的量化系数——金价每涨 10%，同店销售额变化多少；"
     "非黄金业务（镶嵌/翡翠/钟表）的利润贡献和增长潜力——黄金毛利 8%-12%，镶嵌 30%-50%，但占比在缩小；"
     "与周大福的竞争态势对比——第一名 4000+ 店 vs 周生生约 700 店，市场集中度的变化方向。"),

    ("4. DeepSeek（85 分）：核弹级开篇，结尾较弱",
     "【最强之处】\"558 万美元→英伟达一天蒸发 6000 亿\"是全系列最好的开篇 hook。"
     "核心悖论\"技术彻底打开，财务彻底关上\"精确有力。营收传闻与 3500 亿估值的倒挂图表很聪明。开源经济学的讨论是独家的。",
     "【可增加的分析】\"如果换国产芯片\"的推演——昇腾算力效率约 H800 的 60%-80%，R3 训练成本因此升到多少；"
     "DeepSeek 如果闭源，按 OpenAI 定价的年化收入可能是现在的多少倍——开源\"损失的潜在收入\"量化；"
     "全球封禁的市场影响——意韩美部分禁用，这些市场在全球 AI 消费中的占比。"),
    
    ("5. 宇树（84 分）：最深的研究，最难的阅读",
     "【最强之处】最深入的研究工程——819 页招股书、三轮回复、美国国会调查。"
     "开篇\"王兴兴从大疆离职创业\"是全部文章中最有人情味的 hook。核心矛盾\"运动天赋 vs 智力短板\"选得好。",
     "【可增加的分析】拆分建议——做一个 15 分钟精简版和一个 54 分钟深度版；"
     "\"如果宇树做不成消费级机器人\"的终局推演——人形机器人 2026 年最大问题是没有 PMF，如果 2028 年前出货量不到 5 万台，420 亿估值的支撑点是什么；"
     "竞品时间线——Figure AI/Tesla Optimus 的出货量预测对比表。"),
    
    ("6. 小红书（82 分）：身份强、数据弱",
     "【最强之处】\"种草的帝国，信任的裂缝\"标题精准。开篇\"500 亿估值 vs 0.7% 市占率\"数据对比亮眼。"
     "\"帝国\"隐喻贯彻到位——从四亿人的决策入口到估值的斜率。",
     "【可增加的分析】广告 eCPM 对比——小红书的广告效率与抖音/快手/微信的对比；"
     "\"信任裂缝\"的量化指标——虚假种草投诉趋势、平台下架封号数量、监管处罚历史；"
     "IPO 招股书中电商收入占比和增长斜率与抖音电商/快手电商的对比——为什么交易闭环跑不通。"),

    ("7. 赛力斯（81 分）：被低估的灵魂叙事弧线",
     "【最强之处】重新评估后上调 8 分。\"每卖一辆问界，华为拿走 21.4%\"的 donut 图是档案室最好的数据可视化之一。"
     "\"五界分流\"对华为资源稀释的分析是真正的增量洞见。尾声回到陈虹\"灵魂论\"完成叙事闭环——"
     "\"四年前华为是赛力斯唯一的答案，四年后华为成了所有车企共享的考题\"是最佳金句之一。",
     "【可增加的分析】华为之外的核心能力清单——赛力斯在智能制造、供应链管理方面的自研积累；"
     "2026H1 预亏的账本结构深度拆解——亏损的 15-18 亿中，碳酸锂涨价/华为采购刚性增长/旧产线减值各占多少；"
     "与其他四界的横向对比——智界/享界/尊界/尚界的交付量、均价和毛利率。"),
]

# Middle batch
articles.extend([
    ("8. 建滔系（80 分）：家族套现是最好细节",
     "【最强之处】\"家族在周期顶端套现 145 亿\"是整座档案室最刺眼的发现。对 AI 叙事泡沫的质疑恰逢其时。",
     "【可增加的分析】AI 服务器 PCB 在总营收中的实际占比；"
     "周期时间表——覆铜板涨价周期何时结束，参考历史经验信号图；"
     "家族减持的精确时间表——每次配售的日期、价格、套现金额与公司喊话的时间对比。"),
    
    ("9. 长鑫（79 分）：周期分析出色，但太硬",
     "【最强之处】\"十年亏 366 亿→一季净赚 330 亿\"是教科书级的周期分析 hook。技术代差分析讲得清晰。",
     "【可增加的分析】DRAM 赚钱公式简化模型——利润 = 价格 × 产能 × 良率，用三星/海力士数据做参照系；"
     "与三星/海力士的成本对比——10 万片/月产能 vs 三星 50 万片/月的规模差距量化；"
     "国产替代路线图——自给率从 0% 到约 5%，未来 3 年上限由什么决定。"),
    
    ("10. 宝马（78 分）：专业但可预期",
     "【最强之处】标题\"踩不稳的电门\"好。制动系统召回引发利润预警的切入点选得好——小切口撬动大问题。",
     "【可增加的分析】宝马在中国的终端折扣率——i3 终端价比指导价低多少，渠道库存深度；"
     "新世代平台的盈亏平衡点——千亿欧元投入需卖出多少辆车回本；"
     "\"驾驶乐趣\"在电动化时代的品牌价值残值——当电动车加速都一样，这个溢价是否还能维持。"),
    
    ("11. 燧原（76 分）：追问×8 结构太机械",
     "【最强之处】\"腾讯单一客户占比从 8.53% 到 83.79%\"的核心发现尖锐有力。治理章节（不足 30% 投票权）揭示了治理风险。",
     "【可增加的分析】结构重写——以\"如果明天腾讯撤单，燧原会怎样\"贯穿始终，而非 8 个追问段落堆叠；"
     "国产 GPU 四小龙横向对比表——寒武纪/海光/燧原/壁仞的营收、亏损、技术路径；"
     "\"没有 CUDA 兼容\"意味着什么——生态问题，CUDA 有 300 万开发者，GCU 有多少。"),
    
    ("12. 智谱（75 分）：话题大、深度浅",
     "【最强之处】\"全球大模型第一股\"标签和价值 530 亿 vs 收入 7 亿的对比是好 hook。学术基因与商业化困境是真实的矛盾。",
     "【可增加的分析】47 亿亏损的结构性拆解——研发投入/销售费用/股权激励/折旧摊销各占多少；"
     "定价策略分析——API 定价相对同行是高是低，如果提到竞品价格收入增加多少；"
     "与 DeepSeek 的对比——两家清华系公司，一个开源一个闭源，一个不上市一个上市，谁的路线更有道理。"),
    
    ("13. 平安证券（73 分）：输在选题",
     "【最强之处】\"没有独立股票代码\"的独特角度。方正证券从并购民族证券到政泉控股纠纷到破产重整的 SVG 时序图质量不错。",
     "【可增加的分析】平安证券 IPO 的时间线和可能性——什么条件什么时候能拿到自己的股票代码；"
     "\"平安生态\"的内部利益链——平安银行和平安证券的交叉销售创造了多少价值，合规边界在哪；"
     "券商行业整合终局的全国地图——整合后的格局中平安的位置变化轨迹。"),
])

# Render each article
for i, (title, strength, improvement) in enumerate(articles):
    pdf.add_page()
    pdf.section_title(title, 13)
    
    # Strength
    pdf.sub_title("现有优势")
    pdf.body_text(strength)
    
    pdf.short_line()
    
    # Improvement
    pdf.sub_title("可增加的分析")
    pdf.body_text(improvement)

# ══════════════════════════════ 总结 ══════════════════════════════
pdf.add_page()
pdf.section_title("横向比较：关键差距总结", 14)

pdf.body_text(
    "经过全部 13 篇的阅读和重新评估，以下是最有价值的几个发现："
)

pdf.callout(
    "最好的文章都有一个不可替代的核心矛盾：希尔顿是\"99.4% 不拥有任何酒店\"，"
    "五粮液是\"茅台没倒为什么老二倒了\"，周生生是\"金价暴跌反而更值钱\"，"
    "DeepSeek 是\"技术彻底打开，财务彻底关上\"。这些悖论无法用在其他任何公司身上——"
    "它们构成了每篇文章不可替代的阅读理由。"
)

pdf.callout(
    "最弱的文章的共同问题是缺少一个让读者拍案的数字：平安证券的\"没有股票代码\"更像一个背景事实而不是一个发现。"
    "相比之下，希尔顿的\"一间 Hampton 每年贡献 80 万美元\"、赛力斯的\"华为拿走 21.4%\"、"
    "周生生的\"金价跌 25% 但同店涨 17%\"——这些数字本身就值得转发。"
)

pdf.callout(
    "数据可视化分成两个梯队：第一梯队用图表取代文字叙述——希尔顿的税费拆解表、"
    "五粮液的酒企对比图、赛力斯的 donut 图——不看正文也能读出核心结论。"
    "第二梯队用图表装饰文章——这些图表验证而不是揭示。"
)

pdf.ln(4)
pdf.short_line()
pdf.sub_title("最终结论")
pdf.body_text(
    "希尔顿、五粮液、周生生三篇构成了这个档案室目前的质量天花板。它们在\"可读性\"和\"信息密度\"之间"
    "找到了最佳平衡——没有字是多余的，没有图表是装饰性的。从第 4 名往下，每篇文章都有一两个突出的亮点，"
    "但也都有可量化的提升空间——本报告已为每篇列出了具体的改进方向。"
)

pdf.ln(8)
pdf.set_font("Songti", "", 8)
pdf.set_text_color(120, 120, 120)
pdf.multi_cell(0, 5, 
    "本报告基于截至 2026 年 7 月 23 日已部署的 13 篇调查报道。"
    "评级标准和改进建议均为个人观点，仅供内部参考。")

# Save
output_path = "/Users/panyp/WorkBuddy/#深度调查档案室/13篇报道质量评估报告.pdf"
pdf.output(output_path)
print(f"PDF 已生成：{output_path}")
print(f"共 {pdf.page_no()} 页")
