"""Покрокові скріни: шматки справжнього скріна + помаранчеві рамки й номери кроків (як на слайдах gsteps).

compose(crops, marks, nums, row, out) — crops: [((x0, y0, x1, y1) у точках екрана, PIL-зображення у масштабі 2)],
marks: [(x0, y0, x1, y1, бік)] у тих самих точках; бік — left/right/top/bottom, "nonum" — рамка без номера.
Шматки ставимо один під одним (через пунктир) або row=True — перший ліворуч, решта стовпчиком праворуч.
Користуються gdocs_spravzhni.py (Google Документи) і kritakroky.py (Krita)."""
from PIL import Image, ImageDraw, ImageFont

MARK = (242, 113, 28)   # той самий помаранчевий, що й у gsteps
BG = (249, 251, 253)
GAP_BG = (232, 234, 237)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
S = 2      # результат — у подвійному масштабі (як gdocs.Doc.shot), gshot на це розрахований
M = 34     # поле навколо (точки), щоб номери не вилазили
GAP = 16


def _font(px):
    return ImageFont.truetype(FONT, px)


def compose(crops, marks, nums=None, row=False, out=None, key="скрін"):
    gap = GAP * S

    def column(items):
        return max(c[1].width for c in items), sum(c[1].height for c in items) + gap * (len(items) - 1)

    if row:  # перший шматок ліворуч, решта — стовпчиком праворуч
        rw, rh = column(crops[1:])
        W = crops[0][1].width + gap + rw + 2 * M * S
        H = max(crops[0][1].height, rh) + 2 * M * S
    else:
        cw, ch = column(crops)
        W, H = cw + 2 * M * S, ch + 2 * M * S
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    places = []

    def stack(items, x, y, dashed):
        ww = max(c[1].width for c in items)
        for k, (box, im) in enumerate(items):
            canvas.paste(im, (x, y))
            places.append((box, x, y))
            y += im.height
            if k < len(items) - 1:
                if dashed:
                    d.rectangle((x, y, x + ww, y + gap - 1), fill=GAP_BG)
                    for xx in range(x, x + ww, 24):  # «розрив» — пунктир
                        d.line((xx, y + gap // 2, xx + 12, y + gap // 2), fill=(170, 175, 182), width=3)
                y += gap

    if row:
        stack(crops[:1], M * S, M * S, False)
        stack(crops[1:], M * S + crops[0][1].width + gap, M * S, True)
    else:
        stack(crops, M * S, M * S, True)

    def to_out(x, yy):
        for (cx0, cy0, cx1, cy1), ox, oy in places:
            if cx0 - 1 <= x <= cx1 + 1 and cy0 - 1 <= yy <= cy1 + 1:
                return ox + (x - cx0) * S, oy + (yy - cy0) * S
        raise ValueError(f"{key}: точка {x},{yy} поза шматками")

    R = 17 * S
    i = -1
    for (x0, y0, x1, y1, side) in marks:
        if side != "nonum":
            i += 1
        n = None if side == "nonum" else ((i + 1) if nums is None else (None if nums is False else nums[i]))
        ax, ay = to_out((x0 + x1) / 2, (y0 + y1) / 2)
        hw, hh = ((x1 - x0) / 2 + 3) * S, ((y1 - y0) / 2 + 3) * S
        r0 = (ax - hw, ay - hh, ax + hw, ay + hh)
        d.rounded_rectangle(r0, radius=5 * S, outline=MARK, width=3 * S)
        if n is None:
            continue
        g = 4 * S
        cx, cy = {"left": (r0[0] - g - R, ay), "right": (r0[2] + g + R, ay),
                  "top": (ax, r0[1] - g - R), "bottom": (ax, r0[3] + g + R)}[side]
        cx = min(max(cx, R + 2), W - R - 2)
        cy = min(max(cy, R + 2), H - R - 2)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=MARK, outline=(255, 255, 255), width=2 * S)
        f = _font(20 * S)
        d.text((cx, cy + 1), str(n), font=f, fill=(255, 255, 255), anchor="mm")
    canvas.save(out)
    return out
