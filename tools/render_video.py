#!/usr/bin/env python3
"""Render a short explainer video in The Shift design language from a voiceover + word timings + a beat spec.

Usage: python3 tools/render_video.py spec.json out.mp4 [--square]
spec.json = {"audio": "vo.mp3", "words": [{"w": "How", "s": 0.1, "e": 0.3}, ...], "beats": [...], "captions": true}
Each beat: {"cue": "first words spoken", "kind": "title|statement|number|list|seam|end", "bg": "cobalt|paper|night|white", ...}
List items carry their own "cue" so they appear when spoken. Frames are piped to ffmpeg (H.264, yuv420p, 30 fps).
"""
import json
import math
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).parent / "fonts"
COL = {"cobalt": "#1530FF", "cobalt_deep": "#0D1FB8", "coral": "#FF5A5F", "paper": "#E4E1DA", "news": "#9C9890",
       "ink": "#0B0D17", "night": "#0A0B10", "white": "#FFFFFF", "soft": "#D6DBFF", "mist": "#F3F4F8"}
FG = {"cobalt": COL["white"], "night": COL["white"], "paper": COL["ink"], "white": COL["ink"]}
FPS = 30
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(str(FONTS / name), size)
    return _cache[key]


DISPLAY = lambda s: font("Archivo-BlackItalic.ttf", s)
BOLD = lambda s: font("Archivo-ExtraBold.ttf", s)
REG = lambda s: font("Archivo-Regular.ttf", s)
MONO = lambda s: font("JetBrainsMono-Medium.ttf", s)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def find_cue(words, cue, start_idx=0):
    target = [norm(x) for x in cue.split() if norm(x)]
    seq = [norm(w["w"]) for w in words]
    for i in range(start_idx, len(seq)):
        if seq[i:i + len(target)] == target:
            return i
    for i in range(start_idx, len(seq)):  # fallback: first word only
        if seq[i] == target[0]:
            return i
    return None


def wrap_fit(draw, text, fnt_fn, max_w, sizes, max_lines):
    for size in sizes:
        f = fnt_fn(size)
        for width in range(40, 6, -1):
            lines = textwrap.wrap(text, width=width)
            if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
                return f, lines, size
    f = fnt_fn(sizes[-1])
    return f, textwrap.wrap(text, 24)[:max_lines], sizes[-1]


