#!/usr/bin/env python3
"""Capability strip and detection cards for github.com/angorot89.

Colour carries information rather than decoration: cyan = vision,
magenta = platform, violet = AI systems, green = mobile.

Cards are one per row rather than a 2x3 grid. Text baked into an SVG does not
reflow, so a 1000px-wide asset shrinks to ~39% on a 390px phone; a full-width
row buys enough space to set the body at 18px, which survives that reduction
far better than the 14px the two-column layout allowed.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"

DARK = dict(
    name="dark", bg="#0B1020", text="#EAF2FF", muted="#8798B3", rule="#20334D",
    chipink="#05070D", tint="0.10",
    VISION="#2BE0FF", PLATFORM="#FF3DCB", LLM="#A97BFF", MOBILE="#3BE8A6",
)
LIGHT = dict(
    name="light", bg="#FFFFFF", text="#12283F", muted="#5A6B86", rule="#C9D6E6",
    chipink="#FFFFFF", tint="0.07",
    VISION="#0077A6", PLATFORM="#C4008F", LLM="#6B3FD4", MOBILE="#0A8F5E",
)

W, CH_, GAP = 1000, 176, 14
PAD = 30

CARDS = [
    ("01", "Vehicle Speed & Plate Recognition", "VISION",
     ["Tracks vehicles across frames to estimate speed, then pulls the plate out of a moving,",
      "badly-lit, rarely-cooperative image. Most of the work is the frames where it shouldn't fire."],
     "Python · OpenCV · TensorFlow"),
    ("02", "AI-Powered Enterprise OS", "PLATFORM",
     ["Orders, stock, staff, reporting — the system a company runs its day on, with an assistant",
      "living inside it that answers questions about the business rather than about the manual."],
     "Django · PostgreSQL · LLM APIs"),
    ("03", "Face Recognition Attendance", "VISION",
     ["Students enrol once and the system encodes their face; from then on a webcam handles",
      "check-in and check-out, writing timestamped rows organised by department and class."],
     "Django · OpenCV · face_recognition · NumPy"),
    ("04", "Virtual Hair Colour Try-On", "VISION",
     ["Segment the hair, keep the highlights, change the colour — and have it still look like hair",
      "rather than a paint bucket. Vision work where the acceptance test is the human eye."],
     "Python · OpenCV · image segmentation"),
    ("05", "Multilingual E-Commerce Platform", "PLATFORM",
     ["Catalogue, media, orders, and translations that hold up across languages — plus an admin",
      "the client can actually run without me."],
     "Django · PostgreSQL · i18n"),
    ("06", "Offline Recipe Keeper", "MOBILE",
     ["A Flutter app that works on a train with no signal. Local storage, a clean interface,",
      "nothing that phones home to be useful."],
     "Flutter · Dart · local storage"),
]


def card(y, idx, title, cls, lines, stack, p):
    c = p[cls]
    tagw = round(len(cls) * 8.4 + 24)
    return f"""  <g>
    <rect x="0" y="{y}" width="{W}" height="{CH_}" rx="3" fill="{p['bg']}"/>
    <rect x="0" y="{y}" width="{W}" height="{CH_}" rx="3" fill="{c}" opacity="{p['tint']}"/>
    <rect x="0" y="{y}" width="{W}" height="{CH_}" rx="3" fill="none" stroke="{c}" stroke-width="1" opacity="0.45"/>
    <rect x="0" y="{y}" width="5" height="{CH_}" rx="2.5" fill="{c}"/>
    <path d="M{PAD-14} {y+1} L1 {y+1} L1 {y+16}" fill="none" stroke="{c}" stroke-width="2"/>
    <path d="M{W-16} {y+CH_-1} L{W-1} {y+CH_-1} L{W-1} {y+CH_-16}" fill="none" stroke="{c}" stroke-width="2"/>

    <rect x="{PAD}" y="{y+22}" width="{tagw}" height="25" rx="2" fill="{c}"/>
    <text x="{PAD+12}" y="{y+39}" font-family="{MONO}" font-size="13" font-weight="700"
          fill="{p['chipink']}" letter-spacing="1.8">{cls}</text>
    <text x="{W-PAD}" y="{y+40}" text-anchor="end" font-family="{MONO}" font-size="16"
          fill="{c}" opacity="0.5" letter-spacing="1.4">{idx}</text>

    <text x="{PAD}" y="{y+84}" font-family="{SANS}" font-size="30" font-weight="700"
          fill="{p['text']}">{escape(title)}</text>

    <text x="{PAD}" y="{y+118}" font-family="{SANS}" font-size="18" fill="{p['muted']}">
      <tspan x="{PAD}" dy="0">{escape(lines[0])}</tspan>
      <tspan x="{PAD}" dy="25">{escape(lines[1])}</tspan>
    </text>

    <text x="{W-PAD}" y="{y+CH_-18}" text-anchor="end" font-family="{MONO}" font-size="15"
          fill="{c}" opacity="0.95">{escape(stack)}</text>
  </g>"""


def build_cards(p):
    H = len(CARDS) * CH_ + (len(CARDS) - 1) * GAP
    alt = " ".join(
        f"{i} {t} ({c}). {' '.join(l)} Built with {s}."
        for i, t, c, l, s in CARDS
    )
    body = [card(n * (CH_ + GAP), i, t, c, l, s, p)
            for n, (i, t, c, l, s) in enumerate(CARDS)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" aria-label="{escape(alt)}">\n'
            + "\n".join(body) + "\n</svg>\n")


# ───────────────────────────────────────────────── capability strip ──
CAPS = [
    ("AI SYSTEMS", "LLM", "assistants that answer", "about the business"),
    ("COMPUTER VISION", "VISION", "cameras that read", "what they are shown"),
    ("PLATFORMS", "PLATFORM", "the system a company", "runs its day on"),
]


def icon(kind, cx, cy, c):
    if kind == "LLM":
        return (f'<g stroke="{c}" stroke-width="2.4" fill="none">'
                f'<line x1="{cx-15}" y1="{cy+10}" x2="{cx}" y2="{cy-13}"/>'
                f'<line x1="{cx+15}" y1="{cy+10}" x2="{cx}" y2="{cy-13}"/>'
                f'<line x1="{cx-15}" y1="{cy+10}" x2="{cx+15}" y2="{cy+10}"/></g>'
                f'<circle cx="{cx}" cy="{cy-13}" r="5" fill="{c}"/>'
                f'<circle cx="{cx-15}" cy="{cy+10}" r="5" fill="{c}"/>'
                f'<circle cx="{cx+15}" cy="{cy+10}" r="5" fill="{c}"/>')
    if kind == "VISION":
        return (f'<path d="M{cx-19} {cy} q19 -15 38 0 q-19 15 -38 0z" fill="none" stroke="{c}" stroke-width="2.4"/>'
                f'<circle cx="{cx}" cy="{cy}" r="6" fill="{c}"/>'
                f'<g stroke="{c}" stroke-width="1.8" opacity="0.7">'
                f'<line x1="{cx}" y1="{cy-19}" x2="{cx}" y2="{cy-13}"/>'
                f'<line x1="{cx}" y1="{cy+13}" x2="{cx}" y2="{cy+19}"/></g>')
    return (f'<g fill="{c}">'
            f'<rect x="{cx-19}" y="{cy-16}" width="38" height="8" rx="2"/>'
            f'<rect x="{cx-19}" y="{cy-4}" width="38" height="8" rx="2" opacity="0.7"/>'
            f'<rect x="{cx-19}" y="{cy+8}" width="38" height="8" rx="2" opacity="0.42"/></g>')


def build_caps(p):
    H, G = 150, 24
    pw = (W - G * 2) / 3
    alt = " · ".join(f"{t}: {a} {b}" for t, _, a, b in CAPS)
    out = []
    for i, (title, kind, l1, l2) in enumerate(CAPS):
        x = i * (pw + G)
        c = p[kind]
        out.append(f"""  <g>
    <rect x="{x:.0f}" y="0" width="{pw:.0f}" height="{H}" rx="3" fill="{p['bg']}"/>
    <rect x="{x:.0f}" y="0" width="{pw:.0f}" height="{H}" rx="3" fill="{c}" opacity="{p['tint']}"/>
    <rect x="{x:.0f}" y="0" width="{pw:.0f}" height="{H}" rx="3" fill="none" stroke="{c}" stroke-width="1" opacity="0.45"/>
    <rect x="{x:.0f}" y="0" width="{pw:.0f}" height="4" rx="2" fill="{c}"/>
    {icon(kind, x + 48, 60, c)}
    <text x="{x+88:.0f}" y="58" font-family="{MONO}" font-size="17" font-weight="700"
          fill="{p['text']}" letter-spacing="1.6">{title}</text>
    <text x="{x+88:.0f}" y="86" font-family="{SANS}" font-size="15" fill="{p['muted']}">{escape(l1)}</text>
    <text x="{x+88:.0f}" y="108" font-family="{SANS}" font-size="15" fill="{p['muted']}">{escape(l2)}</text>
  </g>""")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" aria-label="{escape(alt)}">\n'
            + "\n".join(out) + "\n</svg>\n")


for pal in (DARK, LIGHT):
    (OUT / f"cards-{pal['name']}.svg").write_text(build_cards(pal), encoding="utf-8")
    (OUT / f"caps-{pal['name']}.svg").write_text(build_caps(pal), encoding="utf-8")

print("wrote:")
for f in sorted(list(OUT.glob("cards-*.svg")) + list(OUT.glob("caps-*.svg"))):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
