# -*- coding: utf-8 -*-
"""聚合：系统层(角度档案.json) + LLM定性层(共享框架/原创性) -> 观点查重报告。"""
import os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VP = os.path.join(BASE, "观点查重")
with open(os.path.join(VP, "角度档案.json"), encoding="utf-8") as f:
    SYS = json.load(f)["results"]

# ---- LLM 定性层（来自 4 个并行子代理的跨篇观点提取）----
QUAL = {
"2026-07-17_宇树科技": {"kao":["73.6%收入来自科研教育而非工业落地","真实工业场景收入<1%","已售机器人无自研'大脑'","90%自研率只覆盖'身体'","研发费率仅8.53%且大模型专利0项","420亿估值71倍PE与'To LP'质疑"],"frame":["'会翻跟头的机器人，翻不过去的那道坎'","'身体很强，脑子很弱'","'To LP'——说服对象是出资人而非终端客户","'窗口会关闭'(供应链成熟后自研优势消解)"],"orig":"原创分析为主：'身体很强脑子很弱''To LP'为作者原创框架；仅'技术壁垒不深'引券商分析师。","second":"中","shared":["账本/账单隐喻","国产替代+地缘双刃","窗口/周期退潮","研发高≠壁垒","客户集中/关联交易"]},
"2026-07-18_建滔集团": {"kao":["AI叙事边界：是否真吃高端AI厚利","M9高端板技术差距与'座上宾'缺席","涨价函=定价权还是周期修复","家族2026顶端套现145亿信号","地产旧伤与铜周期退潮","垂直一体化背后的原材料咽喉"],"frame":["'风向标'vs'座上宾'两分对立","'AI的牌桌'隐喻","'能造覆铜板≠能在AI牌桌坐到散场'"],"orig":"原创分析为主：'AI风向标却非座上宾'为自造金句；数据多引Prismark/券商但立论自创。","second":"中","shared":["牌桌/座次隐喻","叙事vs现实","内部人卖出=信心信号","高股息叙事漏洞"]},
"2026-07-18_长鑫科技": {"kao":["上市时点是否踩在涨价周期顶端","收入来自对手'让出来'的通用市场","330亿利润主驱动是ASP涨价而非份额","HBM代差=有饭碗无入场券","研发33%多为'绕路'而非前沿","十年亏损366亿靠自身无法覆盖折旧","地缘'国产替代标杆也是博弈棋子'"],"frame":["'碎钞机与印钞机'","'周期退潮，才是真的开始'","'通用DDR5是饭碗，HBM是入场券'","'十年亏损由国资承担，周期顶端估值由二级市场承接'"],"orig":"原创分析为主：'吃下三巨头让出的市场而非正面取胜''折旧吞噬利润'系作者自算；事实引招股书/券商。","second":"中","shared":["账本/账单隐喻","周期退潮(最显式)","国产替代+地缘双刃","估值vs收入倒挂","客户/股东即客户","研发高≠壁垒"]},
"2026-07-20_周生生": {"kao":["盈利被金价'单点绑架'","如何与金价'脱钩'","行业集体关店、首饰金被投资金分流","'中高端大众'定位两面夹击","高库存+资本负债率攀升的减值风险"],"frame":["'与金价脱钩/脱钩曲线'","'适应曲线约一个季度'","'卖金子→卖品牌'、'周期股'标签"],"orig":"原创分析为主：'金价涨速才是杀手'由季度同店数据原创归纳；'微笑曲线'数字引中信证券。","second":"中","shared":["摆脱单一盈利依赖/第二曲线","估值溢价vs真实盈利","行业集体困境"]},
"2026-07-20_小红书": {"kao":["种草帝国的信任裂缝：广告76%却建在'真实分享'","交易闭环没跑通：站内转化0.7%-1.2%","收入结构单一，电商第二曲线没接上","估值想象力跑在公司治理前面","破圈赌注能否守调性"],"frame":["'种草的帝国，信任的裂缝'","'广告印钞机'、'临门一脚被绊住'","'估值的想象力跑在上市时间表前面'"],"orig":"混合：'76%广告收入 vs 用户信任被标价'为作者自推；'种草强拔草弱是核心死穴'直接引钛媒体。","second":"中","shared":["帝国隐喻","裂缝/隐藏风险隐喻","第二曲线接不上力","估值溢价vs真实盈利","轻资产不持重"]},
"2026-07-20_深度求索": {"kao":["558万训练成本口径是否含试错/折旧","低成本神话依赖禁令前囤卡窗口","不披露财务致营收与3500亿估值倒挂","开源免费能否自身造血","H20禁令卡住下一程","全球多国封禁的地缘悖论"],"frame":["'开源给世界，账本留给自己'","'558万与6000亿之间隔的是一份没人见过的财报'","'技术彻底打开，财务彻底关上'"],"orig":"原创分析为主：'账本留给自己'对立框架为自创立论；558万/封禁时间线引SemiAnalysis等。","second":"中","shared":["账本/账单隐喻(最显式)","国产替代+地缘","窗口红利终将关闭","估值vs收入倒挂","客户/资本集中"]},
"2026-07-20_燧原科技": {"kao":["营收11倍增长是否靠单一大客户","腾讯既大股东又第一大客户(83.79%)","研发4倍于营收的烧钱可持续","不兼容CUDA自建生态的窄路代价","1.4%市场份额的现实","实控人28%表决权不足30%"],"frame":["'越写越大的腾讯账单'","'腾讯既是钱袋子又是米袋子'","'起个大早赶个晚集'","'没有腾讯也能活吗'"],"orig":"原创分析为主：'钱袋子米袋子'框架自创；收入/份额引招股书/IDC。","second":"中","shared":["腾讯账单隐喻","大客户/股东即客户(最聚焦)","国产GPU+兼容巨头","巨亏+经营现金为负","估值/融资节奏"]},
"2026-07-20_赛力斯": {"kao":["对华为致命依赖与自身造血(750亿采购≈4年净利4倍)","华为'含华量'被五界分流","每辆车21.4%价值流向华为","靠买商标/入股引望'赎回灵魂'","2026H1卖更多却预亏15-18亿","AIVA/出海能否开第二曲线"],"frame":["'灵魂交给华为'","'赎回灵魂的三笔钱'","'华为是赛力斯唯一答案→所有车企共享考题'"],"orig":"原创分析为主：'每车21.4%流向华为'为作者推算，非研报原话；仅上汽灵魂论为引用。","second":"低","shared":["对单一外部要素过度依赖","拟人化物件隐喻定调(灵魂)","尾声金句版式"]},
"2026-07-21_宝马": {"kao":["制动系统召回扯动全球利润预警","中国最大市场被本土品牌蚕食","电动化千亿欧元赌注见效晚","软件是阿喀琉斯之踵","地缘'中欧美'三重依赖"],"frame":["'踩不稳的电门'","'驾驶乐趣越来越是软件问题'","'阿喀琉斯之踵'、'千亿欧元赌注'"],"orig":"原创分析为主：'驾驶乐趣取决于算力算法OTA'为作者论断；齐普策批评关税引路透原话。","second":"低","shared":["对单一旧优势依赖难转移","本土品牌蚕食","重资产对照"]},
"2026-07-21_智谱": {"kao":["7亿营收多少是'国家队'订单/股东即客户","云端毛利-0.4%贴钱换规模","开源权重公开后定价权何在","研发439%且七成买卡而非招人","73倍市销率买什么","-81亿股东权益资不抵债"],"frame":["'学霸造出对标OpenAI模型，却没学会写赚钱的财报'","'四条曲线，三个向上一个向下'","'权重公开了，定价权还在自己手里吗'"],"orig":"原创分析为主：'三上一下'可视化立论自创；'高质量token稀缺'引张鹏业绩会(媒体转述)。","second":"中","shared":["写赚钱的财报(账本)隐喻","国产+国资vs商业化软肋","估值泡沫/市销率畸高","研发高≠壁垒","客户=股东依赖"]},
"2026-07-22_五粮液": {"kao":["营收腰斩最痛是'老二'结构性断裂","茅台没倒为何五粮液倒","消失的486亿:大商制渠道脆弱","夹在茅台与国窖间定价困境","82%反弹=低基数非复苏","6.9%高股息率逻辑漏洞","百亿回购缓慢的信心信号"],"frame":["'半瓶酒的回响'","'千亿门槛前折返半程'","'价格倒挂'镜像框架"],"orig":"混合偏转述汇编：大段转述雪球社区('真正丢掉的不是股价而是信任'直接引用)；'高股息率被当消费+高息混合定价'为自析。","second":"中","shared":["叙事vs现实","内部人动作=信心信号","高股息叙事漏洞","价格倒挂"]},
"2026-07-22_希尔顿": {"kao":["轻资产'卖钥匙':99.4%不持资产","收入靠多层'抽水'边际成本近零","2.11亿会员积分breakage隐秘利润","增长依赖扩建管道，高利率下搁置率升","中国本土巨头加盟费更低渗透更深"],"frame":["'卖钥匙的酒店帝国'、'钥匙印刷机'","'钥匙越多越多人想要钥匙'","'轻资产'核心frame"],"orig":"原创分析为主：'毛利率近100%不盖楼不雇门童'为原创立论；黑石收购史引公开披露。","second":"中","shared":["帝国隐喻","轻资产不持重","估值/利润率vs增长可持续","本土品牌竞争"]},
"2026-07-22_平安证券": {"kao":["前十大券商唯一'没有股票代码'","吞下方正后跻身前十但无王牌业务","平安生态养分vs利益冲突致研究独立性存疑","投行/经纪缺大型IPO能力","注册制下头部效应强化","险企主导券商并购终局"],"frame":["'平安的棋子，与它自己的路'","'王牌还是过了河的卒'","'没有代码的券商=看不见的风险暴露'"],"orig":"原创+部分转述汇编：棋子/无代码为原创；方正沿革为资料汇编式转述；标注'试读版·未经分析师审阅'。","second":"中","shared":["研究/决策独立性缺失","拟人化物件隐喻(棋子)","尾声金句版式"]},
"2026-07-23_基金灰色操作": {"kao":["49家公募净买入1.77亿股≈大股东配售1.55亿股'接盘'巧合","花旗同时做承销+发乐观研报的利益冲突","建滔崩盘后基民承担数十亿亏损","'接盘'灰色模式史","双十限制为何锁不住仓位","制度四裂缝"],"frame":["'大股东减持→投行承销→公募接盘→基民亏损'四环链条","'老鼠仓是一个人偷钱，接盘是一群人分钱'"],"orig":"混合且转述色彩最重：核心持仓数据引自媒体'小明哥讲套利'，密集'据XX称/不愿具名基金经理表示'——正是'编写只来源于别人说的观点'。","second":"高","shared":["基民/持有人亏机构赚(与融通同题)","研究独立性缺失(花旗双重角色)","章节骨架被融通sidenav复制"]},
"2026-07-23_融通基金": {"kao":["'老十三'24年规模仍1556亿排名51","收管理费21.93亿持有人却亏49.55亿'剪刀差'","走马灯式高管更迭","明星总监6产品季亏3.18亿","固收'偏科'但债券仍跑输","'央企拼图'能否延伸到公募"],"frame":["'二次创业'","'二手船票却仍在旧航道上颠簸'","'管理费vs持有人亏损'剪刀差"],"orig":"原创分析为主：'剪刀差'立论自创；但左侧导航目录是建滔文('基民的钱'等)原样残留，正文未写接盘——模板级复制需修正。","second":"低","shared":["基民亏机构赚(与基金灰色同题)","对单一要素过度依赖(固收/明星)","拟人化隐喻(二手船票)"]},
"2026-07-24_中国福彩": {"kao":["两千亿公益巨兽规模增速触顶","体彩逆袭双轨制不对等","资金'三块蛋糕'分配","169亿审计违规玻璃口袋裂痕","14%发行费15年未降","互联网彩票一刀切兴衰","即开型逆势增长与天花板"],"frame":["'公益机器'","'玻璃口袋'裂痕隐喻","'双寡头垄断'","'一张彩票的初心不应被2000亿流水稀释'"],"orig":"原创分析为主：数据来自财政部/审计署公告，作者自行解读，转述第三方观点最少。","second":"低","shared":["规模膨胀带来体制漏洞(对照建滔/空客)"]},
"2026-07-24_大宗商品铜": {"kao":["铜价破万三:真实需求还是资本叙事","加工费归零的利润大挪移","冶炼厂靠硫酸续命","AI铜胃口<2%故事还是现实","供给'死局'与10年资本开支欠账","中国'双重命门'地缘风险","'超级周期'vs'结构性牛市'"],"frame":["'冲天铜价与归零加工费的悖论'","'同一个金属，两个世界'","'大宗新王'(红色石油)","'身份转变:工业金属→战略资源'"],"orig":"转述汇编为主：高盛/标普/华泰/摩根大通等研报结论密集串联，独立原创判断较少。","second":"高","shared":["叙事vs现实/故事or现实","AI需求被夸大(与建滔/五粮液)","冰火两重天/两个世界","X因素/隐性缓冲"]},
"2026-07-24_景顺长城基金": {"kao":["千亿经理刘彦春5年缩水77%","元老余广注销资格'决绝谢幕'","主动权益管理费三连降的降费阵痛","'以量补价'靠低费率指数/固收撑","QDII高溢价双刃","合资基因Invesco赋能与背景风险","平台化转型能否替代明星"],"frame":["'告别刘彦春，一个明星基金时代的尾声'","'长期投资'与'死扛'的边界","'精品店vs超市vs平台型'三路径对照"],"orig":"原创分析为主：'超市模式'转型自创类比；'长期投资和死扛边界非口号可划'为原创立论。","second":"低","shared":["对单一要素过度依赖(明星经理)","拟人化隐喻(明星)","尾声金句版式"]},
"2026-07-24_深圳航空": {"kao":["年运4千万人却亏12.44亿","国航51%控股下'独立王国'","深圳基地被南航+国航双重挤压","全服务配置却没赚到全服务的钱","国航的深航难题——卖留整合"],"frame":["'国航翅膀下的深圳难题'","'冰山一角'、'利润死胡同'","'全服务的配置，低成本的收益'"],"orig":"原创分析为主：'全服务配置低成本收益卡在最不舒服位置'为独立判断；财务数据引国航年报/民航局公报。","second":"中","shared":["隐藏风险物理隐喻(冰山/死胡同)","对单一模式脆弱依赖","行业/集团集体困境","本土同业挤压"]},
"2026-07-24_空客": {"kao":["8754架积压订单的'幸福与烦恼'","普惠GTF发动机卡住产能","Spirit收购垂直整合代价","波音反扑重写双寡头","中国赌局:C919与55%份额防御","防务'断臂求生'","氢能ZEROe梦想与现实","创纪录利润下现金失血"],"frame":["'八千架飞机的赌注'","'甜蜜的痛苦'(订单多≠能交付)","'敌人不是对手，是自己的供应链'","'太擅长接订单了'"],"orig":"混合偏原创：'发动机锁住产业链咽喉''太擅长接订单'为原创金句；数据引年报/Reuters/摩根士丹利。","second":"中","shared":["牌桌/座次隐喻","叙事vs现实","内部人/客户预付款信号","规模即枷锁"]},
}

