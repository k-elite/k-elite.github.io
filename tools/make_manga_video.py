# -*- coding: utf-8 -*-
"""만화 8컷으로 '이렇게 사용하세요' 영상을 만든다.

세로(1080x1920)와 가로(1920x1080) 두 벌을 같은 원본에서 뽑는다.

## 원본

`manga/elite3.png` 한 장에 8컷이 4×2 격자로 들어 있다. 컷을 잘라
한 장씩 화면에 채우고 천천히 밀고 당긴다(켄 번스).

## 나레이션

컷 안에 이미 한 줄짜리 문구가 들어 있다. 그걸 그대로 다시 쓰면 같은
문장이 두 번 보여 실수처럼 읽힌다. 그래서 나레이션은 **그림이 말하지
않는 것**을 말한다 — 왜 그렇게 만들었는지, 무엇을 하지 않는지.

## 실행

    python tools/make_manga_video.py          # 세로 manga.mp4
    python tools/make_manga_video.py wide     # 가로 manga_wide.mp4
    python tools/make_manga_video.py both     # 둘 다
"""
import os
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, "manga", "elite3.png")

FPS = 30

# 원본 그림에서 뽑은 색. 영상이 그림과 한 세트로 보이게 한다.
NAVY = (23, 45, 106)
NAVY_DEEP = (13, 27, 66)
INK = (255, 255, 255)
INK2 = (176, 194, 228)
GOLD = (255, 190, 60)

FONT_DIR = r"C:\Windows\Fonts"
_fonts = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(
            os.path.join(FONT_DIR, "malgunbd.ttf" if bold else "malgun.ttf"),
            size)
    return _fonts[key]


# 컷 좌표 (원본 1536x1024 기준). 4열 × 2행.
COLS = [(14, 382), (394, 762), (774, 1142), (1154, 1522)]
ROWS = [(66, 458), (476, 878)]

TITLES = [
    "종목 선택 및 선수 정보 입력",
    "부상 예방을 위한 관리",
    "루틴 습관화",
    "훈련 기록",
    "분석 리포트",
    "성장 기록",
    "학부모 대시보드",
    "종합 리포트",
]

# 컷마다 세 줄. 그림 속 문구를 되풀이하지 않고 한 겹 더 말한다.
NARRATION = [
    ["38개 종목 중 하나를 고르면 그때부터 다르게 묻습니다.",
     "야구는 투구 수를 세고, 수영은 기록을 초로 받습니다.",
     "처음 3분이면 끝납니다."],
    ["잔소리 대신 알람이 부릅니다.",
     "튜빙과 유연성 동작을 카메라가 보고 점수로 알려 줍니다.",
     "영상은 기기 밖으로 나가지 않습니다."],
    ["오전 7시, 저녁 7시. 알람 두 개면 충분합니다.",
     "오늘의 미션 세 개를 채우면 불꽃이 켜집니다.",
     "이미 다 한 날에는 알림을 보내지 않습니다."],
    ["무엇을 얼마나 했는지, 얼마나 힘들었는지 한 줄.",
     "이 기록이 쌓여야 '평소'를 알 수 있고,",
     "평소를 알아야 무리한 주를 짚어낼 수 있습니다."],
    ["이번 주 훈련량이 지난 4주 평균보다 얼마나 튀었는지 봅니다.",
     "많이 튄 주에 부상이 몰립니다.",
     "위험 구간에 들어가면 그 주에 알려 드립니다."],
    ["키가 자라는 구간과 훈련량이 겹치는 자리를 보여 줍니다.",
     "숫자 하나가 아니라 흐름입니다.",
     "병원에 그대로 가져갈 수 있는 자료가 됩니다."],
    ["오늘 훈련했는지, 어디가 아픈지. 아침에 1분이면 됩니다.",
     "훈련 일지 내용과 AI 코치 대화는 부모에게 가지 않습니다.",
     "무엇을 보여 줄지는 아이가 정합니다."],
    ["대회가 끝나면 그날 한 줄.",
     "3년 뒤 진학 서류가 버튼 하나로 나옵니다.",
     "기억을 뒤지지 않아도 됩니다."],
]

FEATURES = ["선수 관리", "부상 방지 루틴", "튜빙 운동", "루틴 알람",
            "데일리 미션", "훈련 기록", "분석 리포트", "성장 기록",
            "학부모 대시보드", "종합 리포트"]

# 세 줄을 읽을 시간을 준다. 4초로는 마지막 줄을 못 읽는다.
PANEL_SEC = 6.0


