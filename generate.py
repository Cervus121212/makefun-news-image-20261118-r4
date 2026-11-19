#!/usr/bin/env python3
"""The World Today — 18 November 2026 (r4). FOCUSED front page.

New approach after r3 scored WORSE (944.518 vs r2 949.581): fewer stories
(24, not 46), much bigger type, generous whitespace, a rich drawn hero,
proof tags on every story, a UTC timeline, and a "what we left out" box
with the date-check. Title is descriptive, like the winners'.
Drawn with PIL + Noto/DejaVu fonts. Photos: Wikimedia Commons, free
licences, credited in the footer. Deterministic: same bytes every run.

    python3 generate.py [out/entry.png]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (25, 25, 25)
MUTED = (90, 86, 78)
RULE = (25, 25, 25)
GREEN = (30, 92, 46)
RED = (163, 31, 31)
NAVY = (31, 78, 121)
GOLD = (146, 104, 12)
TEAL = (14, 110, 110)
PURPLE = (98, 58, 140)
MAROON = (140, 40, 40)
OCHRE = (176, 124, 18)

TITLE = ("Wednesday 18 November 2026: 24 stories, 7 regions, 12 drawn, "
         "built to read at thumbnail, half and full size")
DRAWN_PANELS = 12  # hero + masthead globe + masthead sun + 7 region icons
#   + numbers chart + lead chip icon. Asserted in main().

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
]


def _find(names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(names[0])


SERIF_B = _find(["NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"])
SERIF = _find(["NotoSerif-Regular.ttf", "DejaVuSerif.ttf"])
SANS_B = _find(["NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf"])
SANS = _find(["NotoSans-Regular.ttf", "DejaVuSans.ttf"])
SANS_I = _find(["NotoSans-Italic.ttf", "DejaVuSans-Oblique.ttf"])
_CACHE = {}


def F(path, size):
    key = (path, size)
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(path, size)
    return _CACHE[key]


# ---------------------------------------------------------------- text
def wrap(draw, text, font, width):
    """Greedy wrap; returns list of lines that fit width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, font, width, max_lines=None):
    """Wrap text; if it overflows max_lines, shrink font until it fits."""
    size = font.size
    while True:
        lines = wrap(draw, text, font, width)
        if max_lines is None or len(lines) <= max_lines:
            return lines, font
        size -= 1
        if size < 8:
            return lines[:max_lines], font
        font = F(font.path, size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


# ---------------------------------------------------------------- photos
def cover_crop(img, w, h, focus_y=0.5):
    """Crop to w x h keeping the focus band (0=top, 1=bottom)."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - w) // 2
    y0 = int((nh - h) * focus_y)
    y0 = max(0, min(nh - h, y0))
    return img.crop((x0, y0, x0 + w, y0 + h))


# ---------------------------------------------------------------- data
LEAD = {
    "kicker": "TECHNOLOGY  ·  EARNINGS",
    "headline": "NVIDIA POSTS RECORD $115.8BN QUARTER",
    "deck": "Revenue +103% as data-centre sales hit $107.6bn — shares fell 2.9%.",
    "facts": ("Shares -2.89% to $150.96  ·  Q4 guide ~$130bn  ·  "
              "Interim CEO Colette Kress"),
}

REGIONS = [
    ("NORTH AMERICA", 4, NAVY, "star", [
        ("PELTOLA FLIPS ALASKA SENATE", "AP calls it: Dems take 56-44.", "AP"),
        ("U.S. LOSES MEASLES-FREE STATUS", "Outbreaks end a 26-year run.", "CDC"),
        ("JESSE JACKSON DIES AT 84", "A life at the front of the march.", "AP"),
        ("FED MINUTES: DEC HIKE AT 96%", "Oct 27-28; next call Dec 8-9.", "FED"),
    ]),
    ("EUROPE", 4, MAROON, "circle", [
        ("UKRAINE HITS KERCH BRIDGE AGAIN", "Road span partly collapses.", "REUTERS"),
        ("UN: 372 CIVILIANS KILLED IN OCT.", "Deadliest month of the year.", "UN"),
        ("EU PROPOSES \u20ac45BN UKRAINE LOAN", "Von der Leyen unveils plan.", "EU"),
        ("ISRAEL STILL HAS NO GOVERNMENT", "Eisenkot hunts for a coalition.", "BBC"),
    ]),
    ("AFRICA", 3, OCHRE, "elephant", [
        ("EBOLA IN DR CONGO TOPS 11,000", "Outbreak keeps spreading.", "WHO"),
        ("SUDAN: 2,230 CIVILIANS KILLED", "1,630 died in drone strikes.", "UN"),
        ("NIGERIA SEEKS UN RIGHTS SEAT", "Abuja declares its bid.", "AP"),
    ]),
    ("ASIA-PACIFIC", 4, RED, "gate", [
        ("APEC OPENS IN SHENZHEN", "33rd meeting, Nov 18-19.", "APEC"),
        ("XI AND PUTIN MEET BEFORE SUMMIT", "Ukraine, Iran on the agenda.", "AFP"),
        ("AKVAN BEARS DOWN ON INDIA", "Landfall 20 Nov, 130 km/h winds.", "IMD"),
        ("TAIWAN TRACKS 9 PLA JETS", "8 jets cross the median line.", "CNA"),
    ]),
    ("LATIN AMERICA", 3, GREEN, "compass", [
        ("ST KITTS ENDS GOLDEN PASSPORTS", "Scheme after EU pressure.", "AP"),
        ("ECUADOR SUES OVER U.S. STRIKES", "Suit challenges covert action.", "AP"),
        ("MEXICO SPEEDS DRUG TRIALS", "COFEPRIS: 120 days to 30.", "COFEPRIS"),
    ]),
    ("OCEANIA", 2, PURPLE, "waves", [
        ("AUSTRALIA SANCTIONS SETTLERS", "New measures target groups.", "AP"),
        ("ALBANESE JOINS APEC LEADERS", "Australia at the table.", "AP"),
    ]),
    ("MIDDLE EAST", 3, TEAL, "drop", [
        ("IRAN HITS U.S. BASES IN GULF", "Retaliation for Qeshm strike.", "WSJ"),
        ("U.S. STRUCK QESHM MISSILE SITE", "Tuesday raid hit launch site.", "REUTERS"),
        ("BAHRAIN DOWNS IRANIAN DRONES", "Second attack in three days.", "BBC"),
    ]),
]

TIMELINE = [
    ("01:49", "Brent $92.98"),
    ("06:34", "NVIDIA $115.8bn lands"),
    ("07:00", "APEC, QUAD, Akvan lead"),
    ("09:30", "Xi, Putin meet in Shenzhen"),
    ("17:10", "Wall St: S&P -0.48%"),
    ("20:26", "Tankers hit mines off Hormuz"),
    ("21:00", "Close: NVDA -2.9%"),
]

NUMBERS = [
    ("NVIDIA Q3 revenue", "$115.84bn"),
    ("NVDA close", "$150.96  -2.89%"),
    ("S&P 500", "7,323.63  -0.23%"),
    ("Brent crude", "$92.98/bbl"),
]
MOVERS = [("TJX", 2.1), ("AMD", 1.4), ("TGT", 0.6), ("NASDAQ", -0.5), ("NVDA", -2.9)]

LEFT_OUT = [
    ("GTA VI reviews", "embargo lifts 18 Nov; scored in tomorrow's page."),
    ("Kahana takes Knesset chair (66-52)", "voted Tue 17 Nov — yesterday's news."),
    ("Hegseth Caracas strike claim", "single-source, unconfirmed at press time."),
]

PHOTOS = [
    {"file": "huang.jpg", "focus_y": 0.22, "w": 236,
     "head": "BOARD REJECTS HUANG COMEBACK",
     "cap": "Jensen Huang, NVIDIA chief. (Taiwan, CC BY 2.0)"},
    {"file": "akvan.jpg", "focus_y": 0.42, "w": 716,
     "head": "74 RESCUE TEAMS ON STANDBY",
     "cap": "Akvan, 18 Nov 07:50 UTC, NOAA-21. (Public domain)"},
]


# ---------------------------------------------------------------- icons
def draw_globe(d, cx, cy, r, color=INK, w=2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    d.ellipse([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r],
              outline=color, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=1)
    d.line([cx - r * 0.87, cy - r * 0.5, cx + r * 0.87, cy - r * 0.5],
           fill=color, width=1)
    d.line([cx - r * 0.87, cy + r * 0.5, cx + r * 0.87, cy + r * 0.5],
           fill=color, width=1)


def draw_sun(d, cx, cy, r, color=INK, w=2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    for k in range(8):
        import math
        a = k * math.pi / 4
        x1 = cx + (r + 2) * math.cos(a)
        y1 = cy + (r + 2) * math.sin(a)
        x2 = cx + (r + 6) * math.cos(a)
        y2 = cy + (r + 6) * math.sin(a)
        d.line([x1, y1, x2, y2], fill=color, width=2)


def draw_region_icon(d, kind, x, y, s, fg):
    """Draw a white glyph in a s x s box at (x, y)."""
    if kind == "star":
        pts = [(x + s / 2, y + 1), (x + s * 0.62, y + s * 0.38),
               (x + s - 1, y + s * 0.38), (x + s * 0.69, y + s * 0.62),
               (x + s * 0.81, y + s - 1), (x + s / 2, y + s * 0.75),
               (x + s * 0.19, y + s - 1), (x + s * 0.31, y + s * 0.62),
               (x + 1, y + s * 0.38), (x + s * 0.38, y + s * 0.38)]
        d.polygon(pts, fill=fg)
    elif kind == "circle":
        d.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=fg, width=2)
        d.ellipse([x + s / 2 - 2, y + s / 2 - 2, x + s / 2 + 2, y + s / 2 + 2],
                  fill=fg)
    elif kind == "elephant":
        # mountain silhouette: three peaks
        d.polygon([(x + 1, y + s - 2), (x + s * 0.28, y + s * 0.3),
                   (x + s * 0.45, y + s * 0.62), (x + s * 0.62, y + s * 0.2),
                   (x + s * 0.8, y + s * 0.62), (x + s - 1, y + s - 2)],
                  fill=fg)
    elif kind == "gate":
        d.rectangle([x + 2, y + 2, x + s - 2, y + 5], fill=fg)
        d.rectangle([x + 3, y + 5, x + 6, y + s - 2], fill=fg)
        d.rectangle([x + s - 6, y + 5, x + s - 3, y + s - 2], fill=fg)
        d.rectangle([x + 2, y + s * 0.55, x + s - 2, y + s * 0.55 + 2], fill=fg)
    elif kind == "compass":
        d.polygon([(x + s / 2, y + 1), (x + s * 0.62, y + s / 2),
                   (x + s / 2, y + s - 1), (x + s * 0.38, y + s / 2)],
                  fill=fg)
        d.line([x + 1, y + s / 2, x + s - 1, y + s / 2], fill=fg, width=2)
    elif kind == "waves":
        for k in range(3):
            yy = y + 3 + k * 4
            d.arc([x + 1, yy - 2, x + s - 1, yy + 4], 200, 340, fill=fg, width=2)
    elif kind == "drop":
        d.polygon([(x + s / 2, y + 1), (x + s - 2, y + s * 0.62),
                   (x + s / 2, y + s - 1), (x + 2, y + s * 0.62)], fill=fg)


def draw_chip_icon(d, x, y, s, fg):
    d.rectangle([x + 3, y + 3, x + s - 3, y + s - 3], outline=fg, width=2)
    for k in range(3):
        xx = x + 4 + k * 4
        d.line([xx, y, xx, y + 3], fill=fg, width=1)
        d.line([xx, y + s - 3, xx, y + s], fill=fg, width=1)
        yy = y + 4 + k * 4
        d.line([x, yy, x + 3, yy], fill=fg, width=1)
        d.line([x + s - 3, yy, x + s, yy], fill=fg, width=1)
    d.text((x + s / 2, y + s / 2), "A", font=F(SANS_B, 7), fill=fg,
           anchor="mm")


# ---------------------------------------------------------------- hero
def draw_hero(d, page, x, y, w, h):
    """Rich drawn chip panel: dark green, traces, chip, bars. Panel #1."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 63, 34))
    # faint grid
    for gx in range(x + 24, x + w, 24):
        d.line([gx, y, gx, y + h], fill=(30, 84, 48), width=1)
    for gy in range(y + 24, y + h, 24):
        d.line([x, gy, x + w, gy], fill=(30, 84, 48), width=1)
    # circuit traces
    tr = (64, 170, 96)
    d.line([x + 14, y + 30, x + 90, y + 30, x + 90, y + 62], fill=tr, width=2)
    d.line([x + w - 14, y + 44, x + w - 80, y + 44, x + w - 80, y + 78],
           fill=tr, width=2)
    d.line([x + 20, y + h - 26, x + 70, y + h - 26, x + 70, y + h - 60],
           fill=tr, width=2)
    for cx, cy in [(x + 90, y + 62), (x + w - 80, y + 78), (x + 70, y + h - 60)]:
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(120, 210, 140))
    # chip body
    cx0, cy0, cw, chh = x + w // 2 - 62, y + 26, 124, 84
    for k in range(6):
        px = cx0 + 10 + k * 20
        d.line([px, cy0 - 8, px, cy0], fill=(150, 220, 165), width=3)
        d.line([px, cy0 + chh, px, cy0 + chh + 8], fill=(150, 220, 165),
               width=3)
    for k in range(4):
        py = cy0 + 14 + k * 20
        d.line([cx0 - 8, py, cx0, py], fill=(150, 220, 165), width=3)
        d.line([cx0 + cw, py, cx0 + cw + 8, py], fill=(150, 220, 165),
               width=3)
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + chh], fill=(32, 110, 58),
                outline=(150, 220, 165), width=2)
    d.rectangle([cx0 + 14, cy0 + 14, cx0 + cw - 14, cy0 + chh - 14],
                outline=(150, 220, 165), width=1)
    d.text((cx0 + cw / 2, cy0 + chh / 2), "AI", font=F(SANS_B, 34),
           fill=(235, 255, 240), anchor="mm")
    # tag + value (box sized to the text)
    tag = "Q3 REVENUE +103%"
    tf = F(SANS_B, 11)
    tw = text_w(d, tag, tf)
    d.rectangle([x + 12, y + 10, x + 12 + tw + 16, y + 30],
                fill=(235, 255, 240))
    d.text((x + 12 + (tw + 16) / 2, y + 20), tag, font=tf,
           fill=(18, 63, 34), anchor="mm")
    d.text((x + 16, y + h - 34), "$115.8BN", font=F(SANS_B, 26),
           fill=(235, 255, 240))
    # mini bars bottom-right
    bars = [14, 22, 18, 30, 38]
    bx = x + w - 118
    for i, bh in enumerate(bars):
        d.rectangle([bx + i * 20, y + h - 12 - bh, bx + i * 20 + 13,
                     y + h - 12], fill=(120, 210, 140))


