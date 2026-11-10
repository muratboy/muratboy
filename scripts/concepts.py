#!/usr/bin/env python3
"""
Alternatif profil konseptleri (SVG + Markdown üreticileri)
==========================================================

Mevcut 'terminal' (whoami) konseptine ek olarak 4 farklı mühendislik konsepti
üretir. Hepsi gerçek GitHub ve blog verisini (ctx) kullanır:

1. terminal : Mevcut 'whoami --verbose' terminal kartı ve göçebe penguen
2. man      : Unix kılavuz sayfası — MURAT(1) (düz metin ağırlıklı, mobilde kusursuz)
3. pipeline : 5 aşamalı RISC/MIPS işlemci hattı (IF → ID → EX → MEM → WB)
4. boot     : Linux çekirdek / systemd açılış ekranı ([  OK  ] satırları)
5. nomad    : Göçebe haritası (Assembly'den Pardus ve bugünkü projeye yolculuk rotası)
"""

from __future__ import annotations

from string import Template

from build import (
    EYES,
    LANG_SHORT,
    PENGUIN,
    TRAFFIC_LIGHTS,
    ago,
    describe,
    ellipsize,
    esc,
    wrap,
    lang_color,
    md_cell,
    parse_ts,
    pct,
    plural,
    svg_doc,
    tenure,
)

CONCEPT_META: list[dict[str, str]] = [
    {
        "id": "terminal",
        "label": "1. Terminal (whoami)",
        "badge": "Mevcut Örnek",
        "summary": (
            "murat@nomad ~> whoami --verbose komutu, göz kırpan göçebe penguen ve dil çubuğu. "
            "Samimi, canlı ve bir Linux geliştiricisi olduğunu ilk saniyede hissettiriyor."
        ),
        "pros": "Sıcak ilk izlenim · Penguen maskotu ile distronomad göndermesi · Dengeli görsel/metin oranı",
        "mobile": "Üst kart SVG olduğu için mobilde küçülür; alt bölümler doğal akar.",
    },
    {
        "id": "man",
        "label": "2. man murat(1)",
        "badge": "Unix Klasik · Mobil Dostu",
        "summary": (
            "Gerçek bir Linux kılavuz sayfası (MURAT(1)). İnce bir durum çubuğu altında tamamen "
            "yapılandırılmış metin: NAME, SYNOPSIS, DESCRIPTION, ACTIVE DAEMON, OPTIONS, FILES, SEE ALSO."
        ),
        "pros": "Mobilde %100 doğal ölçeklenir · Çok zarif ve zamansız · Sistem/Linux vurgusu çok güçlü",
        "mobile": "Kusursuz — metin tabanlı olduğu için her ekran genişliğinde okunaklıdır.",
    },
    {
        "id": "pipeline",
        "label": "3. İşlemci Hattı (CPU)",
        "badge": "En Özgün · Bilgisayar Mimarisi",
        "summary": (
            "5 aşamalı RISC/MIPS işlemci hattı (IF → ID → EX → MEM → WB). En çok yıldızlı MIPS Assembly "
            "reponuz ve blogunuzdaki Sniper / Interval işlemci simülasyonu yazılarınızla doğrudan bağ kurar."
        ),
        "pros": "GitHub'da eşi benzeri yok · Bilgisayar mühendisliği temelini kanıtlar · Canlı saat sinyali animasyonu",
        "mobile": "Yatay mimari diyagram masaüstünde çok etkileyicidir; mobilde yakınlaştırma gerekebilir.",
    },
    {
        "id": "boot",
        "label": "4. Linux Boot ([ OK ])",
        "badge": "Sistem & Çekirdek",
        "summary": (
            "Pardus / systemd açılış akışı: donanım katmanından (MIPS, PIC, C) başlayıp kullanıcı uzayına "
            "(Python, Flutter) ve aktif servis olarak şu anki projeye kadar adım adım [  OK  ] ile açılır."
        ),
        "pros": "Donanımdan yazılıma katmanlı hikâye · Sırayla akan satır animasyonu · Çok tanıdık Linux estetiği",
        "mobile": "Terminal kartıyla benzer; masaüstünde tam konsol havası verir.",
    },
    {
        "id": "nomad",
        "label": "5. Göçebe Haritası",
        "badge": "Hikâye & distronomad Markası",
        "summary": (
            "2017'deki Assembly ve mikrodenetleyici kampından başlayıp C, Python/NLP ve Flutter duraklarından "
            "geçerek bugünkü Pardus + şu anki proje ana kampına ulaşan topografik yolculuk haritası."
        ),
        "pros": "distronomad projesini kişisel markaya dönüştürür · 11 yıllık gelişimi tek bakışta anlatır",
        "mobile": "Harita kartı SVG'dir; altındaki proje ve blog kartları mobilde normal akar.",
    },
]


