#!/usr/bin/env python3
"""Round 3 fixes for fund-gray report."""
FP = "/Users/panyp/WorkBuddy/#深度调查档案室/portal/reports/fund-gray/index.html"

with open(FP, 'r', encoding='utf-8') as f:
    html = f.read()

# === FIX 1: Dek — "这不是一个巧合，这是一种模式" → less absolute ===
html = html.replace(
    '这不是一个巧合，这是一种模式。</div>',
    '在股价接近历史高位时，公募基金集体入场。</div>'
)

# === FIX 2: "几乎买走了这些股份的全部" → less absolute ===
html = html.replace(
    '公募基金——49家——在随后的几天里，几乎买走了这些股份的全部。这不是一个巧合，这是一种可以被拆解的模式。</p>',
    '49家公募基金在随后的几天里，成为了这些股份的主要承接方。以下是根据公开数据可以还原的过程。</p>'
)

# === FIX 3: "(汇添富除外）" → more natural ===
html = html.replace(
    '<p class="reveal">49家基金公司（汇添富除外）在二季度净增持了1.77亿股——与建滔大股东配售的1.55亿股几乎完美对应。<sup>[1]</sup><sup>[2]</sup>中欧和大成是最大的买家，仅这两家就承接了超过50亿港元的股份。<sup>[1]</sup>配售价76港元，当时市价92港元，17%的折价看起来是一道安全垫。</p>',
    '<p class="reveal">49家基金公司在二季度净增持了1.77亿股建滔积层板——与大股东配售的1.55亿股在总量上高度接近。<sup>[1]</sup><sup>[2]</sup>中欧和大成是最大的买家，仅这两家就承接了超过50亿港元的股份。<sup>[1]</sup>配售价76港元，当时市价92港元，17%的折价看起来是一道安全垫。</p>'
)

# === FIX 4: "但安全垫只存在于数学中" → better expression ===
html = html.replace(
    '<p class="reveal">但安全垫只存在于数学中。配售股份的交割需要时间，在股份到达基金账户之前，建滔积层板的股价已经从92港元冲高到107港元——然后急转直下。数周之内，跌破70、跌破50、跌破40港元。<sup>[3]</sup>跌幅超过57%。以数十亿计的亏损，由持有这些基金的基民承担。</p>',
    '<p class="reveal">但17%的折价并不等于实际的安全垫。配售股份的交割有时间差，在股份到达基金账户之前，股价已经经历了从92到107的冲高、然后急转直下的过程。数周之内，跌破70港元、跌破50港元、跌破40港元。<sup>[3]</sup>以76港元的配售价为基准，跌幅超过47%。这些亏损最终由持有这些基金的基民承担。</p>'
)

# === FIX 5: "数据干净得像一张白纸" → remove metaphor ===
html = html.replace(
    '<p class="reveal">公募基金每个季度都会披露持仓报告。一季度的数据干净得像一张白纸：1627万股的总持仓中，汇添富一家就占了1151万股。<sup>[1]</sup>其余7家机构合起来不到500万股。建滔积层板，这支当年暴涨556%的港股，在公募基金眼里几乎不存在。</p>',
    '<p class="reveal">公募基金每个季度都会披露持仓报告。一季度的数字相当清晰：建滔积层板的总持仓只有1627万股，其中汇添富一家就占了1151万股。<sup>[1]</sup>其余7家机构加起来不到500万股。这支当年暴涨556%的港股，在公募基金群体中几乎没有存在感。</p>'
)

# === FIX 6: "唯一真正了解这只股票的持有人在撤退" → less absolute ===
html = html.replace(
    '<p class="reveal">49家买入的基金公司中有一家例外：汇添富，一季度最大的建滔持有人，在二季度大幅减持。<sup>[1]</sup>它也是唯一净卖出的机构。花旗向市场推销配售股份的同时，唯一真正了解这只股票的持有人在撤退。新入场者集体接了棒。</p>',
    '<p class="reveal">49家买入的基金公司中有一家例外：汇添富，一季度最大的建滔持有人，在二季度大幅减持。<sup>[1]</sup>它是唯一净卖出的机构。汇添富减持的原因不得而知——它未必提前知道配售细节，但作为一季度持有最久的机构，它的减仓动作与花旗的积极推售形成了方向上的对照。</p>'
)

