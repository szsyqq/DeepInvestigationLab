# Skills 与工作流 · 整改报告

> 作者：调查团队（自检）
> 日期：2026-07-21
> 状态：待审

---

## 摘要

当前 `~/.workbuddy/skills/` 下共 14 个技能（总计约 4800 行），项目根目录另有 1 份工作流文件（231 行）。经逐文件审计，发现三类结构性问题：**技能与方法论混同**、**项目自动化伪装成技能**、**职责重叠**。本报告详列病灶、分析根因、评估改造风险，并提出整改方案。

---

## 一、现状扫描

### 1.1 文件清单与规模

| 文件 | 行数 | 位置 | 性质判断 |
|------|------|------|---------|
| `llm-wiki-skill/SKILL.md` | 909 | `~/.workbuddy/skills/` | 方法论+项目细节混杂 |
| `gx/SKILL.md` | 528 | `~/.workbuddy/skills/` | **🟡 项目自动化** |
| `web-access/SKILL.md` | 268 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `sl/SKILL.md` | 268 | `~/.workbuddy/skills/` | **🟡 项目自动化** |
| `调查报道工作流-v2.md` | 446 | `#深度调查档案室/` 项目根目录 | **🟡 与 skill 80% 重复** |
| `wsj-investigative-report/SKILL.md` | 185 | `~/.workbuddy/skills/` | **🟡 方法论+项目细节混杂** |
| `minimax-pdf/SKILL.md` | 189 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `jc/SKILL.md` | 218 | `~/.workbuddy/skills/` | **🟡 项目自动化** |
| `second-brain-thinking/SKILL.md` | 137 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `agent-browser-core/SKILL.md` | 67 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `wecom-unified/SKILL.md` | 220 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `obsidian/SKILL.md` | 62 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `browser-use/SKILL.md` | 247 | `~/.workbuddy/skills/` | ✅ 方法论（纯） |
| `link-inbox/SKILL.md` | 72 | `~/.workbuddy/skills/` | **🔴 完全被 sl 覆盖** |
| `pdfkit-py/SKILL.md` | 1105 | `~/.workbuddy/skills/` | ⚠️ 超标（含过多参考内容） |

^（注：pdfkit-py 行数虽然大但属于文档性参考，性质可接受。llm-wiki 有完整子目录含 scripts/docs/CHANGELOG。）

### 1.2 明确问题清单

#### 🔴 问题 A：wsj-investigative-report 与 调查报道工作流 高度重复

逐节对比两份文件，相同或近乎相同的内容占比约 80%：

| 章节 | 技能(SKILL.md) | 工作流(workflow.md) | 关系 |
|------|---------------|-------------------|------|
| 版本历史（v2/v3/v4/v5） | 有（作为备注） | 有（v4 主要、v5 追加） | 🟡 各写各的，不同步 |
| 三大表述纪律 | §12-15 | §1 | 🟡 规则相同、措辞不同 |
| 8 步生产流程 | §37-45 | §2 (9 步) | 🟡 结构相同、步骤数不同 |
| 网页技术规格 | §47-59 | §3 | ✅ 基本一致 |
| 易错点 | §62-77 | §4 | 🟡 同一批教训各写一遍 |
| 写作风格准则 | §79-86 | §5 | ✅ 一致 |
| 推荐结构骨架 | §88-95 | §5.5 | ✅ 一致 |
| v3 新增（6.1–6.12 迭代准则） | §97-169 | §6 | ✅ 完全一致 |
| 交付物 | §180-185 | §7 | 🟡 规则同、措辞不同 |
| 版本归档 | 无单独节 | §8 | 🔴 skill 遗漏此重要节 |

**后果**：修一个文件时必须同步改另一个，否则两处不一致。迭代准则（6.1–6.12）每次从工作流复制到 skill——来源不明、版本历史混乱。

**根因**：当初把工作流的内容"拷贝一份到 skill 作为方法论"时，没有做抽象提取，只做了全文粘贴。

#### 🔴 问题 B：gx/jc/sl 三个 skill 实质是"小红书收藏"项目的自动化操作

这三个文件是 `#LittleRedBook` 工作空间的斜杠命令处理程序。审计发现：