# ── 2. KONSEPT SVG: man murat(1) üst durum çubuğu ───────────────────────────
def svg_man(t: dict, ctx: dict) -> str:
    W, H = 1000, 174
    login = ctx["user"]["login"]
    joined = parse_ts(ctx["user"]["created_at"])
    years, _ = tenure(joined)
    spot = ctx["spotlight"]
    spot_name = spot["name"] if spot else "distronomad"
    langs = ctx["langs"]

    defs = [
        f'<clipPath id="mwin"><rect width="{W}" height="{H}" rx="10"/></clipPath>',
        f'<clipPath id="mbar"><rect x="118" y="110" width="460" height="7" rx="3.5"/></clipPath>',
    ]
    css = (
        ".cur{animation:blink 1.1s step-end infinite}"
        "@keyframes blink{50%{opacity:0}}"
    )
    body = [
        f'<g clip-path="url(#mwin)">'
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="34" fill="{t["fg"]}"/>'
        f'<rect y="{H - 28}" width="{W}" height="28" fill="{t["bar"]}"/>'
        f'<rect y="{H - 28}" width="{W}" height="1" fill="{t["border"]}"/>'
        f'</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{t["border"]}"/>',
        f'<text x="24" y="22" class="mono" font-size="13.5" font-weight="700" fill="{t["bg"]}">MURAT(1)</text>',
        f'<text x="{W / 2}" y="22" text-anchor="middle" class="mono" font-size="13.5" font-weight="700" '
        f'fill="{t["bg"]}">Linux Programmer\'s Manual · System &amp; Architecture</text>',
        f'<text x="{W - 24}" y="22" text-anchor="end" class="mono" font-size="13.5" font-weight="700" '
        f'fill="{t["bg"]}">MURAT(1)</text>',
        # Orta özet alanı
        f'<text x="24" y="62" class="mono k" font-size="13.5">NAME</text>',
        f'<text x="118" y="62" class="mono fg" font-size="14.5" font-weight="700">murat</text>',
        f'<text x="172" y="62" class="mono tx" font-size="14.5">'
        f'— computer engineer · low-level systems, Linux tooling &amp; Flutter</text>',
        f'<text x="24" y="90" class="mono k" font-size="13.5">STATUS</text>',
        f'<text x="118" y="90" class="mono mu" font-size="13.5">'
        f'uptime: <tspan class="tx">{years} yrs (since {joined:%b %Y})</tspan>  ·  '
        f'daemon: <tspan class="hl">{esc(spot_name)}</tspan>  ·  '
        f'host: <tspan class="tx">Pardus / fish</tspan>  ·  '
        f'repos: <tspan class="num">{len(ctx["own"])}</tspan></text>',
        f'<text x="24" y="118" class="mono k" font-size="13.5">LANGS</text>',
        f'<rect x="118" y="110" width="460" height="7" rx="3.5" fill="{t["border"]}" fill-opacity=".35"/>',
    ]
    lx = 118.0
    segs = []
    lparts = []
    for j, (lang, share) in enumerate(langs[:5]):
        w = 460 * share
        gap = 2 if j < len(langs[:5]) - 1 else 0
        col = lang_color(lang, t) if lang != "Other" else t["gray"]
        segs.append(f'<rect x="{lx:.1f}" y="110" width="{max(w - gap, 1):.1f}" height="7" fill="{col}"/>')
        lx += w
        lparts.append(f"{LANG_SHORT.get(lang, lang)} {pct(share)}")
    body.append(f'<g clip-path="url(#mbar)">{"".join(segs)}</g>')
    body.append(
        f'<text x="594" y="118" class="mono mu" font-size="12">'
        f'{esc(" · ".join(lparts[:4]))}</text>'
    )
    # Alt pager durum satırı (imleç metnin kendi içinde, fonttan bağımsız)
    body.append(
        f'<text x="24" y="{H - 9}" class="mono mu" font-size="12">'
        f'Manual page murat(1) line 1/48 (press h for help or star a repo) — github.com/{esc(login)} '
        f'<tspan class="cur" fill="{t["text"]}">█</tspan></text>'
    )
    return svg_doc(W, H, "MURAT(1) — Linux Programmer's Manual", t, defs, body, css)


