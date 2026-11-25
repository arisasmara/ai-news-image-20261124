#!/usr/bin/env python3
"""Render the make.fun news-image-20261124 entry: one dense broadsheet of
24 November 2026 world news (7 main panels + 21 ALSO ON one-liners = 28 stories).
Deterministic: fixed palette, fixed fonts, no randomness, no timestamps.
v1: full layout. Run: python3 draw_image.py [out_path]  (default: entry.png next to this file)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette
BG = (20, 39, 62)          # deep steel-blue base
PANEL = (28, 53, 82)       # panel background
PANEL_DARK = (16, 32, 52)  # darker panel / overlay
BORDER = (49, 82, 122)
AMBER = (242, 168, 29)
AMBER_DK = (199, 127, 10)
WHITE = (244, 247, 250)
MUTED = (159, 180, 200)
GREEN = (70, 185, 120)
RED = (229, 72, 77)
SKY = (38, 74, 110)
SEA = (14, 30, 50)
INK = (20, 39, 62)

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def fit_font(text, path, max_size, max_w, min_size=10):
    """Largest font size <= max_size whose rendered width fits max_w."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap_text(text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def vgrad(draw, box, c1, c2, steps=24):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        yy0 = y0 + int(h * i / steps)
        yy1 = y0 + int(h * (i + 1) / steps)
        draw.rectangle([x0, yy0, x1, yy1], fill=c)


def dashed_line(draw, x1, y1, x2, y2, fill, dash=9, gap=6, width=2):
    import math
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux, uy = dx / dist, dy / dist
    d = 0.0
    while d < dist:
        e = min(d + dash, dist)
        draw.line([x1 + ux * d, y1 + uy * d, x1 + ux * e, y1 + uy * e],
                  fill=fill, width=width)
        d = e + gap


def chip(draw, x, y, text, bg=AMBER, fg=INK, size=11):
    f = font(BOLD, size)
    tw = f.getlength(text)
    pad = 6
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 8],
                           radius=4, fill=bg)
    draw.text((x + pad, y + 4), text, font=f, fill=fg)
    return x + tw + 2 * pad


def kicker(draw, x, y, text, size=11):
    draw.text((x, y), text, font=font(BOLD, size), fill=AMBER)


# ---------------------------------------------------------------- data
HERO = ("JETS SCRAMBLE", "Russian planes enter Korea air zone",
        "ULLEUNG, S. KOREA · EAST ASIA · SECURITY", "OFFICIAL")

PANELS = [
    # (kicker, label, sub, chip, kind)
    ("EAST ASIA · MARKETS", "ASIAN MARKETS SOAR",
     "Huang return lifts Nikkei, Kospi, Taiwan", "CONFIRMED", "markets"),
    ("SE ASIA · ACCIDENT", "HANOI BLAST",
     "6 killed, 10 hurt in shop explosion", "REPORTED", "hanoi"),
    ("EUROPE · WAR", "ZAPORIZHZHIA HIT",
     "Overnight attack kills 2, wounds 40", "OFFICIAL", "zaporizhzhia"),
    ("GLOBAL · BUSINESS", "SANOFI'S $41BN DEAL",
     "Buys Insmed — biggest biotech deal in years", "CONFIRMED", "sanofi"),
    ("MIDDLE EAST · WAR", "POLICE POST HIT",
     "Israeli strikes kill 6 in Gaza", "REPORTED", "gaza"),
    ("GLOBAL · CRYPTO", "BITCOIN SINKS BELOW $60K",
     "Nvidia rally fades — $844M liquidated", "REPORTED", "bitcoin"),
]