SHARED = [
    {"name":"账本/账单隐喻（财务真相 vs 叙事）","arts":["长鑫科技","深度求索","智谱","燧原科技","宇树科技"],"note":"多篇用'账本/账单'作核心立论：长鑫'账本与代差'、DeepSeek'账本留给自己'、燧原'腾讯账单'、智谱'写赚钱的财报'、宇树'819页里最轻的一页'。"},
    {"name":"周期/窗口退潮","arts":["长鑫科技","宇树科技","深度求索"],"note":"长鑫最显式'周期退潮，才是真的开始'；宇树'窗口会关闭'、DeepSeek'窗口红利终将关闭'同源。"},
    {"name":"国产替代 + 地缘博弈 双刃","arts":["长鑫科技","深度求索","智谱","燧原科技","宇树科技"],"note":"硬科技五篇共用：一面'自主可控标杆'，一面'地缘棋子'。这是你举的'国产替代的标杆，也是地缘博弈的棋子'所属框架。"},
    {"name":"估值 vs 收入/利润 倒挂","arts":["长鑫科技","深度求索","智谱","燧原科技","宇树科技"],"note":"五篇共有：估值高企与当期收入/利润/巨亏之间的倒挂拷问。"},
    {"name":"客户/股东即客户 依赖质疑","arts":["燧原科技","智谱","长鑫科技","宇树科技"],"note":"燧原(腾讯83.79%)最聚焦；智谱(股东即客户)、长鑫(境外收入反差)、宇树(科研教育73.6%)是同一拷问的不同面孔。"},
    {"name":"研发高投入 ≠ 壁垒深","arts":["长鑫科技","深度求索","智谱","燧原科技","宇树科技"],"note":"五篇共有：拆解'研发费率高'不等于'技术壁垒深'（长鑫绕路、宇树专利空心化、智谱买卡）。"},
    {"name":"帝国 / 裂缝 / 冰山 隐喻","arts":["小红书","希尔顿","深圳航空"],"note":"小红书'种草的帝国，信任的裂缝'、希尔顿'卖钥匙的酒店帝国'、深航'冰山一角/利润死胡同'——文字不同、框架同一。"},
    {"name":"叙事 vs 现实（故事 or 现实）","arts":["建滔集团","大宗商品铜","五粮液","空客"],"note":"建滔(AI叙事边界)、铜(AI铜胃口<2%)、五粮液(82%反弹=低基数)、空客(8754架订单≠能交付)共用'故事/叙事 vs 现实兑现'底层拷问。"},
    {"name":"拟人化物件/身份隐喻定调","arts":["赛力斯","平安证券","融通基金","景顺长城基金"],"note":"赛力斯'灵魂'、平安'棋子'、融通'二手船票'、景顺'明星'——以一件物/身份隐喻作标题与立论骨架。"},
    {"name":"基民/持有人亏，机构照赚","arts":["基金灰色操作","融通基金"],"note":"直接同题：基金灰色(基民承担建滔亏损)+融通(22亿管理费vs50亿亏损剪刀差)；且融通sidenav残留建滔'基民的钱'目录。"},
    {"name":"对单一外部要素过度依赖","arts":["赛力斯","景顺长城基金","融通基金"],"note":"赛力斯→华为、景顺→明星经理、融通→固收/个别明星，同构。"},
    {"name":"第二曲线 / 脱钩","arts":["小红书","周生生","宝马","深圳航空"],"note":"小红书电商没接上力、周生生与金价解绑、宝马软件接不上、深航国际长航线接不上——'依附单一引擎→能否长出第二曲线'同构。"},
]