# ── 3. KONSEPT SVG: 5-Stage CPU Pipeline (IF → ID → EX → MEM → WB) ──────────
def svg_pipeline(t: dict, ctx: dict) -> str:
    W, H = 1000, 442
    login = ctx["user"]["login"]
    joined = parse_ts(ctx["user"]["created_at"])
    years, _ = tenure(joined)
    own = ctx["own"]
    stars = sum(r["stars"] for r in own)
    followers = ctx["user"]["followers"]
    spot = ctx["spotlight"]
    langs = ctx["langs"][:4]

    defs = [
        f'<clipPath id="pwin"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
        f'<linearGradient id="pbus" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{t["cyan"]}"/><stop offset=".5" stop-color="{t["green"]}"/>'
        f'<stop offset="1" stop-color="{t["purple"]}"/></linearGradient>',
    ]
    css = Template("""
.pkt{animation:flow 3.6s linear infinite}
.pkt2{animation:flow 3.6s linear 1.8s infinite}
@keyframes flow{0%{transform:translateX(0);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateX(760px);opacity:0}}
.alu-pulse{animation:apulse 2.4s ease-in-out infinite}
@keyframes apulse{0%,100%{stroke-opacity:.45}50%{stroke-opacity:1}}
.clk-dot{animation:cblink 1.2s steps(2,end) infinite}
@keyframes cblink{50%{opacity:.25}}
""").substitute()

    body = [
        f'<g clip-path="url(#pwin)">'
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="42" fill="{t["bar"]}"/>'
        f'<rect y="42" width="{W}" height="1" fill="{t["border"]}"/>'
        f'</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>',
        # Üst mimari başlık çubuğu
        f'<rect x="18" y="11" width="10" height="20" rx="2" fill="{t["cyan"]}"/>',
        f'<text x="36" y="26" class="mono fg" font-size="13" font-weight="700">'
        f'ARCH: MURAT-RISC64 PIPELINE</text>',
        f'<text x="275" y="26" class="mono mu" font-size="12">'
        f'5-Stage Datapath · Forwarding: ON · Predictor: NOMAD</text>',
        f'<text x="{W - 20}" y="26" text-anchor="end" class="mono mu" font-size="12">'
        f'UPTIME: <tspan class="hl">{years}Y</tspan> · IPC: <tspan class="fg">{len(own)} REPOS / {stars}★</tspan></text>',
    ]

    # Yatay veri yolu çizgisi ve akan veri paketleri (kutuların arkasında, sadece aralarda görünür)
    bus_y = 200
    body.append(
        f'<line x1="110" y1="{bus_y}" x2="890" y2="{bus_y}" stroke="url(#pbus)" '
        f'stroke-width="2.5" stroke-dasharray="5 4" stroke-opacity=".7"/>'
        f'<circle class="pkt" cx="110" cy="{bus_y}" r="4.5" fill="{t["green"]}"/>'
        f'<circle class="pkt2" cx="110" cy="{bus_y}" r="4.5" fill="{t["cyan"]}"/>'
    )

    stages = [
        ("IF", "Instruction Fetch", "cyan", "PC → 0x2015_2026"),
        ("ID", "Decode / RegFile", "blue", "Registers $r0–$r3"),
        ("EX", "Execute (ALU)", "green", "ACTIVE THREAD"),
        ("MEM", "L1 Cache (Work)", "orange", "Selected Repos"),
        ("WB", "Write-Back", "purple", "Output & Blog"),
    ]
    sw, sh, sy = 172, 246, 68
    gap = 19

    for idx, (code, title, col_key, sub) in enumerate(stages):
        sx = 32 + idx * (sw + gap)
        accent = t[col_key]
        is_ex = code == "EX"
        stroke_w = "2" if is_ex else "1"
        stroke_col = accent if is_ex else t["border"]
        extra_cls = ' class="alu-pulse"' if is_ex else ""

        # Ara pipeline yazmaçları (IF/ID, ID/EX, EX/MEM, MEM/WB)
        if idx < 4:
            rx = sx + sw + 5
            reg_lbl = f"{code}/{stages[idx + 1][0]}"
            body.append(
                f'<rect x="{rx}" y="{sy + 28}" width="9" height="{sh - 42}" rx="3" '
                f'fill="{t["bar"]}" stroke="{t["border"]}"/>'
                f'<text x="{rx + 4.5}" y="{sy - 6}" text-anchor="middle" class="mono mu" '
                f'font-size="9.5">{reg_lbl}</text>'
            )

        title_x = sx + 58 if len(code) == 3 else sx + 50
        body.append(
            f'<g class="in" style="animation-delay:{0.08 + idx * 0.1:.2f}s">'
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="9" fill="{t["bar"]}" '
            f'stroke="{stroke_col}" stroke-width="{stroke_w}"{extra_cls}/>'
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="32" rx="9" fill="{accent}" fill-opacity=".14"/>'
            f'<text x="{sx + 10}" y="{sy + 21}" class="mono" font-size="13.5" font-weight="700" '
            f'fill="{accent}">[{code}]</text>'
            f'<text x="{title_x}" y="{sy + 20}" class="sans fg" font-size="12" font-weight="700">'
            f'{esc(title)}</text>'
            f'<text x="{sx + 12}" y="{sy + 50}" class="mono mu" font-size="11">{esc(sub)}</text>'
            f'<line x1="{sx + 12}" y1="{sy + 58}" x2="{sx + sw - 12}" y2="{sy + 58}" '
            f'stroke="{t["border"]}" stroke-opacity=".6"/>'
        )

        cy = sy + 78
        if code == "IF":
            if_rows = [
                ("Name", "Murat Boy"),
                ("Role", "Computer Eng."),
                ("OS", "Pardus"),
                ("Shell", "fish · VS Code"),
                ("Domain", "CPU Arch · Apps"),
                ("Scope", "ASM → Flutter"),
            ]
            for k, v in if_rows:
                body.append(
                    f'<text x="{sx + 12}" y="{cy}" class="mono mu" font-size="11">{k}:</text>'
                    f'<text x="{sx + 62}" y="{cy}" class="mono tx" font-size="11">{esc(v)}</text>'
                )
                cy += 25
        elif code == "ID":
            for r_i, (lang, share) in enumerate(langs):
                short = LANG_SHORT.get(lang, lang)
                lcol = lang_color(lang, t)
                bw = max(int((sw - 24) * share), 6)
                body.append(
                    f'<text x="{sx + 12}" y="{cy}" class="mono mu" font-size="11">$r{r_i}</text>'
                    f'<text x="{sx + 38}" y="{cy}" class="mono tx" font-size="11.5" font-weight="600">'
                    f'{esc(short)}</text>'
                    f'<text x="{sx + sw - 12}" y="{cy}" text-anchor="end" class="mono mu" font-size="11">'
                    f'{pct(share)}</text>'
                    f'<rect x="{sx + 12}" y="{cy + 5}" width="{sw - 24}" height="5" rx="2.5" '
                    f'fill="{t["border"]}" fill-opacity=".4"/>'
                    f'<rect x="{sx + 12}" y="{cy + 5}" width="{bw}" height="5" rx="2.5" fill="{lcol}"/>'
                )
                cy += 36
            body.append(
                f'<text x="{sx + 12}" y="{sy + sh - 14}" class="mono mu" font-size="10.5">'
                f'ISA: Dart · Py · C · ASM</text>'
            )
        elif code == "EX":
            sname = spot["name"] if spot else "distronomad"
            slang = (spot.get("language") if spot else "Python") or "Python"
            spush = ago(parse_ts(spot["pushed_at"])) if spot else "today"
            sdesc = wrap(describe(spot, ctx["cfg"]) if spot else "", sw - 24, 11, 3)
            body.append(
                f'<rect x="{sx + 12}" y="{cy - 12}" width="{sw - 24}" height="24" rx="5" '
                f'fill="{t["green"]}" fill-opacity=".12" stroke="{t["green"]}" stroke-opacity=".35"/>'
                f'<circle cx="{sx + 23}" cy="{cy}" r="4" fill="{t["green"]}"/>'
                f'<text x="{sx + 33}" y="{cy + 4}" class="mono hl" font-size="12">'
                f'{esc(ellipsize(sname, sw - 50, 12, mono=True))}</text>'
                + "".join(
                    f'<text x="{sx + 12}" y="{cy + 30 + i * 17}" class="sans {"tx" if i == 0 else "mu"}" '
                    f'font-size="11">{esc(line)}</text>'
                    for i, line in enumerate(sdesc)
                )
                + f'<text x="{sx + 12}" y="{cy + 94}" class="mono mu" font-size="11">'
                f'Lang: <tspan class="tx">{esc(slang)}</tspan></text>'
                f'<text x="{sx + 12}" y="{cy + 114}" class="mono mu" font-size="11">'
                f'Push: <tspan class="hl">{esc(spush)}</tspan></text>'
                f'<text x="{sx + 12}" y="{sy + sh - 14}" class="mono mu" font-size="10.5">'
                f'ALU STATUS: ZERO_STALL</text>'
            )
        elif code == "MEM":
            short_names = {
                "Bilgisayar-Organizasyonu_Mibs-Assembly-Ornekleri": "Mibs-Assembly",
            }
            for m_i, repo in enumerate(ctx["featured"][:4]):
                addr = f"0x{m_i * 4:02X}"
                rlabel = short_names.get(repo["name"], ellipsize(repo["name"], 95, 11, mono=True))
                rlang = LANG_SHORT.get(repo.get("language") or "", repo.get("language") or "Code")
                yr = f"{parse_ts(repo['created_at']):%Y}"
                meta_txt = f"★{repo['stars']}" if repo["stars"] else yr
                body.append(
                    f'<text x="{sx + 12}" y="{cy}" class="mono mu" font-size="10.5">{addr}</text>'
                    f'<text x="{sx + 44}" y="{cy}" class="mono fg" font-size="11.5" font-weight="600">'
                    f'{esc(rlabel)}</text>'
                    f'<text x="{sx + 44}" y="{cy + 15}" class="mono mu" font-size="10.5">'
                    f'{esc(rlang)} · {esc(meta_txt)}</text>'
                )
                cy += 38
            body.append(
                f'<text x="{sx + 12}" y="{sy + sh - 14}" class="mono mu" font-size="10.5">'
                f'L1 HIT: 100% · {len(own)} repos</text>'
            )
        elif code == "WB":
            wb_rows = [
                ("Public Repos", str(len(own))),
                ("Stargazers", f"{stars} ★"),
                ("Followers", str(followers)),
                ("Learned Forks", str(len(ctx["forks"]))),
            ]
            for k, v in wb_rows:
                body.append(
                    f'<text x="{sx + 12}" y="{cy}" class="mono mu" font-size="11">{k}:</text>'
                    f'<text x="{sx + sw - 12}" y="{cy}" text-anchor="end" class="mono num" font-size="11">'
                    f'{esc(v)}</text>'
                )
                cy += 24
            body.append(
                f'<line x1="{sx + 12}" y1="{cy - 8}" x2="{sx + sw - 12}" y2="{cy - 8}" '
                f'stroke="{t["border"]}" stroke-opacity=".5"/>'
                f'<text x="{sx + 12}" y="{cy + 10}" class="mono" font-size="11" font-weight="700" '
                f'fill="{t["purple"]}">Blog · Sella Turcica</text>'
                f'<text x="{sx + 12}" y="{cy + 27}" class="sans mu" font-size="11">'
                f'• Sniper CPU Simulator</text>'
                f'<text x="{sx + 12}" y="{cy + 43}" class="sans mu" font-size="11">'
                f'• Interval Simulation</text>'
                f'<text x="{sx + 12}" y="{cy + 59}" class="sans mu" font-size="11">'
                f'• Quantum &amp; Cloud</text>'
            )

        body.append("</g>")

    # Alt Forwarding Unit & Clock Sinyali Çubuğu
    by = 330
    clk_pts = []
    cx0 = 88
    for step in range(11):
        x_a = cx0 + step * 24
        x_b = x_a + 12
        clk_pts.append(f"{x_a},{by + 29} {x_a},{by + 16} {x_b},{by + 16} {x_b},{by + 29}")
    body.extend([
        f'<rect x="32" y="{by}" width="{W - 64}" height="90" rx="9" fill="{t["bar"]}" stroke="{t["border"]}"/>',
        f'<text x="48" y="{by + 26}" class="mono k" font-size="11.5">CLK</text>',
        f'<polyline points="{" ".join(clk_pts)}" fill="none" stroke="{t["green"]}" stroke-width="1.6"/>',
        f'<circle class="clk-dot" cx="368" cy="{by + 22}" r="4" fill="{t["green"]}"/>',
        f'<text x="384" y="{by + 26}" class="mono mu" font-size="11.5">'
        f'FORWARDING UNIT: <tspan class="tx">EX/MEM → ALU (low-level architecture feeds high-level tools)</tspan></text>',
        f'<line x1="48" y1="{by + 44}" x2="{W - 48}" y2="{by + 44}" stroke="{t["border"]}" stroke-opacity=".6"/>',
        f'<text x="48" y="{by + 65}" class="mono mu" font-size="11.5">'
        f'TRACE: '
        f'<tspan fill="{t["orange"]}">[2017] LW $s0, mips_asm</tspan> → '
        f'<tspan fill="{t["blue"]}">[2018] ADD $s1, c_structs</tspan> → '
        f'<tspan fill="{t["purple"]}">[2022] JAL flutter_apps</tspan> → '
        f'<tspan class="hl">[NOW] SYSCALL {esc(spot["name"] if spot else "next_project")}</tspan></text>',
        f'<text x="48" y="{by + 81}" class="mono mu" font-size="10.5">'
        f'github.com/{esc(login)} · plexuschoroideus.blogspot.com</text>',
    ])

    return svg_doc(W, H, "Murat Boy — 5-Stage CPU Pipeline Profile", t, defs, body, css)


