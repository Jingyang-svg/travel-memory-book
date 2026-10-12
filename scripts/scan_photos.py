# -*- coding: utf-8 -*-
"""
scan_photos.py — 扫描照片根目录，辅助选片
照片根目录结构（用户低成本整理，文件名随意）：
  <photos>/1/...  2/...  3/...      子目录名 = 第几天
  <photos>/旅途最佳.jpg ...          根目录图片 = 最佳一张候选
产出（默认 <photos>/_scan/）：
  manifest.md          每天照片清单（序号 / 文件名 / 宽×高 / 方向）
  contact_dN.jpg       每天缩略拼版（序号对应清单），Read 后即可选片
"""
import argparse, io, os
from PIL import Image, ImageOps, ImageDraw

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

def load_font(sz):
    for f in ("C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(f):
            from PIL import ImageFont
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def image_info(p):
    try:
        im = ImageOps.exif_transpose(Image.open(p))
        return im.size, None
    except Exception as e:
        return None, str(e)[:40]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ROOT = a.photos
    OUT = a.out or os.path.join(ROOT, "_scan")
    os.makedirs(OUT, exist_ok=True)
    font = load_font(18); fontT = load_font(26)

    subdirs = sorted([d for d in os.listdir(ROOT)
                      if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith("_")
                      and not d.startswith(".")],
                     key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x))
    md = ["# 照片清单（序号对应 contact sheet）", ""]
    root_imgs = [f for f in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, f)) and f.lower().endswith(IMG_EXT)]
    if root_imgs:
        md += ["## 根目录图片（最佳一张候选）"]
        for f in root_imgs:
            size, err = image_info(os.path.join(ROOT, f))
            md.append("- %s — %s" % (f, ("%d×%d" % size) if size else "无法读取 %s" % err))
        md.append("")

    CELL, PAD, COLS = 300, 12, 4
    for sd in subdirs:
        dpath = os.path.join(ROOT, sd)
        files = [f for f in os.listdir(dpath) if f.lower().endswith(IMG_EXT)]
        files.sort()
        rows = []
        for idx, f in enumerate(files, 1):
            size, err = image_info(os.path.join(dpath, f))
            ori = "横" if (size and size[0] >= size[1]) else ("竖" if size else "?")
            rows.append((idx, f, size, ori, err))
        md += ["## Day %s · %d 张" % (sd, len(files))]
        md += ["| # | 文件名 | 尺寸 | 方向 |", "| - | - | - | - |"]
        for idx, f, size, ori, err in rows:
            md.append("| %d | %s | %s | %s |" %
                      (idx, f, ("%d×%d" % size) if size else ("ERR %s" % err), ori))
        md.append("")

        # contact sheet
        n = len(files)
        nr = max(1, (n + COLS - 1)//COLS)
        W = COLS*CELL + (COLS+1)*PAD
        H = 60 + nr*CELL + (nr+1)*PAD
        sheet = Image.new("RGB", (W, H), "#F2EFE8")
        dr = ImageDraw.Draw(sheet)
        dr.text((PAD, 16), "Day %s · %d photos" % (sd, n), fill="#211F1A", font=fontT)
        for j, f in enumerate(files):
            r, c = divmod(j, COLS)
            x = PAD + c*(CELL+PAD); y = 60 + PAD + r*(CELL+PAD)
            try:
                im = ImageOps.exif_transpose(Image.open(os.path.join(dpath, f))).convert("RGB")
                im.thumbnail((CELL-16, CELL-40), Image.LANCZOS)
                px = x + (CELL-im.width)//2; py = y + 24 + (CELL-24-im.height)//2
                sheet.paste(im, (px, py))
            except Exception:
                dr.text((x+10, y+40), "unreadable", fill="#B00", font=font)
            tag = str(j+1)
            tw = dr.textlength(tag, font=font)
            dr.rectangle([x+4, y+2, x+4+tw+12, y+26], fill="#211F1A")
            dr.text((x+10, y+3), tag, fill="#fff", font=font)
        cp = os.path.join(OUT, "contact_d%s.jpg" % sd)
        sheet.save(cp, format="JPEG", quality=82)

    io.open(os.path.join(OUT, "manifest.md"), "w", encoding="utf-8").write("\n".join(md))
    print("days", len(subdirs), "| report ->", os.path.join(OUT, "manifest.md"))

if __name__ == "__main__":
    main()
