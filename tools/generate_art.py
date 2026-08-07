#!/usr/bin/env python3
"""Generate the 'Night Desk' profile artwork: a hand-authored, animated,
theme-aware SVG pair (hero + workshop) for github.com/angorot89."""

import math
import random
from pathlib import Path
from string import Template
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────── palettes ──
DARK = dict(
    name="dark",
    wall_top="#13100C", wall_bot="#221A13",
    desk_top="#3A2A1C", desk_front="#241A11", desk_hi="#5E4630",
    sky_top="#0A111E", sky_bot="#17253C",
    frame="#2C211789", frame_solid="#2C2117", sill="#3A2A1C",
    moon="#F4E7C6", star="#CFE0F2",
    rain="#8FB6D8", rain_op="0.55",
    curtain="#39241C",
    text="#F3E6D2", muted="#9C8468", accent="#EBA85A",
    lamp="#2E2219", lamp_glow="#FFB65C", glow_op="0.50",
    monitor="#241B14", screen_top="#173230", screen_bot="#0F2321",
    code="#74D6C2",
    mug="#C56C4B", steam="#E9DAC2", steam_op="0.50",
    cat="#2E2117", cat_rim="#FFC078", cat_eye="#5E4732",
    books=("#8C4A3C", "#4F6B57", "#A87C3E"),
    plant="#4C6B4A", pot="#8A5236",
    wire="#3A2C20", bulb="#FFC978",
    vignette="#000000", vig_op="0.55",
    dust_op="0.30",
    frame_art="#2E2219", frame_mat="#1C1510",
)

LIGHT = dict(
    name="light",
    wall_top="#F8F0E3", wall_bot="#EBDCC7",
    desk_top="#CE9F71", desk_front="#B0824F", desk_hi="#EAC79C",
    sky_top="#AFCCE6", sky_bot="#F0D6B4",
    frame="#A9805889", frame_solid="#A98058", sill="#BE8E60",
    moon="#FFD9A0", star="#FFFFFF",
    rain="#7FA6CC", rain_op="0.45",
    curtain="#D9B492",
    text="#2B1D12", muted="#7C6647", accent="#B96C1B",
    lamp="#8A6440", lamp_glow="#FFC163", glow_op="0.42",
    monitor="#8A6845", screen_top="#DCEEE9", screen_bot="#C2DED8",
    code="#2C7C6E",
    mug="#B3573A", steam="#BFA98D", steam_op="0.65",
    cat="#4B3526", cat_rim="#FFD9A0", cat_eye="#8A6A4E",
    books=("#A85C46", "#5E7D63", "#C09246"),
    plant="#5D8055", pot="#9E6039",
    wire="#B29273", bulb="#FFB13D",
    vignette="#6B4A2A", vig_op="0.22",
    dust_op="0.38",
    frame_art="#B08A63", frame_mat="#E4D3BB",
)


# ──────────────────────────────────────────────── procedural helpers ──
def wire_path():
    pts = []
    for x in range(0, 1001, 10):
        y = 5 + 30 * math.sin(math.pi * x / 1000)
        pts.append(f"{x},{y:.1f}")
    return " ".join(pts)


def fairy_bulbs(rnd):
    out, x = [], 42
    while x < 1000:
        y = 5 + 30 * math.sin(math.pi * x / 1000)
        dur = round(rnd.uniform(2.6, 5.2), 2)
        delay = round(rnd.uniform(-5, 0), 2)
        out.append(
            f'<g class="bulb" style="animation-duration:{dur}s;animation-delay:{delay}s">'
            f'<line x1="{x}" y1="{y:.1f}" x2="{x}" y2="{y + 8:.1f}" stroke="$wire" stroke-width="1.3"/>'
            f'<circle cx="{x}" cy="{y + 12.5:.1f}" r="10" fill="$bulb" opacity="0.18" filter="url(#soft)"/>'
            f'<circle cx="{x}" cy="{y + 12.5:.1f}" r="3.2" fill="$bulb"/>'
            f"</g>"
        )
        x += 62
    return "\n      ".join(out)


