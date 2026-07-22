/* 全局分享生图 · 调查团队档案室 —— 单文件框架
 * 每篇文章只需引入一个脚本：<script src="../../share.js" defer></script>
 * 本脚本会自动按需加载 vendor/html2canvas.min.js。
 *
 * 工作原理：
 *  在当前 document 内创建一个 390px 宽的离屏容器，深拷贝 body 内容，
 *  剥离所有脚本/导航/固定 UI，注入覆盖样式强制正文与图表可见，
 *  然后直接对容器调用 html2canvas，整页截图后切片。
 *  每张图顶部叠加红色"内部资料"条，末张底部带合规声明。
 *  结果直接以图片形式展示，长按即可保存/转发（不打包 ZIP）。
 */
(function () {
  "use strict";

  var RED = "#b11";

  // —— 定位自身 URL，推导 vendor 路径 ——
  var SELF = (function () {
    var s = document.currentScript;
    if (s && s.src) return s.src;
    var list = document.getElementsByTagName("script");
    for (var i = list.length - 1; i >= 0; i--) {
      if (list[i].src && /share\.js(\?|$)/.test(list[i].src)) return list[i].src;
    }
    return "";
  })();
  var BASE = SELF.replace(/share\.js.*$/, ""); // 末尾含 "/"

  function loadHtml2canvas() {
    return new Promise(function (resolve, reject) {
      if (typeof window.html2canvas !== "undefined") return resolve();
      var sc = document.createElement("script");
      sc.src = BASE + "vendor/html2canvas.min.js";
      sc.onload = function () { resolve(); };
      sc.onerror = function () { reject(new Error("html2canvas 加载失败")); };
      document.head.appendChild(sc);
    });
  }

  function injectStyles() {
    var css =
      /* 低调深色小钮：右下错位，不遮挡回顶部/首页钮 */
      ".share-fab{position:fixed;right:14px;bottom:90px;z-index:120;width:38px;height:38px;border-radius:50%;" +
      "background:rgba(45,42,38,.72);color:#f4efe4;border:none;cursor:pointer;font-size:9px;line-height:1;" +
      "font-family:inherit;letter-spacing:.5px;display:flex;align-items:center;justify-content:center;flex-direction:column;" +
      "box-shadow:0 2px 8px rgba(0,0,0,.2);opacity:.55;transition:opacity .25s,background .2s;-webkit-tap-highlight-color:transparent}" +
      ".share-fab:hover{opacity:.9;background:rgba(45,42,38,.9)}" +
      ".share-fab .ic{font-size:13px;line-height:1;margin-bottom:1px}" +
      ".share-fab .tx{font-size:8.5px;letter-spacing:0}" +
      /* 预览层 */
      ".share-overlay{position:fixed;inset:0;z-index:99995;background:rgba(20,18,16,.94);display:none;flex-direction:column}" +
      ".share-overlay.show{display:flex}" +
      ".share-ov-head{display:flex;align-items:center;justify-content:space-between;padding:13px 18px;color:#fff;font-size:14px;font-weight:700;flex:0 0 auto;border-bottom:1px solid rgba(255,255,255,.12)}" +
      ".share-ov-head .x{background:none;border:none;color:#fff;font-size:24px;line-height:1;cursor:pointer;padding:0 4px}" +
      ".share-hint{flex:0 0 auto;text-align:center;color:#e9c46a;font-size:12.5px;padding:9px 16px;letter-spacing:.5px}" +
      ".share-ov-body{flex:1 1 auto;overflow:auto;padding:4px 12px 28px;display:flex;flex-direction:column;align-items:center;gap:16px}" +
      ".share-shot{width:100%;max-width:390px;border-radius:6px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.4);background:#fff}" +
      ".share-shot img{display:block;width:100%;height:auto}" +
      ".share-shot .no{font-size:11px;color:#999;text-align:center;padding:5px;background:#fafafa;border-top:1px solid #eee}" +
      /* 生成中 */
      ".share-loading{position:fixed;inset:0;z-index:99999;background:rgba(20,18,16,.95);display:none;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-size:14px;gap:14px}" +
      ".share-loading.show{display:flex}" +
      ".share-loading .spinner{width:38px;height:38px;border:4px solid rgba(255,255,255,.25);border-top-color:#fff;border-radius:50%;animation:shspin 1s linear infinite}" +
      "@keyframes shspin{to{transform:rotate(360deg)}}";
    var st = document.createElement("style");
    st.textContent = css;
    document.head.appendChild(st);
  }

  function getVar(name, fallback) {
    try {
      var v = getComputedStyle(document.documentElement).getPropertyValue(name);
      return v && v.trim() ? v.trim() : fallback;
    } catch (e) { return fallback; }
  }

  function bannerText() {
    var b = document.querySelector(".internal-banner");
    if (!b) return "内部资料 · 仅供研究参考 · 请勿外传";
    return b.textContent.replace(/[●•]/g, "").replace(/\s+/g, " ").trim();
  }

  function forceRender(root) {
    // 固化柱状/阶梯图高度
    var dh = root.querySelectorAll("[data-h]");
    for (var i = 0; i < dh.length; i++) {
      var h = parseInt(dh[i].getAttribute("data-h"), 10);
      if (h > 0) dh[i].style.height = h + "px";
    }
    // 固化条宽
    var dw = root.querySelectorAll("[data-w]");
    for (var j = 0; j < dw.length; j++) {
      var w = dw[j].getAttribute("data-w");
      if (w) dw[j].style.width = w + "%";
    }
    // 强制 reveal 可见
    var rev = root.querySelectorAll(".reveal");
    for (var m = 0; m < rev.length; m++) rev[m].classList.add("visible");
    // SVG 描边动画归零
    var paths = root.querySelectorAll("path[stroke-dasharray]");
    for (var n = 0; n < paths.length; n++) {
      try { paths[n].style.strokeDashoffset = "0"; } catch (e) {}
    }
  }

  function raf2() {
    return new Promise(function (r) {
      requestAnimationFrame(function () { requestAnimationFrame(r); });
    });
  }

  function waitImages(root) {
    return new Promise(function (resolve) {
      var imgs = root.querySelectorAll("img");
      if (!imgs.length) return resolve();
      var pending = 0;
      var done = false;
      function fin() { if (!done) { done = true; resolve(); } }
      for (var i = 0; i < imgs.length; i++) {
        var img = imgs[i];
        img.removeAttribute("loading");
        img.removeAttribute("decoding");
        if (img.complete) continue;
        pending++;
        img.addEventListener("load", function () { if (--pending === 0) fin(); });
        img.addEventListener("error", function () { if (--pending === 0) fin(); });
      }
      setTimeout(fin, 1200); // 兜底：最多等 1.2s
    });
  }

  async function renderCanvas(red) {
    // 等当前页字体稳定（最多 2s，避免无网络字体时挂起）
    try {
      await Promise.race([
        document.fonts.ready,
        new Promise(function (r) { setTimeout(r, 2000); })
      ]);
    } catch (e) {}

    // 1. 创建离屏宿主容器
    var host = document.createElement("div");
    host.id = "__share_host";
    host.style.cssText = "position:absolute;left:-9999px;top:0;width:390px;z-index:-1;overflow:visible;";
    document.body.appendChild(host);

    // 2. 创建相对定位的截图根容器（白底黑字，避免继承深色主题）
    var wrap = document.createElement("div");
    wrap.id = "__share_wrap";
    wrap.style.cssText = "position:relative;width:390px;max-width:390px;background:#fff;color:#1a1a1a;margin:0;padding:0;overflow:visible;";

    // 3. 注入覆盖样式
    var style = document.createElement("style");
    style.textContent =
      "#__share_wrap,#__share_wrap *{box-sizing:border-box}" +
      "#__share_wrap .reveal,#__share_wrap .reveal.visible{opacity:1!important;transform:none!important;transition:none!important}" +
      "#__share_wrap .step-bar,#__share_wrap .bar-fill,#__share_wrap .di-svg,#__share_wrap path,#__share_wrap circle,#__share_wrap rect{transition:none!important;animation:none!important}" +
      "#__share_wrap svg.di-svg.in path[stroke-dasharray],#__share_wrap svg.di-svg path[stroke-dasharray]{stroke-dashoffset:0!important}" +
      "#__share_wrap .term{cursor:default!important}" +
      "#__share_wrap img{max-width:100%;height:auto}";
    wrap.appendChild(style);

    // 4. 深拷贝 body 内容
    var clone = document.body.cloneNode(true);

    // 5. 移除所有不需要的节点：脚本、导航、固定 UI、内部资料横幅（我们自己画）、本功能 UI
    var rmSel = [
      "script", "style", ".top-bar", ".progress-bar", ".sidenav", ".nav-toggle",
      ".toolbar", ".tracker", ".back-top", ".home-fab", ".fn-tooltip",
      ".consent-overlay", ".share-fab", ".share-overlay", ".share-loading",
      "#__share_host", "#__share_wrap", ".internal-banner"
    ].join(",");
    // 注意：先移除 style，后面再把自己注入的 style 加回 wrap 里
    var toRm = clone.querySelectorAll(rmSel);
    for (var i = 0; i < toRm.length; i++) {
      var n = toRm[i];
      if (n && n.parentNode) n.parentNode.removeChild(n);
    }

    // 6. 强制图表/正文渲染
    forceRender(clone);

    // 7. 把 body 子节点全部移入 wrap
    while (clone.firstChild) {
      wrap.appendChild(clone.firstChild);
    }

    // 8. 添加合规声明
    var comp = document.createElement("div");
    comp.className = "share-compliance";
    comp.style.cssText = "margin:30px 14px 10px;padding:16px 18px;border-top:2px solid " + red + ";background:#fbf8f0;font-size:12px;color:#444;line-height:1.8;border-radius:4px";
    comp.innerHTML = "<b style=\"color:" + red + ";display:block;margin-bottom:6px;font-size:13px;letter-spacing:1px\">合规声明</b>本资料基于招股书、年报、问询回复、监管文件与可交叉验证的第三方公开数据整理，仅供研究参考，不构成任何投资建议。内容立场中立，不唱多、不唱空。署名统一为「调查团队」，不使用任何媒体自称。版权归「调查团队」所有，请勿外传。";
    wrap.appendChild(comp);

    host.appendChild(wrap);

    // 9. 等图片与布局稳定
    await waitImages(wrap);
    await raf2();

    // 10. 计算总高并锁死
    var fullH = Math.max(wrap.scrollHeight, wrap.offsetHeight, wrap.getBoundingClientRect().height);
    wrap.style.height = fullH + "px";
    await raf2();

    // 11. 截图
    var scale = Math.min(window.devicePixelRatio || 1, 2.5);
    var canvas;
    try {
      canvas = await window.html2canvas(wrap, {
        backgroundColor: "#ffffff",
        scale: scale,
        width: 390,
        height: fullH,
        windowWidth: 390,
        windowHeight: fullH,
        scrollX: 0,
        scrollY: 0,
        logging: false,
        useCORS: true,
        allowTaint: false,
      });
    } finally {
      // 无论如何先清理 host，避免污染 DOM
      try { document.body.removeChild(host); } catch (e) {}
    }

    return { canvas: canvas, scale: scale };
  }

  function sliceTiles(canvas, scale, red, text) {
    var totalW = canvas.width;
    var totalH = canvas.height;
    var screenH = 900 * scale;
    var slices = Math.ceil(totalH / screenH);
    if (slices < 1) slices = 1;
    if (slices > 9) slices = 9;
    var sliceHpx = Math.ceil(totalH / slices);
    var bannerH = Math.round(36 * scale);

    var tiles = [];
    for (var s = 0; s < slices; s++) {
      var sy = s * sliceHpx;
      var sh = Math.min(sliceHpx, totalH - sy);
      if (sh <= 0) break;
      var tile = document.createElement("canvas");
      tile.width = totalW;
      tile.height = sh + bannerH;
      var ctx = tile.getContext("2d");
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, tile.width, tile.height);
      ctx.drawImage(canvas, 0, sy, totalW, sh, 0, bannerH, totalW, sh);
      // 顶部红色条
      ctx.fillStyle = red;
      ctx.fillRect(0, 0, totalW, bannerH);
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(Math.round(14 * scale), bannerH / 2, Math.round(3 * scale), 0, Math.PI * 2);
      ctx.fill();
      ctx.textBaseline = "middle";
      ctx.textAlign = "left";
      ctx.font = "700 " + Math.round(12 * scale) + 'px -apple-system,"PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText(text, Math.round(24 * scale), bannerH / 2 + Math.round(1 * scale));
      tiles.push(tile);
    }
    return tiles;
  }

  async function generate() {
    var loading = document.getElementById("shareLoading");
    if (loading) loading.classList.add("show");
    try {
      await loadHtml2canvas();
      var red = getVar("--red", RED);
      var text = bannerText();
      var out = await renderCanvas(red);
      var tiles = sliceTiles(out.canvas, out.scale, red, text);
      if (!tiles.length) throw new Error("未生成任何图片");
      showPreview(tiles);
    } catch (err) {
      try { console.error(err); } catch (e) {}
      try { alert("生成失败：" + (err && err.message ? err.message : err)); } catch (e) {}
    } finally {
      if (loading) loading.classList.remove("show");
    }
  }

  function showPreview(tiles) {
    var ov = document.getElementById("shareOverlay");
    if (!ov) {
      ov = document.createElement("div");
      ov.id = "shareOverlay";
      ov.className = "share-overlay";
      ov.innerHTML =
        '<div class="share-ov-head"><span id="shareOvTitle">分享长图</span>' +
        '<button class="x" aria-label="关闭">×</button></div>' +
        '<div class="share-hint">长按任意图片即可保存到相册 / 转发</div>' +
        '<div class="share-ov-body" id="shareOvBody"></div>';
      document.body.appendChild(ov);
      ov.querySelector(".x").addEventListener("click", function () {
        ov.classList.remove("show");
      });
    }
    document.getElementById("shareOvTitle").textContent =
      "分享长图（共 " + tiles.length + " 张）";
    var body = document.getElementById("shareOvBody");
    body.innerHTML = "";
    for (var i = 0; i < tiles.length; i++) {
      var wrap = document.createElement("div");
      wrap.className = "share-shot";
      var img = new Image();
      img.src = tiles[i].toDataURL("image/png");
      img.alt = "分享长图 " + (i + 1);
      wrap.appendChild(img);
      var no = document.createElement("div");
      no.className = "no";
      no.textContent = (i + 1) + " / " + tiles.length;
      wrap.appendChild(no);
      body.appendChild(wrap);
    }
    ov.classList.add("show");
  }

  function init() {
    injectStyles();
    if (!document.getElementById("shareLoading")) {
      var ld = document.createElement("div");
      ld.id = "shareLoading";
      ld.className = "share-loading";
      ld.innerHTML = '<div class="spinner"></div><div>正在生成分享长图…</div>';
      document.body.appendChild(ld);
    }
    if (!document.getElementById("shareFab")) {
      var btn = document.createElement("button");
      btn.id = "shareFab";
      btn.className = "share-fab";
      btn.type = "button";
      btn.title = "生成分享长图";
      btn.innerHTML = '<span class="ic">⇧</span><span class="tx">长图</span>';
      btn.addEventListener("click", function () { generate(); });
      document.body.appendChild(btn);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
