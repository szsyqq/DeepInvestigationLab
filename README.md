# 深度调查档案室 · The Investigative Desk

> 基于公开信息、独立完成的深度公司研究档案室。每一篇都从一组关键数字出发，把一家公司的业务、财务、技术与行业位置，用公开数据摊开来读。

[![Deploy to GitHub Pages](https://github.com/szsyqq/DeepInvestigationLab/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/szsyqq/DeepInvestigationLab/actions/workflows/deploy-pages.yml)

- **在线访问**：https://szsyqq.github.io/DeepInvestigationLab/ （启用 GitHub Pages 后生效，Source 选择 *GitHub Actions*）
- **当前站点版本**：`v1.0.0`（见站点页脚 / 顶栏，及 [`portal/changelog.html`](portal/changelog.html)）

---

## 一、项目简介

本仓库是一个**纯静态、无后端、无构建步骤**的深度调查报道发布站。所有内容基于招股书、年报、监管文件与可交叉验证的第三方公开数据，立场中立、不预设结论，署名统一为中性「调查团队」。

- 覆盖领域：机器人、半导体、AI、消费、汽车、金融、资源、航空等。
- 当前已发布多篇深度报道（详见站点首页，篇目随更新增减，此处不列具体数量）。
- 每篇文章含数据可视化（图表 / 时间线 / 数据卡）与移动端适配。

---

## 二、技术实现

### 2.1 整体架构

| 维度 | 说明 |
| --- | --- |
| 渲染方式 | 纯静态 HTML + 内联/外链 CSS + 原生 JS，**无框架、无打包器** |
| 部署 | GitHub Actions 监听 `main` 分支 → 上传 `portal/` 为 Pages 产物 → GitHub Pages 托管 |
| 合规 | 全站法律声明弹窗（首次访问需勾选同意），署名统一「调查团队」 |
| 分享 | 文章页「📤 生成长图」：基于 `html2canvas` + `JSZip`，依赖置于 `portal/vendor/`，**完全离线、不依赖 CDN** |
| 分析 | 可选 beacon 脚本（腾讯灯塔），不影响页面渲染 |

### 2.2 页面架构（两类页面）

- **首页 `portal/index.html`**：完全自包含（CSS/JS 全部内联），含顶栏、报道卡片目录、侧边导航、合规弹窗、页脚。
- **文章页 `portal/reports/<key>/index.html`**：采用「内联文章样式 + 外链全局 UI」模式——
  - `<link rel="stylesheet" href="../global.css">` 引入共享样式；
  - `<script src="../global.js" defer>` 由 `global.js` **统一注入**顶栏、进度条、合规弹窗、页脚、返回顶部等 chrome；
  - 文章正文与图表样式仍内联在页面 `<style>` 中。

> 这种「文章级样式内联 + 全局 UI 外链」的分工，使各篇文章页共享同一套导航/合规/页脚，改一处即全站生效。

### 2.3 版本号体系（本仓库重点）

站点自 **v1.0.0** 起引入版本号，追踪逻辑如下：

| 位置 | 修改点 |
| --- | --- |
| 文章页顶栏 / 页脚 | 由 `portal/global.js` 的 `SITE_VERSION` 常量注入（**改这一处即全站文章页同步**） |
| 首页顶栏 / 页脚 | `portal/index.html` 内联的 `.ver` 与 `.foot-meta`（需与 global.js 同步） |
| 版本历史页 | `portal/changelog.html`（展示历次版本与升级说明） |
| 仓库文档 | 根目录 `CHANGELOG.md` 与 `portal/VERSION`（单一参考源） |

**版本规则**：语义化 `主版本.次版本.修订`
- **主版本 major**：架构或合规重大变更
- **次版本 minor**：新增报道或功能
- **修订 patch**：修复与文案校正

升级时，请同步更新上述 5 处（其中 `global.js` 与 `index.html` 为代码必改项，`changelog.html` / `CHANGELOG.md` / `VERSION` 为记录项）。

---

## 三、项目结构

```
DeepInvestigationLab/
├── .github/workflows/deploy-pages.yml   # 自动部署到 GitHub Pages
├── portal/                              # ★ 站点根目录（唯一被部署的内容）
│   ├── index.html                       # 首页（自包含）
│   ├── changelog.html                   # 版本历史页
│   ├── global.css                       # 文章页共享样式
│   ├── global.js                        # 文章页共享 UI 注入（含版本号）
│   ├── share.js                         # 分享长图功能
│   ├── vendor/                          # 离线依赖（html2canvas / jszip）
│   └── reports/<key>/index.html         # 各篇报道（数量随更新增减）
├── 底稿/                                # 每篇报道的源稿与原始资料（不参与部署）
├── scripts/                             # 批量处理脚本（校验 / 同步 / 修复）
├── 版本归档/                            # 每次实质修改前的只读快照
├── .gitignore                           # 仅放行 portal/ 与仓库级文档
├── README.md                           # 本文件
├── CHANGELOG.md                        # 版本变更日志（镜像站点版本历史）
└── LICENSE                             # 许可声明（内部资料，保留所有权利）
```

> 仅 `portal/` 通过 Actions 上传为 Pages 产物对外发布。`底稿/`（每篇报道的源稿与原始资料）、`版本归档/`（每次实质修改前的只读快照）、`scripts/`（批量处理脚本）等属于**内部创作与工程资产：不公开、不随站点发布，也不在公开仓库中共享**（公开仓库仅保留 `portal/` 与仓库级文档 `README.md` / `CHANGELOG.md` / `LICENSE`）。底稿包含未定稿内容与受版权限制的原始资料，请勿对外分发。

---

## 四、本地预览

```bash
# 方式一：Python 内置服务器（推荐）
cd portal
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080

# 方式二：项目自带 Node 服务
node serve-portal.js
```

> 注意：直接以 `file://` 打开会因浏览器安全策略限制部分脚本；建议用本地 HTTP 服务器预览。

---

## 五、部署流程

1. 修改 `portal/` 下内容（新增/更新报道、调整样式、升级版本号等）。
2. 提交并推送到 `main` 分支：
   ```bash
   git add portal/ README.md CHANGELOG.md
   git commit -m "feat: ..."
   git push origin main
   ```
3. `.github/workflows/deploy-pages.yml` 自动将 `portal/` 上传为 GitHub Pages 产物并发布。
4. 仓库 **Settings → Pages → Source** 需选择 **GitHub Actions**（仅需配置一次）。

---

## 六、内容创作工作流（简述）

1. 在 `底稿/日期_公司/` 撰写报告底稿，并归档原始资料（舆情网页、招股书/年报、研报数据快照）。
2. 将成稿复制到 `portal/reports/<key>/index.html`（文章页框架）。
3. 在 `portal/index.html` 目录**最前面**新增报道卡片（最新报道排在最前）。
4. 重大修改前，先存一份只读快照到 `版本归档/`。
5. 经确认后推送 `main`，由 Actions 自动上线。

详细写作规范与红线见 `wsj-investigative-report_SKILL.md` 与 `调查报道工作流-v2.md`（项目根）。

---

## 七、法律与免责声明

- 本档案室所载内容为**内部研究资料**，基于公开披露信息，不构成任何投资建议、要约或推荐。
- 部分内容借助人工智能工具辅助生成，可能存在信息幻觉或数据偏差；调查团队已尽合理努力核实，但不保证数据绝对准确与完整。
- **投资有风险，请读者独立判断。**
- 站点含法律合规弹窗，继续浏览即视为已阅读并同意上述声明。

---

## 八、许可

内部研究资料，保留所有权利。未经授权，不得转载、再分发或用于商业用途。