# ── 4. KONSEPT SVG: Linux Kernel / systemd Boot Sequence ([  OK  ]) ──────────
def svg_boot(t: dict, ctx: dict) -> str:
    W, H = 1000, 456
    joined = parse_ts(ctx["user"]["created_at"])
    years, months = tenure(joined)
    own = ctx["own"]
    stars = sum(r["stars"] for r in own)
    followers = ctx["user"]["followers"]
    spot = ctx["spotlight"]
    spot_name = spot["name"] if spot else "distronomad"
    spot_push = ago(parse_ts(spot["pushed_at"])) if spot else "today"
    langs = ctx["langs"]

    defs = [
        f'<clipPath id="bwin"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
        f'<clipPath id="bbar"><rect x="210" y="366" width="754" height="8" rx="4"/></clipPath>',
    ]
    css = (
        ".cur{animation:blink 1.1s step-end infinite}"
        "@keyframes blink{50%{opacity:0}}"
        ".actv{animation:ap 2s ease-in-out infinite}"
        "@keyframes ap{0%,100%{opacity:1}50%{opacity:.45}}"
    )

    body = [
        f'<g clip-path="url(#bwin)">'
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="38" fill="{t["bar"]}"/>'
        f'<rect y="38" width="{W}" height="1" fill="{t["border"]}"/>'
        f'</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>',
        "".join(f'<circle cx="{22 + i * 20}" cy="19" r="6" fill="{c}"/>' for i, c in enumerate(TRAFFIC_LIGHTS)),
        f'<text x="{W / 2}" y="24" text-anchor="middle" class="mono mu" font-size="12.5">'
        f'tty1 — pardus-nomad — Pardus GNU/Linux x86_64 (systemd)</text>',
        f'<text x="32" y="68" class="mono mu" font-size="12.5">'
        f'[  0.000000] <tspan class="fg" font-weight="700">Linux version 6.12.0-amd64 (Pardus)</tspan> '
        f'(murat@nomad) (gcc, GNU ld) #1 SMP PREEMPT_DYNAMIC</text>',
        f'<text x="32" y="92" class="mono mu" font-size="12.5">'
        f'[  0.004812] <tspan fill="{t["cyan"]}">CPU0: Murat Boy</tspan> — Computer Engineer '
        f'(bare-metal assembly, systems C, Python TUI/CLI, Flutter)</text>',
    ]

    boot_lines = [
        ("OK", "Mounted", "/dev/hardware",
         "MIPS Assembly (11★) · PIC16F Microcontrollers · Embedded Systems"),
        ("OK", "Loaded", "/lib/modules/core.ko",
         "C Data Structures · Multicore Processor & Interval Simulation"),
        ("OK", "Started", "workstation.slice",
         "Pardus · fish shell · VS Code · GitHub Actions CI"),
        ("OK", "Mounted", "/usr/share/stack",
         "Dart & Flutter · Python · C · MIPS Assembly · Bash"),
        ("OK", "Reached", "github-net.target",
         f"Uptime: {years}y {months}m (since {joined:%b %Y}) · {len(own)} repos · {stars} ★ · {followers} followers"),
        ("OK", "Mounted", "/var/log/sella",
         "Technical Blog — Processor Simulation, Quantum Computing & Dev Notes"),
        ("ACTV", "Starting", f"{spot_name}.service",
         f"{ellipsize(describe(spot, ctx['cfg']) if spot else 'Something new', 470, 12.5, mono=True)}"),
    ]

    y0, lh = 128, 32
    for idx, (status, verb, unit, desc) in enumerate(boot_lines):
        y = y0 + idx * lh
        is_actv = status == "ACTV"
        badge_col = t["cyan"] if is_actv else t["green"]
        badge_cls = ' class="mono actv"' if is_actv else ' class="mono"'
        badge_txt = "ACTV" if is_actv else "OK"
        unit_cls = "hl" if is_actv else "fg"
        body.append(
            f'<g class="in" style="animation-delay:{0.12 + idx * 0.09:.2f}s">'
            f'<text x="32" y="{y}" class="mono mu" font-size="13">[</text>'
            f'<text x="58" y="{y}" text-anchor="middle"{badge_cls} font-size="13" font-weight="700" '
            f'fill="{badge_col}">{badge_txt}</text>'
            f'<text x="84" y="{y}" class="mono mu" font-size="13">]</text>'
            f'<text x="102" y="{y}" class="mono tx" font-size="13">{esc(verb)}</text>'
            f'<text x="180" y="{y}" class="mono {unit_cls}" font-size="13" font-weight="700">'
            f'{esc(unit)}</text>'
            f'<text x="366" y="{y}" class="mono mu" font-size="12.5">— {esc(desc)}</text>'
            f'</g>'
        )

    body.append(
        f'<line x1="32" y1="348" x2="{W - 32}" y2="348" stroke="{t["border"]}" stroke-opacity=".6"/>'
        f'<text x="32" y="374" class="mono k" font-size="12.5">/proc/languages</text>'
        f'<rect x="210" y="366" width="754" height="8" rx="4" fill="{t["border"]}" fill-opacity=".35"/>'
    )
    lx = 210.0
    segs = []
    legend_parts = []
    for j, (lang, share) in enumerate(langs):
        w = 754 * share
        gap = 2 if j < len(langs) - 1 else 0
        col = lang_color(lang, t) if lang != "Other" else t["gray"]
        segs.append(f'<rect x="{lx:.1f}" y="366" width="{max(w - gap, 1):.1f}" height="8" fill="{col}"/>')
        lx += w
        short = LANG_SHORT.get(lang, lang)
        legend_parts.append(f"{short} {pct(share)}")
    body.append(f'<g clip-path="url(#bbar)">{"".join(segs)}</g>')
    body.append(
        f'<text x="210" y="393" class="mono mu" font-size="12">'
        f'{esc("  ·  ".join(legend_parts))}</text>'
    )

    body.append(
        f'<text x="32" y="426" class="mono mu" font-size="13">'
        f'pardus-nomad login: <tspan class="fg" font-weight="700">murat</tspan> (tty1)  ·  '
        f'<tspan class="hl">murat</tspan>@<tspan fill="{t["cyan"]}" font-weight="700">nomad</tspan>'
        f'<tspan fill="{t["blue"]}"> ~</tspan>&gt; <tspan class="tx">systemctl status {esc(spot_name)}</tspan> '
        f'<tspan class="cur" fill="{t["text"]}">█</tspan></text>'
    )

    return svg_doc(W, H, "Murat Boy — Linux Boot Sequence Profile", t, defs, body, css)