def raindrops(rnd):
    out = []
    for _ in range(52):
        x = rnd.uniform(715, 965)
        dur = round(rnd.uniform(0.55, 1.05), 2)
        delay = round(rnd.uniform(-1.4, 0), 2)
        ln = rnd.uniform(9, 21)
        op = round(rnd.uniform(0.3, 1.0), 2)
        out.append(
            f'<line class="drop" x1="{x:.0f}" y1="0" x2="{x - 4:.0f}" y2="{ln:.0f}" '
            f'stroke="$rain" stroke-width="1.15" stroke-linecap="round" opacity="{op}" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
        )
    return "\n        ".join(out)


def stars(rnd):
    out = []
    for _ in range(16):
        x, y = rnd.uniform(732, 938), rnd.uniform(52, 150)
        r = round(rnd.uniform(0.6, 1.5), 1)
        dur = round(rnd.uniform(2.5, 6.0), 1)
        delay = round(rnd.uniform(-6, 0), 1)
        out.append(
            f'<circle class="star" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="$star" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
        )
    return "\n        ".join(out)


def dust(rnd):
    out = []
    for _ in range(16):
        x, y = rnd.uniform(320, 580), rnd.uniform(205, 300)
        r = round(rnd.uniform(0.8, 2.0), 1)
        dur = round(rnd.uniform(7, 14), 1)
        delay = round(rnd.uniform(-14, 0), 1)
        out.append(
            f'<circle class="mote" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="$lamp_glow" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
        )
    return "\n      ".join(out)


def code_lines(rnd):
    out, y = [], 170
    for i, w in enumerate((118, 84, 148, 62, 106, 132)):
        indent = 456 + (14 if i in (1, 3) else 0)
        dur = round(rnd.uniform(3.2, 6.5), 1)
        delay = round(rnd.uniform(-6, 0), 1)
        out.append(
            f'<rect class="cl" x="{indent}" y="{y}" width="{w}" height="5" rx="2.5" fill="$code" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
        )
        y += 14
    out.append(f'<rect class="caret" x="470" y="{y}" width="9" height="7" rx="1.5" fill="$code"/>')
    return "\n        ".join(out)