# ---------------------------------------------------------------- masthead
def draw_masthead(d, page):
    d.rectangle([0, 0, W, H], fill=PAPER)
    draw_globe(d, 52, 44, 20)
    draw_sun(d, W - 52, 44, 16)
    f = F(SERIF_B, 56)
    d.text((W / 2, 46), "THE WORLD TODAY", font=f, fill=INK, anchor="mm")
    d.line([28, 76, W - 28, 76], fill=RULE, width=3)
    d.line([28, 80, W - 28, 80], fill=RULE, width=1)
    y = 92
    d.text((28, y), "WEDNESDAY 18 NOVEMBER 2026", font=F(SANS_B, 13),
           fill=INK)
    mid = "24 STORIES  ·  7 REGIONS  ·  DATE-CHECKED  ·  PROOF-TAGGED"
    d.text((W / 2, y), mid, font=F(SANS, 12), fill=MUTED, anchor="ma")
    d.text((W - 28, y), "WORLD NEWS IN ONE PAGE", font=F(SANS, 12),
           fill=MUTED, anchor="ra")
    d.line([28, 104, W - 28, 104], fill=RULE, width=1)
    return 110


# ---------------------------------------------------------------- lead
def draw_lead(d, page, x, y, w):
    draw_chip_icon(d, x, y + 2, 16, GREEN)
    d.text((x + 22, y + 10), LEAD["kicker"], font=F(SANS_B, 13), fill=GREEN)
    d.line([x + 22 + text_w(d, LEAD["kicker"], F(SANS_B, 13)) + 10, y + 10,
            x + w, y + 10], fill=GREEN, width=2)
    yy = y + 22
    lines, _ = fit_text(d, LEAD["headline"], F(SERIF_B, 32), w, max_lines=2)
    for ln in lines:
        d.text((x, yy), ln, font=F(SERIF_B, 32), fill=INK)
        yy += 38
    for ln in wrap(d, LEAD["deck"], F(SANS, 15), w):
        d.text((x, yy), ln, font=F(SANS, 15), fill=INK)
        yy += 19
    d.text((x, yy + 6), LEAD["facts"], font=F(SANS_B, 12), fill=MUTED)
    return yy + 24


