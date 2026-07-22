/* =========================================================
   调查团队档案室 · 全局 UI 注入脚本
   负责注入顶部横幅、导航栏、进度条、合规弹窗、页脚
   每页通过 <script>window.__REPORT_CONFIG__ = {...}</script> 传入配置
   ========================================================= */
(function () {
  "use strict";

  var RED = "#a02020";

  // —— 默认配置 ——
  var CONFIG = window.__REPORT_CONFIG__ || {};
  var BANNER_TEXT = CONFIG.bannerText || "内部资料 · 仅供研究参考 · 请勿外传";
  var HOME_URL = CONFIG.homeUrl || "../../index.html";
  var READING_TIME = CONFIG.readingTime || "";
  var REPORT_TITLE = CONFIG.reportTitle || "";
  var DISC_TEXT = CONFIG.discText || "";
  var CONSENT_TEXT = CONFIG.consentText || null;

  // —— 标准免责声明文本（各页统一） ——
  var DEFAULT_DISC =
    '<b>免责声明</b>：本档案室内容为内部研究资料，不构成任何投资建议、要约或推荐。所涉公司、数据及事实均基于公开披露信息，分析仅代表调查团队个人观点，不作为投资决策依据。' +
    '<b>资料性质</b>：本档案室所有内容均基于招股书、年报、审计意见及公开报道，仅用于研究参考，请读者独立判断。';

  if (!DISC_TEXT) DISC_TEXT = DEFAULT_DISC;

  // —— 标准合规弹窗文本 ——
  var DEFAULT_CONSENT = {
    title: "法律声明 · LEGAL NOTICE",
    body: [
      { h: "一、资料性质", p: "本档案室内容为<strong>内部研究资料</strong>，包含对各上市／拟上市公司的独立调研与分析，不构成任何投资建议、要约或推荐。" },
      { h: "二、免责声明", p: "所有数据基于公开披露信息（招股书、年报、审计报告、新闻），分析仅代表调查团队个人观点，所涉判断不保证准确或完整。投资有风险，请读者独立判断。" },
      { h: "三、用户知情同意", p: "继续浏览本档案室，即表示您已阅读并同意以上声明。" }
    ]
  };
  if (!CONSENT_TEXT) CONSENT_TEXT = DEFAULT_CONSENT;

  // —— 工具函数 ——
  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
      }
    }
    if (children) {
      for (var i = 0; i < children.length; i++) {
        var c = children[i];
        if (typeof c === "string") e.appendChild(document.createTextNode(c));
        else e.appendChild(c);
      }
    }
    return e;
  }

  // —— 检查是否已有某个元素 ——
  function exists(sel) { return document.querySelector(sel); }

  // —— 注入内部资料横幅 ——
  function injectBanner() {
    if (exists(".internal-banner")) return;
    var b = el("div", { class: "internal-banner" }, [el("span", null, ["●"]), " " + BANNER_TEXT]);
    document.body.insertBefore(b, document.body.firstChild);
  }

  // —— 注入进度条 ——
  function injectProgress() {
    if (exists(".progress-bar")) return;
    document.body.appendChild(el("div", { class: "progress-bar", id: "progress" }));
  }

  // —— 注入顶部导航栏 ——
  function injectTopBar() {
    if (exists(".top-bar")) return;
    var bar = el("div", { class: "top-bar" });
    var inner = el("div", { class: "top-bar-inner" });
    var left = el("div", { class: "top-bar-left" });
    var right = el("div", { class: "top-bar-right" });

    // 返回首页
    left.appendChild(el("a", { class: "home", href: HOME_URL }, ["返回首页"]));

    // 阅读时间
    if (READING_TIME) {
      left.appendChild(el("span", { class: "sep" }));
      left.appendChild(el("span", { class: "time", id: "readTime" }, [READING_TIME]));
    }

    // 位置追踪（章节）
    if (REPORT_TITLE) {
      right.appendChild(el("span", { class: "pos", id: "tracker" }, ["导语"]));
      right.appendChild(el("span", { class: "sep" }));
      right.appendChild(el("button", { class: "toc nav-toggle", onclick: "toggleNav()" }, ["≡ 目录"]));
    } else {
      right.appendChild(el("button", { class: "toc nav-toggle", onclick: "toggleNav()" }, ["≡ 目录"]));
    }

    inner.appendChild(left);
    inner.appendChild(right);
    bar.appendChild(inner);
    document.body.appendChild(bar);
  }

  // —— 注入阅读时间徽章（右下浮动） ——
  function injectReadingFab() {
    if (exists(".reading-time-fab") || !READING_TIME) return;
    document.body.appendChild(el("div", { class: "reading-time-fab" }, [READING_TIME]));
  }

  // —— 注入侧边目录（如果页面还没有） ——
  function injectSidenav() {
    if (exists(".sidenav")) return;
    // 不自动注入，由页面自己提供章节内容
  }

  // —— 注入返回顶部 ——
  function injectBackTop() {
    if (exists(".back-top")) return;
    var b = el("button", {
      class: "back-top", id: "backTop", onclick: "scrollTop()", title: "回到顶部"
    }, ["↑"]);
    document.body.appendChild(b);
  }

  // —— 注入合规弹窗 ——
  function injectConsent() {
    if (exists(".consent-overlay")) return;
    var overlay = el("div", { class: "consent-overlay", id: "consentOverlay" });
    var box = el("div", { class: "consent-box" });
    var header = el("div", { class: "consent-header" });
    header.appendChild(el("span", null, [CONSENT_TEXT.title]));
    header.appendChild(el("button", {
      class: "consent-close",
      onclick: "document.getElementById('consentOverlay').classList.remove('show');document.body.classList.remove('locked')",
      title: "关闭"
    }, ["×"]));
    box.appendChild(header);

    var body = el("div", { class: "consent-body" });
    for (var i = 0; i < CONSENT_TEXT.body.length; i++) {
      var item = CONSENT_TEXT.body[i];
      body.appendChild(el("h3", null, [item.h]));
      body.appendChild(el("p", null, [item.p]));
    }
    box.appendChild(body);

    var footer = el("div", { class: "consent-footer" });
    var label = el("label", { style: "font-size:13px;color:var(--ink);cursor:pointer" });
    label.appendChild(el("input", { type: "checkbox", id: "consentCheck" }));
    label.appendChild(document.createTextNode(" 我已阅读并同意上述声明"));
    footer.appendChild(label);
    footer.appendChild(el("button", { class: "consent-btn", id: "consentBtn", disabled: "" }, ["确认并进入"]));
    box.appendChild(footer);

    overlay.appendChild(box);
    document.body.appendChild(overlay);

    // 弹窗初始化逻辑
    function _gc() { try { return sessionStorage.getItem("investigative_desk_consent"); } catch (e) { return null; } }
    function _sc() { try { sessionStorage.setItem("investigative_desk_consent", "1"); } catch (e) {} }

    var check = document.getElementById("consentCheck");
    var btn = document.getElementById("consentBtn");
    if (check && btn) {
      btn.addEventListener("click", function () {
        if (check.checked) { _sc(); document.body.classList.remove("locked"); overlay.classList.remove("show"); }
      });
      check.addEventListener("change", function () { btn.disabled = !check.checked; });
    }

    if (!_gc()) {
      overlay.classList.add("show");
      document.body.classList.add("locked");
    }
  }

  // —— 注入页脚 ——
  function injectFooter() {
    if (exists("footer")) return;
    var f = el("footer");
    f.appendChild(el("div", { class: "disc" }, [DISC_TEXT]));
    document.body.appendChild(f);
  }

  // —— 注入全局 JS 辅助函数（供页面内联 JS 调用） ——
  function injectGlobals() {
    if (typeof window.scrollTop === "function") return;
    window.scrollTop = function () { window.scrollTo({ top: 0, behavior: "smooth" }); };
    if (typeof window.toggleNav === "function") return;
    window.toggleNav = (function () {
      var nav = null;
      return function () {
        if (!nav) nav = document.getElementById("sidenav");
        if (nav) nav.classList.toggle("open");
      };
    })();
  }

  // —— 滚动时 compact 模式：红条折叠 + 顶部导航变红变紧凑 ——
  function setupCompact() {
    function compactToggle(){document.body.classList.toggle('compact',window.scrollY>80)}
    window.addEventListener('scroll',compactToggle,{passive:true});
    window.addEventListener('load',compactToggle);
    compactToggle();
  }

  // —— 位置追踪 (#tracker) 点击打开侧边目录 ——
  function setupTrackerNav() {
    var tr = document.getElementById('tracker');
    if (!tr) return;
    tr.classList.add('nav-toggle');
    tr.style.cursor = 'pointer';
    tr.addEventListener('click', function (e) {
      e.stopPropagation();
      var n = document.querySelector('.sidenav');
      if (n) n.classList.toggle('open');
    });
  }

  // —— 执行注入 ——
  function init() {
    injectGlobals();
    injectBanner();
    injectTopBar();
    injectProgress();
    injectReadingFab();
    injectBackTop();
    injectConsent();
    injectFooter();
    setupCompact();
    setupTrackerNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