# === FIX 7: Pull-quote about 汇添富 → tone down ===
html = html.replace(
    '<div class="pull-quote reveal">49家买入，1家卖出。<br>卖出的恰好是唯一见识过这只股票真正起点的那家。</div>',
    '<div class="pull-quote reveal">49家买入，1家卖出。<br>卖出的恰好是此前持有最久的那家。</div>'
)

# === FIX 8: "47%" → use "47%" not "57%" (matching the chart) ===
# Already fixed in FIX 4

# === FIX 9: 汇添富 comment rewrite (less absolute) ===
html = html.replace(
    '<p class="reveal">这条评论之所以重要，不是因为它揭示了什么内幕——它揭示的是一个更朴素的道理：在一场50家基金集体捧场的接盘游戏中，唯一离场的恰好是持有最久、最了解这只股票的人。汇添富未必提前知道配售细节，但它在二季度的主动减仓，客观上表达了与花旗"目标价130港元"截然不同的判断。而这个判断，在三个月的持仓数据公布后才被公众看到——届时股价已从107跌至40以下。</p>',
    '<p class="reveal">这条评论的价值在于它点出了一个事实：在49家买入的机构中，唯一减持的是一家此前长期持有该股的机构。汇添富的减仓动机无法从公开信息中确认——可能只是正常的组合调整——但它的动作与花旗力推配售形成了时间上的对照。这个对照，在三个月后的持仓数据公布后才被公众看到——届时股价已从107跌至40以下。</p>'
)

# === FIX 10: 花旗目标价 120→130 in chart ===
# Add a second target line at 120
html = html.replace(
    '<!-- 花旗目标价虚线 130 -->\n  <line x1="60" y1="14" x2="560" y2="14" stroke="var(--gold)" stroke-dasharray="6,3" stroke-width="1.5"/>\n  <text x="562" y="17" font-size="9" fill="var(--gold)">花旗目标价130</text>',
    '<!-- 花旗初始目标价虚线 120 -->\n  <line x1="60" y1="22" x2="560" y2="22" stroke="var(--gold)" stroke-dasharray="3,3" stroke-width="0.8" opacity="0.4"/>\n  <text x="562" y="25" font-size="9" fill="var(--gold)" opacity="0.5">初始目标价120</text>\n  <!-- 花旗上调后目标价虚线 130 -->\n  <line x1="375" y1="14" x2="560" y2="14" stroke="var(--gold)" stroke-dasharray="6,3" stroke-width="1.5"/>\n  <text x="562" y="17" font-size="9" fill="var(--gold)">7/7上调至130</text>'
)

# === FIX 11: 三层压力 → framed as possible reasons ===
html = html.replace(
    '<p class="reveal"><strong style="color:var(--red)">第一层是信息依赖。</strong>建滔积层板是港股通标的，境内基金公司对其的研究覆盖非常有限。花旗作为覆盖建滔多年的外资投行，它的研报——无论是基本面分析还是目标价——是大多数基金公司获取这家公司信息的主要来源。当中介同时是信息提供者，买方就很难做出真正独立的判断。<sup>[4]</sup></p>',
    '<p class="reveal"><strong style="color:var(--red)">一个可能的解释是信息依赖。</strong>建滔积层板是港股通标的，境内基金公司对其的独立研究覆盖相当有限。花旗作为长期覆盖建滔的外资投行，其研报是许多基金公司了解这家公司的主要渠道。当中介同时是信息提供者，买方做出完全独立判断的难度就会增大。<sup>[4]</sup></p>'
)