# (text, region, flag) — flag "" | "PROPOSAL" | "CLAIM" | "UTC"
ALSO_ON = [
    ("Magyar, Zelenskyy meet, agree gas, borders, trains", "EUROPE", ""),
    ("UAE bus crash kills 13, toll rises in hospital", "MIDDLE EAST", ""),
    ("Magnitude 5.6 quake jolts eastern Nepal, no casualties", "SOUTH ASIA", ""),
    ("Hasina seeks return on 16 December, Dhaka says extradition only", "SOUTH ASIA", "PROPOSAL"),
    ("Baghdad seizes Kurdish border crossings and oilfields", "MIDDLE EAST", ""),
    ("Officer who shot Nahel to face murder trial", "EUROPE", ""),
    ("Pakistan's first astronaut named for Shenzhou-24", "EAST ASIA", ""),
    ("Australia fines Big Tech up to 5% of revenue", "OCEANIA", ""),
    ("Singapore: no backdoor for US chips", "EAST ASIA", ""),
    ("EU pact moves just 1,283 migrants in year one", "EUROPE", ""),
    ("Johannesburg put on flood alert", "AFRICA", ""),
    ("Western chips made in 2026 found in Russian drones", "EUROPE", ""),
    ("Arsenal held 1-1 by Dortmund", "EUROPE", ""),
    ("Gukesh, Sindarov draw world title opener", "EUROPE", ""),
    ("Pope Francis diary published, tells of seeing devil", "EUROPE", ""),
    ("Tehran: no US talks until seven conditions met", "MIDDLE EAST", ""),
    ("31,500 wounded troops treated since October 2023", "MIDDLE EAST", ""),
    ("Jakarta on tidal-flood alert as supermoon peaks", "EAST ASIA", ""),
    ("Car bomb wrecks Colombian state HQ, 23 hurt", "LATIN AMERICA", "UTC"),
    ("Iran says mines set three tankers ablaze", "MIDDLE EAST", "CLAIM"),
    ("Commanders stun Bengals 22-20", "N. AMERICA", "UTC"),
]

BIG_NUMBERS = "TAIWAN +9%  ·  KOSPI +7.5%  ·  NIKKEI +4.5%  ·  $41BN  ·  BTC <$60K  ·  6 KILLED IN HANOI"

# Coarse continent outlines (lon, lat) for the small world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-50, -30), (-60, -38), (-70, -52), (-73, -40), (-75, -20),
     (-80, -5), (-80, 5)],
    # Europe
    [(-10, 36), (-10, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (28, 59), (30, 60), (25, 65), (20, 70), (12, 70),
     (5, 60), (-5, 50), (-9, 43)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (43, 11), (48, 10), (51, 12), (40, 0), (35, -10), (30, -20),
     (25, -30), (20, -35), (15, -30), (12, -18), (8, -2), (9, 4), (-8, 4),
     (-13, 8)],
    # Asia
    [(30, 36), (40, 40), (50, 40), (60, 25), (65, 25), (70, 20), (75, 10),
     (80, 8), (85, 15), (90, 22), (95, 16), (100, 8), (105, 2), (110, 10),
     (115, 20), (120, 30), (122, 38), (127, 40), (130, 42), (135, 44),
     (140, 40), (142, 50), (140, 60), (160, 62), (170, 66), (180, 65),
     (170, 60), (160, 55), (150, 60), (140, 65), (130, 72), (120, 73),
     (110, 74), (100, 77), (90, 75), (80, 73), (70, 72), (60, 69),
     (50, 68), (40, 67), (35, 65), (30, 60), (28, 55), (30, 50), (30, 45)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (145, -15),
     (142, -11), (137, -12), (135, -15), (130, -13), (126, -14), (122, -17),
     (118, -20)],
]
# (lon, lat) map markers
MARKERS = [(129.5, 37.5), (139.7, 35.7), (127.0, 37.5), (121.6, 25.0),
           (105.8, 21.0), (35.2, 47.8), (2.3, 48.9), (34.3, 31.3)]


