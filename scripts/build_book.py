# -*- coding: utf-8 -*-
"""
build_book.py — 旅行纪念册构建器
读 book_data.json（每趟一份）+ 照片根目录，产出可发布的多文件站点。

用法：
  python build_book.py --book book_data.json --photos <照片根目录> --out <输出 site 目录>
照片（cover/photos/best）、music、couple 的路径都相对 --photos。
"""
import argparse, io, json, os, shutil, subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--photos", required=True)
    ap.add_argument("--out", required=True)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--template", default=os.path.join(here, "..", "assets", "template.html"))
    a = ap.parse_args()

    from PIL import Image, ImageOps
    D = json.load(io.open(a.book, encoding="utf-8"))
    PHO = a.photos
    SITE = a.out
    if os.path.exists(SITE):
        shutil.rmtree(SITE)

    # 复制离线字体（模板引用 assets/fonts/fonts.css）
    fonts_src = os.path.join(here, "..", "assets", "fonts")
    if os.path.isdir(fonts_src):
        shutil.copytree(fonts_src, os.path.join(SITE, "assets", "fonts"))

    def src(rel):
        p = os.path.join(PHO, rel)
        if not os.path.exists(p):
            raise FileNotFoundError("缺少素材: %s" % p)
        return p

    def save_jpeg(s, out, maxdim, q):
        im = ImageOps.exif_transpose(Image.open(s))
        if im.mode != "RGB":
            im = im.convert("RGB")
        long = max(im.size)
        if long > maxdim:
            r = maxdim / long
            im = im.resize((round(im.width*r), round(im.height*r)), Image.LANCZOS)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.save(out, format="JPEG", quality=q, optimize=True)
        return im.size

    days_out = []
    for i, d in enumerate(D["days"], 1):
        ad = os.path.join(SITE, "assets", "d%d" % i)
        # cover
        cf, ccap = d["cover"]
        cp = os.path.join(ad, "cover.jpg")
        save_jpeg(src(cf), cp, 1700, 83)
        # photos
        photos = d.get("photos", [])
        nph = len(photos)
        pitems = []
        for k, (rf, cap) in enumerate(photos, 1):
            op = os.path.join(ad, "p%02d.jpg" % k)
            (w, h) = save_jpeg(src(rf), op, 1500, 80)
            shape = "landscape" if w >= h else "portrait"
            span = ("w-6" if k == nph else "w-4") if shape == "landscape" else "w-2"
            pitems.append({"src": "assets/d%d/p%02d.jpg" % (i, k), "cap": cap,
                           "shape": shape, "span": span})
        od = {kk: d[kk] for kk in ("d", "date", "week", "city", "title", "places", "story", "bits")}
        od["cover"] = {"src": "assets/d%d/cover.jpg" % i, "cap": ccap}
        od["photos"] = pitems
        days_out.append(od)

    # best
    best_out = None
    if D.get("best"):
        bf, bcap = D["best"]
        bp = os.path.join(SITE, "assets", "best.jpg")
        save_jpeg(src(bf), bp, 1700, 83)
        best_out = {"src": "assets/best.jpg", "cap": bcap}

    # meta
    m = D["meta"]
    music_src = m.get("music")
    couple_src = m.get("couple")
    meta_out = {kk: m.get(kk) for kk in ("en", "title", "range", "days", "authors", "kicker")}
    meta_out["music"] = "assets/music.m4a" if (music_src and os.path.exists(src(music_src))) else None
    meta_out["couple"] = bool(couple_src and os.path.exists(src(couple_src)))

    BOOK = {
        "meta": meta_out,
        "days": days_out,
        "best": best_out,
        "stats": D.get("stats", []),
        "quotes": D.get("quotes", []),
        "capsule": D.get("capsule", {"q": "下一次，我们想去……", "a": None}),
        "ending": D.get("ending"),
        "map": D.get("map"),
    }

    # music transcode
    if meta_out["music"]:
        mp = os.path.join(SITE, "assets", "music.m4a")
        ok = False
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
            r = subprocess.run([ff, "-y", "-i", src(music_src), "-c:a", "aac",
                                "-b:a", "160k", "-movflags", "+faststart", mp],
                               capture_output=True)
            ok = r.returncode == 0
        except Exception:
            ok = False
        if not ok:  # fallback: copy as-is
            shutil.copy(src(music_src), mp)
            print("警告: 未转码，已原样复制音乐")

    # couple -> RGBA png
    if meta_out["couple"]:
        cp = os.path.join(SITE, "assets", "couple.png")
        im = Image.open(src(couple_src))
        im.convert("RGBA").save(cp, format="PNG")

    # inject
    tpl = io.open(a.template, encoding="utf-8").read()
    js = json.dumps(BOOK, ensure_ascii=False)
    assert tpl.count("/*__BOOK__*/null") == 1
    html = tpl.replace("/*__BOOK__*/null", js)
    io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="").write(html)

    nphoto = sum(len(d["photos"]) for d in days_out)
    print("days", len(days_out), "| grid photos", nphoto,
          "| music", bool(meta_out["music"]), "| couple", meta_out["couple"],
          "| map", bool(BOOK["map"]))
    print("index KB", round(len(html.encode("utf-8"))/1024, 1))

if __name__ == "__main__":
    main()