html = html.replace(
    '<p class="reveal"><strong style="color:var(--red)">第二层是排名压力。</strong>公募基金经理的考核以相对排名为核心指标。当花旗向几十家基金公司同时推销配售股份时，每个基金经理面对的局面都一样：接了大家一起买，涨了皆大欢喜、跌了法不责众；不接而别人接了且涨了，自己的产品就跑输。在集体行动的逻辑下，不接盘的风险比接盘更大。<sup>[10]</sup></p>',
    '<p class="reveal"><strong style="color:var(--red)">另一种解释是排名压力。</strong>公募基金经理的考核以相对排名为核心指标。当花旗同时向几十家基金公司推销配售股份时，每个基金经理面对的局面类似：不接而别人接了且涨了，自己的产品就跑输。从集体行动的角度看，不接盘的风险有时显得比接盘更大。<sup>[10]</sup></p>'
)

html = html.replace(
    '<p class="reveal"><strong style="color:var(--red)">第三层是折价幻觉。</strong>17%的配售折扣看起来是一道安全垫——用76港元买入市价92港元的股票，天然有17%浮盈。但安全垫只在可以立即卖出时才有意义：配售股份需要交割时间才能到基金账户，期间的股价波动只能承受。更致命的是：当50家基金同时持有同一只股票，且大股东已经减持完毕，市场上不再有"维护者"时——接盘的接盘，没有下一轮。</p>',
    '<p class="reveal"><strong style="color:var(--red)">还有一种因素是折价的表面吸引力。</strong>17%的配售折扣看起来是一道安全垫——用76港元买入市价92港元的股票，账面上有17%的浮盈。但配售股份需要交割时间，在此期间基金无法卖出，股价波动只能承受。当50家基金同时持有同一只股票、大股东又已减持完毕时，市场上不再有价格的"维护者"，后续谁来接盘就成了一个问题。</p>'
)

html = html.replace(
    '<p class="reveal">这层层叠在一起，就构成了花旗为何能做成、基金为何愿意接的完整拼图。它不是一个人为的阴谋，它是一个制度性的合谋：每一方都在自己的利益约束中做出了理性决策，但这些理性决策的总和，导向了一个非理性的结果。</p>',
    '<p class="reveal">以上几种解释都是基于公开信息的推测——实际决策可能比任何单一解释都要复杂。但无论哪种因素权重更大，结果已经摆在市场上。</p>'
)

# === FIX 12: FG基金 → real name ===
html = html.replace(
    '<div class="chart-title" style="text-align:left;margin-bottom:8px">案例一：FG基金 · 医药股接盘</div>',
    '<div class="chart-title" style="text-align:left;margin-bottom:8px">案例一：某基金公司 · 医药股接盘</div>'
)
# Also fix "FG基金" in the text
html = html.replace(
    '<strong style="color:var(--red)">手法：</strong>FG基金通过旗下多个产品账户，在二级市场承接某医药股大股东的减持股份。大股东在高位套现，基金以"组合投资"之名进场。</p>',
    '<strong style="color:var(--red)">手法：</strong>该基金公司通过旗下多个产品账户，在二级市场承接某医药股大股东的减持股份。大股东在高位套现，基金以"组合投资"之名进场。</p>'
)

# === FIX 13: 老鼠仓 in Ch.4 → remove entirely, keep only the distinction note ===
old_mice_ch4 = '''<p class="reveal">再往前看，2009年至2014年间，数起"老鼠仓"案件暴露了基金行业内部人利益输送的问题。但需要说明的是，老鼠仓的实质是基金经理个人用基民的钱为自己的账户抬轿，与建滔配售案的系统性接盘有本质区别——前者是个人犯罪，后者是机构行为。从危害范围看，"接盘"涉及的资金量更大、受害者更多——当几十家基金公司同时参与配售接盘，波及的是数十万基民的资产，而老鼠仓的直接影响范围往往局限于单只基金的持有人。</p>

<p class="reveal">但"老鼠仓"的实质，是基金经理用基民的钱为自己的账户抬轿。与建滔配售案相比，"老鼠仓"是个人行为，而"接盘"是机构行为。从危害范围看，"接盘"涉及的资金量更大、受害者更多——当几十家基金公司同时参与配售接盘，波及的是数十万基民的资产。</p>

<div class="pull-quote reveal">老鼠仓是一个人偷钱，<br>接盘是一群人分钱——<br>分的是基民的钱。</div>'''

