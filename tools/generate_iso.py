#!/usr/bin/env python3
"""Isometric architecture panel for github.com/angorot89.

The stack drawn as stacked planes in a 2:1 isometric projection — clients on
top, Django core in the middle, Postgres beneath, vision and language-model
services flanking it. Slabs drift on staggered CSS animations, which is the
only depth cue available: a README cannot run JavaScript, so there is no
scroll-driven or WebGL 3D to be had. This is honest fake depth.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

W, H = 1000, 470
CX = 500                      # projection origin
KX, KY = 1.0, 0.5             # 2:1 isometric ratio

DARK = dict(
    name="dark", bg0="#05070D", bg1="#0B1020", grid="#2BE0FF", grid_op="0.05",
    text="#EAF2FF", muted="#7C8DA8", edge="#EAF2FF", edge_op="0.16",
    cool="#2BE0FF", hot="#FF3DCB", violet="#A97BFF", green="#3BE8A6",
    top_op="0.30", side_op="0.16", face_op="0.10", beam_op="0.45",
)
LIGHT = dict(
    name="light", bg0="#F4F7FC", bg1="#E7EDF7", grid="#0B5FA5", grid_op="0.07",
    text="#12283F", muted="#5A6B86", edge="#12283F", edge_op="0.18",
    cool="#0077A6", hot="#C4008F", violet="#6B3FD4", green="#0A8F5E",
    top_op="0.26", side_op="0.14", face_op="0.09", beam_op="0.40",
)

# label, colour key, half-width, half-depth, y of the slab's top face, thickness
# Sub-labels sit at y+16, where the rhombus has already narrowed, so they are
# kept short enough to stay inside the top face at that height.
SLABS = [
    ("CLIENTS",      "violet", 150, 66,  96, 16, "react · flutter"),
    ("DJANGO CORE",  "hot",    210, 92, 214, 22, "models · views · drf"),
    ("POSTGRES",     "cool",   140, 62, 340, 16, "system of record"),
]
WING_HW, WING_HD = 84, 40
WINGS = [
    ("VISION", "cool",  -340, 232, "opencv · tensorflow"),
    ("LLM",    "green",  340, 232, "claude · openai"),
]


def face(cx, cy, hw, hd, t, c, p):
    """One slab: top rhombus plus two lit side faces."""
    top = f"{cx},{cy - hd*KY} {cx + hw*KX},{cy} {cx},{cy + hd*KY} {cx - hw*KX},{cy}"
    left = (f"{cx - hw*KX},{cy} {cx},{cy + hd*KY} {cx},{cy + hd*KY + t} "
            f"{cx - hw*KX},{cy + t}")
    right = (f"{cx + hw*KX},{cy} {cx},{cy + hd*KY} {cx},{cy + hd*KY + t} "
             f"{cx + hw*KX},{cy + t}")
    return (
        f'<polygon points="{left}"  fill="{c}" fill-opacity="{p["side_op"]}"/>'
        f'<polygon points="{right}" fill="{c}" fill-opacity="{p["face_op"]}"/>'
        f'<polygon points="{top}"   fill="{c}" fill-opacity="{p["top_op"]}"/>'
        f'<polygon points="{top}"   fill="none" stroke="{c}" stroke-width="1.5"/>'
        f'<polygon points="{left}"  fill="none" stroke="{c}" stroke-width="1" opacity="0.55"/>'
        f'<polygon points="{right}" fill="none" stroke="{c}" stroke-width="1" opacity="0.35"/>'
    )


def build(p):
    parts = []

    # connecting beams, drawn first so slabs sit on top of them
    beams = [(CX, 112, CX, 214), (CX, 236, CX, 340)]
    for x1, y1, x2, y2 in beams:
        parts.append(
            f'<line class="beam" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{p["cool"]}" stroke-width="2" stroke-dasharray="6 7" '
            f'opacity="{p["beam_op"]}"/>'
        )
    # Wing beams span only the gap between the wing's inner vertex and the core
    # slab's side vertex. Drawing them any longer would show through the core's
    # semi-transparent top face.
    core_hw = SLABS[1][2]
    for lbl, key, dx, y, _ in WINGS:
        inward = -WING_HW if dx > 0 else WING_HW
        x1 = CX + dx + inward
        x2 = CX + (core_hw if dx > 0 else -core_hw)
        parts.append(
            f'<line class="beam" x1="{x1}" y1="{y}" x2="{x2}" y2="{SLABS[1][4] + 2}" '
            f'stroke="{p[key]}" stroke-width="2" stroke-dasharray="5 7" '
            f'opacity="{p["beam_op"]}"/>'
        )

    # flanking service slabs
    for i, (lbl, key, dx, y, sub) in enumerate(WINGS):
        c = p[key]
        cx = CX + dx
        parts.append(f'<g class="drift d{i+3}">{face(cx, y, WING_HW, WING_HD, 14, c, p)}'
                     f'<text x="{cx}" y="{y + 5}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="13" font-weight="700" fill="{p["text"]}" letter-spacing="1.6">{lbl}</text>'
                     f'<text x="{cx}" y="{y + 52}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="10.5" fill="{p["muted"]}">{escape(sub)}</text></g>')

    # the three stacked planes
    for i, (lbl, key, hw, hd, y, t, sub) in enumerate(SLABS):
        c = p[key]
        parts.append(f'<g class="drift d{i}">{face(CX, y, hw, hd, t, c, p)}'
                     f'<text x="{CX}" y="{y - 2}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="16" font-weight="700" fill="{p["text"]}" letter-spacing="2.2">{lbl}</text>'
                     f'<text x="{CX}" y="{y + 16}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="10.5" fill="{p["muted"]}" letter-spacing="0.6">{escape(sub)}</text></g>')

    grid = "".join(
        f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H + 1, 40)
    ) + "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W + 1, 40)
    )

    alt = ("Isometric architecture: clients (React, Flutter, templates) above a "
           "Django core (models, views, DRF), with vision (OpenCV, TensorFlow) and "
           "language-model (Claude, OpenAI) services either side, over PostgreSQL "
           "as the system of record.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(alt)}">
  <defs>
    <linearGradient id="ig" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="{p['bg1']}"/><stop offset="100%" stop-color="{p['bg0']}"/>
    </linearGradient>
  </defs>
  <style>
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes pulse {{ 0%,100% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: -26; }} }}
    .drift {{ animation: float 7s ease-in-out infinite; }}
    .d0 {{ animation-delay: 0s; }}    .d1 {{ animation-delay: .9s; }}
    .d2 {{ animation-delay: 1.8s; }}  .d3 {{ animation-delay: .45s; }}
    .d4 {{ animation-delay: 1.35s; }}
    .beam {{ animation: pulse 1.6s linear infinite; }}
    @media (prefers-reduced-motion: reduce) {{
      .drift, .beam {{ animation: none; }}
    }}
  </style>

  <rect width="{W}" height="{H}" rx="4" fill="url(#ig)"/>
  <g stroke="{p['grid']}" stroke-width="1" opacity="{p['grid_op']}">{grid}</g>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="4" fill="none"
        stroke="{p['cool']}" stroke-opacity="0.25"/>
  <g stroke="{p['hot']}" stroke-width="2.2" fill="none" stroke-linecap="square" opacity="0.9">
    <path d="M2 24 L2 2 L24 2"/><path d="M{W-24} 2 L{W-2} 2 L{W-2} 24"/>
    <path d="M2 {H-24} L2 {H-2} L24 {H-2}"/><path d="M{W-24} {H-2} L{W-2} {H-2} L{W-2} {H-24}"/>
  </g>

  <text x="30" y="34" font-family="{MONO}" font-size="11"
        fill="{p['muted']}" letter-spacing="2.4">5 PLANES &#183; 2:1 PROJECTION</text>
  <text x="{W-30}" y="34" text-anchor="end" font-family="{MONO}" font-size="11"
        fill="{p['muted']}" letter-spacing="1.8">CLIENT &#8594; CORE &#8594; STORE</text>

{chr(10).join('  ' + s for s in parts)}
</svg>
"""


for pal in (DARK, LIGHT):
    (OUT / f"iso-{pal['name']}.svg").write_text(build(pal), encoding="utf-8")

print("wrote:")
for f in sorted(OUT.glob("iso-*.svg")):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