def draw_skyline(draw, x0, y0, w, base_y, color, seed_heights):
    """Simple flat building silhouettes."""
    n = len(seed_heights)
    bw = w // n
    for i, hh in enumerate(seed_heights):
        bx = x0 + i * bw
        draw.rectangle([bx + 1, base_y - hh, bx + bw - 1, base_y], fill=color)


def draw_jet(draw, cx, cy, s, fill, angle_deg=0):
    """Small delta-jet silhouette pointing up-right; s = scale."""
    import math
    a = math.radians(angle_deg)
    pts = [(0, -14), (5, 6), (16, 12), (4, 10), (0, 16), (-4, 10),
           (-16, 12), (-5, 6)]
    out = []
    for px, py in pts:
        rx = px * s * math.cos(a) - py * s * math.sin(a)
        ry = px * s * math.sin(a) + py * s * math.cos(a)
        out.append((cx + rx, cy + ry))
    draw.polygon(out, fill=fill)


def panel_illustration(draw, kind, x0, y0, w, h):
    """Flat illustration band inside a grid panel (x0,y0,w,h)."""
    if kind == "markets":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (16, 46, 34), (24, 68, 48))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 8,
                     (38, 84, 62), [26, 40, 32, 48, 36, 52, 30])
        draw.line([(x0 + 14, y0 + h - 16), (x0 + w * 0.38, y0 + h - 44),
                   (x0 + w * 0.62, y0 + h - 30), (x0 + w - 14, y0 + 12)],
                  fill=GREEN, width=5, joint="curve")
        draw.polygon([(x0 + w - 34, y0 + 8), (x0 + w - 14, y0 + 8),
                      (x0 + w - 14, y0 + 26)], fill=GREEN)
    elif kind == "hanoi":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (52, 38, 30), (30, 26, 40))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 8,
                     (24, 22, 34), [34, 22, 44, 28, 38])
        # broken shopfront: tilted roof slab
        draw.polygon([(x0 + 96, y0 + h - 40), (x0 + 150, y0 + h - 52),
                      (x0 + 158, y0 + h - 38), (x0 + 104, y0 + h - 28)],
                     fill=(70, 52, 40))
        # smoke
        for cx, cy, r in [(x0 + 130, y0 + 22, 12), (x0 + 148, y0 + 12, 15),
                          (x0 + 168, y0 + 26, 10)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 118, 112))
        # fire glow
        draw.ellipse([x0 + 108, y0 + h - 30, x0 + 156, y0 + h - 6],
                     fill=(232, 120, 40))
    elif kind == "zaporizhzhia":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (10, 18, 34), (22, 34, 58))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 8,
                     (8, 12, 24), [30, 44, 26, 50, 34, 42, 28])
        # lit windows
        for wx, wy in [(x0 + 40, y0 + h - 34), (x0 + 120, y0 + h - 44),
                       (x0 + 210, y0 + h - 30), (x0 + 260, y0 + h - 40)]:
            draw.rectangle([wx, wy, wx + 5, wy + 7], fill=AMBER)
        # fire on one building
        draw.polygon([(x0 + 176, y0 + h - 8), (x0 + 196, y0 + h - 46),
                      (x0 + 216, y0 + h - 8)], fill=(232, 90, 30))
        draw.ellipse([x0 + 182, y0 + h - 52, x0 + 210, y0 + h - 24],
                     fill=(242, 168, 29))
        for cx, cy, r in [(x0 + 196, y0 + 14, 11), (x0 + 214, y0 + 8, 13)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 88, 84))
    elif kind == "sanofi":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (24, 44, 66), (16, 30, 50))
        f = fit_font("$41BN", BOLD, 46, w - 110)
        draw.text((x0 + 14, y0 + 12), "$41BN", font=f, fill=AMBER)
        # pill capsule
        px, py = x0 + w - 96, y0 + 16
        draw.rounded_rectangle([px, py, px + 78, py + 30], radius=15,
                               fill=(220, 230, 240))
        draw.rounded_rectangle([px + 39, py, px + 78, py + 30], radius=15,
                               fill=AMBER)
        draw.line([(px + 39, py), (px + 39, py + 30)], fill=(120, 90, 20),
                  width=2)
        # (no chart line: the band is only 66px tall and any line here
        # strikes through the $41BN text — the figure + pill carry it)
    elif kind == "gaza":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (46, 36, 30), (26, 24, 36))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 8,
                     (20, 18, 30), [26, 36, 24, 40, 30])
        # checkpoint barrier: amber/black stripes
        bx, by = x0 + 90, y0 + h - 34
        for i in range(6):
            col = AMBER if i % 2 == 0 else (30, 30, 30)
            draw.rectangle([bx + i * 18, by, bx + i * 18 + 18, by + 12],
                           fill=col)
        draw.rectangle([bx - 4, by + 12, bx + 4, y0 + h - 6], fill=MUTED)
        draw.rectangle([bx + 104, by + 12, bx + 112, y0 + h - 6], fill=MUTED)
        for cx, cy, r in [(x0 + 230, y0 + 18, 12), (x0 + 250, y0 + 10, 14)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 108, 102))
    elif kind == "bitcoin":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (52, 22, 26), (26, 16, 34))
        # $60K dashed line
        ly = y0 + 26
        dashed_line(draw, x0 + 10, ly, x0 + w - 10, ly, AMBER, dash=8, gap=6,
                    width=2)
        draw.text((x0 + 12, ly - 20), "$60K", font=font(BOLD, 13), fill=AMBER)
        # falling chart breaking below the line
        draw.line([(x0 + 16, y0 + 12), (x0 + w * 0.42, y0 + 24),
                   (x0 + w * 0.62, y0 + 40), (x0 + w - 16, y0 + h - 12)],
                  fill=RED, width=5, joint="curve")
        # bitcoin coin: hand-drawn ₿ (DejaVu lacks U+20BF, renders tofu)
        cx, cy, r = x0 + w - 46, y0 + h - 26, 20
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
        bf = font(BOLD, 24)
        bw = bf.getlength("B")
        draw.text((cx - bw / 2, cy - 14), "B", font=bf, fill=INK)
        draw.line([cx - 7, cy - 13, cx - 7, cy + 13], fill=INK, width=2)
        draw.line([cx + 7, cy - 13, cx + 7, cy + 13], fill=INK, width=2)


