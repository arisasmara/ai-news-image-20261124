#!/usr/bin/env python3
"""Render the make.fun news-image-20261124 entry: one dense broadsheet of
24 November 2026 world news (7 main panels + 21 ALSO ON one-liners = 28 stories).
Deterministic: fixed palette, fixed fonts, no randomness, no timestamps.
v3: dull newspaper-paper theme (Aris feedback); MAGYAR replaces HANOI in the
grid (Hanoi moves to ALSO ON item 1); a description paragraph under every
main panel (hero + 6 grid), text verbatim from the REVISION spec.
Run: python3 draw_image.py [out_path]  (default: entry.png next to this file)
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette — dull newspaper paper
PAPER = (237, 230, 214)      # #EDE6D6 base
BANNER_BG = (232, 223, 202)
PANEL = (246, 241, 229)      # #F6F1E5 panel background
PANEL_DARK = (228, 219, 198)  # #E4DBC6 darker panel / map bg
BORDER = (178, 166, 138)
AMBER = (138, 109, 27)       # #8A6D1B dark amber (headers, numbers)
AMBER_DK = (138, 109, 27)
WHITE = (246, 241, 229)      # paper-white (text on dark chips/bands)
MUTED = (96, 88, 74)
BODY = (56, 51, 44)          # body text on paper
BLUE = (46, 74, 98)          # #2E4A62 region blue
GREEN = (34, 110, 66)
RED = (163, 59, 46)          # #A33B2E claim red
SKY = (38, 74, 110)
SEA = (38, 62, 88)
INK = (27, 26, 23)           # #1B1A17 ink text

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def fit_font(text, path, max_size, max_w, min_size=8):
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


def chip(draw, x, y, text, bg=BLUE, fg=WHITE, size=11):
    f = font(BOLD, size)
    tw = f.getlength(text)
    pad = 6
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 8],
                           radius=4, fill=bg)
    draw.text((x + pad, y + 4), text, font=f, fill=fg)
    return x + tw + 2 * pad


def kicker(draw, x, y, text, size=11):
    draw.text((x, y), text, font=font(BOLD, size), fill=BLUE)


# ---------------------------------------------------------------- data
HERO = ("JETS SCRAMBLE", "Russian planes enter Korea air zone",
        "ULLEUNG, S. KOREA · EAST ASIA · SECURITY", "OFFICIAL",
        "Two Russian Tu-160 bombers with fighter escorts entered Korea's air "
        "defence zone; F-15Ks scrambled, a 3-minute alert sounded on Ulleung "
        "Island. Seoul says no airspace breach; the Russian attaché was summoned.")

PANELS = [
    # (kicker, label, sub, chip, kind, description)
    ("EAST ASIA · MARKETS", "ASIAN MARKETS SOAR",
     "Huang return lifts Nikkei, Kospi, Taiwan", "CONFIRMED", "markets",
     "Taiwan's Taiex closes up 9% after last week's AI rout; Seoul's Kospi "
     "gains 7.5% to retake 5,000; Tokyo's Nikkei adds 4.5% as Jensen Huang's "
     "return lifts chip stocks."),
    ("UZHHOROD, UKRAINE · EUROPE · DIPLOMACY", "MAGYAR MEETS ZELENSKYY",
     "Gas, borders, trains agreed in Uzhhorod", "REPORTED", "magyar",
     "Hungarian opposition leader Péter Magyar meets Zelenskyy in Uzhhorod in "
     "their first formal talks; they agree on gas and fuel supplies, border "
     "crossings, direct trains and demining."),
    ("EUROPE · WAR", "ZAPORIZHZHIA HIT",
     "Overnight attack kills 2, wounds 40", "OFFICIAL", "zaporizhzhia",
     "Overnight Russian attack kills 2 and wounds 40, including 4 children; "
     "a private house was destroyed and a five-storey block partly destroyed, "
     "Ukraine's governor says."),
    ("GLOBAL · BUSINESS", "SANOFI'S $41BN DEAL",
     "Buys Insmed — biggest biotech deal in years", "CONFIRMED", "sanofi",
     "Sanofi agrees to buy Insmed for $175 a share in cash — $41bn in total, "
     "the year's biggest biopharma deal. Both boards approved; the deal is "
     "expected to close in the first half of 2027."),
    ("MIDDLE EAST · WAR", "POLICE POST HIT",
     "Israeli strikes kill 6 in Gaza", "REPORTED", "gaza",
     "Israeli airstrikes kill at least 6 Palestinians on Tuesday — 3 at a "
     "police post in Khan Younis, two of them officers, and 3 near the "
     "Netzarim corridor, Reuters reports."),
    ("GLOBAL · CRYPTO", "BITCOIN SINKS BELOW $60K",
     "Nvidia rally fades — $844M liquidated", "REPORTED", "bitcoin",
     "Bitcoin breaks below $60,000, giving back Monday's Nvidia rally; $844M "
     "in crypto futures were liquidated in 24 hours as US spot ETFs log a "
     "fifth straight day of outflows."),
]

# (text, region, flag) — flag "" | "PROPOSAL" | "CLAIM" | "UTC"
# Item 1 is Hanoi (moved from the grid in the v3 swap); items 2-21 unchanged.
ALSO_ON = [
    ("Hanoi blast kills 6, 10 hurt in shop explosion", "SE ASIA", ""),
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
# (lon, lat) map markers: Ulleung, Tokyo, Seoul, Taipei, Hanoi,
# Zaporizhzhia, Uzhhorod, Paris, Khan Younis
MARKERS = [(129.5, 37.5), (139.7, 35.7), (127.0, 37.5), (121.6, 25.0),
           (105.8, 21.0), (35.2, 47.8), (22.3, 48.6), (2.3, 48.9),
           (34.3, 31.3)]


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
    """Flat illustration band inside a grid panel (x0,y0,w,h); h is ~40."""
    if kind == "markets":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (205, 222, 205), (175, 200, 180))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (110, 145, 115), [14, 20, 16, 24, 18, 26, 15])
        draw.line([(x0 + 14, y0 + h - 8), (x0 + w * 0.38, y0 + h - 22),
                   (x0 + w * 0.62, y0 + h - 14), (x0 + w - 14, y0 + 6)],
                  fill=GREEN, width=4, joint="curve")
        draw.polygon([(x0 + w - 30, y0 + 4), (x0 + w - 12, y0 + 4),
                      (x0 + w - 12, y0 + 20)], fill=GREEN)
    elif kind == "magyar":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (200, 212, 225), (170, 190, 210))
        # two flags on poles: Hungary (red/white/green) and Ukraine (blue/yellow)
        for fx, stripes in ((x0 + 62, [(198, 60, 48), (246, 241, 229), (60, 120, 70)]),
                            (x0 + w - 126, [(58, 108, 178), (238, 198, 60)])):
            draw.line([fx, y0 + 4, fx, y0 + h - 2], fill=(70, 66, 60), width=2)
            fw, fh = 62, 26
            sy = y0 + 5
            for j, col in enumerate(stripes):
                sh = fh // len(stripes)
                draw.rectangle([fx + 2, sy + j * sh,
                                fx + 2 + fw, sy + (j + 1) * sh], fill=col)
        draw.line([x0 + 10, y0 + h - 2, x0 + w - 10, y0 + h - 2],
                  fill=(120, 112, 98), width=1)
    elif kind == "zaporizhzhia":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (60, 72, 92), (40, 52, 72))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (28, 38, 52), [16, 22, 14, 24, 18, 20, 15])
        # lit windows
        for wx, wy in [(x0 + 40, y0 + h - 18), (x0 + 120, y0 + h - 22),
                       (x0 + 210, y0 + h - 16), (x0 + 260, y0 + h - 20)]:
            draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(200, 150, 40))
        # fire on one building
        draw.polygon([(x0 + 176, y0 + h - 4), (x0 + 196, y0 + h - 24),
                      (x0 + 216, y0 + h - 4)], fill=(220, 100, 40))
        draw.ellipse([x0 + 182, y0 + h - 28, x0 + 210, y0 + h - 10],
                     fill=(242, 168, 29))
        for cx, cy, r in [(x0 + 196, y0 + 8, 8), (x0 + 212, y0 + 5, 9)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(130, 128, 122))
    elif kind == "sanofi":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (210, 222, 232), (185, 205, 220))
        f = fit_font("$41BN", BOLD, 30, w - 110)
        draw.text((x0 + 12, y0 + 4), "$41BN", font=f, fill=AMBER)
        # pill capsule
        px, py = x0 + w - 88, y0 + 8
        draw.rounded_rectangle([px, py, px + 70, py + 24], radius=12,
                               fill=(246, 241, 229))
        draw.rounded_rectangle([px + 35, py, px + 70, py + 24], radius=12,
                               fill=AMBER)
        draw.line([(px + 35, py), (px + 35, py + 24)], fill=(120, 90, 20),
                  width=2)
    elif kind == "gaza":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (222, 208, 188), (205, 188, 165))
        draw_skyline(draw, x0 + 8, y0, w - 16, y0 + h - 4,
                     (140, 125, 105), [14, 18, 12, 20, 15])
        # checkpoint barrier: amber/black stripes
        bx, by = x0 + 90, y0 + h - 14
        for i in range(6):
            col = AMBER if i % 2 == 0 else (30, 30, 30)
            draw.rectangle([bx + i * 16, by, bx + i * 16 + 16, by + 9],
                           fill=col)
        draw.rectangle([bx - 4, by + 9, bx + 4, y0 + h - 2], fill=MUTED)
        draw.rectangle([bx + 92, by + 9, bx + 100, y0 + h - 2], fill=MUTED)
        for cx, cy, r in [(x0 + 230, y0 + 10, 9), (x0 + 248, y0 + 6, 10)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 146, 138))
    elif kind == "bitcoin":
        vgrad(draw, (x0, y0, x0 + w, y0 + h), (228, 208, 205), (212, 188, 185))
        # $60K dashed line
        ly = y0 + 16
        dashed_line(draw, x0 + 10, ly, x0 + w - 10, ly, AMBER, dash=8, gap=6,
                    width=2)
        draw.text((x0 + 12, ly - 13), "$60K", font=font(BOLD, 11), fill=AMBER)
        # falling chart breaking below the line
        draw.line([(x0 + 16, y0 + 6), (x0 + w * 0.42, y0 + 14),
                   (x0 + w * 0.62, y0 + 24), (x0 + w - 16, y0 + h - 6)],
                  fill=RED, width=4, joint="curve")
        # bitcoin coin: hand-drawn B (DejaVu lacks U+20BF, renders tofu)
        cx, cy, r = x0 + w - 40, y0 + h - 14, 13
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 150, 40))
        bf = font(BOLD, 15)
        bw = bf.getlength("B")
        draw.text((cx - bw / 2, cy - 9), "B", font=bf, fill=INK)
        draw.line([cx - 5, cy - 8, cx - 5, cy + 8], fill=INK, width=2)
        draw.line([cx + 5, cy - 8, cx + 5, cy + 8], fill=INK, width=2)


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
        draw.polygon(pts, fill=(172, 164, 138), outline=(140, 130, 105))
    for lon, lat in MARKERS:
        mx, my = proj(lon, lat)
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED,
                     outline=WHITE, width=1)


def draw_also_on_item(draw, num, text, region, flag, x, y, w):
    """One numbered one-liner, wrapped to at most 2 lines, region in blue."""
    num_f = font(BOLD, 13)
    txt_f = font(REG, 12)
    reg_f = font(BOLD, 11)
    flag_col = RED if flag == "CLAIM" else BLUE
    tokens = [(wd, txt_f, INK) for wd in text.split()]
    tokens.append(("—", reg_f, BLUE))
    tokens += [(wd, reg_f, BLUE) for wd in region.split()]
    if flag:
        tokens.append(("·", reg_f, flag_col))
        tokens += [(wd, reg_f, flag_col) for wd in flag.split()]
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
        yy += 16
    return yy


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Banner ------------------------------------------------------
    d.rectangle([0, 0, W, 58], fill=BANNER_BG)
    # globe icon
    cx, cy, r = 40, 29, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=2)
    d.ellipse([cx - 7, cy - r, cx + 7, cy + r], outline=AMBER, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=AMBER, width=1)
    title_f = fit_font("24 NOVEMBER 2026", BOLD, 44, 560)
    d.text((66, 7), "24 NOVEMBER 2026", font=title_f, fill=INK)
    d.text((W - 12 - font(REG, 14).getlength("ONE DAY OF WORLD NEWS · 28 STORIES"),
            21), "ONE DAY OF WORLD NEWS · 28 STORIES",
           font=font(REG, 14), fill=MUTED)
    d.rectangle([0, 58, W, 61], fill=AMBER)

    # ---- Big-numbers strip -------------------------------------------
    bn_f = fit_font(BIG_NUMBERS, BOLD, 19, W - 24)
    d.text(((W - bn_f.getlength(BIG_NUMBERS)) / 2, 65), BIG_NUMBERS,
           font=bn_f, fill=AMBER)

    # ---- Hero: KADIZ --------------------------------------------------
    hx0, hy0, hx1, hy1 = 12, 88, W - 12, 246
    vgrad(d, (hx0, hy0, hx1, 148), (140, 168, 198), (95, 125, 158))
    # sun glow top-right
    d.ellipse([hx1 - 120, hy0 + 6, hx1 - 56, hy0 + 58], fill=(240, 205, 110))
    # sea
    d.rectangle([hx0, 132, hx1, 148], fill=SEA)
    dashed_line(d, hx0 + 16, 140, hx1 - 16, 140, (110, 140, 170),
                dash=14, gap=10, width=1)
    # dashed ADIZ boundary across the sky
    dashed_line(d, hx0 + 30, 112, hx1 - 120, 96, AMBER,
                dash=10, gap=8, width=2)
    d.text((hx0 + 34, 116), "KADIZ", font=font(BOLD, 11), fill=AMBER)
    # island with alert
    ix = hx0 + 150
    d.ellipse([ix - 46, 136, ix + 46, 148], fill=(90, 125, 85))
    d.polygon([(ix - 8, 118), (ix + 8, 118), (ix, 134)], fill=AMBER)
    d.text((ix - 2, 120), "!", font=font(BOLD, 11), fill=INK)
    # jets
    draw_jet(d, hx0 + 560, 106, 1.2, (238, 238, 232), -28)
    draw_jet(d, hx0 + 640, 120, 0.9, (215, 220, 225), -28)
    draw_jet(d, hx0 + 480, 98, 0.7, (200, 208, 214), -28)
    # label band
    d.rectangle([hx0, 148, hx1, hy1], fill=PANEL)
    d.rectangle([hx0, 148, hx1, 150], fill=AMBER)
    kicker(d, hx0 + 14, 154, HERO[2], size=11)
    chip(d, hx1 - 92, 152, HERO[3])
    d.text((hx0 + 14, 168), HERO[0], font=font(BOLD, 26), fill=INK)
    d.text((hx0 + 14, 198), HERO[1], font=font(REG, 13), fill=BODY)
    hero_desc = wrap_text(HERO[4], font(REG, 12), hx1 - hx0 - 28)
    yy = 214
    for ln in hero_desc[:2]:
        d.text((hx0 + 14, yy), ln, font=font(REG, 12), fill=BODY)
        yy += 15

    # ---- Grid 2x3 ------------------------------------------------------
    gx = [12, 352, 692]
    gy = [252, 420]
    pw, ph = 320, 164
    for i, (kick, label, sub, chp, kind, desc) in enumerate(PANELS):
        x0 = gx[i % 3]
        y0 = gy[i // 3]
        d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PANEL, outline=BORDER)
        panel_illustration(d, kind, x0 + 1, y0 + 1, pw - 2, 40)
        kf = fit_font(kick, BOLD, 10, pw - 100)
        d.text((x0 + 10, y0 + 46), kick, font=kf, fill=BLUE)
        chip(d, x0 + pw - 78, y0 + 44, chp, size=9)
        lab_f = fit_font(label, BOLD, 20, pw - 20)
        d.text((x0 + 10, y0 + 60), label, font=lab_f, fill=INK)
        d.text((x0 + 10, y0 + 84), sub, font=font(REG, 12), fill=BODY)
        desc_lines = wrap_text(desc, font(REG, 11), pw - 20)
        yy = y0 + 100
        for ln in desc_lines[:4]:
            d.text((x0 + 10, yy), ln, font=font(REG, 11), fill=BODY)
            yy += 13

    # ---- ALSO ON strip -------------------------------------------------
    ay = 590
    d.text((12, ay), "ALSO ON TUESDAY 24 NOVEMBER",
           font=font(BOLD, 20), fill=AMBER)
    right = "21 MORE STORIES · 8 REGIONS · 16 FIELDS"
    d.text((W - 12 - font(REG, 13).getlength(right), ay + 4), right,
           font=font(REG, 13), fill=MUTED)
    d.rectangle([12, ay + 26, W - 12, ay + 28], fill=BORDER)
    col_x = [12, 352, 692]
    col_w = 320
    row_y = ay + 32
    row_h = 36
    for i, (text, region, flag) in enumerate(ALSO_ON):
        col = i % 3
        row = i // 3
        draw_also_on_item(d, i + 1, text, region, flag,
                          col_x[col], row_y + row * row_h, col_w)

    # ---- Bottom band: map + DATE CHECK + legend ------------------------
    by = 878
    d.text((12, by), "WHERE IT HAPPENED",
           font=font(BOLD, 14), fill=AMBER)
    draw_map(d, 12, by + 20, 428, 126)
    rx = 456
    # DATE CHECK box
    d.rectangle([rx, by + 20, W - 12, by + 84], fill=PANEL, outline=AMBER)
    d.text((rx + 12, by + 26), "DATE CHECK",
           font=font(BOLD, 15), fill=AMBER)
    dc_lines = wrap_text(
        "All 28 stories verified as 24 Nov 2026 events. Items 19 & 21 are "
        "UTC-dated (Monday night in the Americas = Tuesday UTC); item 20 "
        "is a CLAIM.", font(REG, 12), W - 12 - rx - 24)
    yy = by + 44
    for ln in dc_lines:
        d.text((rx + 12, yy), ln, font=font(REG, 12), fill=BODY)
        yy += 15
    # Legend
    ly = by + 90
    d.text((rx, ly), "CERTAINTY",
           font=font(BOLD, 13), fill=AMBER)
    leg = ("REPORTED = confirmed by named outlets · CLAIM = single-source / "
           "unverified attribution · PROPOSAL = announced plan, not yet done")
    yy = ly + 16
    for ln in wrap_text(leg, font(REG, 11), W - 12 - rx):
        d.text((rx, yy), ln, font=font(REG, 11), fill=MUTED)
        yy += 13
    src = ("Sources: Reuters · AP · Yonhap · RAK Police · CoinDesk · WSJ · "
           "Sanofi · BMKG")
    d.text((rx, 1010), src, font=font(REG, 10), fill=MUTED)

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
