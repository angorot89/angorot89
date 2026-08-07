#!/usr/bin/env python3
"""HUD section-header strips for the angorot89 profile.

Transparent background so they float on GitHub's page in either theme.
Large type only — these are rendered as images and must stay legible when a
1000px asset is scaled to a 375px phone.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

DARK = dict(name="dark", cyan="#2BE0FF", magenta="#FF3DCB", muted="#7C8DA8", rule="#20334D")
LIGHT = dict(name="light", cyan="#0077A6", magenta="#C4008F", muted="#5A6B86", rule="#B9C8DC")

SECTIONS = [
    ("now", "NOW", "STATUS · LIVE", "Now"),
    ("architecture", "ARCHITECTURE", "ISOMETRIC VIEW", "Architecture"),
    ("detections", "DETECTIONS", "06 OBJECTS", "Detections — selected projects"),
    ("stack", "STACK", "05 CLASSES", "Stack"),
    ("contact", "CONTACT", "OPEN CHANNEL", "Contact"),
]

TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 72" width="1000" height="72" role="img" aria-label="{alt}">
  <style>
    @keyframes blink {{ 0%,52% {{ opacity: 1; }} 53%,100% {{ opacity: .18; }} }}
    .cur {{ animation: blink 1.2s step-end infinite; }}
    @media (prefers-reduced-motion: reduce) {{ .cur {{ animation: none; }} }}
  </style>

  <text x="2" y="33" font-family="{mono}" font-size="22" fill="{muted}">&#9656;</text>
  <text x="34" y="34" font-family="{mono}" font-size="27" font-weight="700"
        fill="{cyan}" letter-spacing="4.5">{title}</text>
  <rect x="34" y="45" width="{ul}" height="3" fill="{magenta}"/>
  <rect class="cur" x="{curx}" y="16" width="10" height="21" fill="{magenta}" opacity="0.9"/>

  <text x="998" y="34" text-anchor="end" font-family="{mono}" font-size="12.5"
        fill="{muted}" letter-spacing="2.4">{meta}</text>

  <line x1="2" y1="64" x2="998" y2="64" stroke="{rule}" stroke-width="1"/>
  <path d="M2 56 L2 64 L14 64" fill="none" stroke="{cyan}" stroke-width="2"/>
  <path d="M998 56 L998 64 L986 64" fill="none" stroke="{cyan}" stroke-width="2"/>
  <g fill="{rule}">
    <rect x="120" y="60" width="1" height="4"/><rect x="200" y="60" width="1" height="4"/>
    <rect x="280" y="60" width="1" height="4"/><rect x="360" y="60" width="1" height="4"/>
    <rect x="440" y="60" width="1" height="4"/><rect x="520" y="60" width="1" height="4"/>
  </g>
</svg>
"""


def build(pal, key, title, meta, alt):
    # Title starts at a fixed x=34, so the ▸ marker's width can't shift it.
    # Monospace advance at 27px ≈ 16.2px; letter-spacing adds 4.5px after every
    # glyph, so visible ink ends one tracking-step short of the full advance.
    adv = 16.2 + 4.5
    ink = len(title) * adv - 4.5
    return TPL.format(
        mono=MONO, alt=alt, title=title, meta=meta,
        ul=round(ink), curx=round(34 + ink + 12), **pal
    )


for pal in (DARK, LIGHT):
    for key, title, meta, alt in SECTIONS:
        (OUT / f"sec-{key}-{pal['name']}.svg").write_text(
            build(pal, key, title, meta, alt), encoding="utf-8"
        )

print("wrote:")
for f in sorted(OUT.glob("sec-*.svg")):
    print(f"  {f.name}  ({f.stat().st_size} bytes)")
