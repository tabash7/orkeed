"""Generate the compact social preview for Orkeed."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "orkeed-og.webp"
image = Image.new("RGB", (1200, 630), "#291f36")
draw = ImageDraw.Draw(image)

for radius in (270, 355, 440, 525):
    draw.arc((135-radius, 315-radius, 135+radius, 315+radius), 280, 80, fill="#40304e", width=2)

petal = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
pd = ImageDraw.Draw(petal)
pd.ellipse((76, 12, 164, 178), fill="#d9b4ca", outline="#f4d9e7", width=3)
for angle in (0, 72, 144, 216, 288):
    rotated = petal.rotate(angle, resample=Image.Resampling.BICUBIC)
    image.paste(rotated, (148, 133), rotated)
draw = ImageDraw.Draw(image)
draw.ellipse((249, 232, 287, 270), fill="#d8c28b")
draw.ellipse((264, 247, 272, 255), fill="#291f36")

font_path = Path("C:/Windows/Fonts/tahoma.ttf")
bold_path = Path("C:/Windows/Fonts/tahomabd.ttf")
font = ImageFont.truetype(str(bold_path if bold_path.exists() else font_path), 83)
small = ImageFont.truetype(str(font_path), 34)
eyebrow = ImageFont.truetype(str(font_path), 23)
draw.text((1120, 180), "ORKEED", font=font, fill="#fbf8f5", anchor="ra")
draw.line((820, 291, 1120, 291), fill="#d8c28b", width=6)
draw.text((1120, 375), "Technology Solutions", font=small, fill="#d9b4ca", anchor="ra")
draw.text((1120, 563), "DEVELOPMENT  •  OPERATIONS  •  EMPID", font=eyebrow, fill="#d8c28b", anchor="ra")
image.save(OUT, "WEBP", quality=86, method=6)
print(f"Created {OUT} ({OUT.stat().st_size:,} bytes)")
