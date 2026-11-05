"""Open Graph images (1200x630) and logo/favicon PNGs, drawn with Pillow in the Ledger style."""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SUP = "/System/Library/Fonts/Supplemental/"
BG, INK, PRIMARY, ACCENT, MUTED, LINE = "#F5F6F3", "#15201C", "#14453D", "#87600F", "#58635E", "#D8DCD6"


def font(name, size):
    try:
        return ImageFont.truetype(SUP + name, size)
    except OSError:
        return ImageFont.load_default()


def fit_title(draw, title, max_w, max_lines=4):
    for size in (68, 62, 56, 50, 46, 42):
        f = font("Georgia.ttf", size)
        for width in range(40, 10, -1):
            lines = textwrap.wrap(title, width=width)
            if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
                return f, lines, size
    f = font("Georgia.ttf", 42)
    return f, textwrap.wrap(title, 44)[:max_lines], 42


def og_image(path, title, label):
    im = Image.new("RGB", (1200, 630), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 14], fill=PRIMARY)
    # double rule, the Ledger signature
    d.line([72, 92, 1128, 92], fill=INK, width=2)
    d.line([72, 100, 1128, 100], fill=INK, width=2)
    d.text((72, 48), label.upper(), font=font("Courier New Bold.ttf", 24), fill=ACCENT)
    f, lines, size = fit_title(d, title, 1056)
    y = 140
    for line in lines:
        d.text((72, y), line, font=f, fill=INK)
        y += int(size * 1.18)
    d.line([72, 530, 1128, 530], fill=LINE, width=2)
    d.text((72, 552), "Enablement Works", font=font("Georgia Bold.ttf", 34), fill=PRIMARY)
    d.text((1128, 560), "enablement.works", font=font("Courier New.ttf", 26), fill=MUTED, anchor="ra")
    im.save(path, optimize=True)


def logo(path, size):
    im = Image.new("RGB", (size, size), PRIMARY)
    d = ImageDraw.Draw(im)
    f = font("Georgia Bold.ttf", int(size * 0.5))
    d.text((size / 2, size / 2 + size * 0.02), "EW", font=f, fill="#FFFFFF", anchor="mm")
    d.line([size * 0.2, size * 0.8, size * 0.8, size * 0.8], fill="#D6A54A", width=max(2, size // 40))
    im.save(path, optimize=True)


def build_all(out: Path, site, docs):
    (out / "og").mkdir(exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    og_image(out / "og" / "default.png", "Your enablement strategy, built and run.", "Sales enablement production and operations")
    for d in docs:
        og_image(out / "og" / f"{d['slug']}.png", d["title"], d.get("category", "Guide"))
    for s in (512, 180, 32):
        logo(out / "assets" / f"logo-{s}.png", s)
    Image.open(out / "assets" / "logo-32.png").save(out / "favicon.ico", sizes=[(32, 32)])
    (out / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="6" fill="#14453D"/>'
        '<text x="32" y="41" font-family="Georgia,serif" font-weight="700" font-size="30" fill="#fff" text-anchor="middle">EW</text>'
        '<rect x="13" y="50" width="38" height="3" fill="#D6A54A"/></svg>')