**gx/SKILL.md (528行) 中的项目特定内容：**
- 硬编码路径（第 14 行）：`/Users/panyp/文稿-本地-不参与同步/# WorkBuddy/#LittleRedBook/小红书收藏/`
- 固定沙箱 ID（第 461 行）：`1ee078db29c64e80b32de54eb5a6e44f`
- 完整 Python 严重度判定逻辑（第 79–98 行）——这明显属于 `bundle_wiki.py` 的实现细节
- 完整的 markdown 模板（第 328–398 行）——属于脚本输出模板
- 完整的 bash 命令（第 455–461 行）
- 完整的总结报告模板（第 470–506 行）

**jc/SKILL.md (218行) 中的项目特定内容：**
- 同样硬编码路径和沙箱 ID
- 完整的 JSON 报告处理步骤（第 67–79 行）
- 完整的更新记录 markdown 模板（第 111–179 行）
- 修复后完整 bash 构建命令（第 92–98 行）

**sl/SKILL.md (268行) 中的项目特定内容：**
- 硬编码路径（第 16 行）
- 完整的 Python 代码片段（OCR 提取、文件名清理——第 128–138 行）
- 完整的小鹅通抓取步骤（第 184–245 行）
- 完整的 bash 命令

**后果**：
1. 文件臃肿：528+218+268 = 1014 行，纯属项目自动化
2. 不可复用：换一个知识库项目，这三个 skill 完全不能用
3. 维护困难：修改小鹅通抓取逻辑，需要改 sl/SKILL.md 里面的大段落

#### 🔴 问题 C：link-inbox 与 sl 职责完全重叠

两个 skill 的 description 几乎一样：
- **link-inbox**: "接收用户的文章链接，自动判断来源并按来源归入本地 inbox 知识库"
- **sl**: "当用户在 #LittleRedBook 空间使用 /sl 命令归档链接或本地文件时使用此 skill（保存链接、快速收藏 URL 到小红书知识库）"

sl 是 link-inbox 的**真超集**——sl 包含了 link-inbox 的所有功能（URL 归档、分类、去重），额外增加了 PDF 文件处理、小鹅通圈子抓取、Word 文档处理。link-inbox 已经事实上被废弃（72 行，从未更新过），保留它只会制造"用 link-inbox 还是 sl？"的困惑。

#### 🟡 问题 D：llm-wiki-skill 内容边界模糊

909 行的 SKILL.md 存在以下越界：
- 包含了 `init` / `ingest` / `query` / `lint` / `graph` / `save` 六条命令的**全部操作细节**（含 Python 命令、完整 bash 语句）
- 包含了 `CHANGELOG.md` 子文件——版本历史不该出现在 skill 目录
- 包含了 `docs/` 子目录（设计文档、brainstorm、需求分析）——这些是开发文档，不是 skill 的一部分
- 包含了 `platforms/` 目录（Claude/Cursor/Codex 平台配置）——多平台支持是架构问题，不是方法论

但优点是：llm-wiki-skill 有完整的 `scripts/` 目录，将脚本从方法论中分离——这正是值得推广的做法。

#### 🟡 问题 E：frontmatter description 描述方式不统一

对比两个 description：

**gx (好)**: "当用户在 #LittleRedBook 空间使用 /gx 命令时使用此 skill。触发场景：用户说「/gx」、「更新」、要求处理 inbox 中待处理的素材并移动到已处理目录。自动扫描 raw/inbox/ 下的所有未处理文件，逐个通过 llm-wiki 消化（ingest），完成后移动到 raw/processed/ 对应子目录。"

**link-inbox (差)**: "接收用户的文章链接，自动判断来源并按来源归入本地 inbox 知识库（小红书→inbox/小红书 即 #LittleRedBook 空间），AI 按主题自动分类打标签并保存为 Markdown。当用户说"保存链接/收藏文章/把这些链接收进 inbox/存到小红书空间/归档文章"时使用。"

问题：有些 description 完全描述项目细节（路径、子目录名），有些只描述触发条件。缺少统一的 frontmatter 书写规范。

---

## 二、根因分析

### 2.1 为什么会出现这种状况？

**原因 1：工具机制诱导——Skill 是"唯一的结构化知识载体"**
WorkBuddy 的技能系统设计让用户倾向于把所有操作知识都塞进 SKILL.md。当需要一个"处理 inbox 的工作流"时，最直接的做法就是写一个 skill，即使它只适用于一个项目。系统未提供"项目级工作流"的显式概念，导致了这种渗透。

**原因 2：增量积累，无人梳理**
从最早的 `link-inbox`（简单链接保存）到 `sl`（加 PDF/OFFICE 支持）到 `gx`（完整消化流程），功能随着需求一步一步叠加。每次"升级"都在旧 skill 上改或建新 skill，从未停下来清理。这和代码库的技术债一模一样。