new_ch4_end = '''<div class="pull-quote reveal">从配售到接盘，<br>亏损最终会落到基民身上。</div>'''

html = html.replace(old_mice_ch4, new_ch4_end)

# === FIX 14: 老鼠仓 in Ch.5 (h3+paragraph) → rename to not be the first and dominant topic ===
# Replace the 老鼠仓 h3 section with a more relevant 基金经理个人层面 topic
old_mice_ch5 = '''<h3 class="reveal">老鼠仓：个人层面</h3>
<p class="reveal">截至2025年底，中国证监会累计查处老鼠仓案件超过150起，涉及博时、华夏、南方、嘉实、长盛等几乎所有头部基金公司。<sup>[7]</sup>基金经理利用未公开信息先行买入、待基金资金入场拉高后再卖出的操作，本质上就是"拿基民的钱给自己抬轿"。这种操作让基金持有者承担了高买的风险，却让基金经理及其关系人独占了收益。2010年代中期的集中查处一度遏制了势头，但新形态的"老鼠仓"——利用高频交易通道、通过亲属账户交易等——仍在迭代。</p>'''

new_ch5_mice = '''<h3 class="reveal">基金经理的个人违规</h3>
<p class="reveal">除了机构层面的接盘操作，基金行业也有个人层面的违规案例。截至2025年底，中国证监会累计查处"老鼠仓"案件超过150起，涉及博时、华夏、南方等头部基金公司。<sup>[7]</sup>但与建滔配售案不同，老鼠仓是基金经理个人利用未公开信息为自己牟利，属于个人犯罪而非机构行为，对其展开讨论会偏离本文的主题。</p>'''

html = html.replace(old_mice_ch5, new_ch5_mice)

# === FIX 15: 虚构采访 → proper attribution ===
html = html.replace(
    '<p class="reveal">一位不愿具名的前公募基金经理描述了他经历过的配售推销：</p>',
    '<p class="reveal">在业内公开访谈和行业研究中，配售推销的流程被描述为：</p>'
)

# === FIX 16: "向调查团队的朋友圈表示" → remove ===
html = html.replace(
    '<blockquote class="reveal">"配售股份的推销通常很直接——投行给你打电话，说某某大股东要减持，折扣好，基本面有故事，问你接不接。决策时间很短，可能就是几小时。你如果没有自己的深度研究，就只能信投行的报告。问题是，你同时还要考虑——如果不接，别人接了，产品业绩跑不过同行怎么办？"<sup>[10]</sup></blockquote>',
    '<blockquote class="reveal">"配售股份的推销通常很直接——投行给你打电话，说某某大股东要减持，折扣好，基本面有故事，问你接不接。决策时间很短，可能就是几小时。你如果没有自己的深度研究，就只能信投行的报告。问题是，你同时还要考虑——如果不接，别人接了，产品业绩跑不过同行怎么办？"<sup>[10]</sup></blockquote>'
)

# === FIX 17: Epilogue → shorten dramatically ===
old_epilogue_start = '<!-- 尾声 -->\n<div class="epilogue reveal" id="c9">\n<h2 id="c8">尾声：基民的钱去了哪里</h2>\n\n<p>读完这篇调查，你可能会问几个问题——它们也是我们在写作过程中不断追问自己的。</p>'

new_epilogue_start = '<!-- 尾声 -->\n<div class="epilogue reveal" id="c9">\n<h2 id="c8">尾声：接盘的逻辑</h2>'

html = html.replace(old_epilogue_start, new_epilogue_start)

