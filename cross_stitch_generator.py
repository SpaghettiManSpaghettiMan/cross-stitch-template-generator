#!/usr/bin/env python3
"""
Cross-Stitch Template Generator
================================
Converts any image into a printable cross-stitch pattern with:
  - PNG chart (full-resolution grid with symbols — works on iPhone)
  - SVG chart (scalable, zoomable)
  - Printable PDF (tiled across pages with legend)
  - DMC thread color matching

Usage:
    python cross_stitch_generator.py <input_image> [options]

Options:
    --width   Grid width in stitches (default: 80)
    --height  Grid height in stitches (auto if omitted, preserves aspect ratio)
    --colors  Max number of thread colors (default: auto, 8-24 based on image)
    --output  Output folder (default: ./cross_stitch_output)
    --name    Project name (default: derived from input filename)
"""

import sys
import os
import math
import argparse
from pathlib import Path

from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

DMC_COLORS = [
    (255, 255, 255, "blanc", "White"),
    (255, 252, 242, "3865", "Winter White"),
    (245, 235, 220, "3866", "Ultra V Lt Mocha Brown"),
    (240, 234, 218, "822",  "Lt Beige Gray"),
    (228, 214, 196, "644",  "Med Beige Gray"),
    (204, 192, 176, "642",  "Dk Beige Gray"),
    (163, 152, 138, "640",  "V Dk Beige Gray"),
    (120, 112, 100, "3787", "Dk Brown Gray"),
    ( 50,  47,  41, "3021", "V Dk Brown Gray"),
    (  0,   0,   0, "310",  "Black"),
    (255, 200, 200, "963",  "Ultra V Lt Dusty Rose"),
    (255, 160, 170, "3716", "Med Lt Dusty Rose"),
    (242, 120, 140, "899",  "Med Rose"),
    (228,  80, 110, "335",  "Rose"),
    (200,  50,  80, "309",  "Deep Rose"),
    (190,  30,  55, "815",  "Med Garnet"),
    (150,  20,  40, "816",  "Garnet"),
    (110,  10,  20, "814",  "Dk Garnet"),
    (255, 180, 190, "761",  "Lt Salmon"),
    (255, 140, 150, "760",  "Salmon"),
    (240, 100, 110, "3712", "Med Salmon"),
    (210,  70,  80, "347",  "V Dk Salmon"),
    (255, 160, 160, "3713", "V Lt Salmon"),
    (240,  60,  60, "606",  "Bright Orange-Red"),
    (220,  30,  30, "666",  "Bright Red"),
    (180,  20,  20, "321",  "Red"),
    (140,  10,  10, "498",  "Dk Red"),
    (255, 220, 160, "3823", "Ultra Pale Yellow"),
    (255, 240, 120, "3078", "V Lt Golden Yellow"),
    (255, 230,  80, "727",  "V Lt Topaz"),
    (255, 210,  40, "725",  "Med Lt Topaz"),
    (255, 190,   0, "972",  "Deep Canary"),
    (240, 170,   0, "971",  "Pumpkin"),
    (240, 150,   0, "970",  "Med Lt Pumpkin"),
    (230, 120,   0, "947",  "Burnt Orange"),
    (210, 100,   0, "946",  "Med Burnt Orange"),
    (190,  80,   0, "900",  "Dk Burnt Orange"),
    (160,  60,   0, "919",  "Red Copper"),
    (255, 200,  80, "744",  "Pale Yellow"),
    (255, 220, 100, "745",  "Lt Pale Yellow"),
    (245, 180,  60, "743",  "Med Yellow"),
    (220, 160,  40, "742",  "Lt Tangerine"),
    (200, 130,  20, "741",  "Med Tangerine"),
    (180, 100,  10, "740",  "Tangerine"),
    (255, 230, 190, "951",  "Lt Tawny"),
    (240, 200, 150, "3856", "Ultra V Lt Mahogany"),
    (220, 170, 110, "3827", "Pale Golden Brown"),
    (200, 140,  80, "977",  "Lt Golden Brown"),
    (180, 110,  50, "976",  "Med Golden Brown"),
    (160,  90,  30, "975",  "Dk Golden Brown"),
    (140,  70,  20, "3826", "Golden Brown"),
    (120,  60,  15, "434",  "Lt Brown"),
    (100,  50,  10, "433",  "Med Brown"),
    ( 80,  40,   5, "801",  "Dk Coffee Brown"),
    ( 60,  30,   5, "938",  "Ultra Dk Coffee Brown"),
    (200, 160, 120, "3855", "Lt Autumn Gold"),
    (180, 130,  90, "3854", "Med Autumn Gold"),
    (160, 100,  60, "3853", "Dk Autumn Gold"),
    (200, 150, 100, "437",  "Lt Tan"),
    (180, 130,  80, "436",  "Tan"),
    (160, 110,  60, "435",  "V Lt Brown"),
    (220, 240, 200, "772",  "V Lt Yellow Green"),
    (190, 220, 160, "3348", "Lt Yellow Green"),
    (160, 200, 120, "3347", "Med Yellow Green"),
    (120, 170,  80, "3346", "Hunter Green"),
    ( 80, 140,  40, "3345", "Dk Hunter Green"),
    (190, 220, 170, "369",  "V Lt Pistachio Green"),
    (160, 200, 140, "368",  "Lt Pistachio Green"),
    (120, 170, 100, "320",  "Med Pistachio Green"),
    ( 80, 130,  60, "367",  "Dk Pistachio Green"),
    ( 50,  90,  30, "319",  "V Dk Pistachio Green"),
    (180, 210, 160, "164",  "Lt Forest Green"),
    (140, 180, 110, "989",  "Forest Green"),
    (100, 150,  70, "988",  "Med Forest Green"),
    ( 60, 110,  40, "987",  "Dk Forest Green"),
    (  0,  80,   0, "986",  "V Dk Forest Green"),
    (160, 210, 180, "954",  "Nile Green"),
    (100, 170, 130, "913",  "Med Nile Green"),
    ( 50, 130,  80, "912",  "Lt Emerald Green"),
    (  0, 100,  50, "911",  "Med Emerald Green"),
    (  0,  70,  30, "910",  "Dk Emerald Green"),
    (180, 220, 190, "966",  "Med Baby Green"),
    (140, 190, 160, "564",  "V Lt Jade"),
    ( 90, 160, 120, "563",  "Lt Jade"),
    ( 50, 130,  80, "562",  "Med Jade"),
    ( 20,  90,  50, "561",  "V Dk Jade"),
    (200, 220, 190, "3817", "Lt Celadon Green"),
    (160, 190, 150, "3816", "Celadon Green"),
    (110, 150, 100, "3815", "Dk Celadon Green"),
    (160, 200, 150, "503",  "Med Blue Green"),
    (120, 170, 120, "502",  "Blue Green"),
    ( 80, 130,  80, "501",  "Dk Blue Green"),
    ( 40,  90,  50, "500",  "V Dk Blue Green"),
    (200, 230, 250, "3747", "V Lt Blue Violet"),
    (160, 200, 240, "341",  "Lt Blue Violet"),
    (100, 150, 210, "340",  "Med Blue Violet"),
    ( 60, 100, 170, "333",  "V Dk Blue Violet"),
    (190, 220, 245, "3756", "Ultra V Lt Baby Blue"),
    (160, 200, 235, "3755", "Baby Blue"),
    (100, 160, 210, "334",  "Med Baby Blue"),
    ( 50, 110, 170, "322",  "Dk Baby Blue"),
    ( 10,  70, 140, "312",  "V Dk Baby Blue"),
    (  0,  40, 100, "336",  "Navy Blue"),
    (180, 210, 235, "827",  "V Lt Blue"),
    (140, 185, 215, "813",  "Lt Blue"),
    ( 90, 145, 190, "826",  "Med Blue"),
    ( 50, 100, 160, "825",  "Dk Blue"),
    ( 20,  60, 120, "824",  "V Dk Blue"),
    (  0,  30,  80, "823",  "Dk Navy Blue"),
    (180, 215, 235, "3325", "Lt Baby Blue"),
    (100, 155, 200, "3753", "Ultra V Lt Antique Blue"),
    ( 80, 130, 175, "932",  "Lt Antique Blue"),
    ( 60, 105, 150, "931",  "Med Antique Blue"),
    ( 40,  80, 120, "930",  "Dk Antique Blue"),
    ( 20,  50,  90, "939",  "V Dk Navy Blue"),
    (160, 210, 225, "747",  "V Lt Sky Blue"),
    (100, 175, 205, "3761", "Lt Sky Blue"),
    ( 50, 140, 180, "519",  "Sky Blue"),
    ( 10, 110, 160, "518",  "Lt Wedgwood"),
    (  0,  80, 130, "517",  "Med Wedgwood"),
    (240, 210, 240, "3743", "V Lt Antique Violet"),
    (210, 175, 215, "3042", "Lt Antique Violet"),
    (170, 130, 175, "3041", "Med Antique Violet"),
    (130,  90, 135, "3740", "Dk Antique Violet"),
    (220, 190, 235, "211",  "Lt Lavender"),
    (190, 155, 215, "210",  "Med Lavender"),
    (150, 110, 185, "209",  "Dk Lavender"),
    (110,  65, 150, "208",  "V Dk Lavender"),
    (200, 160, 220, "554",  "Lt Violet"),
    (165, 110, 190, "553",  "Violet"),
    (120,  60, 150, "552",  "Med Violet"),
    ( 80,  20, 110, "550",  "V Dk Violet"),
    (220, 180, 230, "3836", "Lt Grape"),
    (175, 130, 195, "3835", "Med Grape"),
    (130,  80, 155, "3834", "Dk Grape"),
    (195, 160, 215, "3837", "Ultra Dk Lavender"),
    (240, 240, 240, "762",  "V Lt Pearl Gray"),
    (200, 200, 200, "415",  "Pearl Gray"),
    (160, 160, 160, "318",  "Lt Steel Gray"),
    (120, 120, 120, "414",  "Dk Steel Gray"),
    ( 80,  80,  80, "317",  "Pewter Gray"),
    ( 50,  50,  50, "413",  "Dk Pewter Gray"),
    (100, 110, 115, "3799", "V Dk Pewter Gray"),
    (180, 235, 230, "3811", "V Lt Turquoise"),
    (130, 210, 210, "3810", "Dk Turquoise"),
    ( 80, 185, 185, "3809", "V Dk Turquoise"),
    ( 30, 150, 155, "3808", "Ultra V Dk Turquoise"),
    (160, 225, 220, "964",  "Lt Seagreen"),
    (100, 195, 195, "959",  "Med Seagreen"),
    ( 50, 165, 160, "958",  "Dk Seagreen"),
    (  0, 130, 120, "943",  "Med Aquamarine"),
    (  0, 100,  90, "991",  "Dk Aquamarine"),
    (  0,  70,  60, "992",  "Lt Aquamarine"),
    (255, 225, 195, "3774", "V Lt Desert Sand"),
    (245, 205, 170, "948",  "V Lt Peach"),
    (235, 185, 145, "353",  "Peach"),
    (220, 160, 115, "352",  "Lt Coral"),
    (200, 130,  90, "351",  "Coral"),
    (180, 105,  70, "350",  "Med Coral"),
    (255, 220, 185, "3770", "V Lt Tawny"),
    (240, 195, 155, "945",  "Tawny"),
    (200, 135,  80, "402",  "V Lt Mahogany"),
    (175, 100,  50, "3776", "Lt Mahogany"),
    (150,  75,  30, "301",  "Med Mahogany"),
    (120,  55,  15, "400",  "Dk Mahogany"),
]

