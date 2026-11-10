#!/usr/bin/env python3
"""
Profil README üreticisi
=======================

GitHub'dan herkese açık verileri çeker, koyu ve açık temaya uygun SVG kartlar
çizer ve README.md içindeki

    <!-- auto:AD -->  …  <!-- /auto:AD -->

bölgelerini yeniden yazar. Bu bölgelerin dışına dokunmaz; kişisel ayarların
hepsi profile.toml'dadır.

    python3 scripts/build.py             # canlı veriyle üret
    python3 scripts/build.py --offline   # ağa çıkmadan, .cache/data.json ile üret

Yalnızca Python standart kütüphanesi kullanılır (3.11+). GITHUB_TOKEN ortam
değişkeni tanımlıysa kullanılır; GitHub Actions bunu kendisi sağlar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import hashlib
import json
import math
import os
import re
import sys
import tomllib
import urllib.request
from html import escape
from pathlib import Path
from string import Template
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CONFIG = ROOT / "profile.toml"
ASSETS = ROOT / "assets"
CACHE = ROOT / ".cache" / "data.json"
NOW = dt.datetime.now(dt.timezone.utc)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

# ── Temalar ──────────────────────────────────────────────────────────────────
# GitHub'ın kendi (Primer) renkleri: kartlar sayfanın doğal bir parçası gibi dursun.
THEMES = {
    "dark": dict(
        bg="#0d1117", bar="#151b23", border="#3d444d",
        fg="#f0f6fc", text="#d1d7e0", muted="#9198a1",
        red="#ff7b72", orange="#ffa657", yellow="#e3b341", green="#7ee787",
        cyan="#56d4dd", blue="#79c0ff", purple="#d2a8ff", gray="#6e7681",
        grad=("#7ee787", "#56d4dd", "#79c0ff"),
        penguin=dict(K="#3a414b", W="#e6edf3", E="#0d1117", O="#f0a04b",
                     S="#a5794f", R="#ff7b72", w="#f0f6fc"),
    ),
    "light": dict(
        bg="#ffffff", bar="#f6f8fa", border="#d1d9e0",
        fg="#1f2328", text="#1f2328", muted="#59636e",
        red="#cf222e", orange="#bc4c00", yellow="#9a6700", green="#1a7f37",
        cyan="#1b7c83", blue="#0969da", purple="#8250df", gray="#6e7781",
        grad=("#1a7f37", "#1b7c83", "#0969da"),
        penguin=dict(K="#1f2328", W="#ffffff", E="#1f2328", O="#f08a24",
                     S="#8a5a2b", R="#cf222e", w="#ffffff"),
    ),
}
TRAFFIC_LIGHTS = ("#ff5f57", "#febc2e", "#28c840")

# GitHub Linguist renkleri (en yaygınlar; listede olmayan dil gri görünür).
LANG_COLORS = {
    "Assembly": "#6E4C13", "Batchfile": "#C1F12E", "C": "#555555", "C#": "#178600",
    "C++": "#f34b7d", "CMake": "#DA3434", "CSS": "#663399", "Dart": "#00B4AB",
    "Dockerfile": "#384d54", "Elixir": "#6e4a7e", "Go": "#00ADD8", "HTML": "#e34c26",
    "Haskell": "#5e5086", "Java": "#b07219", "JavaScript": "#f1e05a",
    "Jupyter Notebook": "#DA5B0B", "Kotlin": "#A97BFF", "Lua": "#000080",
    "MATLAB": "#e16737", "Makefile": "#427819", "Nix": "#7e7eff",
    "Objective-C": "#438eff", "PHP": "#4F5D95", "Perl": "#0298c3",
    "PowerShell": "#012456", "Python": "#3572A5", "QML": "#44a51c", "R": "#198CE7",
    "Ruby": "#701516", "Rust": "#dea584", "SCSS": "#c6538c", "Scala": "#c22d40",
    "Shell": "#89e051", "Svelte": "#ff3e00", "Swift": "#F05138", "TeX": "#3D6117",
    "TypeScript": "#3178c6", "Vim Script": "#199f4b", "Vue": "#41b883", "Zig": "#ec915c",
}
LANG_SHORT = {"Jupyter Notebook": "Jupyter", "Objective-C": "Obj-C"}

# Terminal kartındaki "göçebe penguen" (distronomad'a selam) — her karakter bir piksel.
# K gövde · W beyaz · E göz bebeği · O gaga/ayak · S sopa · R bohça · w bohça deseni
PENGUIN = (
    ".....KKKKKK..............",
    "....KKKKKKKK.............",
    "...KKKKKKKKKK............",
    "...KKWWKKWWKK........SR..",
    "...KKWEKKEWKK.......SRRR.",
    "...KKKOOOOKKK......SRwRRR",
    "..KKKKKOOKKKKK....S.RRRwR",
    "..KKWWWWWWWWKK...S..RRRRR",
    ".KKWWWWWWWWWWKK.S....RRR.",
    ".KWWWWWWWWWWWWKS.........",
    "KKWWWWWWWWWWWWKK.........",
    "KKWWWWWWWWWWWWKK.........",
    ".KWWWWWWWWWWWWK..........",
    ".KKWWWWWWWWWWKK..........",
    "..KKWWWWWWWWKK...........",
    "...KKKKKKKKKK............",
    "..OOOO....OOOO...........",
)
EYES = ((3, 5), (3, 9))  # (satır, sütun): göz kapaklarının sol üst köşesi, 2×2 piksel


# ── Küçük yardımcılar ────────────────────────────────────────────────────────
def esc(value) -> str:
    return escape(str(value), quote=True)


def warn(msg: str) -> None:
    print(f"  ! {msg}", file=sys.stderr)


def parse_ts(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def ago(ts: dt.datetime) -> str:
    days = (NOW - ts).days
    if days < 1:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    if days < 365:
        return f"{plural(days // 30, 'month')} ago"
    return f"{plural(days // 365, 'year')} ago"


def tenure(start: dt.datetime) -> tuple[int, int]:
    years, months = NOW.year - start.year, NOW.month - start.month
    if NOW.day < start.day:
        months -= 1
    if months < 0:
        years, months = years - 1, months + 12
    return years, months


def pct(share: float) -> str:
    return "<1%" if share < 0.01 else f"{share * 100:.0f}%"


def text_width(s: str, size: float, mono: bool = False) -> float:
    """Metnin piksel genişliğini kabaca tahmin eder (sarmak ve kırpmak için).
    Linux'taki geniş yedek fontlar da sığsın diye bilerek cömert hesaplar."""
    if mono:
        return len(s) * size * 0.6
    em = 0.0
    for ch in s:
        if ch == " ":
            em += 0.28
        elif ch in "fijlrtIı.,:;'!|()[]":
            em += 0.31
        elif ch in "mwMW@—":
            em += 0.86
        elif ch.isupper():
            em += 0.68
        elif ch.isdigit():
            em += 0.57
        else:
            em += 0.56
    return em * size


