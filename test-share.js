const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

(async () => {
  const url = process.argv[2] || "http://127.0.0.1:8125/reports/changxin/index.html";
  const outDir = "/Users/panyp/WorkBuddy/#深度调查档案室/share-test-output";
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: "new",
    defaultViewport: { width: 390, height: 844, deviceScaleFactor: 2 },
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--allow-file-access-from-files"]
  });

  const page = await browser.newPage();
  page.on("console", (msg) => console.log("[console]", msg.text()));
  page.on("pageerror", (err) => console.log("[pageerror]", err.message));
  page.on("dialog", async (dialog) => {
    console.log("[dialog]", dialog.type(), dialog.message());
    await dialog.accept();
  });

  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  console.log("[OK] page loaded");

  await page.waitForSelector("#shareFab", { timeout: 15000 });
  console.log("[OK] shareFab rendered");

  // 如果存在合规弹窗，先勾选并确认
  const hasConsent = await page.evaluate(() => {
    const ov = document.getElementById("consentOverlay");
    return ov && ov.classList.contains("show");
  });
  if (hasConsent) {
    console.log("[OK] consent overlay shown, accepting...");
    await page.click("#consentCheck");
    await page.click("#consentBtn");
    await page.waitForFunction(() => {
      const ov = document.getElementById("consentOverlay");
      return !ov || !ov.classList.contains("show");
    }, { timeout: 10000 });
    console.log("[OK] consent accepted");
  }

  await page.screenshot({ path: path.join(outDir, "page-start.png"), fullPage: false });

  await page.click("#shareFab");
  console.log("[OK] clicked shareFab");

  await page.waitForFunction(() => {
    const ov = document.getElementById("shareOverlay");
    return ov && ov.classList.contains("show");
  }, { timeout: 120000 });
  console.log("[OK] preview overlay shown");

  await new Promise(function (r) { setTimeout(r, 1000); });
  await page.screenshot({ path: path.join(outDir, "preview.png"), fullPage: true });

  const firstImgSrc = await page.evaluate(() => {
    const img = document.querySelector("#shareOvBody img");
    return img ? img.src : null;
  });

  if (firstImgSrc && firstImgSrc.startsWith("data:image/png;base64,")) {
    const buf = Buffer.from(firstImgSrc.split(",")[1], "base64");
    fs.writeFileSync(path.join(outDir, "tile-1.png"), buf);
    console.log("[OK] saved tile-1.png, size=" + buf.length);
  } else {
    console.log("[WARN] no base64 image found, src=" + (firstImgSrc || "null"));
  }

  const count = await page.evaluate(() => document.querySelectorAll("#shareOvBody img").length);
  console.log("[INFO] generated " + count + " tiles");

  await browser.close();
  console.log("[DONE] outputs in " + outDir);
})();