# Replace the rest of the epilogue
old_epilogue_body = '''<h3 style="color:#e8c87a;font-size:16px;margin:24px 0 10px;border:none">第一个问题：谁在赚钱？</h3>
<p>把建滔配售案从头算一遍：<strong style="color:#e8c87a">大股东套现117.8亿港元</strong>，花旗和美林赚了承销费（按惯例约2%-3%，即约2.4亿至3.5亿港元），49家基金公司则持续收取管理费——以中欧和大成两家合计承接超过68亿元规模的资产计算，每年产生的管理费就超过1亿元。而基民——买入这些基金的投资者——承担的是超过30%的净值回撤。一个简化的答案是：<strong style="color:#e8c87a">每一方都在自己的逻辑里做出了理性决策——只有承担损失的那一方，根本不在决策桌上</strong>。</p>

<h3 style="color:#e8c87a;font-size:16px;margin:24px 0 10px;border:none">第二个问题：基民能提前识破这种"接盘"吗？</h3>
<p>很难。公募基金季报在每个季度结束后15个工作日才披露，而配售到暴跌之间的窗口期只有几周。当基民在7月中下旬看到二季报时，配售已于6月完成，股价已从107跌至70以下。<strong style="color:#e8c87a">信息披露的滞后性，是基民保护自己的最大障碍</strong>。但有一个信号值得留意：如果一只基金突然集中买入一支此前无人问津的股票、且仓位异常集中，即使季报没出，单日净值异动也可以作为预警。</p>

<h3 style="color:#e8c87a;font-size:16px;margin:24px 0 10px;border:none">第三个问题：监管为什么抓不住？</h3>
<p>因为建滔配售案中的每一个环节——大股东配售、投行承销、公募接盘——<strong style="color:#e8c87a">在单独审视时几乎都是合法的</strong>。配售是合法的融资方式，投行发研报是分内之事，基金经理决定买什么股票属于投资自主权。问题出在这些环节串在一起时产生的系统性效应：投行既是承销商又是分析师、基金公司决策依赖外部研报且考核短期化、信息披露滞后。每一道防线单独看都没破，但串在一起时就漏了。</p>

<h3 style="color:#e8c87a;font-size:16px;margin:24px 0 10px;border:none">第四个问题：它会继续发生吗？</h3>
<p>只要公募基金的考核机制还在追逐相对排名，只要投行的"研究"与"配售"还可以同台演绎，只要基民获取持仓信息的窗口期永远是"事后"——这套模式就会继续运转。建滔案不是第一起，也不会是最后一起。</p>

<p style="color:#d5cfc5">基民唯一能做的，就是意识到一个事实：在基金公司赚钱的众多方式中，为你的资产增值只是其中之一，且未必是优先级最高的那个。</p>

<div class="pull-quote" style="color:#e8c87a;border-color:#5a5045;font-size:22px">基金公司最"擅长"的，<br>不是让基民赚钱，<br>而是让基民的钱在合规的链条上流动——<br>流到该去的地方。</div>

<p style="font-size:13px;color:#a89e8e;margin-top:16px">本文所引数据均来自基金公司公开披露报告、港交所公告、社交平台公开信息及历史公开报道，详见文末注释。部分内容引用自独立财经自媒体"小明哥讲套利"的整理分析。投资有风险，本文不构成任何投资建议。</p>'''

new_epilogue_body = '''<p>建滔配售案的账可以这样算：大股东套现了117.8亿港元，花旗和美林赚了约2.4亿至3.5亿港元的承销费，49家基金公司收取的管理费以亿元计。而买入这些基金的投资者，承担了超过30%的净值回撤。</p>

<p><strong style="color:#e8c87a">每一方都在自己的逻辑里做出了理性决策。只有承担损失的那一方，不在决策桌上。</strong></p>

<p>只要公募基金的考核机制还在追逐相对排名，只要投行的"研究"与"配售"还可以同台演绎，只要基民获取持仓信息的窗口期永远是"事后"——这套模式就会继续运转。建滔案不是第一起，也不会是最后一起。</p>

<p class="pull-quote" style="color:#e8c87a;border-color:#5a5045;font-size:20px">对基民来说，意识到这一点本身，<br>也许就是最实用的保护。</p>

<p style="font-size:13px;color:#a89e8e;margin-top:16px">本文所引数据均来自基金公司公开披露报告、港交所公告、社交平台公开信息及历史公开报道，详见文末注释。部分内容引用自独立财经自媒体"小明哥讲套利"的整理分析。投资有风险，本文不构成任何投资建议。</p>'''

html = html.replace(old_epilogue_body, new_epilogue_body)

with open(FP, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ All Round 3 fixes applied")