# ─────────────────────────────────────────────────────── hero template ──
HERO = Template(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 360" width="1000" height="360" role="img" aria-labelledby="t d">
  <title id="t">Amine Amraoui</title>
  <desc id="d">A desk at night: rain on the window, a lamp burning low, code on the screen, and a cat asleep on the wood.</desc>

  <defs>
    <linearGradient id="gWall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$wall_top"/><stop offset="100%" stop-color="$wall_bot"/>
    </linearGradient>
    <linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$sky_top"/><stop offset="100%" stop-color="$sky_bot"/>
    </linearGradient>
    <linearGradient id="gDesk" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$desk_top"/><stop offset="100%" stop-color="$desk_front"/>
    </linearGradient>
    <linearGradient id="gScreen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$screen_top"/><stop offset="100%" stop-color="$screen_bot"/>
    </linearGradient>
    <linearGradient id="gCone" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="$lamp_glow" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="$lamp_glow" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="$lamp_glow" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="gHalo"><stop offset="0%" stop-color="$lamp_glow" stop-opacity="0.75"/><stop offset="100%" stop-color="$lamp_glow" stop-opacity="0"/></radialGradient>
    <radialGradient id="gMoon"><stop offset="0%" stop-color="$moon" stop-opacity="0.55"/><stop offset="100%" stop-color="$moon" stop-opacity="0"/></radialGradient>
    <radialGradient id="gScreenGlow"><stop offset="0%" stop-color="$code" stop-opacity="0.30"/><stop offset="100%" stop-color="$code" stop-opacity="0"/></radialGradient>
    <radialGradient id="gVig" cx="0.5" cy="0.45" r="0.78">
      <stop offset="55%" stop-color="$vignette" stop-opacity="0"/>
      <stop offset="100%" stop-color="$vignette" stop-opacity="$vig_op"/>
    </radialGradient>

    <clipPath id="winClip"><rect x="729" y="49" width="212" height="182" rx="3"/></clipPath>
    <filter id="soft" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="softer" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="12"/></filter>
  </defs>

  <style>
    @keyframes fall   { from { transform: translate(7px, -44px); } to { transform: translate(-15px, 252px); } }
    @keyframes twinkl { 0%,100% { opacity: .18; } 50% { opacity: .95; } }
    @keyframes glim   { 0%,100% { opacity: .30; } 50% { opacity: 1; } }
    @keyframes flick  { 0%,100% { opacity: 1; } 41% { opacity: .93; } 44% { opacity: .74; } 47% { opacity: .97; }
                        62% { opacity: .82; } 65% { opacity: .99; } 84% { opacity: .88; } }
    @keyframes steam  { 0%   { opacity: 0; transform: translate(0,0) scale(1); }
                        22%  { opacity: $steam_op; }
                        100% { opacity: 0; transform: translate(-7px,-42px) scale(1.5); } }
    @keyframes breath { 0%,100% { transform: scaleY(1); } 50% { transform: scaleY(1.035); } }
    @keyframes drift  { 0%   { opacity: 0; transform: translate(0,0); }
                        25%  { opacity: $dust_op; }
                        100% { opacity: 0; transform: translate(16px,-52px); } }
    @keyframes blink  { 0%,48% { opacity: 1; } 49%,100% { opacity: 0; } }

    .drop  { animation-name: fall;   animation-timing-function: linear;    animation-iteration-count: infinite; }
    .star  { animation-name: twinkl; animation-timing-function: ease-in-out; animation-iteration-count: infinite; }
    .bulb  { animation-name: twinkl; animation-timing-function: ease-in-out; animation-iteration-count: infinite; }
    .cl    { animation-name: glim;   animation-timing-function: ease-in-out; animation-iteration-count: infinite; opacity: .55; }
    .lamp  { animation: flick 7s ease-in-out infinite; }
    .mote  { animation-name: drift;  animation-timing-function: ease-in-out; animation-iteration-count: infinite; opacity: 0;
             transform-box: fill-box; transform-origin: center; }
    .stm   { animation: steam 5.5s ease-out infinite; transform-box: fill-box; transform-origin: center bottom; opacity: 0; }
    .cat   { animation: breath 4.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center bottom; }
    .caret { animation: blink 1.15s step-end infinite; }
    .tcaret{ animation: blink 1.15s step-end infinite; }

    @media (prefers-reduced-motion: reduce) {
      .drop, .star, .bulb, .cl, .lamp, .mote, .stm, .cat, .caret, .tcaret { animation: none; }
      .mote, .stm { opacity: .25; }
      .cl { opacity: .7; }
    }
  </style>

  <!-- ─── room ─── -->
  <rect width="1000" height="360" fill="url(#gWall)"/>

  <!-- ─── fairy lights ─── -->
  <g>
    <polyline points="$wire_pts" fill="none" stroke="$wire" stroke-width="1.6"/>
      $bulbs
  </g>

  <!-- ─── window ─── -->
  <g>
    <rect x="720" y="40" width="230" height="200" rx="4" fill="$frame_solid"/>
    <rect x="729" y="49" width="212" height="182" rx="3" fill="url(#gSky)"/>
    <g clip-path="url(#winClip)">
      <circle cx="902" cy="82" r="34" fill="url(#gMoon)"/>
      <circle cx="902" cy="82" r="14" fill="$moon"/>
      <circle cx="896" cy="77" r="14" fill="url(#gSky)" opacity="0.55"/>
        $stars
      <path d="M729 196 L 772 168 L 812 192 L 856 158 L 900 188 L 941 168 L 941 231 L 729 231 Z"
            fill="$vignette" opacity="0.28"/>
        $rain
    </g>
    <rect x="833" y="49" width="5" height="182" fill="$frame_solid"/>
    <rect x="729" y="138" width="212" height="5" fill="$frame_solid"/>
    <rect x="708" y="236" width="254" height="11" rx="3" fill="$sill"/>
    <!-- curtain -->
    <path d="M700 34 C 716 96 706 172 720 240 L 700 240 Z" fill="$curtain" opacity="0.92"/>
    <path d="M962 34 C 950 96 960 172 948 240 L 968 240 Z" fill="$curtain" opacity="0.72"/>
    <!-- plant on the sill -->
    <g>
      <path d="M756 236 L 760 210 L 786 210 L 790 236 Z" fill="$pot"/>
      <path d="M773 210 C 773 190 762 182 752 178 C 760 192 762 200 766 210 Z" fill="$plant"/>
      <path d="M773 210 C 773 186 784 176 796 172 C 788 188 784 198 780 210 Z" fill="$plant" opacity="0.85"/>
      <path d="M773 210 C 770 196 771 186 773 176 C 777 188 777 200 776 210 Z" fill="$plant" opacity="0.7"/>
    </g>
  </g>

  <!-- ─── framed picture ─── -->
  <g>
    <rect x="618" y="72" width="54" height="46" rx="2" fill="$frame_art"/>
    <rect x="623" y="77" width="44" height="36" rx="1" fill="$frame_mat"/>
    <path d="M623 113 L 637 94 L 647 104 L 657 88 L 667 113 Z" fill="$accent" opacity="0.45"/>
    <circle cx="632" cy="86" r="3.4" fill="$accent" opacity="0.6"/>
  </g>

  <!-- ─── name ─── -->
  <g>
    <text x="70" y="118" font-family="Georgia, 'Iowan Old Style', 'Palatino Linotype', Palatino, 'Times New Roman', serif"
          font-size="50" fill="$text" letter-spacing="0.4">Amine Amraoui</text>
    <text x="73" y="150" font-family="ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
          font-size="12" fill="$muted" letter-spacing="2.2">AI DEVELOPER &amp; FULL-STACK ENGINEER</text>
    <text x="73" y="172" font-family="ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
          font-size="12" fill="$muted" letter-spacing="1.5" opacity="0.82">COMPUTER VISION · AUTOMATION · DJANGO</text>
    <line x1="73" y1="192" x2="133" y2="192" stroke="$accent" stroke-width="2" stroke-linecap="round"/>
    <text x="73" y="224" font-family="Georgia, 'Iowan Old Style', Palatino, serif" font-size="16.5"
          font-style="italic" fill="$muted">building quiet, useful software</text>
    <rect class="tcaret" x="308" y="212" width="8" height="15" fill="$accent" opacity="0.85"/>
  </g>

  <!-- ─── desk ─── -->
  <rect x="0" y="296" width="1000" height="64" fill="url(#gDesk)"/>
  <rect x="0" y="296" width="1000" height="2.5" fill="$desk_hi" opacity="0.55"/>
  <g opacity="0.11" stroke="$desk_hi" stroke-width="1.2" stroke-linecap="round" fill="none">
    <path d="M40 316 q 180 -3 360 0 t 380 2"/>
    <path d="M120 334 q 220 4 420 -2 t 400 1"/>
    <path d="M0 350 q 260 -4 520 1 t 480 -2"/>
  </g>

  <!-- ─── lamp ─── -->
  <g class="lamp">
    <path d="M398 176 L 432 190 L 588 296 L 322 296 Z" fill="url(#gCone)" filter="url(#soft)"/>
    <ellipse cx="418" cy="182" rx="70" ry="52" fill="url(#gHalo)" opacity="$glow_op" filter="url(#softer)"/>
  </g>
  <g>
    <ellipse cx="370" cy="294" rx="31" ry="7" fill="$lamp"/>
    <rect x="367" y="198" width="6" height="96" rx="3" fill="$lamp"/>
    <line x1="370" y1="200" x2="416" y2="170" stroke="$lamp" stroke-width="6" stroke-linecap="round"/>
    <path d="M400 148 L 442 164 L 430 192 L 394 174 Z" fill="$lamp"/>
    <path d="M394 174 L 430 192 L 428 196 L 396 179 Z" fill="$lamp_glow" opacity="0.85"/>
  </g>
    $dust

  <!-- ─── monitor ─── -->
  <g>
    <ellipse cx="535" cy="270" rx="150" ry="86" fill="url(#gScreenGlow)" filter="url(#softer)"/>
    <rect x="522" y="286" width="26" height="12" fill="$monitor"/>
    <ellipse cx="535" cy="297" rx="40" ry="6" fill="$monitor"/>
    <rect x="430" y="140" width="210" height="150" rx="9" fill="$monitor"/>
    <rect x="442" y="152" width="186" height="118" rx="4" fill="url(#gScreen)"/>
        $codeblk
    <rect x="442" y="152" width="186" height="118" rx="4" fill="$star" opacity="0.05"/>
  </g>

  <!-- ─── mug ─── -->
  <g>
    <path class="stm" d="M668 262 C 660 246 676 240 668 224" fill="none" stroke="$steam" stroke-width="2.6" stroke-linecap="round" style="animation-delay:0s"/>
    <path class="stm" d="M681 262 C 673 244 689 236 681 218" fill="none" stroke="$steam" stroke-width="2.6" stroke-linecap="round" style="animation-delay:1.7s"/>
    <path class="stm" d="M694 262 C 686 246 702 240 694 226" fill="none" stroke="$steam" stroke-width="2.6" stroke-linecap="round" style="animation-delay:3.3s"/>
    <path d="M699 270 C 712 271 714 286 700 288" fill="none" stroke="$mug" stroke-width="6" stroke-linecap="round"/>
    <path d="M657 264 L 661 291 C 661.5 294.5 664 296 667 296 L 693 296 C 696 296 698.5 294.5 699 291 L 703 264 Z" fill="$mug"/>
    <ellipse cx="680" cy="264" rx="23" ry="5" fill="$mug" opacity="0.55"/>
    <ellipse cx="680" cy="264" rx="19" ry="4" fill="$vignette" opacity="0.35"/>
  </g>

  <!-- ─── stack of books ─── -->
  <g>
    <rect x="252" y="282" width="66" height="14" rx="2" fill="$b0"/>
    <rect x="257" y="269" width="58" height="13" rx="2" fill="$b1"/>
    <rect x="254" y="257" width="62" height="12" rx="2" fill="$b2" transform="rotate(-2.2 285 263)"/>
    <line x1="252" y1="289" x2="318" y2="289" stroke="$vignette" stroke-width="1" opacity="0.25"/>
  </g>

  <!-- ─── sleeping cat (lamp is to her right, so the rim light falls on that edge) ─── -->
  <g class="cat">
    <path d="M234 296 C 246 288 249 272 238 265 C 230 261 223 267 226 274" fill="none" stroke="$cat" stroke-width="7" stroke-linecap="round"/>
    <path d="M124 296 C 122 262 146 244 178 244 C 212 244 238 262 238 296 Z" fill="$cat"/>
    <path d="M139 250 L 135 236 L 150 245 Z" fill="$cat"/>
    <path d="M165 245 L 180 236 L 176 250 Z" fill="$cat"/>
    <circle cx="152" cy="264" r="19" fill="$cat"/>
    <path d="M178 244 C 212 244 238 262 238 296" fill="none" stroke="$cat_rim" stroke-width="2.2" opacity="0.55" stroke-linecap="round"/>
    <path d="M176 240 L 176 250" fill="none" stroke="$cat_rim" stroke-width="1.8" opacity="0.5" stroke-linecap="round"/>
    <path d="M144 265 q 5 4.5 10 0" fill="none" stroke="$cat_eye" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M160 265 q 5 4.5 10 0" fill="none" stroke="$cat_eye" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M150 276 q 4 3 8 0" fill="none" stroke="$cat_eye" stroke-width="1.5" opacity="0.7" stroke-linecap="round"/>
  </g>

  <rect width="1000" height="360" fill="url(#gVig)"/>
</svg>
"""
)


# ─────────────────────────────────────────────────── workshop template ──
ROWS = [
    ("backend", ["Python", "Django", "DRF", "PostgreSQL", "MySQL", "Node.js"]),
    ("vision & ml", ["OpenCV", "TensorFlow", "face_recognition", "NumPy"]),
    ("language models", ["Claude API", "OpenAI API", "prompt design"]),
    ("front & mobile", ["TypeScript", "React", "Flutter", "Dart", "Bootstrap"]),
    ("the bench", ["Git", "Docker", "Linux", "Cloudflare", "Railway"]),
]

WORKSHOP = Template(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 272" width="1000" height="272" role="img" aria-labelledby="wt wd">
  <title id="wt">The workshop</title>
  <desc id="wd">Tools Amine works with, grouped by backend, vision, language models, and general bench tools.</desc>
  <defs>
    <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$wall_top"/><stop offset="100%" stop-color="$wall_bot"/>
    </linearGradient>
    <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="$muted" opacity="0.16"/>
    </pattern>
  </defs>
  <style>
    .chip { fill: $chipbg; stroke: $chipbd; stroke-width: 1; }
    .lbl  { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; fill: $text; }
    .grp  { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace; font-size: 11px;
            fill: $muted; letter-spacing: 2.2px; text-transform: uppercase; }
  </style>

  <rect width="1000" height="272" rx="10" fill="url(#wg)"/>
  <rect width="1000" height="272" rx="10" fill="url(#dots)"/>
  <rect x="0.5" y="0.5" width="999" height="271" rx="10" fill="none" stroke="$chipbd" stroke-width="1"/>

$rows
</svg>
"""
)