# ── 5. KONSEPT SVG: Distro Nomad Trail Map (Göçebe Haritası) ─────────────────
def svg_nomad(t: dict, ctx: dict) -> str:
    W, H = 1000, 436
    joined = parse_ts(ctx["user"]["created_at"])
    years, _ = tenure(joined)
    own = ctx["own"]
    stars = sum(r["stars"] for r in own)
    followers = ctx["user"]["followers"]
    spot = ctx["spotlight"]
    spot_name = spot["name"] if spot else "distronomad"
    spot_push = ago(parse_ts(spot["pushed_at"])) if spot else "today"
    langs = ctx["langs"]
    spot_lang = (spot.get("language") if spot else None) or "code"
    dart = sorted((r for r in own if r.get("language") == "Dart" and r is not spot),
                  key=lambda r: r["pushed_at"], reverse=True)
    flutter_end = parse_ts(dart[0]["pushed_at"]) if dart else joined
    flutter_sub = ellipsize("Flutter · " + " · ".join(r["name"] for r in dart[:2]), 158, 10.5, mono=True)

    defs = [
        f'<clipPath id="nwin"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
        f'<linearGradient id="trail" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{t["orange"]}"/>'
        f'<stop offset=".5" stop-color="{t["cyan"]}"/>'
        f'<stop offset="1" stop-color="{t["green"]}"/></linearGradient>',
        f'<clipPath id="nbar"><rect x="556" y="370" width="408" height="8" rx="4"/></clipPath>',
    ]
    css = (
        ".beacon{transform-box:fill-box;transform-origin:center;animation:bcn 2.2s ease-out infinite}"
        "@keyframes bcn{0%{opacity:.7;transform:scale(1)}100%{opacity:0;transform:scale(2.8)}}"
        ".lid{opacity:0;animation:lid 5s 1.5s infinite}"
        "@keyframes lid{0%,93%,100%{opacity:0}94%,97%{opacity:1}}"
        ".dash{stroke-dashoffset:400;animation:march 18s linear infinite}"
        "@keyframes march{to{stroke-dashoffset:0}}"
    )

    body = [
        f'<g clip-path="url(#nwin)">'
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="42" fill="{t["bar"]}"/>'
        f'<rect y="42" width="{W}" height="1" fill="{t["border"]}"/>'
        f'<ellipse cx="220" cy="190" rx="210" ry="95" fill="none" stroke="{t["border"]}" stroke-opacity=".28" stroke-dasharray="4 6"/>'
        f'<ellipse cx="520" cy="185" rx="260" ry="110" fill="none" stroke="{t["border"]}" stroke-opacity=".22" stroke-dasharray="3 5"/>'
        f'<ellipse cx="820" cy="165" rx="190" ry="90" fill="none" stroke="{t["border"]}" stroke-opacity=".32"/>'
        f'<ellipse cx="820" cy="165" rx="130" ry="60" fill="none" stroke="{t["border"]}" stroke-opacity=".25"/>'
        f'</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["border"]}"/>',
        f'<text x="28" y="26" class="mono fg" font-size="13.5" font-weight="700">'
        f'🧭 THE NOMAD ENGINEER\'S TRAIL  ·  MURAT BOY</text>',
        f'<text x="{W - 28}" y="26" text-anchor="end" class="mono mu" font-size="12.5">'
        f'2015 → {joined.year + years}  ·  '
        f'<tspan class="hl">{years} Years</tspan>  ·  {len(own)} Repos  ·  {stars} ★</text>',
    ]

    trail_d = (
        "M 96 238 C 175 190, 230 190, 300 205 "
        "C 375 220, 440 205, 510 175 "
        "C 565 150, 610 194, 658 194 "
        "C 710 194, 745 168, 790 158"
    )
    body.extend([
        f'<path d="{trail_d}" fill="none" stroke="url(#trail)" stroke-width="5" stroke-opacity=".25" stroke-linecap="round"/>',
        f'<path class="dash" d="{trail_d}" fill="none" stroke="url(#trail)" stroke-width="3" '
        f'stroke-dasharray="8 7" stroke-linecap="round"/>',
    ])

    waypoints = [
        (96, 238, "CAMP 01 · 2017", "Silicon & Assembly", "MIPS Assembly (11★)", "orange", -84),
        (300, 205, "CAMP 02 · 2018", "Bare Metal & C", "Data Structures · PIC16F", "yellow", 42),
        (510, 175, "CAMP 03 · 2021–22", "NLP & Simulation", "Python · CPU Sim · Quantum", "cyan", -80),
        (658, 194, f"CAMP 04 · 2022–{flutter_end:%y}", "Mobile Craft", flutter_sub, "blue", 46),
    ]
    for idx, (wx, wy, tag, title, sub, col_key, dy) in enumerate(waypoints):
        col = t[col_key]
        ly = wy + dy
        line_y2 = ly + 39 if dy < 0 else ly - 15
        body.append(
            f'<g class="in" style="animation-delay:{0.1 + idx * 0.1:.2f}s">'
            f'<line x1="{wx}" y1="{wy}" x2="{wx}" y2="{line_y2}" stroke="{col}" stroke-width="1.5" stroke-dasharray="2 2"/>'
            f'<circle cx="{wx}" cy="{wy}" r="8" fill="{t["bg"]}" stroke="{col}" stroke-width="3"/>'
            f'<circle cx="{wx}" cy="{wy}" r="3.5" fill="{col}"/>'
            f'<rect x="{wx - 82}" y="{ly - 15}" width="164" height="54" rx="7" fill="{t["bar"]}" stroke="{t["border"]}"/>'
            f'<text x="{wx}" y="{ly}" text-anchor="middle" class="mono" font-size="10.5" font-weight="700" '
            f'fill="{col}">{esc(tag)}</text>'
            f'<text x="{wx}" y="{ly + 16}" text-anchor="middle" class="sans fg" font-size="12.5" font-weight="700">'
            f'{esc(title)}</text>'
            f'<text x="{wx}" y="{ly + 31}" text-anchor="middle" class="mono mu" font-size="10.5">'
            f'{esc(sub)}</text>'
            f'</g>'
        )

    bx, by = 790, 158
    body.append(
        f'<circle class="beacon" cx="{bx}" cy="{by}" r="12" fill="{t["green"]}" opacity="0"/>'
        f'<circle cx="{bx}" cy="{by}" r="11" fill="{t["bg"]}" stroke="{t["green"]}" stroke-width="3.5"/>'
        f'<circle cx="{bx}" cy="{by}" r="5" fill="{t["green"]}"/>'
    )

    P = 5
    px, py = 838, 72
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
            pixels.append(
                f'<rect x="{px + start * P}" y="{py + r * P}" width="{(c - start) * P}" '
                f'height="{P}" fill="{pal[line[start]]}"/>'
            )
    lids = "".join(
        f'<rect x="{px + c * P}" y="{py + r * P}" width="{2 * P}" height="{2 * P}" fill="{pal["K"]}"/>'
        for r, c in EYES
    )
    body.extend([
        f'<ellipse cx="{px + 8 * P}" cy="{py + len(PENGUIN) * P + 3}" rx="{8 * P}" ry="3" '
        f'fill="{t["muted"]}" fill-opacity=".2"/>',
        f'<g shape-rendering="crispEdges">{"".join(pixels)}<g class="lid">{lids}</g></g>',
        f'<rect x="752" y="184" width="220" height="94" rx="9" fill="{t["bar"]}" '
        f'stroke="{t["green"]}" stroke-width="1.8"/>',
        f'<text x="766" y="205" class="mono hl" font-size="11" font-weight="700">'
        f'🏕️ BASECAMP · NOW BUILDING</text>',
        f'<text x="766" y="226" class="mono fg" font-size="15" font-weight="700">'
        f'{esc(ellipsize(spot_name, 192, 15, mono=True))}</text>',
        f'<text x="766" y="244" class="sans tx" font-size="11.5">'
        f'{esc(ellipsize(describe(spot, ctx["cfg"]) if spot else "Something new is on the way", 196, 11.5))}</text>',
        f'<text x="766" y="264" class="mono mu" font-size="11">'
        f'{esc(spot_lang)} · pushed {esc(spot_push)}</text>',
    ])

    fy = 326
    body.extend([
        f'<rect x="28" y="{fy}" width="{W - 56}" height="88" rx="9" fill="{t["bar"]}" stroke="{t["border"]}"/>',
        f'<text x="46" y="{fy + 26}" class="mono k" font-size="12">BACKPACK (SETUP &amp; STACK)</text>',
        f'<text x="46" y="{fy + 48}" class="mono tx" font-size="12">'
        f'OS: <tspan class="fg" font-weight="600">Pardus</tspan> · '
        f'Shell: <tspan class="fg" font-weight="600">fish</tspan> · '
        f'Editor: <tspan class="fg" font-weight="600">VS Code</tspan></text>',
        f'<text x="46" y="{fy + 70}" class="mono mu" font-size="11.5">'
        f'Stack: Dart &amp; Flutter · Python · C · MIPS Assembly  ·  {followers} followers</text>',
        f'<line x1="534" y1="{fy + 14}" x2="534" y2="{fy + 74}" stroke="{t["border"]}"/>',
        f'<text x="556" y="{fy + 26}" class="mono k" font-size="12">TRAIL LANGUAGE MIX</text>',
        f'<rect x="556" y="370" width="408" height="8" rx="4" fill="{t["border"]}" fill-opacity=".35"/>',
    ])
    lx = 556.0
    segs = []
    lparts = []
    for j, (lang, share) in enumerate(langs):
        w = 408 * share
        gap = 2 if j < len(langs) - 1 else 0
        col = lang_color(lang, t) if lang != "Other" else t["gray"]
        segs.append(f'<rect x="{lx:.1f}" y="370" width="{max(w - gap, 1):.1f}" height="8" fill="{col}"/>')
        lx += w
        lparts.append(f"{LANG_SHORT.get(lang, lang)} {pct(share)}")
    body.append(f'<g clip-path="url(#nbar)">{"".join(segs)}</g>')
    body.append(
        f'<text x="556" y="{fy + 70}" class="mono mu" font-size="11">'
        f'{esc(" · ".join(lparts[:5]))}</text>'
    )

    return svg_doc(W, H, "Murat Boy — Distro Nomad Trail Map Profile", t, defs, body, css)


