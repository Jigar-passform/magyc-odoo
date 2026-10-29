"""Draw numbered red rectangles onto the Odoo screenshots."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

SHOT = r"C:/Users/ABC/magyc-odoo/docs/screenshots"
RED = (220, 38, 38)
WHITE = (255, 255, 255)

TARGETS = {
    "01-kiosk-kontakt": ["kiosk_id", "kundentyp", "komm_lager", "gebiet"],
    "02-kommission-neu": ["partner", "von", "bis", "zeilen"],
    "03-abverkauf-formular": ["drucken", "status", "totals"],
    "04-pfand-gutschrift": ["partner", "gutschrift", "status"],
}


def font(size=26):
    for name in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def main():
    rects = json.load(open(os.path.join(SHOT, "rects.json")))
    for key, order in TARGETS.items():
        src = os.path.join(SHOT, f"raw-{key}.png")
        if not os.path.exists(src):
            print("missing", src)
            continue
        img = Image.open(src).convert("RGB")
        draw = ImageDraw.Draw(img)
        data = dict(rects.get(key, {}))
        if "totals" not in data and "summen_abverkauf" in data and "netto" in data:
            x0, y0, w0, h0 = data["summen_abverkauf"]
            x1, y1, w1, h1 = data["netto"]
            data["totals"] = [min(x0, x1), y0, max(w0, w1), (y1 + h1) - y0]
        f = font(24)
        for number, name in enumerate(order, start=1):
            box = data.get(name)
            if not box:
                continue
            x, y, w, h = box
            pad = 3
            draw.rectangle([x - pad, y - pad, x + w + pad, y + h + pad], outline=RED, width=4)
            label = str(number)
            bx, by = max(x - 30, 2), max(y - 28, 2)
            draw.rectangle([bx, by, bx + 26, by + 26], fill=RED)
            draw.text((bx + 7, by + 1), label, fill=WHITE, font=f)
        out = os.path.join(SHOT, f"ann-{key}.png")
        img.save(out)
        print("saved", out)


if __name__ == "__main__":
    main()