def build_workshop(pal):
    parts, y = [], 40
    for group, tools in ROWS:
        parts.append(f'  <text class="grp" x="34" y="{y + 20}">{escape(group)}</text>')
        parts.append(
            f'  <rect x="34" y="{y + 4}" width="2.5" height="22" rx="1.25" fill="$accent" opacity="0.0"/>'
        )
        x = 214
        for t in tools:
            w = round(len(t) * 7.6 + 26)
            parts.append(
                f'  <rect class="chip" x="{x}" y="{y}" width="{w}" height="30" rx="15"/>'
                f'<text class="lbl" x="{x + 13}" y="{y + 20}">{escape(t)}</text>'
            )
            x += w + 10
        y += 42
    return "\n".join(parts)


# ────────────────────────────────────────────────────────────── build ──
for pal in (DARK, LIGHT):
    rnd = random.Random(11)
    p = dict(pal)
    p["b0"], p["b1"], p["b2"] = pal["books"]
    p["chipbg"] = pal["wall_top"] if pal["name"] == "light" else "#00000033"
    p["chipbd"] = pal["muted"] + "55"

    hero = HERO.substitute(
        p,
        wire_pts=wire_path(),
        bulbs=Template(fairy_bulbs(rnd)).substitute(p),
        stars=Template(stars(rnd)).substitute(p),
        rain=Template(raindrops(rnd)).substitute(p),
        dust=Template(dust(rnd)).substitute(p),
        codeblk=Template(code_lines(rnd)).substitute(p),
    )
    (OUT / f"night-desk-{pal['name']}.svg").write_text(hero, encoding="utf-8")

    shop = WORKSHOP.substitute(p, rows=Template(build_workshop(p)).substitute(p))
    (OUT / f"workshop-{pal['name']}.svg").write_text(shop, encoding="utf-8")

print("wrote:")
for f in sorted(OUT.iterdir()):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