def ellipsize(s: str, max_w: float, size: float, mono: bool = False) -> str:
    if text_width(s, size, mono) <= max_w:
        return s
    while s and text_width(s + "…", size, mono) > max_w:
        s = s[:-1]
    return s.rstrip(" ·,;:-—") + "…"


def wrap(s: str, max_w: float, size: float, max_lines: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in s.split():
        candidate = f"{current} {word}".strip()
        if text_width(candidate, size) <= max_w or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return [ellipsize(line, max_w, size) for line in lines]


def fit_mono(s: str, size: float, max_w: float, min_size: float) -> tuple[str, float]:
    """Tek satırlık monospace metni önce küçülterek, olmazsa kırparak sığdırır."""
    while size > min_size and text_width(s, size, mono=True) > max_w:
        size -= 1
    return ellipsize(s, max_w, size, mono=True), size


def hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def mix(a: str, b: str, amount: float) -> str:
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(ra, rb))


def luminance(color: str) -> float:
    def channel(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in hex_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lang_color(lang: str | None, t: dict) -> str:
    return LANG_COLORS.get(lang or "", t["gray"])


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[-_. ]+|(?<=[a-z])(?=[A-Z])", name) if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:1].upper()


def describe(repo: dict, cfg: dict) -> str:
    custom = cfg.get("projects", {}).get("descriptions", {})
    return custom.get(repo["name"]) or repo.get("description") or "No description yet."


# ── Veri ─────────────────────────────────────────────────────────────────────
def http(url: str, *, accept: str = "application/vnd.github+json",
         body: bytes | None = None, token: str | None = None) -> bytes:
    headers = {"Accept": accept, "User-Agent": "profile-readme-builder"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def fetch(cfg: dict) -> dict:
    login = cfg["github"]["user"]
    token = os.environ.get("GITHUB_TOKEN") or None

    def api(path: str):
        return json.loads(http("https://api.github.com" + path, token=token))

    print(f"→ GitHub verisi çekiliyor: {login}")
    user = api(f"/users/{login}")
    raw_repos, page = [], 1
    while True:
        batch = api(f"/users/{login}/repos?type=owner&per_page=100&page={page}")
        raw_repos += batch
        if len(batch) < 100:
            break
        page += 1

    repos = []
    for r in raw_repos:
        item = {k: r.get(k) for k in ("name", "description", "html_url", "language", "fork",
                                      "archived", "created_at", "pushed_at", "topics")}
        item["stars"], item["forks"] = r["stargazers_count"], r["forks_count"]
        spdx = (r.get("license") or {}).get("spdx_id")
        item["license"] = None if spdx in (None, "NOASSERTION") else spdx
        item["languages"] = {}
        if not r["fork"] and r["name"].lower() != login.lower():
            item["languages"] = api(f"/repos/{login}/{r['name']}/languages")
        repos.append(item)

    return {
        "fetched_at": NOW.isoformat(timespec="seconds"),
        "user": {k: user.get(k) for k in ("login", "name", "html_url", "blog", "followers",
                                          "following", "created_at", "avatar_url")},
        "repos": repos,
        "contributions": fetch_contributions(login, token),
        "feed": fetch_feed(cfg.get("writing", {}).get("feed")),
    }


def fetch_contributions(login: str, token: str | None) -> int | None:
    """Son bir yıldaki katkı sayısı: token varsa GraphQL, yoksa herkese açık takvim."""
    if token:
        query = ("query($login:String!){user(login:$login){contributionsCollection"
                 "{contributionCalendar{totalContributions}}}}")
        try:
            body = json.dumps({"query": query, "variables": {"login": login}}).encode()
            result = json.loads(http("https://api.github.com/graphql", body=body, token=token))
            return result["data"]["user"]["contributionsCollection"]["contributionCalendar"][
                "totalContributions"]
        except Exception as error:  # noqa: BLE001 — yedek yönteme geç
            warn(f"GraphQL ile katkı sayısı alınamadı ({error}); takvim sayfası deneniyor")
    try:
        page = http(f"https://github.com/users/{login}/contributions", accept="text/html").decode()
        match = re.search(r"([\d,.]+)\s+contributions?\s+in the last year", page)
        return int(re.sub(r"\D", "", match.group(1))) if match else None
    except Exception as error:  # noqa: BLE001
        warn(f"katkı sayısı alınamadı: {error}")
        return None


def fetch_feed(url: str | None) -> dict | None:
    """Herhangi bir RSS 2.0 veya Atom akışından yazı başlıklarını okur."""
    if not url:
        return None
    try:
        root = ET.fromstring(http(url, accept="application/atom+xml, application/rss+xml, "
                                               "application/xml;q=0.9, */*;q=0.5"))
    except Exception as error:  # noqa: BLE001
        warn(f"blog akışı okunamadı: {error}")
        return None

    atom = "{http://www.w3.org/2005/Atom}"

    def alternate(node) -> str | None:
        links = node.findall(atom + "link")
        return next((l.get("href") for l in links if l.get("rel", "alternate") == "alternate"),
                    links[0].get("href") if links else None)

    posts = []
    if root.tag == atom + "feed":
        title, site = (root.findtext(atom + "title") or "").strip(), alternate(root) or url
        for entry in root.findall(atom + "entry"):
            posts.append({"title": (entry.findtext(atom + "title") or "").strip(),
                          "url": alternate(entry),
                          "date": entry.findtext(atom + "published") or entry.findtext(atom + "updated")})
    else:
        channel = root.find("channel")
        if channel is None:
            warn("blog akışı RSS ya da Atom değil")
            return None
        title, site = (channel.findtext("title") or "").strip(), (channel.findtext("link") or url).strip()
        for item in channel.findall("item"):
            date = item.findtext("pubDate")
            try:
                date = email.utils.parsedate_to_datetime(date).isoformat() if date else None
            except (TypeError, ValueError):
                date = None
            posts.append({"title": (item.findtext("title") or "").strip(),
                          "url": (item.findtext("link") or "").strip(), "date": date})

    def https(link: str) -> str:
        return re.sub(r"^http://", "https://", link)

    posts = [dict(p, url=https(p["url"])) for p in posts if p["title"] and p["url"]]
    return {"title": title, "url": https(site), "posts": posts}


# ── Veriden anlam çıkarma ────────────────────────────────────────────────────
def select(data: dict, cfg: dict) -> dict:
    login = data["user"]["login"]
    pcfg = cfg.get("projects", {})
    hidden = {n.lower() for n in pcfg.get("exclude", [])} | {login.lower()}  # profil reposu hariç
    own = [r for r in data["repos"] if not r["fork"] and r["name"].lower() not in hidden]
    forks = [r for r in data["repos"] if r["fork"]]
    by_name = {r["name"].lower(): r for r in own}
    active = sorted((r for r in own if not r["archived"]), key=lambda r: r["pushed_at"], reverse=True)

    wanted = str(pcfg.get("spotlight", "auto"))
    # Eski bir repoda README düzeltmek "Now building"i ele geçirmesin: önce son bir yılın repoları.
    recent = [r for r in active if (NOW - parse_ts(r["created_at"])).days <= 365]
    spotlight = (recent or active or [None])[0] if wanted == "auto" else by_name.get(wanted.lower())
    if wanted != "auto" and spotlight is None:
        warn(f"spotlight reposu bulunamadı: {wanted}")

    featured: list[dict] = []
    for name in pcfg.get("featured", []):
        repo = by_name.get(name.lower())
        if repo is None:
            warn(f"featured listesindeki repo bulunamadı: {name}")
        elif repo is not spotlight and repo not in featured:
            featured.append(repo)
    count = int(pcfg.get("featured_count", 4))
    for repo in sorted(active, key=lambda r: (r["stars"], r["pushed_at"]), reverse=True):
        if len(featured) >= count:
            break
        if repo is not spotlight and repo not in featured:
            featured.append(repo)

    return {"own": own, "forks": forks, "spotlight": spotlight, "featured": featured[:count]}


def language_shares(repos: list[dict], top: int = 5) -> list[tuple[str, float]]:
    """Her proje eşit ağırlıkta: tek bir dev repo tüm çubuğu yutmasın."""
    totals: dict[str, float] = {}
    for repo in repos:
        langs = repo.get("languages") or {}
        size = sum(langs.values())
        for lang, nbytes in langs.items():
            totals[lang] = totals.get(lang, 0) + nbytes / size
    whole = sum(totals.values())
    if not whole:
        return []
    ranked = sorted(((k, v / whole) for k, v in totals.items()), key=lambda kv: -kv[1])
    shares, rest = ranked[:top], sum(v for _, v in ranked[top:])
    if rest >= 0.005:
        shares.append(("Other", rest))
    return shares


def terminal_rows(cfg: dict, data: dict, picked: dict) -> list[tuple[str, list[tuple[str, str]]]]:
    term = cfg.get("terminal", {})
    spotlight, own = picked["spotlight"], picked["own"]
    rows = []
    for key, value in term.get("lines", []):
        segs: list[tuple[str, str]]
        if value == "@building":
            if not spotlight:
                continue
            segs = [(spotlight["name"], "hl")]
            for extra in (spotlight.get("language"), f"pushed {ago(parse_ts(spotlight['pushed_at']))}"):
                if extra:
                    segs += [(" · ", "sep"), (extra, "mu")]
        elif value == "@uptime":
            joined = parse_ts(data["user"]["created_at"])
            years, months = tenure(joined)
            segs = [(f"{plural(years, 'year')}, {plural(months, 'month')}", "tx"),
                    (" · ", "sep"), (f"since {joined:%b %Y}", "mu")]
        elif value == "@stats":
            stars = sum(r["stars"] for r in own)
            segs = [(str(len(own)), "num"), (" projects", "tx"), (" · ", "sep"),
                    (str(stars), "num"), (" stars", "tx"), (" · ", "sep"),
                    (str(data["user"]["followers"]), "num"), (" followers", "tx")]
        elif value == "@contribs":
            n = data.get("contributions")
            if n is None or n < int(term.get("contributions_min", 0)):
                continue
            segs = [(f"{n:,}", "num"), (" contributions in the last year", "tx")]
        else:
            segs = []
            for i, part in enumerate(str(value).split(" · ")):
                segs += ([(" · ", "sep")] if i else []) + [(part, "tx")]
        rows.append((key, segs))
    return rows


# ── SVG parçaları ────────────────────────────────────────────────────────────
BASE_CSS = Template("""
text{white-space:pre}
.mono{font-family:$MONO}.sans{font-family:$SANS}
.fg{fill:$fg}.tx{fill:$text}.mu{fill:$muted}.sep{fill:$gray}
.hl{fill:$green;font-weight:700}.num{fill:$fg;font-weight:700}.k{fill:$blue;font-weight:700}
.in{animation:in .55s cubic-bezier(.2,.7,.2,1) backwards}
@keyframes in{from{opacity:0;transform:translateY(6px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""")


def svg_doc(width: float, height: float, title: str, t: dict, defs: list[str],
            body: list[str], css: str = "") -> str:
    style = BASE_CSS.substitute(MONO=MONO, SANS=SANS, **{k: v for k, v in t.items() if isinstance(v, str)})
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">\n'
            f'<title id="title">{esc(title)}</title>\n'
            f'<style>{style}{css}</style>\n'
            f'<defs>{"".join(defs)}</defs>\n' + "\n".join(body) + "\n</svg>\n")


def card_frame(width: float, height: float, t: dict) -> str:
    return (f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="11.5" '
            f'fill="{t["bg"]}" stroke="{t["border"]}"/>')


def tile(x: float, y: float, size: float, repo: dict, t: dict, font: float, gid: str) -> tuple[str, str]:
    base = lang_color(repo.get("language"), t)
    ink = "#ffffff" if luminance(base) < 0.45 else "#1f2328"
    grad = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{mix(base, "#ffffff", .3)}"/>'
            f'<stop offset="1" stop-color="{base}"/></linearGradient>')
    shape = (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * .24:.1f}" fill="url(#{gid})"/>'
             f'<rect x="{x + .5}" y="{y + .5}" width="{size - 1}" height="{size - 1}" rx="{size * .24 - .5:.1f}" '
             f'fill="none" stroke="#ffffff" stroke-opacity=".18"/>'
             f'<text x="{x + size / 2}" y="{y + size / 2 + font * .36:.1f}" text-anchor="middle" class="mono" '
             f'font-size="{font}" font-weight="700" fill="{ink}">{esc(initials(repo["name"]))}</text>')
    return grad, shape