def draw_map(draw, x0, y0, w, h):
    """Simplified equirectangular world map with red markers."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=PANEL_DARK,
                   outline=BORDER)
    lat_top, lat_bot = 85.0, -55.0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * w,
                y0 + (lat_top - lat) / (lat_top - lat_bot) * h)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(42, 74, 107), outline=(74, 107, 140))
    for lon, lat in MARKERS:
        mx, my = proj(lon, lat)
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED,
                     outline=WHITE, width=1)


def draw_also_on_item(draw, num, text, region, flag, x, y, w):
    """One numbered one-liner, wrapped to at most 2 lines, region in amber."""
    num_f = font(BOLD, 13)
    txt_f = font(REG, 13)
    reg_f = font(BOLD, 11)
    suffix = " — " + region
    if flag:
        suffix += " · " + flag
    # Wrap "text + suffix" as words, tracking which words belong to suffix.
    words = text.split()
    suf_words = suffix.split()
    # Build token list: (word, font, fill)
    tokens = [(wd, txt_f, WHITE) for wd in words]
    tokens += [(wd, reg_f, AMBER) for wd in suf_words]
    lines, cur, cur_w = [], [], 0.0
    num_w = num_f.getlength(f"{num}. ")
    avail = w - num_w
    for wd, fnt, fill in tokens:
        ww = fnt.getlength(wd + " ")
        if cur_w + ww <= avail or not cur:
            cur.append((wd, fnt, fill))
            cur_w += ww
        else:
            lines.append(cur)
            cur = [(wd, fnt, fill)]
            cur_w = ww
    if cur:
        lines.append(cur)
    lines = lines[:2]
    # Draw
    draw.text((x, y), f"{num}. ", font=num_f, fill=AMBER)
    yy = y
    for ln in lines:
        xx = x + num_w
        for wd, fnt, fill in ln:
            draw.text((xx, yy), wd + " ", font=fnt, fill=fill)
            xx += fnt.getlength(wd + " ")
        yy += 17
    return yy


def render():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- Banner ------------------------------------------------------
    d.rectangle([0, 0, W, 60], fill=(14, 30, 51))
    # globe icon
    cx, cy, r = 40, 30, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=2)
    d.ellipse([cx - 7, cy - r, cx + 7, cy + r], outline=AMBER, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=AMBER, width=1)
    title_f = fit_font("24 NOVEMBER 2026", BOLD, 44, 560)
    d.text((66, 8), "24 NOVEMBER 2026", font=title_f, fill=WHITE)
    d.text((W - 12 - font(REG, 14).getlength("ONE DAY OF WORLD NEWS · 28 STORIES"),
            22), "ONE DAY OF WORLD NEWS · 28 STORIES",
           font=font(REG, 14), fill=MUTED)
    d.rectangle([0, 60, W, 63], fill=AMBER)

    # ---- Big-numbers strip -------------------------------------------
    bn_f = fit_font(BIG_NUMBERS, BOLD, 20, W - 24)
    d.text(((W - bn_f.getlength(BIG_NUMBERS)) / 2, 68), BIG_NUMBERS,
           font=bn_f, fill=AMBER)

    # ---- Hero: KADIZ --------------------------------------------------
    hx0, hy0, hx1, hy1 = 12, 90, W - 12, 250
    vgrad(d, (hx0, hy0, hx1, hy1), (30, 62, 100), (16, 34, 58))
    # sun glow top-right
    d.ellipse([hx1 - 120, hy0 + 8, hx1 - 56, hy0 + 72], fill=(242, 190, 80))
    # sea
    d.rectangle([hx0, hy1 - 52, hx1, hy1], fill=SEA)
    for wy in (hy1 - 44, hy1 - 32, hy1 - 20):
        dashed_line(d, hx0 + 16, wy, hx1 - 16, wy, (70, 110, 150),
                    dash=14, gap=10, width=1)
    # dashed ADIZ boundary across the sky
    dashed_line(d, hx0 + 30, hy0 + 96, hx1 - 120, hy0 + 44, AMBER,
                dash=10, gap=8, width=2)
    d.text((hx0 + 34, hy0 + 100), "KADIZ", font=font(BOLD, 11), fill=AMBER)
    # island with alert
    ix, iy = hx0 + 150, hy1 - 52
    d.ellipse([ix - 46, iy - 6, ix + 46, iy + 6], fill=(52, 84, 52))
    d.polygon([(ix - 8, iy - 34), (ix + 8, iy - 34), (ix, iy - 12)],
              fill=AMBER)
    d.text((ix - 2, iy - 30), "!", font=font(BOLD, 12), fill=INK)
    # jets
    draw_jet(d, hx0 + 560, hy0 + 62, 1.5, (220, 228, 236), -28)
    draw_jet(d, hx0 + 640, hy0 + 92, 1.1, (180, 190, 200), -28)
    draw_jet(d, hx0 + 480, hy0 + 40, 0.9, (160, 170, 182), -28)
    # label band
    d.rectangle([hx0, hy1 - 62, hx1, hy1], fill=PANEL_DARK)
    d.rectangle([hx0, hy1 - 62, hx1, hy1 - 60], fill=AMBER)
    kicker(d, hx0 + 14, hy1 - 56, HERO[2], size=11)
    chip(d, hx1 - 92, hy1 - 58, HERO[3])
    d.text((hx0 + 14, hy1 - 46), HERO[0], font=font(BOLD, 28), fill=WHITE)
    d.text((hx0 + 14, hy1 - 16), HERO[1], font=font(REG, 15),
           fill=MUTED)

    # ---- Grid 2x3 ------------------------------------------------------
    gx = [12, 352, 692]
    gy = [256, 402]
    pw, ph = 320, 138
    for i, (kick, label, sub, chp, kind) in enumerate(PANELS):
        x0 = gx[i % 3]
        y0 = gy[i // 3]
        d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PANEL, outline=BORDER)
        panel_illustration(d, kind, x0 + 1, y0 + 1, pw - 2, 66)
        kicker(d, x0 + 10, y0 + 72, kick, size=10)
        chip(d, x0 + pw - 78, y0 + 70, chp, size=9)
        lab_f = fit_font(label, BOLD, 20, pw - 20)
        d.text((x0 + 10, y0 + 86), label, font=lab_f, fill=WHITE)
        sub_lines = wrap_text(sub, font(REG, 12), pw - 20)
        yy = y0 + 110
        for ln in sub_lines[:2]:
            d.text((x0 + 10, yy), ln, font=font(REG, 12), fill=MUTED)
            yy += 14

    # ---- ALSO ON strip -------------------------------------------------
    ay = 548
    d.text((12, ay), "ALSO ON TUESDAY 24 NOVEMBER",
           font=font(BOLD, 20), fill=AMBER)
    right = "21 MORE STORIES · 8 REGIONS · 16 FIELDS"
    d.text((W - 12 - font(REG, 13).getlength(right), ay + 4), right,
           font=font(REG, 13), fill=MUTED)
    d.rectangle([12, ay + 28, W - 12, ay + 30], fill=BORDER)
    col_x = [12, 352, 692]
    col_w = 320
    row_y = ay + 32
    row_h = 39
    for i, (text, region, flag) in enumerate(ALSO_ON):
        col = i % 3
        row = i // 3
        draw_also_on_item(d, i + 1, text, region, flag,
                          col_x[col], row_y + row * row_h, col_w)

    # ---- Bottom band: map + DATE CHECK + legend ------------------------
    by = 860
    d.text((12, by), "WHERE IT HAPPENED",
           font=font(BOLD, 14), fill=AMBER)
    draw_map(d, 12, by + 22, 428, 138)
    rx = 456
    # DATE CHECK box
    d.rectangle([rx, by + 22, W - 12, by + 92], fill=PANEL, outline=AMBER)
    d.text((rx + 12, by + 28), "DATE CHECK",
           font=font(BOLD, 15), fill=AMBER)
    dc_lines = wrap_text(
        "All 28 stories verified as 24 Nov 2026 events. Items 19 & 21 are "
        "UTC-dated (Monday night in the Americas = Tuesday UTC); item 20 "
        "is a CLAIM.", font(REG, 12), W - 12 - rx - 24)
    yy = by + 50
    for ln in dc_lines:
        d.text((rx + 12, yy), ln, font=font(REG, 12), fill=WHITE)
        yy += 15
    # Legend
    ly = by + 100
    d.text((rx, ly), "CERTAINTY",
           font=font(BOLD, 13), fill=AMBER)
    leg = ("REPORTED = confirmed by named outlets · CLAIM = single-source / "
           "unverified attribution · PROPOSAL = announced plan, not yet done")
    yy = ly + 18
    for ln in wrap_text(leg, font(REG, 12), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 12), fill=MUTED)
        yy += 15
    src = ("Sources: Reuters · AP · Yonhap · RAK Police · CoinDesk · WSJ · "
           "Sanofi · BMKG")
    yy += 2
    for ln in wrap_text(src, font(REG, 11), W - 12 - rx)[:1]:
        d.text((rx, yy), ln, font=font(REG, 11), fill=MUTED)
        yy += 14

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
