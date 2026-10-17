"""Shared palette and SVG helpers for the profile README graphics (stdlib only)."""
import os
import textwrap
from xml.sax.saxutils import escape

# ---------- blue gradient palette ----------
BG0, BG1, BG2 = "#060a17", "#0b1226", "#12204a"
LINE = "#1e2d5a"
SKY, AZURE, BLUE, CYAN, INDIGO, ICE = "#7dd3fc", "#38bdf8", "#60a5fa", "#22d3ee", "#818cf8", "#dbeafe"
TEXT, MUTED, DIM = "#eef4ff", "#a9b8d6", "#5f6f8f"
GRAD = ["#e0f2fe", SKY, AZURE, "#6366f1"]          # headline gradient
RING = [CYAN, AZURE, "#6366f1"]                      # accent gradient
ACCENTS = [INDIGO, AZURE, CYAN, BLUE]                # card accents, cycled

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'Cascadia Code', Consolas, 'Liberation Mono', monospace"
EASE = "cubic-bezier(.22,1,.36,1)"  # soft ease-out, no overshoot

REDUCED = """
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; }
}"""


def stops(colors, opacity=None):
    n = len(colors) - 1
    op = f' stop-opacity="{opacity}"' if opacity is not None else ""
    return "".join(f'<stop offset="{i / n:.2f}" stop-color="{c}"{op}/>' for i, c in enumerate(colors))


def svg(w, h, style, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title, {chr(34): "&quot;"})}">\n<title>{escape(title)}</title>\n'
            f'<style>{style}{REDUCED}</style>\n{body}\n</svg>\n')


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"{os.path.basename(path):34} {len(content.encode()) / 1024:6.1f} KB")


def tw(text, size, mono=False):
    """Rough text width estimate (no font metrics inside an <img> SVG)."""
    return len(text) * size * (0.6 if mono else 0.5)


def wrap(text, width=56, lines=3):
    out = textwrap.wrap(" ".join(text.split()), width)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: width - 1].rstrip(" ,.;:—-") + "…"
    return out


# =====================================================================================
# project card — used for the hand-picked featured cards and the auto-generated ones
# =====================================================================================
def card(title, tag, desc_lines, stack, accent, emoji="✨", number="", live=False, badge=None):
    W, H = 580, 282
    a = accent
    chips, x = [], 32
    for t in stack:
        w = tw(t, 13) + 24
        if x + w > W - 32:
            break
        chips.append(f'<rect x="{x}" y="184" width="{w:.0f}" height="28" rx="14" fill="{a}" fill-opacity=".1" stroke="{a}" stroke-opacity=".35"/>'
                     f'<text x="{x + w / 2:.0f}" y="203" font-family="{SANS}" font-size="13" fill="{TEXT}" text-anchor="middle">{escape(t)}</text>')
        x += w + 8
    desc = "".join(f'<text x="32" y="{114 + i * 24}" font-family="{SANS}" font-size="15.5" fill="{MUTED}">{escape(d)}</text>'
                   for i, d in enumerate(desc_lines))
    if live:
        cta = (f'<rect x="32" y="228" width="128" height="30" rx="15" fill="url(#cta)"/>'
               f'<circle class="pulse" cx="50" cy="243" r="4" fill="{BG0}"/><circle cx="50" cy="243" r="4" fill="{BG0}"/>'
               f'<text x="62" y="248" font-family="{SANS}" font-size="13" font-weight="700" fill="{BG0}">LIVE DEMO ↗</text>'
               f'<text x="176" y="248" font-family="{SANS}" font-size="13" fill="{DIM}">+ source on GitHub</text>')
    else:
        cta = (f'<rect x="32" y="228" width="128" height="30" rx="15" fill="none" stroke="{a}"/>'
               f'<text x="96" y="248" font-family="{SANS}" font-size="13" font-weight="700" fill="{a}" text-anchor="middle">VIEW CODE ↗</text>')
    if badge:
        bw = tw(badge, 11, mono=True) + 22
        cta += (f'<rect x="{W - 32 - bw:.0f}" y="232" width="{bw:.0f}" height="22" rx="11" fill="{a}" fill-opacity=".12"/>'
                f'<text x="{W - 32 - bw / 2:.0f}" y="247" font-family="{MONO}" font-size="11" fill="{a}" text-anchor="middle">{escape(badge)}</text>')
    title_size = 26 if tw(title, 26) < 330 else 21

    style = f"""
.in {{ animation: rise .8s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
.sweep {{ animation: sweep 7s ease-in-out 1s infinite; }}
@keyframes sweep {{ 0% {{ transform: translateX(-260px) skewX(-20deg); }} 35%, 100% {{ transform: translateX(760px) skewX(-20deg); }} }}
.glow {{ transform-box: fill-box; transform-origin: center; animation: breathe 6s ease-in-out infinite alternate; }}
@keyframes breathe {{ to {{ transform: scale(1.25); opacity: .6; }} }}
.pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 1.8s ease-out infinite; }}
@keyframes pulse {{ from {{ opacity: .8; transform: scale(1); }} to {{ opacity: 0; transform: scale(2.8); }} }}"""

    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="g"><stop offset="0" stop-color="{a}" stop-opacity=".35"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
  <linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}" stop-opacity=".9"/><stop offset=".5" stop-color="{a}" stop-opacity=".12"/><stop offset="1" stop-color="{INDIGO}" stop-opacity=".55"/></linearGradient>
  <linearGradient id="cta" x1="0" y1="0" x2="1" y2="0">{stops([a, SKY])}</linearGradient>
  <linearGradient id="s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <circle class="glow" cx="{W - 40}" cy="30" r="190" fill="url(#g)"/>
  <rect class="sweep" x="0" y="-40" width="160" height="{H + 80}" fill="url(#s)"/>
  <text x="{W - 28}" y="92" font-family="{SANS}" font-size="96" font-weight="800" fill="{a}" fill-opacity=".1" text-anchor="end">{escape(number)}</text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#b)" stroke-width="1.5"/>
<g class="in">
  <rect x="32" y="26" width="54" height="54" rx="16" fill="{a}" fill-opacity=".14" stroke="{a}" stroke-opacity=".4"/>
  <text x="59" y="63" font-size="26" text-anchor="middle">{emoji}</text>
  <text x="104" y="53" font-family="{SANS}" font-size="{title_size}" font-weight="800" fill="{TEXT}">{escape(title)}</text>
  <text x="105" y="76" font-family="{MONO}" font-size="13" fill="{a}">{escape(tag)}</text>
</g>
<g class="in" style="animation-delay:.12s">{desc}</g>
<g class="in" style="animation-delay:.24s">{''.join(chips)}</g>
<g class="in" style="animation-delay:.36s">{cta}</g>
"""
    return svg(W, H, style, body, f"{title} — {' '.join(desc_lines)}")
