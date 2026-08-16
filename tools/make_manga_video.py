# -*- coding: utf-8 -*-
"""만화 8컷으로 '이렇게 사용하세요' 영상을 만든다.

세로 1080x1920 · 30fps · 약 40초.

## 원본

`manga/elite3.png` 한 장에 8컷이 4×2 격자로 들어 있다. 컷을 잘라
한 장씩 화면에 채우고 천천히 밀고 당긴다(켄 번스).

컷 안에 이미 설명 문구가 들어 있으므로 자막을 덧대지 않는다. 같은 문장을
두 번 보여 주면 실수처럼 보인다. 화면에는 몇 번째 컷인지만 얹는다.

## 실행

    python tools/make_manga_video.py

`manga.mp4` 와 `tools/manga_b64.txt` 가 만들어진다.
"""
import base64
import os
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, "manga", "elite3.png")
OUT = os.path.join(ROOT, "manga.mp4")
OUT_B64 = os.path.join(HERE, "manga_b64.txt")

W, H = 1080, 1920
FPS = 30

# 원본 그림에서 뽑은 색. 영상이 그림과 한 세트로 보이게 한다.
NAVY = (23, 45, 106)
NAVY_DEEP = (13, 27, 66)
PAPER = (238, 242, 248)
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

# 컷 속 띠 문구. 화면에 다시 그리지는 않는다 — 같은 문장을 두 번
# 보여 주면 실수처럼 보인다. 자막이 필요할 때 쓰려고 남겨 둔다.
CAPTIONS = [
    "정확한 정보 입력이 맞춤 관리의 시작",
    "AI 모션 인식으로 올바른 자세를 체크",
    "매일의 루틴이 최고의 선수를 만듭니다",
    "기록이 쌓일수록 더 정확한 분석",
    "AI 분석으로 더 스마트한 성장",
    "성장의 모든 순간을 데이터로",
    "학부모와 함께, 더 건강한 성장을",
    "기록이 모여, 미래의 기회를 만듭니다",
]

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
    out = []
    for r0, r1 in ROWS:
        for c0, c1 in COLS:
            out.append(im.crop((c0, r0, c1, r1)))
    return out


PANELS = load_panels()


def backdrop():
    """컷 뒤에 깔리는 지면. 위아래로 남색이 짙어진다."""
    bg = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = abs(y - H * 0.42) / (H * 0.6)
        c = tuple(int(lerp(NAVY[i], NAVY_DEEP[i], clamp01(t))) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return bg


BG = backdrop()


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.width - 1, im.height - 1], radius=radius, fill=255)
    out = im.copy()
    out.putalpha(mask)
    return out


def scene_title(t, dur):
    """여는 화면."""
    im = BG.copy()
    d = ImageDraw.Draw(im, "RGBA")

    k = ease_out(clamp01(t / 1.0))
    # 방패 마크
    cx, cy = W // 2, 660
    s = lerp(.86, 1.0, k)
    a = int(255 * k)
    r = int(96 * s)
    d.rounded_rectangle([cx - r, cy - r - 10, cx + r, cy + r + 14],
                        radius=int(r * .42), fill=INK + (a,))
    text(d, (cx, cy + 4), "E", font(int(120 * s)), NAVY, "mm", a)

    a2 = int(255 * ease_out(clamp01((t - .5) / .9)))
    text(d, (cx, 900), "엘리트 루틴 케어", font(84), INK, "ma", a2)
    a3 = int(255 * ease_out(clamp01((t - .85) / .9)))
    text(d, (cx, 1024), "이렇게 사용하세요", font(60), GOLD, "ma", a3)
    a4 = int(255 * ease_out(clamp01((t - 1.2) / .9)))
    text(d, (cx, 1140), "여덟 걸음이면 끝납니다", font(38, False), INK2, "ma", a4)

    p = clamp01(t / dur)
    if p > .86:
        im = Image.blend(im, BG, (p - .86) / .14)
    return im


