"""Open Graph images (1200x630), logo and favicons in The Shift language: newsprint before, cobalt after, coral seam."""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"
COBALT, COBALT_DEEP, CORAL, PAPER, NEWS, INK, WHITE, SOFT = "#1530FF", "#0D1FB8", "#FF5A5F", "#E4E1DA", "#9C9890", "#0B0D17", "#FFFFFF", "#D6DBFF"


def f(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except OSError:
        return ImageFont.load_default()


FONTS = Path(__file__).parent / "tools" / "fonts"
HEAVY_IT = lambda s: f(str(FONTS / "Archivo-BlackItalic.ttf"), s)
BOLD = lambda s: f(str(FONTS / "Archivo-ExtraBold.ttf"), s)
MONO = lambda s: f(str(FONTS / "JetBrainsMono-Medium.ttf"), s)


def fit(draw, title, max_w, max_lines=4):
    for size in (78, 70, 64, 58, 52, 46):
        font = HEAVY_IT(size)
        for width in range(34, 8, -1):
            lines = textwrap.wrap(title, width=width)
            if len(lines) <= max_lines and all(draw.textlength(l, font=font) <= max_w for l in lines):
                return font, lines, size
    return HEAVY_IT(46), textwrap.wrap(title, 40)[:max_lines], 46


def wordmark(draw, x, y, size, fill):
    font = HEAVY_IT(size)
    draw.text((x, y), "Enablement", font=font, fill=fill)
    w = draw.textlength("Enablement", font=font)
    sx = x + w + size * 0.18
    draw.line([sx + size * 0.38, y + size * 0.18, sx + size * 0.02, y + size * 1.02], fill=CORAL, width=max(3, size // 9))
    draw.text((sx + size * 0.55, y), "Works", font=font, fill=fill)


def og_image(path, title, label):
    im = Image.new("RGB", (1200, 630), COBALT)
    d = ImageDraw.Draw(im)
    # newsprint "before" strip on the left, coral seam line
    d.rectangle([0, 0, 64, 630], fill=PAPER)
    d.rectangle([64, 0, 70, 630], fill=CORAL)
    d.rounded_rectangle([110, 54, 110 + d.textlength(label.upper(), font=MONO(22)) + 28, 92], radius=6, fill=CORAL)
    d.text((124, 61), label.upper(), font=MONO(22), fill=WHITE)
    font, lines, size = fit(d, title, 1000)
    y = 132
    for line in lines:
        d.text((110, y), line, font=font, fill=WHITE)
        y += int(size * 1.02)
    wordmark(d, 110, 548, 38, WHITE)
    d.text((1140, 560), "enablement.works", font=MONO(24), fill=SOFT, anchor="ra")
    im.save(path, optimize=True)


def logo(path, size):
    im = Image.new("RGB", (size, size), COBALT)
    d = ImageDraw.Draw(im)
    d.text((size * 0.47, size * 0.5), "EW", font=HEAVY_IT(int(size * 0.5)), fill=WHITE, anchor="mm")
    d.line([size * 0.72, size * 0.18, size * 0.56, size * 0.84], fill=CORAL, width=max(2, size // 22))
    im.save(path, optimize=True)


def build_all(out: Path, site, docs):
    (out / "og").mkdir(exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    og_image(out / "og" / "default.png", "Your enablement strategy, built and run.", "Sales enablement · built and run")
    for doc in docs:
        og_image(out / "og" / f"{doc['slug']}.png", doc["title"], doc.get("category", "Guide"))
    for s in (512, 180, 32):
        logo(out / "assets" / f"logo-{s}.png", s)
    Image.open(out / "assets" / "logo-32.png").save(out / "favicon.ico", sizes=[(32, 32)])
    (out / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#1530FF"/>'
        '<text x="29" y="43" font-family="Archivo,Arial,sans-serif" font-style="italic" font-weight="900" font-size="30" fill="#fff" text-anchor="middle">EW</text>'
        '<path d="M48 10 L38 54" stroke="#FF5A5F" stroke-width="4" stroke-linecap="round"/></svg>')