# ── TÜM KONSEPTLER İÇİN TAM README ÜRETİCİSİ ────────────────────────────────
def build_concept_readmes(ctx: dict, versions: dict[str, str], sections: dict[str, str]) -> dict[str, str]:
    """5 konseptin her biri için tam GitHub README.md metnini döndürür."""
    login = ctx["user"]["login"]
    cfg = ctx["cfg"]
    branch = cfg["github"].get("branch", "main")
    base = f"https://raw.githubusercontent.com/{login}/{login}/{branch}/assets/"
    joined = parse_ts(ctx["user"]["created_at"])
    years, months = tenure(joined)
    own = ctx["own"]
    stars = sum(r["stars"] for r in own)
    followers = ctx["user"]["followers"]
    spot = ctx["spotlight"]
    spot_name = spot["name"] if spot else "distronomad"

    def picture(stem: str, alt: str, width: str = "100%") -> str:
        dark = f"{base}{stem}-dark.svg?v={versions[stem + '-dark']}"
        light = f"{base}{stem}-light.svg?v={versions[stem + '-light']}"
        return (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
            f'<source media="(prefers-color-scheme: light)" srcset="{light}">'
            f'<img alt="{esc(alt)}" src="{light}" width="{width}"></picture>'
        )

    skill_icons = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=py,c,dart,flutter,linux,arch,bash,git,githubactions,vscode&amp;theme=dark">
  <source media="(prefers-color-scheme: light)" srcset="https://skillicons.dev/icons?i=py,c,dart,flutter,linux,arch,bash,git,githubactions,vscode&amp;theme=light">
  <img alt="Python, C, Dart, Flutter, Linux, Arch Linux, Bash, Git, GitHub Actions, VS Code" src="https://skillicons.dev/icons?i=py,c,dart,flutter,linux,arch,bash,git,githubactions,vscode&amp;theme=light" height="40">
