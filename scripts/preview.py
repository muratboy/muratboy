#!/usr/bin/env python3
"""
Yerel önizleme (Çoklu Konsept Karşılaştırıcı)
=============================================

5 farklı profil konseptini (Terminal, man murat(1), İşlemci Hattı, Linux Boot,
Göçebe Haritası) GitHub profil sayfasına benzeyen bir çerçevede yan yana / tek
tıkla geçişli olarak gösteren preview.html üretir. Hiçbir şey GitHub'a gönderilmez.

    python3 scripts/preview.py          # preview.html oluştur
    python3 scripts/preview.py --open   # oluştur ve tarayıcıda aç

Sayfanın üstündeki düğmelerle 5 konsept, koyu/açık tema ve masaüstü/mobil
genişlik arasında geçiş yapılabilir (klavyeden 1-5 tuşları da çalışır).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
import webbrowser
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preview.html"

TEMPLATE = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Önizleme · __LOGIN__/README.md (5 Konsept Karşılaştırma)</title>
<link id="css-light" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-light.css">
<link id="css-dark" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-dark.css">
<script src="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js"></script>
<style>
  :root { --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0; --subtle:#f6f8fa; --accent:#0969da; --badge-bg:#ddf4ff; --badge-fg:#0969da; color-scheme: light; }
  [data-theme="dark"] { --bg:#0d1117; --fg:#f0f6fc; --muted:#9198a1; --border:#3d444d; --subtle:#151b23; --accent:#4493f8; --badge-bg:#121d2f; --badge-fg:#79c0ff; color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif; }
  .bar { position:sticky; top:0; z-index:10; display:flex; flex-wrap:wrap; gap:10px; align-items:center;
         padding:10px 16px; background:var(--subtle); border-bottom:1px solid var(--border); }
  .bar-title { display:flex; flex-direction:column; margin-right:auto; min-width:180px; }
  .bar-title strong { font-weight:600; font-size:13.5px; }
  .bar-title .note { color:var(--muted); font-size:11.5px; }
  .seg { display:inline-flex; flex-wrap:wrap; border:1px solid var(--border); border-radius:6px; overflow:hidden; background:var(--bg); }
  .seg button { font:inherit; font-size:13px; color:var(--fg); background:transparent; border:0; padding:6px 11px; cursor:pointer; transition:background .12s; }
  .seg button:hover { background:var(--subtle); }
  .seg button + button { border-left:1px solid var(--border); }
  .seg button[aria-pressed="true"] { background:var(--accent); color:#fff; font-weight:600; }
  .concept-banner { max-width:1280px; margin:16px auto 0; padding:0 24px; }
  .concept-box { background:var(--subtle); border:1px solid var(--border); border-radius:8px; padding:12px 16px;
                 display:flex; flex-wrap:wrap; gap:12px 24px; align-items:center; justify-content:space-between; }
  .concept-info { flex:1 1 520px; }
  .concept-head { display:flex; align-items:center; gap:8px; margin-bottom:4px; }
  .concept-head strong { font-size:14.5px; }
  .c-badge { font-size:11.5px; font-weight:600; padding:1px 8px; border-radius:999px; background:var(--badge-bg); color:var(--badge-fg); border:1px solid var(--border); }
  .concept-desc { margin:0 0 6px; color:var(--fg); font-size:13.5px; }
  .concept-meta { margin:0; color:var(--muted); font-size:12px; }
  .concept-cmd { display:flex; align-items:center; gap:8px; background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:6px 10px; font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
  .concept-cmd button { font:inherit; font-size:11.5px; padding:3px 8px; border-radius:4px; border:1px solid var(--border); background:var(--subtle); color:var(--fg); cursor:pointer; }
  .concept-cmd button:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
  .page { max-width:1280px; margin:0 auto; padding:20px 24px 64px; display:grid;
          grid-template-columns:296px minmax(0,1fr); gap:24px; align-items:start; }
  .side .avatar { width:100%; aspect-ratio:1; border-radius:50%; border:1px solid var(--border); display:block; }
  .side h1 { margin:16px 0 0; font-size:24px; line-height:1.25; font-weight:600; }
  .side .login { display:block; color:var(--muted); font-size:20px; font-weight:300; }
  .side p { color:var(--muted); margin:16px 0 0; }
  .side a { color:var(--fg); text-decoration:none; }
  .readme { border:1px solid var(--border); border-radius:6px; padding:24px; min-width:0; }
  .readme-head { display:flex; justify-content:space-between; align-items:center; font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; color:var(--muted); margin-bottom:16px; }
  .markdown-body { background:transparent !important; font-size:16px; }
  body.mobile .concept-banner { max-width:430px; padding:0 16px; }
  body.mobile .page { max-width:430px; grid-template-columns:1fr; padding:16px; gap:16px; }
  body.mobile .side { display:grid; grid-template-columns:64px 1fr; gap:4px 12px; align-items:center; }
  body.mobile .side h1 { margin:0; font-size:20px; }
  body.mobile .side p { grid-column:1 / -1; margin:8px 0 0; }
  body.mobile .readme { padding:16px; }
  .missing { color:var(--muted); }
</style>
</head>
<body>
<div class="bar">
  <div class="bar-title">
    <strong>Önizleme · __LOGIN__/README.md</strong>
    <span class="note">5 konsept hazır (klavyeden 1–5 ile de geçebilirsiniz) · GitHub'a hiçbir şey gönderilmez</span>
  </div>
  <div class="seg" id="concept-seg" role="group" aria-label="Konsept"></div>
  <div class="seg" role="group" aria-label="Tema">
    <button data-theme-btn="dark">Koyu</button><button data-theme-btn="light">Açık</button>
  </div>
  <div class="seg" role="group" aria-label="Genişlik">
    <button data-view-btn="desktop">Masaüstü</button><button data-view-btn="mobile">Mobil</button>
  </div>
</div>

<section class="concept-banner">
  <div class="concept-box">
    <div class="concept-info">
      <div class="concept-head">
        <strong id="c-title"></strong>
        <span class="c-badge" id="c-badge"></span>
      </div>
      <p class="concept-desc" id="c-summary"></p>
      <p class="concept-meta">
        <b>✨ Güçlü yanı:</b> <span id="c-pros"></span> &nbsp;·&nbsp;
        <b>📱 Mobil:</b> <span id="c-mobile"></span>
      </p>
    </div>
    <div class="concept-cmd" title="Bu konsepti ana README.md olarak kaydetmek için terminal komutu">
      <code id="c-cmd"></code>
      <button id="c-copy" type="button">Kopyala</button>
    </div>
  </div>
</section>

<main class="page">
  <aside class="side">
    <img class="avatar" src="__AVATAR__" alt="">
    <h1>__NAME__<span class="login">__LOGIN__</span></h1>
    <p>👥 <b>__FOLLOWERS__</b> followers · <b>__FOLLOWING__</b> following<br>🔗 <a href="__BLOG__">__BLOG_LABEL__</a></p>
  </aside>
  <section class="readme">
    <div class="readme-head">
      <span>__LOGIN__ / README.md</span>
      <span id="c-file-note"></span>
    </div>
    <article id="md" class="markdown-body"></article>
  </section>
</main>
<script>
const CONCEPTS = __CONCEPTS__;
const params = new URLSearchParams(location.search);
let concept = params.get("concept") || CONCEPTS.active || "terminal";
if (!CONCEPTS.readmes[concept]) concept = "terminal";
let theme = params.get("theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
let view = params.get("view") || "desktop";

const segEl = document.getElementById("concept-seg");
CONCEPTS.meta.forEach(m => {
  const btn = document.createElement("button");
  btn.dataset.conceptBtn = m.id;
  btn.textContent = m.label;
  btn.onclick = () => { concept = m.id; renderConcept(); apply(); };
  segEl.appendChild(btn);
});

function renderConcept() {
  const mdText = CONCEPTS.readmes[concept] || CONCEPTS.readmes.terminal;
  document.getElementById("md").innerHTML = marked.parse(mdText, { gfm: true });
  document.querySelectorAll("#md img").forEach(img => img.addEventListener("error", () => {
    img.replaceWith(Object.assign(document.createElement("span"), { className: "missing", textContent: "[görsel yüklenemedi: " + img.alt + "]" }));
  }));
  const info = CONCEPTS.meta.find(m => m.id === concept) || CONCEPTS.meta[0];
  document.getElementById("c-title").textContent = info.label;
  document.getElementById("c-badge").textContent = info.badge;
  document.getElementById("c-summary").textContent = info.summary;
  document.getElementById("c-pros").textContent = info.pros;
  document.getElementById("c-mobile").textContent = info.mobile;
  const cmd = "python3 scripts/build.py --offline --concept " + info.id;
  document.getElementById("c-cmd").textContent = cmd;
  document.getElementById("c-file-note").textContent = "konsept: " + info.id;
}

document.getElementById("c-copy").onclick = () => {
  navigator.clipboard.writeText(document.getElementById("c-cmd").textContent);
  const btn = document.getElementById("c-copy");
  btn.textContent = "Kopyalandı ✓";
  setTimeout(() => { btn.textContent = "Kopyala"; }, 1500);
};

function apply() {
  document.documentElement.dataset.theme = theme;
  document.getElementById("css-dark").disabled = theme !== "dark";
  document.getElementById("css-light").disabled = theme !== "light";
  document.body.classList.toggle("mobile", view === "mobile");
  document.querySelectorAll("#md picture source").forEach(source => {
    if (source.dataset.media === undefined) source.dataset.media = source.getAttribute("media") || "";
    const match = source.dataset.media.match(/prefers-color-scheme:\\s*(dark|light)/);
    if (match) source.setAttribute("media", match[1] === theme ? "all" : "not all");
  });
  document.querySelectorAll("[data-concept-btn]").forEach(b => b.setAttribute("aria-pressed", b.dataset.conceptBtn === concept));
  document.querySelectorAll("[data-theme-btn]").forEach(b => b.setAttribute("aria-pressed", b.dataset.themeBtn === theme));
  document.querySelectorAll("[data-view-btn]").forEach(b => b.setAttribute("aria-pressed", b.dataset.viewBtn === view));
  history.replaceState(null, "", "?concept=" + concept + "&theme=" + theme + "&view=" + view);
}

document.querySelectorAll("[data-theme-btn]").forEach(b => b.onclick = () => { theme = b.dataset.themeBtn; apply(); });
document.querySelectorAll("[data-view-btn]").forEach(b => b.onclick = () => { view = b.dataset.viewBtn; apply(); });
window.addEventListener("keydown", e => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
  const idx = parseInt(e.key, 10) - 1;
  if (idx >= 0 && idx < CONCEPTS.meta.length) {
    concept = CONCEPTS.meta[idx].id;
    renderConcept();
    apply();
  }
});

renderConcept();
apply();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="README.md ve 5 konsept için yerel önizleme üretir.")
    parser.add_argument("--open", action="store_true", help="oluşturduktan sonra tarayıcıda aç")
    args = parser.parse_args()

    cfg = tomllib.loads((ROOT / "profile.toml").read_text("utf-8"))
    login, branch = cfg["github"]["user"], cfg["github"].get("branch", "main")
    raw_prefix = f"https://raw.githubusercontent.com/{login}/{login}/{branch}/"

    concepts_path = ROOT / ".cache" / "concepts.json"
    if not concepts_path.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--offline"], check=True)

    concepts_data = json.loads(concepts_path.read_text("utf-8"))
    for k, md in concepts_data["readmes"].items():
        concepts_data["readmes"][k] = md.replace(raw_prefix, "")

    cache = ROOT / ".cache" / "data.json"
    user = json.loads(cache.read_text("utf-8"))["user"] if cache.exists() else {}
    blog = user.get("blog") or ""
    blog_url = blog if blog.startswith("http") else f"https://{blog}" if blog else "#"

    html = TEMPLATE
    for key, value in {
        "__LOGIN__": escape(login),
        "__NAME__": escape(user.get("name") or login),
        "__AVATAR__": escape(user.get("avatar_url") or f"https://github.com/{login}.png"),
        "__FOLLOWERS__": str(user.get("followers", "–")),
        "__FOLLOWING__": str(user.get("following", "–")),
        "__BLOG__": escape(blog_url),
        "__BLOG_LABEL__": escape(blog or "—"),
        "__CONCEPTS__": json.dumps(concepts_data, ensure_ascii=False).replace("</", "<\\/"),
    }.items():
        html = html.replace(key, value)
    OUT.write_text(html, "utf-8")
    print(f"✓ {OUT}")
    if args.open:
        webbrowser.open(OUT.as_uri())


if __name__ == "__main__":
    main()
