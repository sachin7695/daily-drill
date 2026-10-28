"""Draw the app icon (a `>_` prompt) into assets/ for @capacitor/assets. Needs Pillow."""
from pathlib import Path

from PIL import Image, ImageDraw

BG, GOLD = (16, 27, 43, 255), (242, 194, 48, 255)
OUT = Path(__file__).parent / "assets"


def glyph(draw, size, scale):
    """Chevron plus underscore, centred, occupying `scale` of the canvas."""
    u = size * scale
    cx, cy = size / 2, size / 2
    w = int(u * 0.13)
    chevron = [(cx - u * 0.36, cy - u * 0.30), (cx - u * 0.02, cy), (cx - u * 0.36, cy + u * 0.30)]
    draw.line(chevron, fill=GOLD, width=w, joint="curve")
    r = w / 2
    for x, y in (chevron[0], chevron[2]):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=GOLD)
    draw.rounded_rectangle((cx + u * 0.08, cy + u * 0.22, cx + u * 0.42, cy + u * 0.22 + w), radius=r, fill=GOLD)


def make(name, size, scale, background):
    img = Image.new("RGBA", (size, size), BG if background else (0, 0, 0, 0))
    glyph(ImageDraw.Draw(img), size, scale)
    img.save(OUT / name)


OUT.mkdir(exist_ok=True)
make("icon-only.png", 1024, 0.62, True)
make("icon-foreground.png", 1024, 0.42, False)   # adaptive icons crop to the centre ~66%
Image.new("RGBA", (1024, 1024), BG).save(OUT / "icon-background.png")
make("splash.png", 2732, 0.18, True)
make("splash-dark.png", 2732, 0.18, True)
print("icons written to", OUT)