</picture>"""

    footer = f"""<div align="center">
<sub>This page maintains itself: a small Python script, run daily by GitHub Actions, redraws every card from live GitHub data.<br>
<a href="https://github.com/{login}/{login}">See how it works →</a></sub>
</div>"""

    # 1) TERMINAL (Mevcut)
    terminal_md = f"""<!-- auto:whoami -->

{sections["whoami"]}

<!-- /auto:whoami -->

<div align="center">

Hi, I'm **Murat** — a computer engineer who likes to understand machines all the way down,<br>
from assembly and microcontrollers to Linux tooling and offline-first Flutter apps.<br>
I live on Pardus, write about what I learn, and build the tools I wish existed — no ads, no accounts, no tracking.

<a href="https://plexuschoroideus.blogspot.com">✍️&nbsp;Blog</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}?tab=repositories">📦&nbsp;Repositories</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}/{spot_name}">🏕️&nbsp;{spot_name}</a>

<br>

{skill_icons}

</div>

### 🛠️ Now building

<!-- auto:spotlight -->

{sections["spotlight"]}

<!-- /auto:spotlight -->

### 📌 Selected work

<!-- auto:featured -->

{sections["featured"]}

<!-- /auto:featured -->

<details>
<summary><b>All projects</b> — every public repo, listed automatically</summary>
<br>

<!-- auto:projects -->

{sections["projects"]}

<!-- /auto:projects -->

</details>

### ✍️ Writing