_seen = set()
_deduped = []
for row in DMC_COLORS:
    key = row[3]
    if key not in _seen:
        _seen.add(key)
        _deduped.append(row)
DMC_COLORS = _deduped

def rgb_to_lab(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = linearize(r), linearize(g), linearize(b)
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    def f(t):
        return t ** (1/3) if t > 0.008856 else 7.787 * t + 16/116
    fx, fy, fz = f(X / Xn), f(Y / Yn), f(Z / Zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return (L, a, b_val)

DMC_LAB = [(rgb_to_lab(row[:3]), row) for row in DMC_COLORS]

def nearest_dmc(rgb):
    lab = rgb_to_lab(rgb)
    best_dist = float('inf')
    best = DMC_COLORS[0]
    for dmc_lab, row in DMC_LAB:
        dist = sum((a - b) ** 2 for a, b in zip(lab, dmc_lab))
        if dist < best_dist:
            best_dist = dist
            best = row
    return best

SYMBOLS = (
    list("ABCDEFGHJKLMNPQRSTUVWXYZ") +
    list("234567890") +
    ["!", "@", "#", "$", "%", "&", "?", "+", "=", "~", "<", ">"]
)

def auto_color_count(image_array):
    flat = image_array.reshape(-1, 3)
    sample = flat[::max(1, len(flat)//5000)]
    unique = np.unique(sample, axis=0)
    n = len(unique)
    if n < 50:   return max(4, n)
    if n < 200:  return 12
    if n < 1000: return 16
    return 20

def process_image(img_path, grid_w, grid_h=None, max_colors=None):
    img = Image.open(img_path).convert("RGB")
    ow, oh = img.size
    if grid_h is None:
        grid_h = max(1, round(grid_w * oh / ow))
    small = img.resize((grid_w, grid_h), Image.LANCZOS)
    arr = np.array(small, dtype=np.float32)
    if max_colors is None:
        max_colors = auto_color_count(arr)
    max_colors = max(4, min(max_colors, len(SYMBOLS)))
    pixels = arr.reshape(-1, 3)
    km = KMeans(n_clusters=max_colors, n_init=10, random_state=42)
    km.fit(pixels)
    centers = km.cluster_centers_
    labels = km.labels_.reshape(grid_h, grid_w)
    cluster_to_dmc = {}
    for i, center in enumerate(centers):
        cluster_to_dmc[i] = nearest_dmc(tuple(int(c) for c in center))
    grid = []
    for row in labels:
        grid.append([cluster_to_dmc[c] for c in row])
    counts = {}
    for row in grid:
        for cell in row:
            key = cell[3]
            counts[key] = counts.get(key, 0) + 1
    seen_keys = set()
    palette_order = []
    for row in grid:
        for cell in row:
            if cell[3] not in seen_keys:
                seen_keys.add(cell[3])
                palette_order.append(cell)
    palette = []
    for i, dmc_entry in enumerate(palette_order):
        sym = SYMBOLS[i % len(SYMBOLS)]
        palette.append((dmc_entry, sym, counts.get(dmc_entry[3], 0)))
    sym_map = {p[0][3]: p[1] for p in palette}
    return grid, palette, sym_map


# ──────────────────────────────────────────────
# PNG OUTPUT  (symbols + legend — works on iPhone)
# ──────────────────────────────────────────────

def render_png(grid, palette, sym_map, out_path, cell_size=20, font_size=10):
    """Render a color-filled grid PNG with symbols and legend. Works on iPhone."""
    from PIL import ImageDraw, ImageFont

    rows = len(grid)
    cols = len(grid[0])

    LEGEND_W = 300
    HEADER_H = 50
    img_w = cols * cell_size + LEGEND_W
    img_h = max(rows * cell_size + HEADER_H, len(palette) * 28 + HEADER_H + 30)

    img = Image.new("RGB", (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to load a legible font; fall back gracefully
    font = font_bold = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try:
            font      = ImageFont.truetype(font_path, font_size)
            font_bold = ImageFont.truetype(font_path, font_size + 1)
            break
        except Exception:
            pass
    if font is None:
        font = font_bold = ImageFont.load_default()

    # Header
    draw.text((8, 8),  "Cross-Stitch Pattern", fill=(30, 30, 30), font=font_bold)
    draw.text((8, 28), f"{cols} \u00d7 {rows} stitches \u2014 {len(palette)} colors",
              fill=(100, 100, 100), font=font)

    g_x_off = 0
    g_y_off = HEADER_H

    # Draw cells
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            x0 = c * cell_size + g_x_off
            y0 = r * cell_size + g_y_off
            x1 = x0 + cell_size - 1
            y1 = y0 + cell_size - 1
            fill = (cell[0], cell[1], cell[2])
            draw.rectangle([x0, y0, x1, y1], fill=fill, outline=(180, 180, 180))

            sym = sym_map[cell[3]]
            lum = 0.299 * cell[0] + 0.587 * cell[1] + 0.114 * cell[2]
            txt_fill = (0, 0, 0) if lum > 128 else (255, 255, 255)

            # Center symbol in cell
            try:
                bbox = draw.textbbox((0, 0), sym, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except AttributeError:
                tw, th = draw.textsize(sym, font=font)
            tx = x0 + (cell_size - tw) // 2
            ty = y0 + (cell_size - th) // 2
            draw.text((tx, ty), sym, fill=txt_fill, font=font)

    # Bold 10-stitch grid lines
    for r in range(0, rows + 1, 10):
        y = r * cell_size + g_y_off
        draw.line([(g_x_off, y), (cols * cell_size, y)], fill=(80, 80, 80), width=1)
    for c_ in range(0, cols + 1, 10):
        x = c_ * cell_size + g_x_off
        draw.line([(x, g_y_off), (x, rows * cell_size + g_y_off)], fill=(80, 80, 80), width=1)

    # Legend
    lx = cols * cell_size + 10
    draw.text((lx, HEADER_H + 4), "Thread Legend", fill=(50, 50, 50), font=font_bold)
    for i, (dmc_entry, sym, count) in enumerate(palette):
        ly = HEADER_H + 26 + i * 28
        swatch_fill = (dmc_entry[0], dmc_entry[1], dmc_entry[2])
        draw.rectangle([lx, ly, lx + 22, ly + 22], fill=swatch_fill, outline=(120, 120, 120))
        lum = 0.299 * dmc_entry[0] + 0.587 * dmc_entry[1] + 0.114 * dmc_entry[2]
        sym_fill = (0, 0, 0) if lum > 128 else (255, 255, 255)
        try:
            bbox = draw.textbbox((0, 0), sym, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except AttributeError:
            tw, th = draw.textsize(sym, font=font)
        draw.text((lx + (22 - tw) // 2, ly + (22 - th) // 2), sym, fill=sym_fill, font=font)
        label = f"DMC {dmc_entry[3]} \u2014 {dmc_entry[4]} ({count} ct)"
        draw.text((lx + 28, ly + 5), label, fill=(50, 50, 50), font=font)

    img.save(out_path, "PNG")
    print(f"  \u2713 PNG saved: {out_path}")


# ──────────────────────────────────────────────
# SVG OUTPUT
# ──────────────────────────────────────────────

def render_svg(grid, palette, sym_map, out_path, cell_size=16):
    rows = len(grid)
    cols = len(grid[0])
    LEGEND_W = 260
    HEADER_H = 50
    svg_w = cols * cell_size + LEGEND_W
    svg_h = max(rows * cell_size + HEADER_H, len(palette) * 26 + HEADER_H + 30)
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
                 f'viewBox="0 0 {svg_w} {svg_h}" style="background:#fff;font-family:sans-serif">')
    lines.append(f'<text x="10" y="30" font-size="18" font-weight="bold" fill="#222">Cross-Stitch Pattern</text>')
    lines.append(f'<text x="10" y="46" font-size="11" fill="#666">{cols} \u00d7 {rows} stitches \u2014 {len(palette)} colors</text>')
    g_x_off = 0
    g_y_off = HEADER_H
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            x = c * cell_size + g_x_off
            y = r * cell_size + g_y_off
            fill = f"rgb({cell[0]},{cell[1]},{cell[2]})"
            sym = sym_map[cell[3]]
            lum = 0.299 * cell[0] + 0.587 * cell[1] + 0.114 * cell[2]
            txt_fill = "#000" if lum > 128 else "#fff"
            lines.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#ccc" stroke-width="0.4"/>'
            )
            lines.append(
                f'<text x="{x + cell_size//2}" y="{y + cell_size//2 + 4}" '
                f'text-anchor="middle" font-size="{cell_size - 4}" fill="{txt_fill}">{sym}</text>'
            )
    for r in range(0, rows + 1, 10):
        y = r * cell_size + g_y_off
        lines.append(f'<line x1="{g_x_off}" y1="{y}" x2="{cols*cell_size}" y2="{y}" stroke="#666" stroke-width="0.8"/>')
    for c in range(0, cols + 1, 10):
        x = c * cell_size + g_x_off
        lines.append(f'<line x1="{x}" y1="{g_y_off}" x2="{x}" y2="{rows*cell_size+g_y_off}" stroke="#666" stroke-width="0.8"/>')
    lx = cols * cell_size + 10
    lines.append(f'<text x="{lx}" y="{HEADER_H + 15}" font-size="13" font-weight="bold" fill="#333">Thread Legend</text>')
    for i, (dmc_entry, sym, count) in enumerate(palette):
        ly = HEADER_H + 30 + i * 26
        fill = f"rgb({dmc_entry[0]},{dmc_entry[1]},{dmc_entry[2]})"
        lum = 0.299 * dmc_entry[0] + 0.587 * dmc_entry[1] + 0.114 * dmc_entry[2]
        txt_fill = "#000" if lum > 128 else "#fff"
        lines.append(f'<rect x="{lx}" y="{ly}" width="20" height="20" fill="{fill}" stroke="#999" stroke-width="1"/>')
        lines.append(f'<text x="{lx+10}" y="{ly+14}" text-anchor="middle" font-size="12" fill="{txt_fill}">{sym}</text>')
        label = f"DMC {dmc_entry[3]} \u2014 {dmc_entry[4]} ({count} ct)"
        lines.append(f'<text x="{lx+26}" y="{ly+14}" font-size="11" fill="#333">{label}</text>')
    lines.append('</svg>')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  \u2713 SVG saved: {out_path}")


# ──────────────────────────────────────────────
# PDF OUTPUT
# ──────────────────────────────────────────────

def render_pdf(grid, palette, sym_map, out_path, project_name="Cross-Stitch Pattern"):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as rl_canvas

    PAGE_W, PAGE_H = letter
    MARGIN = 36
    CELL = 14

    rows = len(grid)
    cols = len(grid[0])

    CELLS_PER_ROW = int((PAGE_W - 2 * MARGIN) // CELL)
    CELLS_PER_COL = int((PAGE_H - 2 * MARGIN - 30) // CELL)

    c = rl_canvas.Canvas(out_path, pagesize=letter)

    page_num = 0
    for tile_r in range(0, rows, CELLS_PER_COL):
        for tile_c in range(0, cols, CELLS_PER_ROW):
            page_num += 1
            c.setFont("Helvetica-Bold", 10)
            c.drawString(MARGIN, PAGE_H - MARGIN, project_name)
            r_end = min(tile_r + CELLS_PER_COL, rows)
            c_end = min(tile_c + CELLS_PER_ROW, cols)
            section_label = f"Rows {tile_r+1}-{r_end}, Cols {tile_c+1}-{c_end}  |  Page {page_num}"
            c.setFont("Helvetica", 8)
            c.drawString(MARGIN, PAGE_H - MARGIN - 14, section_label)
            base_y = PAGE_H - MARGIN - 30
            for r in range(tile_r, r_end):
                for col in range(tile_c, c_end):
                    cell = grid[r][col]
                    x = MARGIN + (col - tile_c) * CELL
                    y = base_y - (r - tile_r + 1) * CELL
                    c.setFillColorRGB(cell[0]/255, cell[1]/255, cell[2]/255)
                    c.rect(x, y, CELL, CELL, fill=1, stroke=0)
                    c.setStrokeColorRGB(0.7, 0.7, 0.7)
                    c.setLineWidth(0.3)
                    c.rect(x, y, CELL, CELL, fill=0, stroke=1)
                    lum = 0.299 * cell[0] + 0.587 * cell[1] + 0.114 * cell[2]
                    if lum > 128:
                        c.setFillColorRGB(0, 0, 0)
                    else:
                        c.setFillColorRGB(1, 1, 1)
                    c.setFont("Helvetica", 6)
                    c.drawCentredString(x + CELL/2, y + CELL/2 - 3, sym_map[cell[3]])
            c.setStrokeColorRGB(0.3, 0.3, 0.3)
            c.setLineWidth(0.8)
            for step in range(0, c_end - tile_c + 1, 10):
                cx = MARGIN + step * CELL
                c.line(cx, base_y, cx, base_y - (r_end - tile_r) * CELL)
            for step in range(0, r_end - tile_r + 1, 10):
                ry = base_y - step * CELL
                c.line(MARGIN, ry, MARGIN + (c_end - tile_c) * CELL, ry)
            c.showPage()

    # Legend page
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, PAGE_H - MARGIN, f"{project_name} -- Thread Legend")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, PAGE_H - MARGIN - 16, f"{cols} x {rows} stitches  |  {len(palette)} DMC thread colors")
    y_pos = PAGE_H - MARGIN - 45
    for i, (dmc_entry, sym, count) in enumerate(palette):
        if y_pos < MARGIN + 20:
            c.showPage()
            y_pos = PAGE_H - MARGIN
        c.setFillColorRGB(dmc_entry[0]/255, dmc_entry[1]/255, dmc_entry[2]/255)
        c.rect(MARGIN, y_pos - 12, 20, 14, fill=1, stroke=1)
        lum = 0.299 * dmc_entry[0] + 0.587 * dmc_entry[1] + 0.114 * dmc_entry[2]
        c.setFillColorRGB(0 if lum > 128 else 1, 0 if lum > 128 else 1, 0 if lum > 128 else 1)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(MARGIN + 10, y_pos - 7, sym)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 26, y_pos - 5, f"DMC {dmc_entry[3]}")
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 75, y_pos - 5, f"{dmc_entry[4]}")
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(MARGIN + 260, y_pos - 5, f"{count} stitches")
        y_pos -= 20
    c.showPage()
    c.save()
    print(f"  \u2713 PDF saved: {out_path}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate cross-stitch templates from images")
    parser.add_argument("image", help="Input image path (JPG, PNG, etc.)")
    parser.add_argument("--width",  type=int, default=80,   help="Grid width in stitches (default: 80)")
    parser.add_argument("--height", type=int, default=None, help="Grid height in stitches (auto if omitted)")
    parser.add_argument("--colors", type=int, default=None, help="Max thread colors (auto if omitted)")
    parser.add_argument("--output", type=str, default="./cross_stitch_output", help="Output folder")
    parser.add_argument("--name",   type=str, default=None, help="Project name")
    args = parser.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"Error: image not found: {img_path}")
        sys.exit(1)

    project_name = args.name or img_path.stem.replace("_", " ").title()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n\U0001f9f5 Cross-Stitch Generator")
    print(f"   Image   : {img_path}")
    print(f"   Project : {project_name}")
    print(f"   Grid W  : {args.width} stitches")
    print(f"   Colors  : {'auto' if args.colors is None else args.colors}")
    print()

    print("Processing image...")
    grid, palette, sym_map = process_image(
        img_path, args.width, args.height, args.colors
    )
    rows = len(grid)
    cols = len(grid[0])
    print(f"  \u2192 Grid: {cols} \u00d7 {rows} stitches, {len(palette)} colors\n")

    print("Generating outputs...")
    base = out_dir / project_name.replace(" ", "_").lower()

    render_png(grid, palette, sym_map, str(base) + "_chart.png")
    render_svg(grid, palette, sym_map, str(base) + "_chart.svg")
    render_pdf(grid, palette, sym_map, str(base) + "_pattern.pdf", project_name)

    print(f"\n\u2705 Done! Files saved to: {out_dir.resolve()}")
    print("\n  Thread list:")
    for dmc_entry, sym, count in palette:
        print(f"    {sym}  DMC {dmc_entry[3]:>5}  {dmc_entry[4]:<35} {count:>5} stitches")


if __name__ == "__main__":
    main()
