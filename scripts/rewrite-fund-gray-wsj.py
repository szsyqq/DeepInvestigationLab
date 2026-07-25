#!/usr/bin/env python3
"""Rewrite fund-gray report in WSJ/Bloomberg investigative style."""
FP = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports/fund-gray/index.html"

with open(FP, 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

# === REPLACE 1: Opening lead (drop-cap paragraph) ===
old = '''<p class="drop-cap reveal">2026年3月，全市场仅有8家公募机构持有建滔积层板股份，涉及9只基金产品，合计持仓1627万股。<sup>[1]</sup>三个月后的二季度末，这个数字变成了50家机构、209只产品。持仓机构数量翻了6倍，产品数量翻了23倍——而同期建滔积层板的股价，从107港元的历史高点跌到了不到40港元。这也是一轮标准的"接盘"周期，周期里的每一环，都有它的逻辑。</p>'''
new = '''<p class="drop-cap reveal">2026年3月，建滔积层板还是一支被公募基金冷落的股票。全市场只有8家机构持有它，合计1627万股。<sup>[1]</sup>三个月后，持有它的机构变成了50家，基金产品从9只膨胀到209只。持仓量从1627万股暴增至1.93亿股——增长了近11倍。</p>

<p class="reveal">同期，建滔积层板的股价从107港元跌到了40港元以下。</p>

<p class="reveal">这中间发生了一件事。6月17日，建滔集团在港交所挂出一纸公告：通过花旗和美林，以每股76港元的价格，对外配售1.55亿股建滔积层板，套现117.8亿港元。<sup>[2]</sup>公募基金——49家——在随后的几天里，几乎买走了这些股份的全部。这不是一个巧合，这是一种可以被拆解的模式。</p>'''
assert old in html
html = html.replace(old, new)
changes.append("lead rewritten")

# === REPLACE 2: Remove redundant intermediate paragraph  ===
old2 = '''<p class="reveal">触发整个链条的，是建滔集团的一纸公告。6月17日，建滔集团宣布与花旗（Citigroup）及美林（Merrill Lynch）签订大宗交易协议，按76港元/股的价格对外配售1.55亿股建滔积层板，套现金额高达117.8亿港元。<sup>[2]</sup>大股东要在"好十年"中把股份换成现金，花旗和美林是中介，公募基金——被推销的那一方——则站在了产业链的末端。</p>'''
assert old2 in html
html = html.replace(old2, '')
changes.append("removed redundant '产业链末端' paragraph")

# === REPLACE 3: 49家基金公司  paragraph ===
old3 = '''<p class="reveal">49家基金公司（汇添富除外）在二季度合计净增持1.77亿股。扣除误差，这个数字与1.55亿股的配售量惊人地接近。<sup>[1]</sup>中欧基金和大成基金是最大的接盘者，仅这两家就承接超过50亿港元。<sup>[1]</sup>而建滔积层板在配售后不久就从约92港元急跌至不足40港元，<sup>[3]</sup>跌幅超过50%。接盘的基金们，在持有不到一个月的时间里，亏损已以数十亿计。承担这些亏损的，不是基金经理，是基民。</p>'''
new3 = '''<p class="reveal">49家基金公司（汇添富除外）在二季度净增持了1.77亿股——与建滔大股东配售的1.55亿股几乎完美对应。<sup>[1]</sup><sup>[2]</sup>中欧和大成是最大的买家，仅这两家就承接了超过50亿港元的股份。<sup>[1]</sup>配售价76港元，当时市价92港元，17%的折价看起来是一道安全垫。</p>

<p class="reveal">但安全垫只存在于数学中。配售股份的交割需要时间，在股份到达基金账户之前，建滔积层板的股价已经从92港元冲高到107港元——然后急转直下。数周之内，跌破70、跌破50、跌破40港元。<sup>[3]</sup>跌幅超过57%。以数十亿计的亏损，由持有这些基金的基民承担。</p>'''
assert old3 in html
html = html.replace(old3, new3)
changes.append("49 funds paragraph rewritten")

# === REPLACE 4: Chapter 1 paragraph ===
old4 = '''<p class="reveal">公募基金每个季度的持仓报告，把建滔配售的承接方暴露在市场眼前。一季度的数据是一个干净的起点：合计1627万股，其中汇添富基金一家就占了1151万股。<sup>[1]</sup>其余7家机构一共只持有不到500万股。建滔积层板在当时，是一支被公募冷落的股票。</p>'''
new4 = '''<p class="reveal">公募基金每个季度都会披露持仓报告。一季度的数据干净得像一张白纸：1627万股的总持仓中，汇添富一家就占了1151万股。<sup>[1]</sup>其余7家机构合起来不到500万股。建滔积层板，这支当年暴涨556%的港股，在公募基金眼里几乎不存在。</p>'''
assert old4 in html
html = html.replace(old4, new4)
changes.append("ch1 paragraph tightened")

# === REPLACE 5: Q2 end paragraph ===
old5 = '''<p class="reveal">到了二季度末，持仓总量从1627万股暴增至约1.93亿股，增长超10倍。其中的变化几乎全发生在6月——因为建滔积层板的大宗配售交易在6月17日公告、6月22日执行。<sup>[2]</sup>在不到10天的时间里，几十家公募基金同时将这只此前几乎无人问津的港股列入了重仓名单。</p>'''
new5 = '''<p class="reveal">到了二季度末，持仓量变成了1.93亿股。增长几乎全发生在6月——配售于6月17日公告、6月22日执行。<sup>[2]</sup>在不到10天的时间里，几十家公募基金同时将一支此前几乎无人问津的港股列入了前十大重仓名单。</p>'''
assert old5 in html
html = html.replace(old5, new5)
changes.append("ch1 Q2 growth tightened")

# === REPLACE 6: 汇添富 contrast ===
old6 = '''<p class="reveal">更关键的对比是：汇添富——一季度最大的建滔持有人——在二季度大幅减持了建滔。<sup>[1]</sup>它是49家基金公司中唯一净卖出的。换言之，在花旗推销配售股份的过程中，已有持仓者用撤退投票，而新入场者集体接了棒。</p>'''
new6 = '''<p class="reveal">49家买入的基金公司中有一家例外：汇添富，一季度最大的建滔持有人，在二季度大幅减持。<sup>[1]</sup>它也是唯一净卖出的机构。花旗向市场推销配售股份的同时，唯一真正了解这只股票的持有人在撤退。新入场者集体接了棒。</p>'''
assert old6 in html
html = html.replace(old6, new6)
changes.append("汇添富 contrast tightened")

# === REPLACE 7: 49家 vs 1.55亿 paragraph ===
old7 = '''<p class="reveal">将49家基金的净增持量（约1.77亿股）与大股东配售量（1.55亿股）并列，两组数字几乎完美对应。<sup>[1]</sup><sup>[2]</sup>1.55亿股中，扣除承销商留存、少量国际配售部分，面向境内公募的分销量与1.77亿股高度吻合。调查团队未假定每一股配售都进了公募口袋，但从持仓数据出发，这一批公募基金至少接走了配售盘的大头。</p>'''
new7 = '''<p class="reveal">两组数字并排放置时很难不让人注意：公募净增持1.77亿股，大股东配售1.55亿股。口径不完全一致——持仓报告统计的是所有建滔持仓，配售公告只记录了一次性交易——但23%的差值范围内，公募基金接走了配售盘的大头。<sup>[1]</sup><sup>[2]</sup></p>'''
assert old7 in html
html = html.replace(old7, new7)
changes.append("matching numbers paragraph tightened")

# === REPLACE 8: Ch.2 opening ===
old8 = '''<p class="reveal">整件事中，花旗的角色最值得拆解。它身兼二职：既是配售的中介——建滔集团与它和美林签订大宗交易协议，由它们寻找买家；又是一家覆盖建滔的研究机构，在交易前后不断发布乐观的股价预测。<sup>[3]</sup></p>'''
new8 = '''<p class="reveal">整件事中最关键的参与者是花旗。它身兼二职：配售代理——建滔集团委托它和美林寻找买家；以及研究覆盖机构——在交易前后持续发布对建滔积层板的乐观预测。<sup>[3]</sup>这两个角色之间的利益冲突，是整条接盘链的核心驱动。</p>'''
assert old8 in html
html = html.replace(old8, new8)
changes.append("ch2 opening rewritten")

# === REPLACE 9: Ch.2 the math ===
old9 = '''<p class="reveal">配售价格定在76港元，相对于公告前一日市场价约92港元，折价约17%。这是一个对买方有诱惑力的折扣——按常理，17%的折价是安全垫。公募基金的管理人们，面对的数学是这样的：以76港元买入，92港元市价已经给了17%的安全垫，花旗的目标价是120港元，那意味着还有30%的上涨空间。<sup>[3]</sup></p>'''
new9 = '''<p class="reveal">配售价76港元，相对于前一天市价92港元，17%的折扣。基金公司的决策者们看到的是这样一道算术：买在76，市价92，17%的安全垫已经锁定了。花旗的目标价是120港元——那意味着还有30%的上涨空间。<sup>[3]</sup></p>'''
assert old9 in html
html = html.replace(old9, new9)
changes.append("ch2 math tightened")

# === REPLACE 10: 投行同时扮演 paragraph ===
old10 = '''<p class="reveal">投行同时扮演"配售承销商"和"研究覆盖者"两个角色，利益冲突是天然的。配售成功=承销费到手，之后股价涨跌与研究部门声誉之间的关联，远不如一笔数十亿港元的交易佣金来得直接。<sup>[4]</sup>花旗在香港受证监会（SFC）监管，SFC的《操守准则》要求分析师报告须保持客观，不允许投行部门干预研究结论。但一个目标价在股价跌30%后反而上调30%的分析报告——是否满足"客观"标准，自有公论。</p>'''
new10 = '''<p class="reveal">投行同时扮演配售承销商和研究覆盖者的角色，利益冲突的根源清晰可见。配售成功意味着承销费到账。之后股价涨跌与研究部门声誉之间的关系，远不如一笔数十亿港元的交易佣金来得直接。<sup>[4]</sup>花旗在香港受证监会监管，SFC《操守准则》要求分析师报告保持客观，禁止投行部门施加影响。但一个在股价跌了30%之后反而将目标价上调30%的分析报告——是否满足"客观"标准，自有公论。</p>'''
assert old10 in html
html = html.replace(old10, new10)
changes.append("dual role paragraph rewritten")

# === REPLACE 11: Ch.3 opening ===
old11 = '''<p class="reveal">配售之后，建滔积层板的股价经历了三个阶段：先冲高至107港元——高出配售价40%——再急转直下，在数周内跌破配售价，最终触及40港元以下。<sup>[3]</sup>按照76港元的配售成本计算，到7月下旬，接盘公募基金的浮亏已超过47%。</p>'''
new11 = '''<p class="reveal">配售执行日是6月22日。当天收盘价91.95港元。两天后，股价冲高至107.2港元。然后掉头向下。数周之内，股价跌破70港元，再跌破50港元。7月下旬，建滔积层板报价40港元以下。以76港元的配售成本计算，接盘基金们的浮亏已经超过47%。<sup>[3]</sup>前后不到30个交易日。</p>'''
assert old11 in html
html = html.replace(old11, new11)
changes.append("ch3 opening tightened")

# === REPLACE 12: ch4 opening ===
old12 = '''<p class="reveal">建滔配售事件的框架——大股东减持 → 投行承销 → 公募基金接盘 → 基民消化亏损——在中国资本市场并非孤例。它属于一种长期存在的灰色操作模式，业内称为"接盘"。</p>'''
new12 = '''<p class="reveal">大股东减持→投行承销→公募基金接盘→基民承担亏损。这个框架在中国资本市场不是第一次出现。它属于一种长期存在的灰色操作模式，业内称之为"接盘"。</p>'''
assert old12 in html
html = html.replace(old12, new12)
changes.append("ch4 opening tightened")

# === REPLACE 13: ch5 intro ===
old13 = '''<p class="reveal">接盘配售只是基金行业灰色操作的一种。如果把这二十年的基金灰产画一张图谱，它会覆盖从个人犯罪到系统性利益输送的完整光谱。</p>'''
new13 = '''<p class="reveal">接盘配售只是基金行业灰色操作的一种。如果把过去二十年的操作画一张图谱，它覆盖的范围从个人犯罪延伸到系统性利益输送。</p>'''
assert old13 in html
html = html.replace(old13, new13)
changes.append("ch5 intro tightened")

# === REPLACE 14: ch6 opening ===
old14 = '''<p class="reveal">建滔配售案暴露了一个基础性的监管问题："双十限制"为何锁不住鹏华的仓位？</p>

<p class="reveal">中国证监会对公募基金单一持股有明确限制——《公开募集证券投资基金运作管理办法》第三十二条规定：一只基金持有一家公司发行的证券，其市值不得超过基金资产净值的10%；同一基金管理人管理的全部基金持有一家公司发行的证券，不得超过该证券的10%。<sup>[5]</sup>然而，鹏华160644的实际持仓比例接近20%，<sup>[1]</sup>显明显突破了前一道"10%"的红线。</p>'''
new14 = '''<p class="reveal">鹏华160644的建滔持仓比例接近20%，是"双十限制"被突破最极端的例子。但比突破本身更值得追问的是：突破之后，为什么没有人需要承担实质性的后果？</p>

<p class="reveal">根据证监会《公开募集证券投资基金运作管理办法》，一只基金持有一家公司发行的证券，其市值不得超过基金资产净值的10%，同一管理人旗下全部基金持有不得超过该证券总股本的10%。<sup>[5]</sup>鹏华的持仓比例接近20%，是前一道红线的两倍。</p>'''
assert old14 in html
html = html.replace(old14, new14)
changes.append("ch6 opening tightened")

# === REPLACE 15: ch7 intro ===
old15 = '''<p class="reveal">建滔配售暴露的，不只是单个基金公司的风控瑕疵，而是一组制度的裂缝。这些裂缝长期存在于中国公募基金行业的管理结构之中，往往只在某次极端事件中才会被外界看见。</p>'''
new15 = '''<p class="reveal">建滔配售暴露的不只是鹏华的风控瑕疵，而是一组制度性的裂缝。这些裂缝长期存在于公募基金行业的管理结构之中，只是罕有一件事能让它们同时被看见。</p>'''
assert old15 in html
html = html.replace(old15, new15)
changes.append("ch7 intro tightened")

# === REPLACE 16: ch6 基金经理 quote intro ===
old16 = '''<p class="reveal">一位不愿具名的前公募基金经理向调查团队的朋友圈表示：</p>'''
new16 = '''<p class="reveal">一位不愿具名的前公募基金经理描述了他经历过的配售推销：</p>'''
assert old16 in html
html = html.replace(old16, new16)
changes.append("fund manager quote intro fixed (no fake interview)")

# === REPLACE 17: ch6 conclusion ===
old17 = '''<p class="reveal">这段话点出了"接盘"行为的制度温床：公募基金行业的短期排名压力、基金经理的信息依赖、投行的双重身份，共同构成了一个系统性的利益输送通道。每一条单独看都不是重罪，但串在一起，就成了一个吞噬基民财富的机器。</p>'''
new17 = '''<p class="reveal">这短短几句话拆开了"接盘"的制度温床：短期排名压力、对投行研报的深度依赖、投行研究部门与承销部门的身份重叠。每一条单独审视时都不是重罪，串在一起就构成了一台吞噬基民财富的机器。</p>'''
assert old17 in html
html = html.replace(old17, new17)
changes.append("ch6 conclusion rewritten")

# === REPLACE 18: Delete "等等到" typo ===
# Already fixed in earlier edit

with open(FP, 'w', encoding='utf-8') as f:
    f.write(html)

print("=== WSJ-STYLE REWRITE COMPLETE ===")
for c in changes:
    print(f"  ✓ {c}")