# ── 보조 ──────────────────────────────────────────────────

def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return 3 * t * t - 2 * t * t * t


def clamp01(v):
    return max(0.0, min(1.0, v))


def lerp(a, b, t):
    return a + (b - a) * t


def text(d, xy, s, f, fill, anchor="la", alpha=255):
    if alpha <= 0:
        return
    d.text(xy, s, font=f, fill=fill if alpha >= 255 else fill + (alpha,),
           anchor=anchor)


def load_panels():
    im = Image.open(SRC).convert("RGB")
    return [im.crop((c0, r0, c1, r1))
            for r0, r1 in ROWS for c0, c1 in COLS]


PANELS = load_panels()


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.width - 1, im.height - 1], radius=radius, fill=255)
    out = im.copy()
    out.putalpha(mask)
    return out


_measure = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def wrap(s, f, max_w):
    """폭에 맞춰 띄어쓰기에서 자른다.

    한글은 글자 폭이 넓어 한 줄이 쉽게 넘친다. 넘친 줄은 화면 밖으로
    잘려 나가는데, 잘린 자막은 없는 것보다 나쁘다.
    """
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if _measure.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Stage:
    """가로·세로에서 달라지는 것만 들고 있는 무대."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.bg = self._backdrop()

    def _backdrop(self):
        bg = Image.new("RGB", (self.w, self.h), NAVY)
        d = ImageDraw.Draw(bg)
        for y in range(self.h):
            t = abs(y - self.h * 0.42) / (self.h * 0.6)
            c = tuple(int(lerp(NAVY[i], NAVY_DEEP[i], clamp01(t)))
                      for i in range(3))
            d.line([(0, y), (self.w, y)], fill=c)
        return bg

    def frame(self):
        im = self.bg.copy()
        return im, ImageDraw.Draw(im, "RGBA")

    def fade(self, im, p, start):
        if p <= start:
            return im
        return Image.blend(im, self.bg, (p - start) / (1 - start))

    def panel(self, im, idx, cx, cy, base_w, p):
        """컷 하나를 얹는다. 1.0 → 1.07 로 아주 천천히 당긴다."""
        src = PANELS[idx]
        zoom = lerp(1.0, 1.07, ease_in_out(p))
        pw = int(base_w * zoom)
        ph = int(src.height * pw / src.width)
        card = rounded(src.resize((pw, ph), Image.LANCZOS), 30)

        sh = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [30, 34, pw + 30, ph + 34], radius=30, fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        im.paste(sh, (cx - sh.width // 2, cy - sh.height // 2), sh)
        im.paste(card, (cx - pw // 2, cy - ph // 2), card)
        return ph

    def dots(self, d, idx, y):
        dw, gap = 26, 14
        total = 8 * dw + 7 * gap
        x0 = (self.w - total) // 2
        for i in range(8):
            on = i == idx
            d.rounded_rectangle(
                [x0 + i * (dw + gap), y, x0 + i * (dw + gap) + dw, y + 8],
                radius=4, fill=(GOLD if on else INK2) + (255 if on else 90,))

    def logo(self, d, cx, cy, size, alpha):
        r = int(size)
        d.rounded_rectangle([cx - r, cy - r - 10, cx + r, cy + r + 12],
                            radius=int(r * .42), fill=INK + (alpha,))
        text(d, (cx, cy + 4), "E", font(int(size * 1.25)), NAVY, "mm", alpha)


VERT = Stage(1080, 1920)
WIDE = Stage(1920, 1080)


# ── 장면: 세로 ────────────────────────────────────────────

def v_title(t, dur):
    im, d = VERT.frame()
    k = ease_out(clamp01(t / 1.0))
    VERT.logo(d, VERT.w // 2, 620, 96 * lerp(.86, 1.0, k), int(255 * k))
    text(d, (VERT.w // 2, 860), "엘리트 루틴 케어", font(84), INK, "ma",
         int(255 * ease_out(clamp01((t - .5) / .9))))
    text(d, (VERT.w // 2, 984), "이렇게 사용하세요", font(60), GOLD, "ma",
         int(255 * ease_out(clamp01((t - .85) / .9))))
    text(d, (VERT.w // 2, 1100), "여덟 걸음이면 끝납니다", font(38, False),
         INK2, "ma", int(255 * ease_out(clamp01((t - 1.2) / .9))))
    return VERT.fade(im, clamp01(t / dur), .86)


def v_panel(idx):
    def render(t, dur):
        im, d = VERT.frame()
        p = clamp01(t / dur)
        a = int(255 * ease_out(clamp01(t / .5)))
        text(d, (72, 168), f"{idx + 1:02d}", font(40), GOLD, "la", a)
        text(d, (72, 228), TITLES[idx], font(54), INK, "la", a)

        cy = 880 + int(lerp(14, -14, ease_in_out(p)))
        ph = VERT.panel(im, idx, VERT.w // 2, cy, VERT.w - 96, p)
        d = ImageDraw.Draw(im, "RGBA")

        nf = font(34, False)
        y = cy + ph // 2 + 104
        for i, line in enumerate(NARRATION[idx]):
            aa = int(255 * ease_out(clamp01((t - .6 - i * .38) / .6)))
            for sub in wrap(line, nf, VERT.w - 150):
                text(d, (VERT.w // 2, y), sub, nf, INK2, "ma", aa)
                y += 52
            y += 18

        VERT.dots(d, idx, 1800)
        return VERT.fade(im, p, .93)
    return render


def v_end(t, dur):
    im, d = VERT.frame()
    text(d, (VERT.w // 2, 560), "매일 3분,", font(76), INK, "ma",
         int(255 * ease_out(clamp01(t / .7))))
    text(d, (VERT.w // 2, 664), "평생 가는 루틴", font(76), GOLD, "ma",
         int(255 * ease_out(clamp01((t - .3) / .7))))
    for i, s in enumerate(FEATURES):
        k = ease_out(clamp01((t - .7 - i * .07) / .5))
        if k <= 0:
            continue
        col, row = i % 2, i // 2
        x, yy, aa = 130 + col * 430, 880 + row * 96, int(255 * k)
        d.rounded_rectangle([x - 24, yy - 30, x + 390, yy + 40], radius=20,
                            fill=NAVY_DEEP + (int(aa * .85),))
        d.ellipse([x - 4, yy - 4, x + 14, yy + 14], fill=GOLD + (aa,))
        text(d, (x + 34, yy - 22), s, font(34, False), INK, "la", aa)
    text(d, (VERT.w // 2, 1500), "엘리트 루틴 케어", font(52), INK, "ma",
         int(255 * ease_out(clamp01((t - 2.0) / .7))))
    text(d, (VERT.w // 2, 1580), "k-elite.github.io", font(34, False), INK2,
         "ma", int(255 * ease_out(clamp01((t - 2.3) / .7))))
    p = clamp01(t / dur)
    if p > .88:
        im = Image.blend(im, Image.new("RGB", (VERT.w, VERT.h), NAVY_DEEP),
                         (p - .88) / .12)
    return im


# ── 장면: 가로 ────────────────────────────────────────────
#
# 컷을 왼쪽에 세로로 꽉 채우고 오른쪽을 글로 쓴다. 세로처럼 위아래로
# 쌓으면 컷이 작아져 그림 속 글씨가 안 읽힌다.

def w_title(t, dur):
    im, d = WIDE.frame()
    k = ease_out(clamp01(t / 1.0))
    WIDE.logo(d, WIDE.w // 2, 360, 84 * lerp(.86, 1.0, k), int(255 * k))
    text(d, (WIDE.w // 2, 542), "엘리트 루틴 케어", font(82), INK, "ma",
         int(255 * ease_out(clamp01((t - .5) / .9))))
    text(d, (WIDE.w // 2, 662), "이렇게 사용하세요", font(58), GOLD, "ma",
         int(255 * ease_out(clamp01((t - .85) / .9))))
    text(d, (WIDE.w // 2, 774), "여덟 걸음이면 끝납니다", font(36, False),
         INK2, "ma", int(255 * ease_out(clamp01((t - 1.2) / .9))))
    return WIDE.fade(im, clamp01(t / dur), .86)


def w_panel(idx):
    def render(t, dur):
        im, d = WIDE.frame()
        p = clamp01(t / dur)

        # 컷은 왼쪽. 화면 높이에 맞춰 채운다.
        src = PANELS[idx]
        panel_h = 830
        base_w = int(src.width * panel_h / src.height)
        WIDE.panel(im, idx, 496, WIDE.h // 2 - 6, base_w, p)
        d = ImageDraw.Draw(im, "RGBA")

        # 오른쪽은 글. 칸 폭을 넘기지 않게 줄을 나눈다.
        x, right = 1000, WIDE.w - 90
        col_w = right - x
        k0 = ease_out(clamp01(t / .5))
        a, dx = int(255 * k0), int(30 * (1 - k0))
        text(d, (x + dx, 196), f"{idx + 1:02d}", font(42), GOLD, "la", a)
        text(d, (x + dx, 262), TITLES[idx], font(56), INK, "la", a)
        d.line([(x, 372),
                (x + int(150 * ease_out(clamp01((t - .3) / .6))), 372)],
               fill=GOLD, width=5)

        nf = font(34, False)
        y = 442
        for i, line in enumerate(NARRATION[idx]):
            k = ease_out(clamp01((t - .7 - i * .38) / .6))
            if k <= 0:
                continue
            for sub in wrap(line, nf, col_w):
                text(d, (x + int(24 * (1 - k)), y), sub, nf, INK2, "la",
                     int(255 * k))
                y += 52
            y += 22

        # 점은 글 칸 아래. 가운데에 두면 컷 위에 얹힌다.
        dw, gap = 24, 12
        total = 8 * dw + 7 * gap
        x0 = x
        for i in range(8):
            on = i == idx
            d.rounded_rectangle([x0 + i * (dw + gap), 940,
                                 x0 + i * (dw + gap) + dw, 948],
                                radius=4,
                                fill=(GOLD if on else INK2) + (255 if on else 90,))
        return WIDE.fade(im, p, .93)
    return render


def w_end(t, dur):
    im, d = WIDE.frame()
    text(d, (WIDE.w // 2, 230), "매일 3분,", font(72), INK, "ma",
         int(255 * ease_out(clamp01(t / .7))))
    text(d, (WIDE.w // 2, 330), "평생 가는 루틴", font(72), GOLD, "ma",
         int(255 * ease_out(clamp01((t - .3) / .7))))
    for i, s in enumerate(FEATURES):
        k = ease_out(clamp01((t - .7 - i * .06) / .5))
        if k <= 0:
            continue
        col, row = i % 5, i // 5
        x, yy, aa = 176 + col * 328, 540 + row * 96, int(255 * k)
        d.rounded_rectangle([x - 24, yy - 30, x + 286, yy + 40], radius=20,
                            fill=NAVY_DEEP + (int(aa * .85),))
        d.ellipse([x - 4, yy - 4, x + 14, yy + 14], fill=GOLD + (aa,))
        text(d, (x + 34, yy - 22), s, font(32, False), INK, "la", aa)
    text(d, (WIDE.w // 2, 830), "엘리트 루틴 케어", font(50), INK, "ma",
         int(255 * ease_out(clamp01((t - 2.0) / .7))))
    text(d, (WIDE.w // 2, 902), "k-elite.github.io", font(34, False), INK2,
         "ma", int(255 * ease_out(clamp01((t - 2.3) / .7))))
    p = clamp01(t / dur)
    if p > .88:
        im = Image.blend(im, Image.new("RGB", (WIDE.w, WIDE.h), NAVY_DEEP),
                         (p - .88) / .12)
    return im


MODES = {
    "vertical": (VERT, "manga.mp4",
                 [(v_title, 3.4)] + [(v_panel(i), PANEL_SEC) for i in range(8)]
                 + [(v_end, 4.2)]),
    "wide": (WIDE, "manga_wide.mp4",
             [(w_title, 3.4)] + [(w_panel(i), PANEL_SEC) for i in range(8)]
             + [(w_end, 4.2)]),
}


def render(mode):
    stage, name, scenes = MODES[mode]
    out = os.path.join(ROOT, name)
    total = sum(d for _, d in scenes)
    nframes = int(total * FPS)
    print(f"[{mode}] {total:.1f}s | {nframes}f | {stage.w}x{stage.h}")

    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y",
           "-f", "rawvideo", "-vcodec", "rawvideo",
           "-s", f"{stage.w}x{stage.h}", "-pix_fmt", "rgb24", "-r", str(FPS),
           "-i", "-", "-an",
           "-vcodec", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "23",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    done = 0
    for fn, dur in scenes:
        for i in range(int(dur * FPS)):
            proc.stdin.write(fn(i / FPS, dur).tobytes())
            done += 1
            if done % 150 == 0:
                print(f"  {done}/{nframes}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f"{mode}: ffmpeg encoding failed")
    print(f"  -> {out} {os.path.getsize(out) // 1024} KB")


def main():
    arg = (sys.argv[1] if len(sys.argv) > 1 else "vertical").lower()
    modes = ["vertical", "wide"] if arg == "both" else [arg]
    for m in modes:
        if m not in MODES:
            raise SystemExit("mode must be vertical / wide / both")
        render(m)


if __name__ == "__main__":
    main()