Occasional notes (in Turkish) on processor simulation, quantum computing and dev setups — from my blog **[Sella Turcica](https://plexuschoroideus.blogspot.com)**:

<!-- auto:writing -->

{sections["writing"]}

<!-- /auto:writing -->

<br>

{footer}
"""

    # 2) MAN PAGE (MURAT(1))
    man_hero = f'<a href="https://github.com/{login}/{login}">{picture("man", "MURAT(1) — Linux Programmer Manual")}</a>'
    lang_summary = " · ".join(f"{LANG_SHORT.get(k, k)} ({pct(v)})" for k, v in ctx["langs"])
    man_files = []
    for r in sorted(own, key=lambda r: r["pushed_at"], reverse=True):
        lang = LANG_SHORT.get(r.get("language") or "", r.get("language") or "misc")
        star_b = f" [★ {r['stars']}]" if r["stars"] else ""
        yr = f"{parse_ts(r['pushed_at']):%Y}"
        man_files.append(
            f"- **`/repos/{r['name']}`** ({lang}, {yr}){star_b} — [{md_cell(describe(r, cfg))}]({r['html_url']})"
        )
    man_files_md = "\n".join(man_files)

    man_md = f"""<!-- auto:whoami -->

{man_hero}

<!-- /auto:whoami -->

```text
NAME
       murat — computer engineer, Linux toolmaker, low-level & mobile developer

SYNOPSIS
       murat [--os pardus] [--shell fish] [--editor vscode]
             [--stack python,dart,flutter,c,mips-asm]
             [--daemon {spot_name}] [--uptime "{years}y {months}m (since {joined:%b %Y})"]
```

#### `DESCRIPTION`
**Murat Boy** is a computer engineer who likes to understand machines all the way down — from **MIPS assembly** and **PIC microcontrollers** to **C data structures**, **Python CLI/TUI tooling**, and **Flutter** mobile apps. Lives on Linux, documents experiments on **[Sella Turcica](https://plexuschoroideus.blogspot.com)**, and builds the tools he wishes existed.

#### `ACTIVE DAEMON (--now-building)`

<!-- auto:spotlight -->

{sections["spotlight"]}

<!-- /auto:spotlight -->

#### `OPTIONS (ARCHITECTURE & STACK)`
* **`-l, --low-level`** — `MIPS Assembly` · `C` · `PIC Basic Pro` · Computer Organization · Multicore CPU & Interval Simulation
* **`-s, --systems`** — `Python` · `Pardus` · `fish` shell · `Bash` · `GitHub Actions`
* **`-m, --mobile`** — `Dart` · `Flutter` · Offline-first Android apps with no ads, accounts or tracking ([`bilge`](https://github.com/{login}/bilge), [`envanter`](https://github.com/{login}/envanter), [`seyir`](https://github.com/{login}/seyir))
* **`-d, --distribution`** — {lang_summary}

#### `SELECTED FILES (/home/murat/featured)`

<!-- auto:featured -->

{sections["featured"]}

<!-- /auto:featured -->

<details open>
<summary><b>FILES (/home/murat/repos/*)</b> — {len(own)} public repositories · {stars} stars · {followers} followers</summary>
<br>

{man_files_md}

</details>

#### `NOTES & PUBLICATIONS (/var/log/sella-turcica)`
Technical articles (in Turkish) on processor simulation, quantum computing, and engineering resources:

<!-- auto:writing -->

{sections["writing"]}

<!-- /auto:writing -->

#### `SEE ALSO`
[`distronomad(1)`](https://github.com/{login}/distronomad) · [`mibs-assembly(2)`](https://github.com/{login}/Bilgisayar-Organizasyonu_Mibs-Assembly-Ornekleri) · [`sella-turcica(7)`](https://plexuschoroideus.blogspot.com) · [`github-repos(1)`](https://github.com/{login}?tab=repositories)

{footer}
"""

    # 3) CPU PIPELINE (IF → ID → EX → MEM → WB)
    pipe_hero = f'<a href="https://github.com/{login}/{login}">{picture("pipeline", "Murat Boy — 5-Stage CPU Pipeline Profile")}</a>'
    pipeline_md = f"""<!-- auto:whoami -->

{pipe_hero}

<!-- /auto:whoami -->

<div align="center">

**Architecture-first software engineering:** from hardware registers, **MIPS assembly** and **multicore processor simulation**<br>
to **C data structures**, **Python Linux tooling** and **Flutter** mobile apps.

<a href="https://plexuschoroideus.blogspot.com">✍️&nbsp;Blog (Sella Turcica)</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}?tab=repositories">📦&nbsp;All Repositories</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}/{spot_name}">⚡&nbsp;Active Thread: {spot_name}</a>

<br>

{skill_icons}

</div>

### ⚡ Stage 3 (`EX`) — Currently Executing on the ALU

<!-- auto:spotlight -->

{sections["spotlight"]}

<!-- /auto:spotlight -->

### 🗄️ Stage 4 (`MEM`) — L1 Cache (Selected Work)

<!-- auto:featured -->

{sections["featured"]}

<!-- /auto:featured -->

<details>
<summary><b>Main Memory Map (`0x0000` – `0xFFFF`)</b> — all {len(own)} public repositories</summary>
<br>

<!-- auto:projects -->

{sections["projects"]}

<!-- /auto:projects -->

</details>

### 📡 Stage 5 (`WB`) — Write-Back Buffer (Writing)

Notes (in Turkish) on **Sniper multicore processor simulation**, **interval simulation**, **quantum computing** and developer setups from **[Sella Turcica](https://plexuschoroideus.blogspot.com)**:

<!-- auto:writing -->

{sections["writing"]}

<!-- /auto:writing -->

<br>

{footer}
"""

    # 4) LINUX BOOT ([  OK  ])
    boot_hero = f'<a href="https://github.com/{login}/{login}">{picture("boot", "Murat Boy — Linux Boot Sequence Profile")}</a>'
    boot_md = f"""<!-- auto:whoami -->

{boot_hero}

<!-- /auto:whoami -->

<div align="center">

**System online.** I'm **Murat** — a computer engineer living on **Pardus** (`fish` + VS Code),<br>
building tools across the stack from **MIPS assembly** and **C** to **Python CLI/TUI utilities** and **Flutter**.

<a href="https://plexuschoroideus.blogspot.com">✍️&nbsp;/var/log/blog</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}?tab=repositories">📦&nbsp;/usr/src/repos</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}/{spot_name}">🟢&nbsp;{spot_name}.service</a>

<br>

{skill_icons}

</div>

### 🟢 Active Unit — `{spot_name}.service`

<!-- auto:spotlight -->

{sections["spotlight"]}

<!-- /auto:spotlight -->

### 🧩 Loaded Kernel & User Modules — Selected Work

<!-- auto:featured -->

{sections["featured"]}

<!-- /auto:featured -->

<details>
<summary><b><code>/proc/repositories</code></b> — full table of public projects</summary>
<br>

<!-- auto:projects -->

{sections["projects"]}

<!-- /auto:projects -->

</details>

### 📜 `journalctl -u sella-turcica` — Recent Writing

Technical entries (in Turkish) on processor simulation, quantum computing and development environments:

<!-- auto:writing -->

{sections["writing"]}

<!-- /auto:writing -->

<br>

{footer}
"""

    # 5) NOMAD MAP (Göçebe Haritası)
    nomad_hero = f'<a href="https://github.com/{login}/{login}">{picture("nomad", "Murat Boy — Distro Nomad Trail Map Profile")}</a>'
    nomad_md = f"""<!-- auto:whoami -->

{nomad_hero}

<!-- /auto:whoami -->

<div align="center">

Hi, I'm **Murat** — a computer engineer exploring the full computing trail,<br>
from **2017 bare-metal assembly & microcontrollers** to **Linux tooling** on **Pardus** and **offline-first Flutter apps**.<br>
Pack light, automate your setup, and understand the machine underneath.

<a href="https://plexuschoroideus.blogspot.com">📓&nbsp;Field Notes (Blog)</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}?tab=repositories">🧭&nbsp;All Waypoints</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/{login}/{spot_name}">🏕️&nbsp;Basecamp: {spot_name}</a>

<br>

{skill_icons}

</div>

### 🏕️ Current Basecamp — Now Building

<!-- auto:spotlight -->

{sections["spotlight"]}

<!-- /auto:spotlight -->

### 🧭 Key Waypoints on the Trail — Selected Work

<!-- auto:featured -->

{sections["featured"]}

<!-- /auto:featured -->

<details>
<summary><b>Full Expedition Log</b> — every public repository since 2017</summary>
<br>

<!-- auto:projects -->

{sections["projects"]}

<!-- /auto:projects -->

</details>

### 📓 Field Notes — Writing ([Sella Turcica](https://plexuschoroideus.blogspot.com))

Occasional essays (in Turkish) on multicore CPU simulation, quantum computing and developer tooling:

<!-- auto:writing -->

{sections["writing"]}

<!-- /auto:writing -->

<br>

{footer}
"""

    return {
        "terminal": terminal_md,
        "man": man_md,
        "pipeline": pipeline_md,
        "boot": boot_md,
        "nomad": nomad_md,
    }