def star_icon(cx: float, cy: float, r: float, color: str) -> str:
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * .46
        points.append(f"{cx + radius * math.cos(angle):.2f},{cy + radius * math.sin(angle):.2f}")
    return (f'<polygon points="{" ".join(points)}" fill="none" stroke="{color}" '
            f'stroke-width="1.3" stroke-linejoin="round"/>')


def fork_icon(x: float, y: float, color: str) -> str:
    return (f'<g fill="none" stroke="{color}" stroke-width="1.3" stroke-linecap="round">'
            f'<circle cx="{x + 2}" cy="{y + 2}" r="1.7"/><circle cx="{x + 10}" cy="{y + 2}" r="1.7"/>'
            f'<circle cx="{x + 6}" cy="{y + 11}" r="1.7"/>'
            f'<path d="M{x + 2} {y + 3.7}v1.3a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-1.3M{x + 6} {y + 7}v2.3"/></g>')


def meta_row(x: float, y: float, repo: dict, t: dict, extra: list[str] | None = None,
             size: float = 13) -> str:
    """Dil · yıldız · fork · ek bilgiler; hepsi monospace, genişlikler kesin."""
    cw, parts, gap = size * .6, [], 22
    lang = repo.get("language")
    if lang:
        parts.append(f'<circle cx="{x + 5}" cy="{y - size * .35:.1f}" r="5" fill="{lang_color(lang, t)}"/>'
                     f'<text x="{x + 15}" y="{y}" class="mono mu" font-size="{size}">{esc(lang)}</text>')
        x += 15 + len(lang) * cw + gap
    for count, icon in ((repo["stars"], "star"), (repo["forks"], "fork")):
        if count > 0:
            glyph = (star_icon(x + 6, y - size * .38, 6.5, t["muted"]) if icon == "star"
                     else fork_icon(x, y - size * .38 - 6.5, t["muted"]))
            parts.append(f'{glyph}<text x="{x + 17}" y="{y}" class="mono mu" font-size="{size}">{count}</text>')
            x += 17 + len(str(count)) * cw + gap
    for item in extra or []:
        parts.append(f'<text x="{x}" y="{y}" class="mono mu" font-size="{size}">{esc(item)}</text>')
        x += len(item) * cw + gap
    return "".join(parts)