FLAGS = [
    {"a":"基金灰色操作","issue":"最依赖他人观点——核心持仓数据引自媒体'小明哥讲套利'，密集'据XX称/不愿具名基金经理表示'，属'编写只是来源于别人说的观点'。建议补强一手信源、弱化'自媒体说→作者定论'链条。"},
    {"a":"大宗商品铜","issue":"转述汇编为主——高盛/标普/华泰/摩根大通等研报结论密集串联，独立原创判断较少。建议增加作者独立论证。"},
    {"a":"五粮液","issue":"偏汇编——大段转述雪球社区用户观点（'真正丢掉的不是股价而是信任'等直接引用），约40%为转述。"},
    {"a":"融通基金","issue":"左侧导航目录为建滔文（'数字里的巧合/花旗的角色/灰色接盘的历史/基民的钱'）原样残留，但正文未写'接盘'——模板级复制，需修正目录。"},
    {"a":"平安证券","issue":"方正证券沿革为资料汇编式转述；全文标注'试读版·未经分析师审阅'，独立性结论需谨慎。"},
]

# 二手评估 -> 颜色
SEC_COLOR = {"高":"#c0392b","中":"#e67e22","低":"#27ae60"}

def build_md():
    L = []
    L.append("# 观点层级查重报告（第四层）\n")
    L.append("> 本层不比'字'也不比'句'，而是比**观点/论证结构**：① 各篇拷问了哪些分析角度；② 哪些文章'都拷问了这些点'（共享框架）；③ 论点是引用别人说的，还是作者自己分析出来的。\n")
    L.append("> 方法 = 系统层（21角度 taxonomy + 跨篇角度重合 + 二手观点密度，确定性算法，见 `角度档案.json`）+ LLM定性层（4个并行代理跨篇提取共享框架与原创性）。系统层密度偏保守（仅抓显式'据/称'标记），定性层为更准的原创性信号。\n")
    L.append("\n## 一、跨篇共享框架（他们都拷问了这些点）\n")
    for s in SHARED:
        L.append(f"### {s['name']}\n- 涉及：{'、'.join(s['arts'])}\n- {s['note']}\n")
    L.append("\n## 二、需重点核查（原创性 / 模板残留）\n")
    for fl in FLAGS:
        L.append(f"- **{fl['a']}**：{fl['issue']}\n")
    L.append("\n## 三、各篇角度档案 + 原创性\n")
    for f in sorted(QUAL):
        q = QUAL[f]
        sysr = SYS.get(f, {})
        ang = "、".join(f"{k}({v})" for k, v in sorted(sysr.get('angles', {}).items(), key=lambda x:-x[1]))
        L.append(f"### {f}\n- 系统层角度数：{sysr.get('angle_count','-')}；算法二手密度：{sysr.get('second_hand_ratio',0):.1%}；定性二手评估：**{q['second']}**\n- 角度：{ang}\n- 拷问点：{'；'.join(q['kao'])}\n- 叙事框架：{'；'.join(q['frame'])}\n- 原创性：{q['orig']}\n- 共享框架：{'、'.join(q['shared'])}\n")
    L.append("\n## 四、系统层：跨篇角度重合（Top 15 对）\n")
    L.append("（确定性算法输出，Jaccard + 共享角度数；详见 `角度档案.json`）\n")
    L.append("\n*— 报告由 `scripts/check_viewpoints.py`（系统层）+ LLM定性提取（定性层）聚合生成。—*")
    with open(os.path.join(VP, "汇总.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("[ok] 汇总.md")

def build_html():
    data = {"sys": SYS, "qual": QUAL, "shared": SHARED, "flags": FLAGS, "secColor": SEC_COLOR}
    DATA = json.dumps(data, ensure_ascii=False)
    html = TEMPLATE.replace("/*__DATA__*/", DATA)
    with open(os.path.join(BASE, "观点查重报告", "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("[ok] 观点查重报告/index.html")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>观点层级查重报告</title>
<style>
:root{--red:#c0392b;--ink:#1a1a1a;--mut:#777;--line:#e6e6e6;--bg:#fafafa;--acc:#2c3e50;--hl:#fff3cd}
*{box-sizing:border-box}
body{margin:0;font:15px/1.7 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg)}
header{background:var(--acc);color:#fff;padding:18px 24px}
header h1{margin:0;font-size:20px;letter-spacing:1px}
header p{margin:6px 0 0;font-size:13px;opacity:.85}
.wrap{display:flex;height:calc(100vh - 70px)}
.col1{width:268px;border-right:1px solid var(--line);overflow:auto;background:#fff}
.col2{flex:1;overflow:auto;padding:22px 26px}
.col3{width:340px;border-left:1px solid var(--line);overflow:auto;background:#fff;padding:16px}
.art{padding:11px 16px;border-bottom:1px solid var(--line);cursor:pointer}
.art:hover{background:var(--bg)}
.art.on{background:#eef3f8;border-left:3px solid var(--acc)}
.art .nm{font-weight:600;font-size:14px}
.art .meta{font-size:11px;color:var(--mut);margin-top:3px;display:flex;gap:8px;align-items:center}
.badge{font-size:10px;padding:1px 6px;border-radius:10px;color:#fff}
.bar{height:4px;background:#eee;border-radius:2px;margin-top:4px;overflow:hidden}
.bar>i{display:block;height:100%}
h2.t{font-size:17px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px;margin-bottom:14px}
.sec{margin:18px 0 8px;font-size:13px;font-weight:700;color:var(--acc);border-left:3px solid var(--acc);padding-left:8px}
.chip{display:inline-block;background:#eef3f8;color:#2c3e50;border:1px solid #d6e2ee;font-size:12px;padding:2px 9px;border-radius:12px;margin:3px 4px 0 0}
.k{font-size:13.5px;margin:5px 0 0;padding-left:14px;position:relative}
.k:before{content:"•";position:absolute;left:2px;color:var(--acc)}
.frame{background:var(--hl);border-left:3px solid #e0a800;padding:6px 10px;margin:5px 0;font-size:13px;border-radius:0 4px 4px 0}
.orig{font-size:13px;background:#f4f8f4;border-left:3px solid #27ae60;padding:7px 10px;border-radius:0 4px 4px 0}
.sh{margin:10px 0;padding:10px 12px;border:1px solid var(--line);border-radius:6px}
.sh .sn{font-weight:700;font-size:13.5px;color:var(--red)}
.sh .sa{font-size:12px;color:var(--mut);margin:3px 0}
.sh .sd{font-size:12.5px}
.flag{background:#fdecea;border-left:3px solid var(--red);padding:8px 11px;margin:8px 0;font-size:12.5px;border-radius:0 4px 4px 0}
.search{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:6px;font-size:13px;margin:10px 0}
.legend{font-size:11px;color:var(--mut);padding:0 16px 10px}
</style></head>
<body>
<header><h1>观点层级查重报告 <a href="../查重报告/index.html" style="color:#ffe;font-size:13px;text-decoration:underline;margin-left:10px" target="_blank">← 文字层查重</a></h1><p>不比字、不比句——比「观点/论证结构」：各篇拷问了哪些角度 · 哪些文章「都拷问了这些点」· 论点是引用别人还是自己分析</p></header>
<div class="wrap">
<div class="col1"><input class="search" id="q" placeholder="搜索文章…"><div id="list"></div>
<div class="legend">徽标：角=角度数 · 二手=定性二手观点评估（高红/中橙/低绿）</div></div>
<div class="col2" id="detail"><p style="color:#777">← 从左侧选择一篇文章查看其观点档案</p></div>
<div class="col3">
<div class="sec" style="margin-top:0">跨篇共享框架（他们都拷问了这些点）</div>
<div id="shared"></div>
<div class="sec">需重点核查</div>
<div id="flags"></div>
</div>
</div>
<script>
const DATA = /*__DATA__*/;
const $=(s)=>document.querySelector(s);
const arts=Object.keys(DATA.qual);
function secColor(v){return DATA.secColor[v]||'#999';}
function renderList(){
  const q=$('#q').value.trim();
  const box=$('#list');box.innerHTML='';
  arts.filter(a=>!q||a.includes(q)).forEach(a=>{
    const qd=DATA.qual[a], sr=DATA.sys[a]||{};
    const d=document.createElement('div');d.className='art';d.dataset.a=a;
    const sec=sr.second_hand_ratio? (sr.second_hand_ratio*100).toFixed(0)+'%':'-';
    d.innerHTML=`<div class="nm">${a.replace(/^\d+-\d+-\d+_/,'')}</div>
      <div class="meta"><span class="badge" style="background:#2c3e50">角 ${sr.angle_count||'-'}</span>
      <span class="badge" style="background:${secColor(qd.second)}">二手 ${qd.second}</span></div>
      <div class="bar"><i style="width:${sec}%;background:${secColor(qd.second)}"></i></div>`;
    d.onclick=()=>{document.querySelectorAll('.art').forEach(x=>x.classList.remove('on'));d.classList.add('on');renderDetail(a);};
    box.appendChild(d);
  });
}
function renderDetail(a){
  const qd=DATA.qual[a], sr=DATA.sys[a]||{};
  const ang=Object.entries(sr.angles||{}).sort((x,y)=>y[1]-x[1]).map(([k,v])=>`${k}(${v})`).join('、');
  let h=`<h2 class="t">${a}</h2><div class="sub">系统层角度数 ${sr.angle_count||'-'} · 算法二手密度 ${(sr.second_hand_ratio*100||0).toFixed(1)}% · 定性二手评估 <b style="color:${secColor(qd.second)}">${qd.second}</b></div>`;
  h+=`<div class="sec">角度档案（拷问了哪些点）</div>`;
  h+=`<div>${Object.keys(sr.angles||{}).map(k=>`<span class="chip">${k}</span>`).join('')||'—'}</div>`;
  h+=`<div class="sec">拷问点</div>`+qd.kao.map(k=>`<div class="k">${k}</div>`).join('');
  h+=`<div class="sec">叙事框架 / 比喻</div>`+qd.frame.map(f=>`<div class="frame">${f}</div>`).join('');
  h+=`<div class="sec">原创性判断</div><div class="orig">${qd.orig}</div>`;
  h+=`<div class="sec">与其他篇共享的框架</div>`+qd.shared.map(s=>`<span class="chip">${s}</span>`).join('');
  $('#detail').innerHTML=h;
  $('#detail').scrollTop=0;
}
function renderShared(){
  $('#shared').innerHTML=DATA.shared.map(s=>`<div class="sh"><div class="sn">${s.name}</div><div class="sa">涉及：${s.arts.join('、')}</div><div class="sd">${s.note}</div></div>`).join('');
  $('#flags').innerHTML=DATA.flags.map(f=>`<div class="flag"><b>${f.a}</b><br>${f.issue}</div>`).join('');
}
$('#q').addEventListener('input',renderList);
renderList();renderShared();
if(arts[0]){document.querySelector('.art').classList.add('on');renderDetail(arts[0]);}
</script>
</body></html>"""

if __name__ == "__main__":
    os.makedirs(os.path.join(BASE, "观点查重报告"), exist_ok=True)
    build_md()
    build_html()
    print("done.")