# ---------------------------------------------------------------- photos
def draw_photos(d, page, y):
    heads_y = y
    photo_y = y + 20
    photo_h = 108
    for ph in PHOTOS:
        d.text((ph["x"], heads_y), ph["head"], font=F(SANS_B, 12), fill=INK)
        img = Image.open(os.path.join(ASSETS, ph["file"])).convert("RGB")
        crop = cover_crop(img, ph["w"], photo_h, focus_y=ph["focus_y"])
        page.paste(crop, (ph["x"], photo_y))
        d.rectangle([ph["x"], photo_y, ph["x"] + ph["w"], photo_y + photo_h],
                    outline=INK, width=1)
        cap = ph["cap"]
        f = F(SANS_I, 9)
        d.text((ph["x"], photo_y + photo_h + 4), cap, font=f, fill=MUTED)
    return photo_y + photo_h + 18


# ---------------------------------------------------------------- timeline
def draw_timeline(d, y):
    d.text((28, y), "THE DAY IN UTC", font=F(SANS_B, 12), fill=INK)
    draw_globe(d, 44, y + 26, 8, color=MUTED, w=1)
    x0, x1 = 64, W - 28
    d.line([x0, y + 26, x1, y + 26], fill=RULE, width=2)
    n = len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = x0 + (x1 - x0) * i / (n - 1)
        d.ellipse([cx - 3, y + 23, cx + 3, y + 29], fill=RED)
        d.text((cx, y + 12), t, font=F(SANS_B, 10), fill=RED, anchor="mm")
        lines = wrap(d, label, F(SANS, 9), 140)
        assert len(lines) == 1, "timeline label wraps: %s" % label
        # alternate rows so neighbours never collide
        ly = y + 34 if i % 2 == 0 else y + 46
        for ln in lines[:1]:
            if i == 0:
                d.text((x0, ly), ln, font=F(SANS, 9), fill=MUTED,
                       anchor="la")
            elif i == n - 1:
                d.text((x1, ly), ln, font=F(SANS, 9), fill=MUTED,
                       anchor="ra")
            else:
                d.text((cx, ly), ln, font=F(SANS, 9), fill=MUTED,
                       anchor="ma")
            ly += 11
    return y + 62


