#!/usr/bin/env python3
"""Generate the 'Detection HUD' profile artwork for github.com/angorot89.

The profile renders as a computer-vision inference pass: bounding boxes with
class labels and confidence scores, a sweeping scanline, and a locking reticle.
Both theme variants come from one template so they can never drift apart.
"""

import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)


# ────────────────────────────────────────────────────────── telemetry ──
# The HUD claims to be an instrument, so the readouts should not be props.
# Everything below is derived from the repository itself — no API token and
# no third-party service, which keeps the workflow to a single cron job.
def _git(*args, default=""):
    try:
        return subprocess.run(
            ["git", *args], cwd=HERE, capture_output=True, text=True, timeout=10
        ).stdout.strip() or default
    except Exception:
        return default


def telemetry():
    """One honest status line: build counter, commit count, age, timestamp."""
    counter = HERE / ".frame"
    try:
        n = int(counter.read_text().strip()) + 1
    except Exception:
        n = 1
    counter.write_text(f"{n}\n")

    commits = _git("rev-list", "--count", "HEAD", default="0")

    first = _git("log", "--reverse", "--format=%cI", "--max-parents=0")
    days = "0"
    if first:
        try:
            born = datetime.fromisoformat(first)
            days = str((datetime.now(timezone.utc) - born).days)
        except ValueError:
            pass

    # Date only, no clock time: a value that changed every run would force the
    # workflow to commit on every run, faking daily activity on the profile's
    # contribution graph. Weekly granularity keeps the readout honest.
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gap = "&#160;&#160;&#160;"
    return (f"frame {n:05d}{gap}commits {commits}{gap}uptime {days}d"
            f"{gap}built {built}")


# ─────────────────────────────────────────────────────────── palettes ──
DARK = dict(
    name="dark",
    bg0="#05070D", bg1="#0B1020",
    grid="#2BE0FF", grid_op="0.055",
    text="#EAF2FF", muted="#7C8DA8",
    hot="#FF3DCB",          # magenta — primary detection
    cool="#2BE0FF",         # cyan — instrumentation
    violet="#8B5CF6",
    chip_text="#05070D",
    chip_fill="#2BE0FF", chip_fill_op="0.07",
    chip_stroke_op="0.45", chip_label="#D6E6FA",
    glow_op="0.85", scan_op="0.22", ghost_op="0.46", ghost_lo="0.20",
    vig="#000000", vig_op="0.55",
    panel="#070B14",
)

LIGHT = dict(
    name="light",
    bg0="#F4F7FC", bg1="#E7EDF7",
    grid="#0B5FA5", grid_op="0.09",
    text="#0A1020", muted="#5A6B86",
    hot="#C4008F",
    cool="#0077A6",
    violet="#6D3BE4",
    chip_text="#FFFFFF",
    chip_fill="#0077A6", chip_fill_op="0.07",
    chip_stroke_op="0.40", chip_label="#12283F",
    glow_op="0.28", scan_op="0.14", ghost_op="0.50", ghost_lo="0.24",
    vig="#20334D", vig_op="0.14",
    panel="#FBFCFE",
)

# frame geometry
FX0, FY0, FX1, FY1 = 40, 44, 960, 316


# ──────────────────────────────────────────────── procedural helpers ──
def grid_lines():
    out = []
    for x in range(0, 1001, 40):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="360"/>')
    for y in range(0, 361, 40):
        out.append(f'<line x1="0" y1="{y}" x2="1000" y2="{y}"/>')
    return "\n      ".join(out)


def edge_ticks():
    """Ruler ticks along the inside of the frame's bottom and top edges."""
    out = []
    for i, x in enumerate(range(FX0 + 12, FX1 - 8, 22)):
        tall = i % 5 == 0
        h = 9 if tall else 5
        op = "0.55" if tall else "0.28"
        out.append(f'<line x1="{x}" y1="{FY1}" x2="{x}" y2="{FY1 - h}" opacity="{op}"/>')
        out.append(f'<line x1="{x}" y1="{FY0}" x2="{x}" y2="{FY0 + h}" opacity="{op}"/>')
    return "\n      ".join(out)


