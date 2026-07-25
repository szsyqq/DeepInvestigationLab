const http = require("http");
const fs = require("fs");
const path = require("path");
const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript",
  ".css": "text/css",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".ttf": "font/ttf"
};
const root = "/Users/panyp/WorkBuddy/#深度调查档案室/portal";
const port = 8125;

const server = http.createServer((req, res) => {
  let p = path.join(root, decodeURIComponent(req.url).split("?")[0]);
  if (p.endsWith("/")) p += "index.html";
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) {
    res.writeHead(404);
    return res.end("Not found");
  }
  const ext = path.extname(p);
  res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});

server.listen(port, "127.0.0.1", () => {
  console.log("Portal local server at http://127.0.0.1:" + port);
});