**原因 3：拷贝粘贴 ≠ 抽象**
`wsj` 技能和工作流的关系证明了 "把项目流程拷贝到技能目录里" 不等于 "抽象出了可复用的方法论"。复制 80% 的内容只保留了项目细节，没有提炼出项目无关的原则。

### 2.2 现有文件做对了什么

客观说，也有很多做得好的地方值得保留：

- **sl 有外部 scripts/ 目录**（`pdf_ocr_extract.py`）——实现了代码与流程的分离
- **llm-wiki-skill 的 scripts/** 目录结构完善——比 gx/jc 的"全文内嵌"方式成熟
- **second-brain-thinking 保持纯抽象**——完全没有项目细节，真正的可复用方法论
- **web-access 和 wecom-unified**——有 clean 的前置检查、版本号、决策规则
- **调查报道工作流**虽然有重复，但内容组织清晰（按 v1→v5 版本历史标记，易回溯）

---

## 三、方案风险评估

### 3.1 方案：三层架构（技能 ⇢ 工作流 ⇢ 脚本）

重复提议的关键结构：

```
~/.workbuddy/skills/           ← 层1: 可复用方法论（不绑定项目）
项目根目录/workflow.md          ← 层2: 项目特有流程（引用技能名+脚本名）
项目根目录/scripts/             ← 层3: 可执行脚本（实现细节）
```

### 3.2 风险清单

| # | 风险 | 严重度 | 可能性 | 缓解措施 |
|---|------|--------|--------|---------|
| R1 | **斜杠命令失效**：`/gx`/`/jc`/`/sl` 是靠 skill 名路由的。把 gx/jc/sl 拆成"瘦 skill + 工作流文件"后，skill 文件变薄了但依然存在，路由不中断 | 低 | 低 | 保留 skill 作为薄壳，仅做 dispatch + 引用工作流 |
| R2 | **工作流文件无法自动加载**：skill 是 WorkBuddy 自动加载的，但工作流文件需要手动读。AI 可能忘记读工作流就开干 | 中 | 中 | 在 skill 的第一条指令就是"打开工作流文件"。把工作流文件名写进 skill 的硬约束。这个模式已有先例（sl 引用 llm-wiki skill） |
| R3 | **碎片化——三份文件找起来更麻烦**：一个流程要读三份文件才能理解全貌 | 低 | 高 | 设定原则：skill 文件本身应是**可独立理解的概要**（读 skill 就知道做什么），工作流是"在本项目的具体做法"，脚本是"详细实现"。三份文件各自有一个明确的阅读目的 |
| R4 | **过度抽象**：为了避免"过拟合"，把方法论写得过于抽象泛化，反而难以使用 | 中 | 中 | 保留 skill 的**核心方法+决策规则+示例**，不做完全的"零上下文"抽象。例如 wsj 方法论可以保留宇树作为示例，但不能让整套流程依赖于宇树的特殊约定 |
| R5 | **version history 没有归属**：现在版本历史同时在 skill 和工作流里写。拆开后放哪？ | 低 | 低 | 工作流文件记录"项目操作流程的版本历史"，skill 不记版本（已稳定）。如果有方法论升级，新建 skill 或更新现有 skill |
| R6 | **脚本目录被遗忘使用**：AI 可能继续在 workflow 文件里内嵌 bash 命令，不去建 scripts/ | 中 | 高 | 在书写准则中设硬性边界：**工作流文件里的 bash 命令不能超过 3 行**。多于 3 行的必须写成 scripts/ 下的独立文件 |

### 3.3 关键风险：R2 细化

R2 是最值得担忧的——"AI 忘记读工作流文件"。分析两种场景：

**场景 A：AI 已加载 skill 后接到命令**
- 技能加载后，AI 首先按 skill 指令行动。如果 skill 第一条就是"读取项目工作流文件"，则自动跳转，无遗忘风险。

**场景 B：用户直接给命令（"处理 inbox"）没有触发 skill？**
- 触发词匹配后 skill 被加载，同上。

**结论**：R2 的风险等级可降为"低"，条件是**技能 frontmatter 把"必须先读的工作流文件"作为触发条件的一部分写进 description**。AI 在加载 skill 后执行的第一步就是读工作流。

---

## 四、行业参考

### 4.1 同类工具的做法

| 工具/方法 | 分层方式 | 与我们的可比性 |
|----------|---------|--------------|
| **Cursor (.cursorrules)** | 全局规则（~/.cursorrules）+ 项目规则（.cursorrules）。全局层限行为价值观，项目层限具体操作。 | 高——同样区分全局和项目 |
| **Claude Code (CLAUDE.md)** | 每个项目一个 CLAUDE.md。不设全局配置层，所有上下文在项目里。 | 中——只处理项目级 |
| **Cline (.clinerules)** | 类似 Cursor，全局 + 项目。MCP tools 作为能力层独立配置。 | 高——能力（工具）与规则分离 |
| **DevOps 12-Factor App** | 代码/配置/脚本严格分离。环境变量注入配置，不做硬编码。 | 高——我们的"硬编码路径"就是违反 12-Factor |
| **PARA 方法 (Tiago Forte)** | Projects (有期限任务) / Areas (长期领域) / Resources (主题参考) / Archives。 | 中——Projects 对应工作流，Resources 对应 skill |
| **Infrastructure as Code (Terraform)** | Modules = 可复用组件；Configs = 环境实例（dev/staging/prod）。模块从不写死环境细节。 | 高——这是最贴切的类比 |

### 4.2 关键启示

**启示 1：能力层与配置层分离**
Terraform module 从不写死 region 或 account ID。同理，skill 不应写死项目路径或沙箱 ID。

**启示 2：全局层"瘦"，项目层"实"**
Cursor 的全局规则极简（"使用 TypeScript""使用 React"），项目规则丰满（"API 端点定义在 src/api/""测试在 __tests__/"）。同理，我们的 skill 层应该薄（方法/原则/决策规则），工作流层应该实（本项目怎么用、路径是什么、命令是什么）。

**启示 3：脚本从方法论中剥离**
Cline 的 MCP tools（对应脚本）与 .clinerules（对应工作流）分离。sl 的 `scripts/pdf_ocr_extract.py` 就是正确做法，sl/SKILL.md 却还在重复贴 bash 和 python。

---

## 五、整改方案

### 5.1 原则（总纲）

> **层1 (skill)** = 做什么（what）和怎么想（how to think）
> **层2 (workflow)** = 在本项目怎么干（how to do it here）
> **层3 (script)** = 具体命令是什么（how to execute exactly）

### 5.2 具体行动

根据上述分析，将整改分为两个阶段：

#### 阶段 A —— 清理边界（立即执行，低风险）

| 操作 | 说明 | 工作量 | 依赖 |
|------|------|--------|------|
| **A1** 删除 link-inbox skill | 被 sl 完全覆盖 | 低（1 个目录） | 你的确认 |
| **A2** 重写 wsj-investigative-report skill | 保留纯方法论（原则/风格/技术规格），删除：项目路径、portal 部署细节、版本历史（v2→v5）、迭代准则（6.1–6.12 的逐条小红书教训）、宇树/长鑫/小红书案例细节 | 中 | 你的确认 |
| **A3** 重写调查报道工作流 | 精简为：① 引用 skill 名；② 项目特有路径约定（底稿/portal/版本归档）；③ 项目特例（宇树标题、小红书 Canonical）；④ 版本历史 | 中 | A2 完成后再做 |
| **A4** 去除 gx/jc/sl 中的硬编码 | 把绝对路径参数化（如 `WIKI_ROOT`），把沙箱 ID 写成变量，把 bash 命令提取到 scripts/ 目录 | 高（跨 3 文件） | |

#### 阶段 B —— 建立规范（持续执行）

| 操作 | 说明 |
|------|------|
| **B1** 制定书写准则（固化到 skill 或 MEMORY.md） | 本报告第五节的"书写准则" |
| **B2** 为 gx/jc/sl 在 LittleRedBook 项目根目录建工作流文件 | 让 skill 变薄，引用项目文件 |
| **B3** 规范 llm-wiki-skill 的目录边界 | 移除 CHANGELOG、docs/、platforms/（或移到仓库 README） |
| **B4** 建立定期审核机制 | 每出 3 篇新报道或每 3 个月，检查一次 skill 目录 |

### 5.3 书写准则（全文）

以下为所有技能/工作流/脚本文件的书写规范：

#### 准则 1：Skill 层规范

**文件位置**：`~/.workbuddy/skills/<name>/SKILL.md`

**必须包含**：
- ✅ frontmatter 的 `description` 精确描述**触发条件**，不描述具体步骤
- ✅ 核心方法/算法/原则
- ✅ 决策规则：什么情况下做什么选择
- ✅ 抽象路径变量（如 `$PROJECT_ROOT`、`$WIKI_ROOT`），不硬编码绝对路径
- ✅ 引用外部脚本时写 `scripts/<文件名>`（相对 skill 目录）

**不得包含**：
- ❌ 硬编码的绝对路径（如 `/Users/xxx/...`）
- ❌ 完整 bash 命令（>3 行的命令提取到 scripts/）
- ❌ 完整 markdown 模板（提取到 scripts/ 或写入工作流）
- ❌ 项目版本历史（v1/v2/v3 changelog）
- ❌ 具体项目的案例细节（如"宇树科技的标题特例"）
- ❌ 固定沙箱 ID 或部署 URL

#### 准则 2：Workflow 层规范

**文件位置**：项目根目录下的 `*.md`（如 `调查报道工作流.md`）

**必须包含**：
- ✅ 项目特有路径约定
- ✅ 步骤序列（先做什么再做什么）
- ✅ 引用技能名（"加载 wsj-investigative-report 技能"）
- ✅ 引用脚本名（"运行 scripts/deploy.sh"）
- ✅ 项目特例和红线（如"宇树标题例外"）
- ✅ 项目版本历史（仅限本项目流程的改动记录）

**不得包含**：
- ❌ 技能的通用方法论（应引用技能名）
- ❌ 完整 bash 命令原文（应引用脚本名）
- ❌ Python 代码片段

#### 准则 3：Script 层规范

**文件位置**：项目 `scripts/` 或 skill 同级 `scripts/` 目录

**必须包含**：
- ✅ 完整可执行的命令
- ✅ 参数说明
- ✅ 错误处理和边界情况

**准则 3.5：行数红线**

在任何文件中：
- **bash 命令内联**：工作流文件中，任何单条 bash 命令不得超过 3 行（管道链）。超过则提取为 `.sh` 脚本。
- **markdown 模板内联**：任何超过 10 行的模板（如生成更新记录的 markdown），必须提取到 `scripts/` 目录下的独立文件，工作流/技能中只写 `参考 scripts/template-update-record.md`。
- **Python/JS 代码内联**：不允许在技能或工作流中出现任何完整函数/类的 Python 或 JavaScript 代码。只允许作为快捷提示的一行命令（如 `python3 extract_text.py input.pdf`）。
- **Skill 文件上限**：任何 skill 的 SKILL.md 正文（不含 frontmatter）不超过 300 行。超过则表示该方法论应该简化或拆分。

---

## 六、附录

### A. 文件归属建议（最终状态）

| 当前文件 | 整改后归属 |
|---------|-----------|
| `~/.workbuddy/skills/wsj-investigative-report/SKILL.md` | ✅ 保留，瘦身为纯方法论（~80 行） |
| `#深度调查档案室/调查报道工作流-v2.md` | ✅ 保留，只留项目特有内容（~60 行） |
| `~/.workbuddy/skills/link-inbox/SKILL.md` | ❌ 删除 |
| `~/.workbuddy/skills/gx/SKILL.md` | ⚠️ 保留薄壳（dispatch only）+ 小红书项目建 workflow |
| `~/.workbuddy/skills/jc/SKILL.md` | ⚠️ 同上 |
| `~/.workbuddy/skills/sl/SKILL.md` | ⚠️ 同上 |
| `~/.workbuddy/skills/llm-wiki-skill/SKILL.md` | ⚠️ 瘦身至 ~400 行，移除 docs/CHANGELOG |
| 其他 8 个 skill | ✅ 保持现状 |
| 小红书收藏/ 项目 | 🆕 新建 `更新工作流.md`（收 gx/jc/sl 的项目内容） |

### B. 预计效果

| 指标 | 当前 | 整改后 |
|------|------|--------|
| skill 文件总数 | 14 | 13（删 link-inbox） |
| SKILL.md 总行数 | ~4800 | ~3000（瘦身 37%） |
| 硬编码绝对路径 | 8+ 处 | 0 处 |
| 重复内容 | wsj 与 workflow 重叠 80% | 0% 重复 |
| 斜杠命令可用性 | 全部可用 | 全部可用（保留薄壳） |
| 可移植性 | 0（gx/jc/sl 换项目即废） | high（项目细节已移到项目文件） |