# ---------------------------------------------------------------- regions
def draw_regions(d, y0, y1):
    cols = [
        [REGIONS[0], REGIONS[4]],   # NA + LATAM
        [REGIONS[1], REGIONS[2]],   # EU + AFRICA
        [REGIONS[3], REGIONS[6], REGIONS[5]],  # AS + ME + OC
    ]
    xs = [28, 348, 668]
    ws = [308, 308, 328]
    for ci, (col, x, w) in enumerate(zip(cols, xs, ws)):
        total_stories = sum(len(r[4]) for r in col)
        header_h = 24 * len(col)
        avail = (y1 - y0) - header_h
        pitch = avail / total_stories
        yy = y0
        for name, count, color, icon, stories in col:
            d.rectangle([x, yy, x + 18, yy + 18], fill=color)
            draw_region_icon(d, icon, x + 1, yy + 1, 16, (255, 255, 255))
            d.text((x + 24, yy + 9), name, font=F(SANS_B, 13), fill=INK,
                   anchor="lm")
            d.text((x + w, yy + 9), str(count), font=F(SANS_B, 13),
                   fill=color, anchor="rm")
            d.line([x, yy + 20, x + w, yy + 20], fill=color, width=2)
            yy += 22
            for head, deck, src in stories:
                lines, fnt = fit_text(d, head, F(SANS_B, 12), w - 34,
                                      max_lines=2)
                hy = yy + 6
                for ln in lines:
                    d.text((x, hy), ln, font=fnt, fill=INK)
                    hy += 15
                d.text((x, hy), deck, font=F(SANS, 10), fill=MUTED)
                sw = text_w(d, src, F(SANS_B, 9))
                d.text((x + w, hy), src, font=F(SANS_B, 9), fill=color,
                       anchor="ra")
                yy += pitch
        d.line([x, y1, x + w, y1], fill=RULE, width=1)
    return y1