def scene_panel(idx):
    """컷 하나. 천천히 밀고 당긴다."""

    def render(t, dur):
        im = BG.copy()
        d = ImageDraw.Draw(im, "RGBA")
        p = clamp01(t / dur)

        # 머리말
        a = int(255 * ease_out(clamp01(t / .5)))
        text(d, (72, 232), f"{idx + 1:02d}", font(40), GOLD, "la", a)
        text(d, (72, 292), TITLES[idx], font(56), INK, "la", a)

        # 컷 — 화면 폭에 맞추고 1.0 → 1.07 로 아주 천천히 당긴다.
        panel = PANELS[idx]
        base_w = W - 56
        zoom = lerp(1.0, 1.07, ease_in_out(p))
        pw = int(base_w * zoom)
        ph = int(panel.height * pw / panel.width)
        img = panel.resize((pw, ph), Image.LANCZOS)

        # 위아래로 아주 조금 흐른다.
        cx = W // 2
        cy = 1060 + int(lerp(16, -16, ease_in_out(p)))
        card = rounded(img, 34)

        # 그림자
        sh = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [30, 34, pw + 30, ph + 34], radius=34, fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(22))
        im.paste(sh, (cx - sh.width // 2, cy - sh.height // 2), sh)
        im.paste(card, (cx - pw // 2, cy - ph // 2), card)
        d = ImageDraw.Draw(im, "RGBA")

        # 진행 점
        dotw, gap = 26, 14
        total = 8 * dotw + 7 * gap
        x0 = (W - total) // 2
        for i in range(8):
            on = i == idx
            d.rounded_rectangle(
                [x0 + i * (dotw + gap), 1790,
                 x0 + i * (dotw + gap) + dotw, 1790 + 8],
                radius=4, fill=(GOLD if on else INK2) + (255 if on else 90,))

        if p > .93:
            im = Image.blend(im, BG, (p - .93) / .07)
        return im

    return render


def scene_end(t, dur):
    """닫는 화면 — 원본 아래 띠의 기능 목록을 옮긴다."""
    im = BG.copy()
    d = ImageDraw.Draw(im, "RGBA")

    a = int(255 * ease_out(clamp01(t / .7)))
    text(d, (W // 2, 560), "매일 3분,", font(76), INK, "ma", a)
    a1 = int(255 * ease_out(clamp01((t - .3) / .7)))
    text(d, (W // 2, 664), "평생 가는 루틴", font(76), GOLD, "ma", a1)

    items = ["선수 관리", "부상 방지 루틴", "튜빙 운동", "루틴 알람",
             "데일리 미션", "훈련 기록", "분석 리포트", "성장 기록",
             "학부모 대시보드", "종합 리포트"]
    y = 880
    for i, s in enumerate(items):
        k = ease_out(clamp01((t - .7 - i * .07) / .5))
        if k <= 0:
            continue
        col, row = i % 2, i // 2
        x = 130 + col * 430
        yy = y + row * 96
        aa = int(255 * k)
        d.rounded_rectangle([x - 24, yy - 30, x + 390, yy + 40],
                            radius=20, fill=NAVY_DEEP + (int(aa * .85),))
        d.ellipse([x - 4, yy - 4, x + 14, yy + 14], fill=GOLD + (aa,))
        text(d, (x + 34, yy - 22), s, font(34, False), INK, "la", aa)

    a2 = int(255 * ease_out(clamp01((t - 2.0) / .7)))
    text(d, (W // 2, 1500), "엘리트 루틴 케어", font(52), INK, "ma", a2)
    text(d, (W // 2, 1580), "k-elite.github.io", font(34, False), INK2, "ma",
         int(255 * ease_out(clamp01((t - 2.3) / .7))))

    p = clamp01(t / dur)
    if p > .88:
        im = Image.blend(im, Image.new("RGB", (W, H), NAVY_DEEP),
                         (p - .88) / .12)
    return im


SCENES = ([(scene_title, 3.4)]
          + [(scene_panel(i), 4.0) for i in range(8)]
          + [(scene_end, 4.2)])


def main():
    total = sum(d for _, d in SCENES)
    nframes = int(total * FPS)
    print(f"길이 {total:.1f}초 · {nframes}프레임 · {W}x{H} @{FPS}fps")

    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y",
           "-f", "rawvideo", "-vcodec", "rawvideo",
           "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
           "-i", "-", "-an",
           "-vcodec", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "23",
           "-movflags", "+faststart", OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    done = 0
    for fn, dur in SCENES:
        for i in range(int(dur * FPS)):
            proc.stdin.write(fn(i / FPS, dur).tobytes())
            done += 1
            if done % 120 == 0:
                print(f"  {done}/{nframes}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg 인코딩 실패")

    print("영상:", OUT, os.path.getsize(OUT) // 1024, "KB")
    with open(OUT, "rb") as f:
        b64 = "data:video/mp4;base64," + base64.b64encode(f.read()).decode()
    with open(OUT_B64, "w", encoding="utf-8") as f:
        f.write(b64)
    print("base64:", OUT_B64, len(b64) // 1024, "KB")


if __name__ == "__main__":
    main()