# ── Terminal kartı (hero) ────────────────────────────────────────────────────
def svg_whoami(t: dict, ctx: dict) -> str:
    term = ctx["cfg"].get("terminal", {})
    login = ctx["user"]["login"]
    user, host = term.get("user", login), term.get("host", "github")
    command = term.get("command", "whoami --verbose")
    name = term.get("name") or ctx["user"].get("name") or login
    rows, langs = ctx["rows"], ctx["langs"]

    W, FS = 1000, 16
    CW = FS * .6                                    # karakter genişliği; textLength ile sabitlenir
    PX, KX, VX, RX = 36, 300, 424, 964              # kenar · anahtar · değer · sağ kenar
    max_chars = int((RX - VX) // CW)

    y_prompt, y_name, y_sep, y_row, LH = 78, 136, 154, 190, 27
    y_last = y_row + LH * (len(rows) - 1) if rows else y_sep
    y_lang = y_last + LH + 6
    # Dil açıklaması: tek satıra sığmazsa dengeli bir ızgaraya dizilir (ör. 6 dil → 3×2).
    labels = [(f"{LANG_SHORT.get(lang, lang)} {pct(share)}",
               lang_color(lang, t) if lang != "Other" else t["gray"]) for lang, share in langs]
    widths = [14 + len(label) * 13 * .6 for label, _ in labels]
    cols = len(labels)
    while cols > 1 and sum(sorted(widths)[-cols:]) + 22 * (cols - 1) > RX - VX:
        cols -= 1
    if labels:
        cols = math.ceil(len(labels) / math.ceil(len(labels) / cols))
    col_w = (RX - VX) / max(cols, 1) if cols < len(labels) else None
    legend, lx = [], VX
    for i, (label, color) in enumerate(labels):
        row, col = divmod(i, cols)
        x = VX + col * col_w if col_w else lx
        legend.append((x, y_lang + 27 + row * 21, label, color))
        lx += widths[i] + 22
    ly = legend[-1][1] if legend else y_last
    y_blocks = ly + 22
    y_prompt2 = y_blocks + 22 + 48
    H = y_prompt2 + 34

    t_type, per_char = .5, .055
    t_out = t_type + len(command) * per_char + .3
    prompt = f"{user}@{host} ~>"
    x_cmd = PX + (len(prompt) + 1) * CW
    cmd_w = len(command) * CW

    def prompt_text(y: float) -> str:
        return (f'<text x="{PX}" y="{y}" class="mono" font-size="{FS}" textLength="{len(prompt) * CW:.1f}" '
                f'lengthAdjust="spacing"><tspan class="hl">{esc(user)}</tspan><tspan class="mu">@</tspan>'
                f'<tspan fill="{t["cyan"]}" font-weight="700">{esc(host)}</tspan>'
                f'<tspan fill="{t["blue"]}"> ~</tspan><tspan class="tx">&gt;</tspan></text>')

    g0, g1, g2 = t["grad"]
    defs = [
        f'<clipPath id="win"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
        f'<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{g0}"/>'
        f'<stop offset=".55" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>',
        f'<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{g0}"/>'
        f'<stop offset=".4" stop-color="{g2}" stop-opacity=".5"/>'
        f'<stop offset="1" stop-color="{t["border"]}" stop-opacity=".2"/></linearGradient>',
        f'<clipPath id="bar"><rect x="{VX}" y="{y_lang - 11}" width="{RX - VX}" height="10" rx="5"/></clipPath>',
    ]
    css = Template("""
.typer{transform:translateX(${w}px);animation:type ${d}s steps(${n}) ${t0}s backwards}
@keyframes type{from{transform:translateX(0)}to{transform:translateX(${w}px)}}
.cur1{opacity:0;animation:cur1 ${out}s linear}
@keyframes cur1{0%,97%{opacity:1}100%{opacity:0}}
.cur2{animation:blink 1.1s step-end ${end}s infinite}
@keyframes blink{50%{opacity:0}}
.lid{opacity:0;animation:lid 5.5s ${lid}s infinite}
@keyframes lid{0%,93%,100%{opacity:0}94%,97%{opacity:1}}
.seg{transform-box:fill-box;transform-origin:0 50%;animation:grow .7s cubic-bezier(.2,.7,.2,1) backwards}
@keyframes grow{from{transform:scaleX(0)}}
""").substitute(w=f"{cmd_w:.1f}", d=f"{len(command) * per_char:.2f}", n=len(command), t0=t_type,
                out=f"{t_out:.2f}", end=f"{t_out + 1.6:.2f}", lid=f"{t_out + 2:.2f}")

    body = [
        f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="40" fill="{t["bar"]}"/>'
        f'<rect y="40" width="{W}" height="1" fill="{t["border"]}"/></g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>',
        "".join(f'<circle cx="{22 + i * 20}" cy="20" r="6" fill="{c}"/>' for i, c in enumerate(TRAFFIC_LIGHTS)),
        f'<text x="{W / 2}" y="25" text-anchor="middle" class="mono mu" font-size="13">'
        f'{esc(user)}@{esc(host)}: ~</text>',
        # 1) komut yazılıyor
        prompt_text(y_prompt),
        f'<text x="{x_cmd:.1f}" y="{y_prompt}" class="mono tx" font-size="{FS}" textLength="{cmd_w:.1f}" '
        f'lengthAdjust="spacing">{esc(command)}</text>',
        f'<g transform="translate({x_cmd:.1f} {y_prompt - 15})"><g class="typer">'
        f'<rect width="{cmd_w + CW:.1f}" height="21" fill="{t["bg"]}"/>'
        f'<rect class="cur1" y=".5" width="{CW:.1f}" height="20" fill="{t["text"]}"/></g></g>',
    ]

    # 2) çıktı: penguen
    P = 9
    pw, ph = len(PENGUIN[0]) * P, len(PENGUIN) * P
    px = PX + (KX - 40 - PX - pw) / 2
    py = 104 + (y_prompt2 - 40 - 104 - ph) / 2
    pal = t["penguin"]
    pixels = []
    for r, line in enumerate(PENGUIN):
        c = 0
        while c < len(line):
            if line[c] == ".":
                c += 1
                continue
            start = c
            while c < len(line) and line[c] == line[start]:
                c += 1
            pixels.append(f'<rect x="{px + start * P:.1f}" y="{py + r * P:.1f}" width="{(c - start) * P}" '
                          f'height="{P}" fill="{pal[line[start]]}"/>')
    lids = "".join(f'<rect x="{px + c * P:.1f}" y="{py + r * P:.1f}" width="{2 * P}" height="{2 * P}" '
                   f'fill="{pal["K"]}"/>' for r, c in EYES)
    body.append(
        f'<g class="in" style="animation-delay:{t_out:.2f}s">'
        f'<ellipse cx="{px + 8 * P:.1f}" cy="{py + ph + 5:.1f}" rx="{8.5 * P:.1f}" ry="4.5" '
        f'fill="{t["muted"]}" fill-opacity=".16"/>'
        f'<g shape-rendering="crispEdges">{"".join(pixels)}<g class="lid">{lids}</g></g></g>')

    # 3) çıktı: isim, çizgi, satırlar
    delay = t_out + .1
    body.append(
        f'<g class="in" style="animation-delay:{delay:.2f}s">'
        f'<text x="{KX}" y="{y_name}" class="sans" font-size="36" font-weight="800" letter-spacing="-.5" '
        f'fill="url(#name)">{esc(name)}</text>'
        f'<text x="{RX}" y="{y_name}" text-anchor="end" class="mono mu" font-size="14">github.com/{esc(login)}</text>'
        f'<rect x="{KX}" y="{y_sep}" width="{RX - KX}" height="2" rx="1" fill="url(#rule)"/></g>')

    for i, (key, segs) in enumerate(rows):
        fitted, used = [], 0
        for text, cls in segs:
            if used + len(text) <= max_chars:
                fitted.append((text, cls))
                used += len(text)
            else:
                room = max_chars - used - 1
                if room > 0:
                    fitted.append((text[:room].rstrip() + "…", cls))
                break
        spans = "".join(f'<tspan class="{cls}">{esc(text)}</tspan>' for text, cls in fitted)
        y = y_row + i * LH
        body.append(f'<g class="in" style="animation-delay:{delay + .12 + i * .07:.2f}s">'
                    f'<text x="{KX}" y="{y}" class="mono k" font-size="{FS}">{esc(key)}</text>'
                    f'<text x="{VX}" y="{y}" class="mono" font-size="{FS}">{spans}</text></g>')

    # 4) dil çubuğu ve renk blokları
    t_bar = delay + .2 + len(rows) * .07
    if langs:
        body.append(f'<g class="in" style="animation-delay:{t_bar:.2f}s">'
                    f'<text x="{KX}" y="{y_lang}" class="mono k" font-size="{FS}">Languages</text></g>')
        x, segs = VX, []
        for j, (lang, share) in enumerate(langs):
            width = (RX - VX) * share
            gap = 2 if j < len(langs) - 1 else 0
            color = lang_color(lang, t) if lang != "Other" else t["gray"]
            segs.append(f'<rect class="seg" x="{x:.1f}" y="{y_lang - 11}" width="{max(width - gap, 1):.1f}" '
                        f'height="10" fill="{color}" style="animation-delay:{t_bar + .1 + j * .09:.2f}s"/>')
            x += width
        body.append(f'<rect class="in" x="{VX}" y="{y_lang - 11}" width="{RX - VX}" height="10" rx="5" '
                    f'fill="{t["border"]}" fill-opacity=".35" style="animation-delay:{t_bar:.2f}s"/>'
                    f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
        for j, (x, y, label, color) in enumerate(legend):
            body.append(f'<g class="in" style="animation-delay:{t_bar + .3 + j * .06:.2f}s">'
                        f'<circle cx="{x + 4:.1f}" cy="{y - 4.5}" r="4" fill="{color}"/>'
                        f'<text x="{x + 14:.1f}" y="{y}" class="mono mu" font-size="13" '
                        f'textLength="{len(label) * 13 * .6:.1f}" lengthAdjust="spacing">{esc(label)}</text></g>')

    t_blocks = t_bar + .5
    palette = ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "gray")
    body.append("".join(
        f'<rect class="in" x="{VX + j * 30}" y="{y_blocks}" width="22" height="22" rx="5" fill="{t[c]}" '
        f'style="animation-delay:{t_blocks + j * .05:.2f}s"/>' for j, c in enumerate(palette)))

    # 5) yeni komut satırı, yanıp sönen imleç
    body.append(f'<g class="in" style="animation-delay:{t_out + 1.5:.2f}s">{prompt_text(y_prompt2)}'
                f'<rect class="cur2" x="{x_cmd:.1f}" y="{y_prompt2 - 14.5}" width="{CW:.1f}" height="20" '
                f'fill="{t["text"]}"/></g>')

    return svg_doc(W, H, f"{name} — terminal profile card", t, defs, body, css)


# ── "Now building" kartı ─────────────────────────────────────────────────────
def svg_spotlight(t: dict, repo: dict, ctx: dict) -> str:
    W, H = 1000, 204
    pad, nx = 32, 120
    max_w = W - pad - nx
    label = "NOW BUILDING"
    label_w = len(label) * (12 * .6 + 1.4)
    tile_grad, tile_shape = tile(pad, 72, 66, repo, t, 25, "tile")
    name, size = fit_mono(repo["name"], 27, max_w, 18)
    lines = wrap(describe(repo, ctx["cfg"]), max_w, 16, 2)
    extra = [f"{repo['license']} license"] if repo.get("license") else []
    extra.append(f"started {parse_ts(repo['created_at']):%b %Y}")
    g0, _, g2 = t["grad"]

    defs = [f'<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
            f'<linearGradient id="accent" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{g0}"/>'
            f'<stop offset="1" stop-color="{g2}"/></linearGradient>', tile_grad]
    css = (".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-out infinite}"
           "@keyframes pulse{0%{opacity:.6;transform:scale(1)}100%{opacity:0;transform:scale(2.8)}}")
    body = [
        card_frame(W, H, t),
        f'<rect width="4" height="{H}" fill="url(#accent)" clip-path="url(#card)"/>',
        f'<rect x="{pad}" y="26" width="{40 + label_w:.0f}" height="26" rx="13" fill="{t["green"]}" '
        f'fill-opacity=".1" stroke="{t["green"]}" stroke-opacity=".35"/>',
        f'<circle class="pulse" cx="{pad + 15}" cy="39" r="4.5" fill="{t["green"]}" opacity="0"/>'
        f'<circle cx="{pad + 15}" cy="39" r="4.5" fill="{t["green"]}"/>',
        f'<text x="{pad + 28}" y="43.5" class="mono" font-size="12" font-weight="700" letter-spacing="1.4" '
        f'fill="{t["green"]}">{label}</text>',
        f'<text x="{W - pad}" y="44" text-anchor="end" class="mono mu" font-size="13">'
        f'pushed {esc(ago(parse_ts(repo["pushed_at"])))}</text>',
        tile_shape,
        f'<text x="{nx}" y="{98}" class="mono fg" font-size="{size}" font-weight="700">{esc(name)}</text>',
        *(f'<text x="{nx}" y="{128 + i * 23}" class="sans tx" font-size="16">{esc(line)}</text>'
          for i, line in enumerate(lines)),
        meta_row(nx, 180, repo, t, extra),
    ]
    return svg_doc(W, H, f"Now building: {repo['name']}", t, defs, body, css)


# ── Proje kartı ──────────────────────────────────────────────────────────────
def svg_card(t: dict, repo: dict, ctx: dict) -> str:
    W, H = 490, 150
    pad, nx = 20, 76
    tile_grad, tile_shape = tile(pad, pad, 42, repo, t, 16, "tile")
    name, size = fit_mono(repo["name"], 16, W - nx - 44, 12)
    lines = wrap(describe(repo, ctx["cfg"]), W - 2 * pad, 14, 2)
    year = f"{parse_ts(repo['created_at']):%Y}"
    arrow = (f'<path d="M{W - 34} {34}l9-9M{W - 32} {25}h7v7" fill="none" stroke="{t["muted"]}" '
             f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    body = [
        card_frame(W, H, t),
        tile_shape,
        f'<text x="{nx}" y="{pad + 21 + size * .36:.1f}" class="mono fg" font-size="{size}" '
        f'font-weight="700">{esc(name)}</text>',
        arrow,
        *(f'<text x="{pad}" y="{90 + i * 21}" class="sans tx" font-size="14">{esc(line)}</text>'
          for i, line in enumerate(lines)),
        meta_row(pad, 132, repo, t, size=12),
        f'<text x="{W - pad}" y="132" text-anchor="end" class="mono mu" font-size="12">{year}</text>',
    ]
    return svg_doc(W, H, f"{repo['name']} — {describe(repo, ctx['cfg'])}", t, [tile_grad], body)


# ── README bölümleri ─────────────────────────────────────────────────────────
def md_cell(text: str) -> str:
    return escape(text, quote=False).replace("|", "\\|").strip()


def readme_sections(ctx: dict, versions: dict[str, str]) -> dict[str, str]:
    login, cfg = ctx["user"]["login"], ctx["cfg"]
    branch = cfg["github"].get("branch", "main")
    base = f"https://raw.githubusercontent.com/{login}/{login}/{branch}/assets/"

    def picture(stem: str, alt: str, width: str = "100%") -> str:
        dark = f"{base}{stem}-dark.svg?v={versions[stem + '-dark']}"
        light = f"{base}{stem}-light.svg?v={versions[stem + '-light']}"
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
                f'<source media="(prefers-color-scheme: light)" srcset="{light}">'
                f'<img alt="{esc(alt)}" src="{light}" width="{width}"></picture>')

    sections = {}
    name = cfg.get("terminal", {}).get("name") or login
    facts = "; ".join(f"{key}: {''.join(text for text, _ in segs)}" for key, segs in ctx["rows"])
    sections["whoami"] = (f'<a href="https://github.com/{login}/{login}">'
                          f'{picture("whoami", f"Terminal profile card. {name} — {facts}")}</a>')

    spot = ctx["spotlight"]
    if spot:
        alt = "Now building {}: {}".format(spot["name"], describe(spot, cfg))
        sections["spotlight"] = f'<a href="{spot["html_url"]}">{picture("now", alt)}</a>'
    else:
        sections["spotlight"] = "_Something new is on the way._"

    cards = []
    for r in ctx["featured"]:
        alt = "{}: {}".format(r["name"], describe(r, cfg))
        cards.append(f'<a href="{r["html_url"]}">{picture("card-" + slug(r["name"]), alt, "49%")}</a>')
    rows = [" ".join(cards[i:i + 2]) for i in range(0, len(cards), 2)]
    sections["featured"] = '<p align="center">\n' + "\n<br>\n".join(rows) + "\n</p>" if cards else ""

    table = ["| Project | About | Language | ★ | Updated |", "|:--|:--|:--|--:|:--:|"]
    for r in sorted(ctx["own"], key=lambda r: r["pushed_at"], reverse=True):
        about = describe(r, cfg)
        about = about if len(about) <= 72 else about[:71].rstrip(" ,.;") + "…"
        lang = LANG_SHORT.get(r.get("language") or "", r.get("language") or "—")
        table.append(f"| [{md_cell(r['name'])}]({r['html_url']}) | {md_cell(about)} | "
                     f"{lang} | {r['stars'] or ''} | {parse_ts(r['pushed_at']):%Y} |")
    if ctx["forks"]:
        table.append(f'\n<sub>Plus {len(ctx["forks"])} forks of projects I learned from — '
                     f'<a href="https://github.com/{login}?tab=repositories&amp;type=fork">browse them</a>.</sub>')
    sections["projects"] = "\n".join(table)

    feed = ctx["feed"]
    count = int(cfg.get("writing", {}).get("count", 4))
    posts = (feed or {}).get("posts", [])[:count]
    sections["writing"] = ("\n".join(f"- [{md_cell(p['title'])}]({p['url']})" for p in posts)
                           if posts else "_New posts are on the way._")
    return sections


def replace_region(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- auto:{name} -->)(.*?)(<!-- /auto:{name} -->)", re.S)
    if not pattern.search(text):
        warn(f"README'de <!-- auto:{name} --> bölgesi yok, atlandı")
        return text
    return pattern.sub(lambda m: f"{m.group(1)}\n\n{content}\n\n{m.group(3)}", text, count=1)


# ── Çalıştırma ───────────────────────────────────────────────────────────────
def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def write_if_changed(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text("utf-8") != content:
        path.write_text(content, "utf-8")
        print(f"  ✓ {path.relative_to(ROOT)}")


def build(cfg: dict, data: dict, concept_override: str | None = None) -> None:
    from concepts import CONCEPT_META, build_concept_readmes, svg_boot, svg_man, svg_nomad, svg_pipeline

    picked = select(data, cfg)
    ctx = {"cfg": cfg, "user": data["user"], "feed": data.get("feed"), **picked,
           "rows": terminal_rows(cfg, data, picked), "langs": language_shares(picked["own"])}

    svgs: dict[str, str] = {}
    for theme, t in THEMES.items():
        svgs[f"whoami-{theme}"] = svg_whoami(t, ctx)
        svgs[f"man-{theme}"] = svg_man(t, ctx)
        svgs[f"pipeline-{theme}"] = svg_pipeline(t, ctx)
        svgs[f"boot-{theme}"] = svg_boot(t, ctx)
        svgs[f"nomad-{theme}"] = svg_nomad(t, ctx)
        if ctx["spotlight"]:
            svgs[f"now-{theme}"] = svg_spotlight(t, ctx["spotlight"], ctx)
        for repo in ctx["featured"]:
            svgs[f"card-{slug(repo['name'])}-{theme}"] = svg_card(t, repo, ctx)

    versions = {}
    for stem, content in svgs.items():
        ET.fromstring(content)  # bozuk SVG asla yazılmasın
        write_if_changed(ASSETS / f"{stem}.svg", content)
        versions[stem] = hashlib.sha1(content.encode()).hexdigest()[:8]
    for old in [*ASSETS.glob("card-*.svg"), *ASSETS.glob("now-*.svg")]:  # eski kartları temizle
        if old.stem not in svgs:
            old.unlink()
            print(f"  ✗ {old.relative_to(ROOT)}")

    sections = readme_sections(ctx, versions)
    concept_readmes = build_concept_readmes(ctx, versions, sections)
    active_concept = concept_override or cfg.get("github", {}).get("concept", "terminal")
    if active_concept not in concept_readmes:
        warn(f"bilinmeyen konsept '{active_concept}', 'terminal' kullanılıyor")
        active_concept = "terminal"

    # Önizleme aracının 5 konsepti tek tıkla karşılaştırabilmesi için kaydet
    concepts_cache = ROOT / ".cache" / "concepts.json"
    concepts_cache.parent.mkdir(exist_ok=True)
    concepts_cache.write_text(
        json.dumps(
            {"active": active_concept, "meta": CONCEPT_META, "readmes": concept_readmes},
            ensure_ascii=False,
            indent=1,
        ),
        "utf-8",
    )

    if concept_override:
        header = (
            "<!--\n"
            "  Bu dosya muratboy/muratboy reposunda durduğunda GitHub profilinin en üstünde görünür.\n"
            '  "auto" adlı yorum işaretleri arasındaki kısımları scripts/build.py üretir — elle\n'
            "  değiştirilen içerik bir sonraki çalıştırmada ezilir. Geri kalan her yer serbest.\n"
            "  Kişisel ayarlar: profile.toml\n"
            "-->\n\n"
        )
        write_if_changed(README, header + concept_readmes[active_concept])
    else:
        text = README.read_text("utf-8")
        for name, content in sections.items():
            text = replace_region(text, name, content)
        write_if_changed(README, text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profil README'sini ve kartlarını üretir.")
    parser.add_argument("--offline", action="store_true",
                        help="ağa çıkma, .cache/data.json'daki son veriyi kullan")
    parser.add_argument("--concept", choices=["terminal", "man", "pipeline", "boot", "nomad"],
                        help="ana README.md dosyasını seçilen konsepte dönüştür")
    args = parser.parse_args()

    cfg = tomllib.loads(CONFIG.read_text("utf-8"))
    if args.offline:
        data = json.loads(CACHE.read_text("utf-8"))
    else:
        data = fetch(cfg)
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")
    build(cfg, data, concept_override=args.concept or cfg.get("github", {}).get("concept"))
    print("✓ Tamam.")


if __name__ == "__main__":
    main()