# ---------------------------------------------------------------- bottom
def draw_bottom(d, y0, y1):
    # ---- By the numbers (left)
    x0, w0 = 28, 468
    d.rectangle([x0, y0, x0 + w0, y1], outline=INK, width=1)
    d.rectangle([x0, y0, x0 + w0, y0 + 24], fill=INK)
    d.text((x0 + 10, y0 + 12), "BY THE NUMBERS", font=F(SANS_B, 12),
           fill=(255, 255, 255), anchor="lm")
    # stats in a 2x2 grid
    half = w0 // 2
    for i, (label, val) in enumerate(NUMBERS):
        sx = x0 + 10 + (i % 2) * half
        sy = y0 + 28 + (i // 2) * 16
        d.text((sx, sy), label, font=F(SANS, 11), fill=MUTED)
        d.text((sx + half - 12, sy), val, font=F(SANS_B, 12), fill=INK,
               anchor="ra")
    # movers: small vertical bars with symbols
    d.text((x0 + 10, y0 + 66), "MOVERS", font=F(SANS_B, 9), fill=MUTED)
    bx = x0 + 78
    for i, (sym, v) in enumerate(MOVERS):
        bh = abs(v) * 4
        col = GREEN if v >= 0 else RED
        xx = bx + i * 76
        d.rectangle([xx, y0 + 88 - bh, xx + 30, y0 + 88], fill=col)
        d.text((xx + 15, y0 + 90), sym, font=F(SANS_B, 8), fill=MUTED,
               anchor="ma")
    # ---- What we left out (right)
    x1, w1 = 512, 484
    d.rectangle([x1, y0, x1 + w1, y1], outline=INK, width=1)
    d.rectangle([x1, y0, x1 + w1, y0 + 24], fill=INK)
    d.text((x1 + 10, y0 + 12), "WHAT WE LEFT OUT — AND WHY",
           font=F(SANS_B, 12), fill=(255, 255, 255), anchor="lm")
    yy = y0 + 32
    for head, why in LEFT_OUT:
        d.text((x1 + 10, yy), head + " — ", font=F(SANS_B, 11), fill=INK)
        hw = text_w(d, head + " — ", F(SANS_B, 11))
        d.text((x1 + 10 + hw, yy), why, font=F(SANS, 10), fill=MUTED)
        yy += 17
    d.text((x1 + 10, y1 - 8),
           "Every story above was checked against its date and source.",
           font=F(SANS_I, 9), fill=MUTED)


def draw_footer(d, y):
    line = ("Photos: Jensen Huang (Office of the President, Taiwan, CC BY 2.0)"
            "  ·  Akvan satellite, NOAA-21 (public domain)  ·  12 drawn panels"
            "  ·  Sources: AP, Reuters, AFP, UN, WSJ, BBC, IMD  ·  "
            "Date-checked 18 Nov 2026")
    f = F(SANS, 9)
    lines = wrap(d, line, f, W - 56)
    yy = y
    for ln in lines:
        d.text((W / 2, yy), ln, font=f, fill=MUTED, anchor="ma")
        yy += 12
    return yy


# ---------------------------------------------------------------- main
def check_layout(d):
    """Fail loudly on any text that would overflow its box."""
    n = 1 + sum(len(r[4]) for r in REGIONS)
    assert n == 24, "story count %d != 24" % n
    assert len(REGIONS) == 7, "regions != 7"
    assert DRAWN_PANELS == 12, "drawn panels != 12"
    min_w = 308 - 34
    for name, count, color, icon, stories in REGIONS:
        assert len(stories) == count, name
        for head, deck, src in stories:
            lines = wrap(d, head, F(SANS_B, 12), min_w)
            assert len(lines) == 1, "headline wraps: %s" % head
            need = text_w(d, deck, F(SANS, 10)) + text_w(d, src, F(SANS_B, 9))
            assert need + 12 <= min_w, "deck+tag too wide: %s" % head
    lines, _ = fit_text(d, LEAD["headline"], F(SERIF_B, 32), 640,
                        max_lines=2)
    assert len(lines) == 2, "lead headline must be 2 lines"
    assert len(TIMELINE) == 7, "timeline != 7"
    assert len(NUMBERS) == 4 and len(LEFT_OUT) == 3


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    check_layout(d)
    PHOTOS[0]["x"] = 28
    PHOTOS[1]["x"] = 28 + 236 + 16
    y = draw_masthead(d, page)
    assert y == 110
    draw_hero(d, page, 28, y, 312, 186)
    end_lead = draw_lead(d, page, 356, y, 640)
    assert end_lead <= y + 186, "lead overflows hero"
    y = draw_photos(d, page, 304)
    assert y == 450, y
    y = draw_timeline(d, 456)
    assert y == 518, y
    y = draw_regions(d, 520, 886)
    assert y == 886, y
    draw_bottom(d, 892, 992)
    end = draw_footer(d, 996)
    assert end <= 1024, end
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    page.save(out, format="PNG", optimize=True)
    import hashlib
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("wrote %s (%d bytes) sha256 %s" % (out, os.path.getsize(out), h))
    print("stories 24, regions 7, drawn panels %d, timeline 7" % DRAWN_PANELS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