def noise_paper(W, H):
    import random
    im = Image.new("RGB", (W, H), COL["paper"])
    px = im.load()
    rnd = random.Random(7)
    for _ in range(W * H // 18):
        x, y = rnd.randrange(W), rnd.randrange(H)
        v = rnd.randrange(200, 222)
        px[x, y] = (v, v - 3, v - 10)
    return im


class Renderer:
    def __init__(self, spec, W=1920, H=1080):
        self.spec, self.W, self.H = spec, W, H
        self.paper = noise_paper(W, H)
        self.words = spec["words"]
        self.u = W / 1920  # scale unit
        self.margin = int(140 * self.u) if W > H else int(90 * self.u)

    def bg(self, name):
        if name == "paper":
            return self.paper.copy()
        return Image.new("RGB", (self.W, self.H), COL.get(name, COL["cobalt"]))

    # ---------------------------------------------------------------- beat drawers; t = seconds since beat start
    def chrome(self, d, bgname, beat_i, n):
        fg = FG[bgname]
        u = self.u
        # top-left wordmark, bottom progress ticks
        d.text((self.margin, int(56 * u)), "Enablement", font=DISPLAY(int(34 * u)), fill=fg)
        w = d.textlength("Enablement", font=DISPLAY(int(34 * u)))
        x = self.margin + w + 10 * u
        d.line([x + 14 * u, 62 * u, x + 2 * u, 92 * u], fill=COL["coral"], width=max(3, int(5 * u)))
        d.text((x + 22 * u, int(56 * u)), "Works", font=DISPLAY(int(34 * u)), fill=fg)
        for i in range(n):
            x0 = self.W - self.margin - (n - i) * 46 * u
            d.rounded_rectangle([x0, 66 * u, x0 + 34 * u, 72 * u], radius=3, fill=COL["coral"] if i <= beat_i else (COL["news"] if bgname in ("paper", "white") else "#4b5cff" if bgname == "cobalt" else "#33364a"))

    def eyebrow(self, d, text, x, y, bgname, t):
        if not text:
            return
        f = MONO(int(26 * self.u))
        w = d.textlength(text.upper(), font=f)
        k = ease(t / 0.35)
        d.rounded_rectangle([x, y, x + (w + 32 * self.u) * k, y + 46 * self.u], radius=6, fill=COL["coral"])
        if k > 0.9:
            d.text((x + 16 * self.u, y + 8 * self.u), text.upper(), font=f, fill=COL["white"])

    def draw_big(self, d, text, bgname, t, top, max_lines=3, sizes=(150, 132, 116, 100, 88, 76), color=None):
        fg = color or FG[bgname]
        f, lines, size = wrap_fit(d, text, DISPLAY, self.W - 2 * self.margin, [int(s * self.u) for s in sizes], max_lines)
        y = top
        for i, line in enumerate(lines):
            k = ease((t - 0.08 * i) / 0.45)
            if k <= 0:
                break
            d.text((self.margin, y + (1 - k) * 60 * self.u), line, font=f, fill=fg)
            y += int(size * 1.0)
        return y

    def beat_title(self, img, d, b, t):
        self.eyebrow(d, b.get("eyebrow"), self.margin, int(250 * self.u), b["bg"], t)
        y = self.draw_big(d, b["text"], b["bg"], t - 0.15, int(330 * self.u))
        k = ease((t - 0.7) / 0.6)
        d.rectangle([self.margin, y + 24 * self.u, self.margin + k * 420 * self.u, y + 36 * self.u], fill=COL["coral"])

    def beat_statement(self, img, d, b, t):
        self.eyebrow(d, b.get("eyebrow"), self.margin, int(250 * self.u), b["bg"], t)
        hl = b.get("highlight")
        y = self.draw_big(d, b["text"], b["bg"], t, int(330 * self.u), max_lines=4)
        if b.get("sub"):
            k = ease((t - 0.6) / 0.4)
            if k > 0:
                d.text((self.margin, y + 30 * self.u + (1 - k) * 30 * self.u), b["sub"], font=BOLD(int(40 * self.u)), fill=COL["coral"] if b["bg"] != "paper" else COL["cobalt"])

    def beat_number(self, img, d, b, t):
        self.eyebrow(d, b.get("eyebrow"), self.margin, int(240 * self.u), b["bg"], t)
        k = ease(t / 0.5)
        f = DISPLAY(int(300 * self.u))
        d.text((self.margin - (1 - k) * 80 * self.u, int(320 * self.u)), b["number"], font=f, fill=COL["coral"] if b["bg"] in ("night", "cobalt") else COL["cobalt"])
        k2 = ease((t - 0.5) / 0.4)
        if k2 > 0:
            fl, lines, size = wrap_fit(d, b["label"], BOLD, self.W - 2 * self.margin, [int(46 * self.u), int(40 * self.u)], 2)
            y = int(690 * self.u)
            for line in lines:
                d.text((self.margin, y + (1 - k2) * 30 * self.u), line, font=fl, fill=FG[b["bg"]])
                y += int(size * 1.25)

    def beat_list(self, img, d, b, t, now):
        fg = FG[b["bg"]]
        d.text((self.margin, int(220 * self.u)), b["heading"], font=DISPLAY(int(84 * self.u)), fill=fg)
        y = int(380 * self.u)
        n = len(b["items"])
        step = min(int(150 * self.u), int((self.H - y - 140 * self.u) / max(1, n)))
        for i, it in enumerate(b["items"]):
            st = it.get("_t", 0)
            k = ease((now - st) / 0.45)
            if k <= 0:
                y += step
                continue
            x = self.margin + (1 - k) * 80 * self.u
            d.text((x, y + 8 * self.u), f"{i + 1:02d}", font=MONO(int(40 * self.u)), fill=COL["coral"])
            f, lines, size = wrap_fit(d, it["text"], BOLD, self.W - 2 * self.margin - 120 * self.u, [int(64 * self.u), int(56 * self.u), int(48 * self.u)], 2)
            yy = y
            for line in lines:
                d.text((x + 110 * self.u, yy), line, font=f, fill=fg)
                yy += int(size * 1.08)
            if it.get("note"):
                d.text((x + 110 * self.u, yy + 4 * self.u), it["note"], font=MONO(int(28 * self.u)), fill=COL["news"] if b["bg"] == "paper" else COL["soft"])
            y += step

    def beat_seam(self, img, d, b, t):
        W, H, u = self.W, self.H, self.u
        k = ease(t / 1.4)
        seam = int(W * (0.92 - 0.42 * k))
        img.paste(self.paper.crop((0, 0, seam, H)), (0, 0))
        d.rectangle([seam, 0, W, H], fill=COL["cobalt"])
        # before half
        d.rectangle([self.margin, int(200 * u), self.margin + 190 * u, int(250 * u)], fill=COL["ink"])
        d.text((self.margin + 18 * u, int(208 * u)), "BEFORE", font=BOLD(int(30 * u)), fill=COL["paper"])
        f, lines, size = wrap_fit(d, b["before"], DISPLAY, W * 0.42 - self.margin, [int(s * u) for s in (110, 96, 84, 72, 62)], 4)
        y = int(300 * u)
        for line in lines:
            d.text((self.margin, y), line, font=f, fill="#262626")
            y += size
        # after half (only once the seam has moved past the middle-ish)
        ax = W // 2 + int(60 * u)
        if seam < W * 0.6:
            k2 = ease((t - 1.0) / 0.5)
            d.rectangle([ax, int(200 * u), ax + 160 * u, int(250 * u)], fill=COL["coral"])
            d.text((ax + 18 * u, int(208 * u)), "AFTER", font=BOLD(int(30 * u)), fill=COL["white"])
            f2, lines2, size2 = wrap_fit(d, b["after"], DISPLAY, W - ax - self.margin, [int(s * u) for s in (110, 96, 84, 72, 62)], 4)
            y = int(300 * u)
            for line in lines2:
                d.text((ax + (1 - k2) * 50 * u, y), line, font=f2, fill=COL["white"])
                y += size2
        d.rectangle([seam - 2, 0, seam + 2, H], fill=COL["white"])
        r = int(34 * u)
        cy = H // 2
        d.ellipse([seam - r, cy - r, seam + r, cy + r], fill=COL["white"])
        d.line([seam - 10 * u, cy - 12 * u, seam - 22 * u, cy, seam - 10 * u, cy + 12 * u], fill=COL["coral"], width=int(5 * u))
        d.line([seam + 10 * u, cy - 12 * u, seam + 22 * u, cy, seam + 10 * u, cy + 12 * u], fill=COL["coral"], width=int(5 * u))

    def beat_end(self, img, d, b, t):
        y = self.draw_big(d, b["text"], "night", t, int(270 * self.u), max_lines=3, sizes=(130, 112, 96, 84))
        k = ease((t - 0.6) / 0.5)
        if k > 0:
            f = MONO(int(44 * self.u))
            url = b.get("url", "enablement.works")
            w = d.textlength(url, font=f)
            x, yy = self.margin, y + 50 * self.u
            d.rounded_rectangle([x, yy, x + (w + 60 * self.u) * k, yy + 86 * self.u], radius=12, fill=COL["coral"])
            if k > 0.9:
                d.text((x + 30 * self.u, yy + 18 * self.u), url, font=f, fill=COL["white"])

    # ---------------------------------------------------------------- captions
    def caption(self, d, now, bgname):
        if not self.spec.get("captions", True):
            return
        cur = [w for w in self.words if w["s"] - 0.05 <= now <= w["e"] + 0.35]
        if not cur:
            return
        # caption = the phrase (up to 7 words) around the current word
        idx = self.words.index(cur[-1])
        start = max(0, idx - (idx % 6))
        text = " ".join(w["w"] for w in self.words[start:start + 6])
        f = MONO(int(30 * self.u))
        w = d.textlength(text, font=f)
        x, y = (self.W - w) / 2, self.H - 110 * self.u
        d.rounded_rectangle([x - 18 * self.u, y - 10 * self.u, x + w + 18 * self.u, y + 46 * self.u], radius=8, fill=COL["ink"])
        d.text((x, y), text, font=f, fill=COL["white"])

    def run(self, out):
        words = self.words
        beats = self.spec["beats"]
        dur = self.spec.get("duration") or (words[-1]["e"] + 1.6)
        idx = 0
        for b in beats:
            i = find_cue(words, b["cue"], idx)
            b["_t"] = words[i]["s"] if i is not None else (beats[beats.index(b) - 1]["_t"] + 3 if beats.index(b) else 0)
            if i is not None:
                idx = i
            for it in b.get("items", []):
                j = find_cue(words, it["cue"], idx) if it.get("cue") else None
                it["_t"] = words[j]["s"] if j is not None else b["_t"] + 0.4
                if j is not None:
                    idx = j
        beats[0]["_t"] = 0.0
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{self.W}x{self.H}", "-r", str(FPS), "-i", "-",
               "-i", self.spec["audio"], "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
               "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-shortest", "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n_frames = int(math.ceil(dur * FPS))
        for fi in range(n_frames):
            now = fi / FPS
            bi = max(i for i, b in enumerate(beats) if b["_t"] <= now + 1e-6)
            b = beats[bi]
            t = now - b["_t"]
            img = self.bg(b["bg"] if b["kind"] != "end" else "night")
            d = ImageDraw.Draw(img)
            kind = b["kind"]
            if kind == "list":
                self.beat_list(img, d, b, t, now)
            elif kind == "seam":
                self.beat_seam(img, d, b, t)
            else:
                getattr(self, "beat_" + kind)(img, d, b, t)
            if kind != "seam":
                self.chrome(d, b["bg"] if kind != "end" else "night", bi, len(beats))
            self.caption(d, now, b["bg"])
            p.stdin.write(img.tobytes())
        p.stdin.close()
        p.wait()
        return dur


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    square = "--square" in sys.argv
    r = Renderer(spec, *( (1080, 1350) if square else (1920, 1080) ))
    print("rendered", out, round(r.run(out), 1), "s")