def corner(px, py, sx, sy, n):
    """One L-shaped bracket. sx/sy point the arms inward."""
    a = 30
    return (
        f'<g class="br" style="animation-delay:{n * 0.18:.2f}s">'
        f'<path d="M{px} {py + sy * a} L{px} {py} L{px + sx * a} {py}"/></g>'
    )


def ghosts(rnd):
    """Faint secondary detections, to sell the idea that this is a frame."""
    boxes = [(596, 74, 104, 58, "0.71"), (712, 226, 128, 62, "0.66"), (468, 246, 78, 44, "0.58")]
    out = []
    for i, (x, y, w, h, c) in enumerate(boxes):
        out.append(
            f'<g class="ghost" style="animation-delay:{i * 1.3:.1f}s">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
            f'stroke="$cool" stroke-width="1" stroke-dasharray="4 4"/>'
            f'<text x="{x + 3}" y="{y - 5}" class="tiny" fill="$cool">obj {c}</text>'
            f"</g>"
        )
    return "\n      ".join(out)


HERO = Template(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 360" width="1000" height="360" role="img" aria-labelledby="t d">
  <title id="t">Amine Amraoui — AI developer and full-stack engineer</title>
  <desc id="d">A computer-vision inference frame. A bounding box labelled "person 0.99" locks onto the name Amine Amraoui, with instrumentation readouts and a sweeping scanline.</desc>

  <defs>
    <linearGradient id="gBg" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="$bg1"/><stop offset="100%" stop-color="$bg0"/>
    </linearGradient>
    <linearGradient id="gScan" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="$cool" stop-opacity="0"/>
      <stop offset="50%" stop-color="$cool" stop-opacity="1"/>
      <stop offset="100%" stop-color="$cool" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="gVig" cx="0.5" cy="0.45" r="0.8">
      <stop offset="52%" stop-color="$vig" stop-opacity="0"/>
      <stop offset="100%" stop-color="$vig" stop-opacity="$vig_op"/>
    </radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <style>
    .mono { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace; }
    .sans { font-family: 'Helvetica Neue', Helvetica, Arial, system-ui, sans-serif; }
    .tiny { font-size: 9.5px; letter-spacing: 0.6px;
            font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace; }

    @keyframes sweep  { 0% { transform: translateY(0); opacity: 0; }
                        8% { opacity: 1; } 92% { opacity: 1; }
                        100% { transform: translateY(268px); opacity: 0; } }
    @keyframes lock   { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    @keyframes blink  { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }
    @keyframes spin   { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes fadein { 0%, 100% { opacity: $ghost_lo; } 50% { opacity: $ghost_op; } }
    @keyframes bar    { 0% { width: 0; } 70%, 100% { width: 96px; } }

    .scan  { animation: sweep 4.6s cubic-bezier(.4,0,.6,1) infinite; }
    .br    { animation: lock 2.8s ease-in-out infinite; }
    .rec   { animation: blink 1.1s step-end infinite; }
    .caret { animation: blink 1.05s step-end infinite; }
    .ret   { animation: spin 18s linear infinite; transform-box: fill-box; transform-origin: center; }
    .ghost { animation: fadein 7s ease-in-out infinite; opacity: $ghost_lo; }
    .fill  { animation: bar 4.6s ease-out infinite; }

    @media (prefers-reduced-motion: reduce) {
      .scan, .br, .rec, .caret, .ret, .ghost, .fill { animation: none; }
      .ghost { opacity: $ghost_op; }
      .scan  { opacity: 0; }
    }
  </style>

  <rect width="1000" height="360" fill="url(#gBg)"/>
  <g stroke="$grid" stroke-width="1" opacity="$grid_op">
      $gridlines
  </g>

  <!-- faint secondary detections -->
  <g>
      $ghosts
  </g>

  <!-- scanline, clipped to the frame -->
  <g class="scan">
    <rect x="$fx0" y="$fy0" width="920" height="2" fill="url(#gScan)" opacity="$scan_op" filter="url(#glow)"/>
  </g>

  <!-- primary bounding box -->
  <rect x="$fx0" y="$fy0" width="920" height="272" fill="none" stroke="$hot" stroke-width="1" opacity="0.22"/>
  <g stroke="$hot" stroke-width="2.6" fill="none" stroke-linecap="square" filter="url(#glow)" opacity="$glow_op">
      $corners
  </g>
  <g stroke="$cool" stroke-width="1">
      $ticks
  </g>

  <!-- class label -->
  <rect x="$fx0" y="20" width="126" height="20" fill="$hot"/>
  <text class="mono" x="48" y="34.5" font-size="11" font-weight="700" fill="$chip_text" letter-spacing="0.8">person 0.994</text>
  <rect x="$fx0" y="40" width="126" height="2" fill="$hot" opacity="0.35"/>
  <rect class="fill" x="$fx0" y="40" height="2" fill="$cool"/>

  <!-- REC -->
  <circle class="rec" cx="886" cy="30" r="4" fill="$hot"/>
  <text class="mono" x="898" y="34" font-size="10.5" fill="$muted" letter-spacing="1.4">REC</text>

  <!-- identity -->
  <text class="sans" x="84" y="166" font-size="52" font-weight="700" fill="$text" letter-spacing="2.4">AMINE AMRAOUI</text>
  <rect x="84" y="184" width="104" height="2.5" fill="$hot"/>
  <text class="mono" x="84" y="214" font-size="13" fill="$cool" letter-spacing="2.4">AI DEVELOPER &#183; FULL-STACK ENGINEER</text>
  <text class="mono" x="84" y="238" font-size="11.5" fill="$muted" letter-spacing="1.6">MOROCCO &#8594; CHINA &#160;&#183;&#160; AR / EN / FR / ZH</text>
  <rect class="caret" x="430" y="228" width="7" height="13" fill="$hot"/>

  <!-- instrumentation -->
  <g class="mono" font-size="11" letter-spacing="1.2" text-anchor="end">
    <text x="920" y="96"  fill="$muted">CLS &#160;&#160;&#160;<tspan fill="$cool">person</tspan></text>
    <text x="920" y="116" fill="$muted">CONF &#160;&#160;<tspan fill="$cool">0.994</tspan></text>
    <text x="920" y="136" fill="$muted">BBOX &#160;&#160;<tspan fill="$cool">920&#215;272</tspan></text>
    <text x="920" y="156" fill="$muted">MODEL &#160;<tspan fill="$cool">amraoui-v2</tspan></text>
  </g>

  <!-- reticle -->
  <g opacity="0.75">
    <g class="ret" fill="none" stroke="$cool" stroke-width="1.1">
      <circle cx="862" cy="232" r="27" stroke-dasharray="30 12" opacity="0.6"/>
      <circle cx="862" cy="232" r="19" stroke-dasharray="8 6" opacity="0.35"/>
    </g>
    <g stroke="$hot" stroke-width="1.3">
      <line x1="862" y1="210" x2="862" y2="222"/><line x1="862" y1="242" x2="862" y2="254"/>
      <line x1="840" y1="232" x2="852" y2="232"/><line x1="872" y1="232" x2="884" y2="232"/>
    </g>
    <circle cx="862" cy="232" r="2.2" fill="$hot"/>
  </g>

  <text class="tiny" x="$fx0" y="332" fill="$muted" opacity="0.75">$telemetry</text>

  <rect width="1000" height="360" fill="url(#gVig)"/>
</svg>
"""
)


# ─────────────────────────────────────────────────── stack panel ──
ROWS = [
    ("backend", ["Python", "Django", "DRF", "PostgreSQL", "MySQL", "Node.js"]),
    ("vision & ml", ["OpenCV", "TensorFlow", "face_recognition", "NumPy"]),
    ("language models", ["Claude API", "OpenAI API", "prompt design"]),
    ("front & mobile", ["TypeScript", "React", "Flutter", "Dart", "Bootstrap"]),
    ("the bench", ["Git", "Docker", "Linux", "Cloudflare", "Railway"]),
]
PH = 34 + len(ROWS) * 42 + 22

STACK = Template(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 $ph" width="1000" height="$ph" role="img" aria-labelledby="wt wd">
  <title id="wt">Stack</title>
  <desc id="wd">$alt</desc>
  <defs>
    <linearGradient id="pg" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="$bg1"/><stop offset="100%" stop-color="$bg0"/>
    </linearGradient>
  </defs>
  <style>
    .chip { fill: $chip_fill; fill-opacity: $chip_fill_op; stroke: $cool; stroke-opacity: $chip_stroke_op; stroke-width: 1; }
    .lbl  { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 13px; fill: $chip_label; }
    .grp  { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 11px; fill: $muted; letter-spacing: 2.2px; }
    .cf   { font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 10px; fill: $cool; opacity: .7; letter-spacing: 1px; }
  </style>

  <rect width="1000" height="$ph" fill="url(#pg)"/>
  <g stroke="$grid" stroke-width="1" opacity="$grid_op">$pgrid</g>
  <rect x="0.5" y="0.5" width="999" height="$phm" fill="none" stroke="$cool" stroke-opacity="0.25"/>
  <g stroke="$hot" stroke-width="2.2" fill="none" stroke-linecap="square" opacity="0.9">
    <path d="M2 22 L2 2 L22 2"/><path d="M978 2 L998 2 L998 22"/>
    <path d="M2 $phc L2 $phm L22 $phm"/><path d="M978 $phm L998 $phm L998 $phc"/>
  </g>
$rows
</svg>
"""
)


def build_rows():
    parts, y = [], 34
    for group, tools in ROWS:
        parts.append(f'  <text class="grp" x="30" y="{y + 20}">{escape(group.upper())}</text>')
        x = 214
        for t in tools:
            w = round(len(t) * 7.6 + 26)
            parts.append(
                f'  <rect class="chip" x="{x}" y="{y}" width="{w}" height="30" rx="4"/>'
                f'<text class="lbl" x="{x + 13}" y="{y + 20}">{escape(t)}</text>'
            )
            x += w + 10
        parts.append(f'  <text class="cf" x="970" y="{y + 20}" text-anchor="end">{len(tools):02d}</text>')
        y += 42
    return "\n".join(parts)


def panel_grid():
    out = []
    for x in range(0, 1001, 40):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{PH}"/>')
    for y in range(0, PH + 1, 40):
        out.append(f'<line x1="0" y1="{y}" x2="1000" y2="{y}"/>')
    return "".join(out)


ALT = ("Stack — backend: Python, Django, DRF, PostgreSQL, MySQL, Node.js. "
       "Vision and ML: OpenCV, TensorFlow, face_recognition, NumPy. "
       "Language models: Claude API, OpenAI API, prompt design. "
       "Front and mobile: TypeScript, React, Flutter, Dart, Bootstrap. "
       "The bench: Git, Docker, Linux, Cloudflare, Railway.")


# ────────────────────────────────────────────────────────────── build ──
TELEMETRY = telemetry()

for pal in (DARK, LIGHT):
    rnd = random.Random(11)
    corners = "".join(
        corner(*c, n) for n, c in enumerate(
            [(FX0, FY0, 1, 1), (FX1, FY0, -1, 1), (FX0, FY1, 1, -1), (FX1, FY1, -1, -1)])
    )
    hero = HERO.substitute(
        pal, fx0=FX0, fy0=FY0, telemetry=TELEMETRY,
        gridlines=grid_lines(),
        ticks=edge_ticks(),
        corners=corners,
        ghosts=Template(ghosts(rnd)).substitute(pal),
    )
    (OUT / f"hud-{pal['name']}.svg").write_text(hero, encoding="utf-8")

    stack = STACK.substitute(
        pal, ph=PH, phm=PH - 1, phc=PH - 21, alt=ALT,
        pgrid=panel_grid(), rows=build_rows(),
    )
    (OUT / f"stack-{pal['name']}.svg").write_text(stack, encoding="utf-8")

print("wrote:")
for f in sorted(OUT.iterdir()):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
