# -*- coding: utf-8 -*-
"""소개 영상을 만든다.

세로 1080x1920 · 30fps · 약 37초. 카톡·인스타·유튜브 쇼츠에 그대로
올릴 수 있는 비율이다.

핵심만 여덟 장면으로 담는다 —
  로고 → 만든 이유 → 훈련 부하 → 투구 수 → 성장 기록 → 진학 실적표
  → 학부모 → 마무리

## 원칙

앱 화면은 `shots/` 에 있는 **실제로 찍은 것**을 쓴다. 없는 화면을 그려
넣지 않는다. 소개 영상에 실물과 다른 화면이 나오면 설치한 사람이
속았다고 느낀다.

## 준비물

    pip install pillow numpy imageio-ffmpeg

`imageio-ffmpeg` 는 ffmpeg 실행 파일을 함께 받아 오므로 시스템에 따로
설치할 필요가 없다. 글꼴은 윈도우의 맑은 고딕을 쓴다.

## 실행

    python tools/make_video.py

`intro.mp4` 가 저장소 루트에 생긴다. 사이트에 박아 넣으려면
`build_site_landing.py` 가 읽는 `video_b64.txt` 도 함께 만들어진다.
"""
import base64
import math
import os
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.join(HERE, "shots")
OUT = os.path.join(ROOT, "intro.mp4")
OUT_B64 = os.path.join(HERE, "video_b64.txt")

W, H = 1080, 1920
FPS = 30

# 사이트와 같은 팔레트. 부상 신호 삼색은 장식이 아니라 훈련 부하 구간이다.
GROUND = (7, 12, 20)
PANEL = (17, 26, 40)
RULE = (30, 42, 60)
INK = (238, 243, 250)
INK2 = (169, 184, 204)
INK3 = (109, 127, 151)
BEAM = (46, 125, 246)
BEAM2 = (99, 164, 255)
SAFE = (46, 212, 122)
WATCH = (255, 176, 32)
RISK = (255, 90, 82)
PLASTER = (241, 236, 226)
PLASTER_INK = (26, 22, 16)
PLASTER_INK2 = (86, 78, 64)

FONT_DIR = r"C:\Windows\Fonts"


def font(size, bold=True):
    return ImageFont.truetype(
        os.path.join(FONT_DIR, "malgunbd.ttf" if bold else "malgun.ttf"), size)


F_HUGE = font(112)
F_BIG = font(78)
F_MID = font(54)
F_BODY = font(40, False)
F_SMALL = font(32, False)
F_TINY = font(26, False)


# ── 보조 ──────────────────────────────────────────────────

def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return 3 * t * t - 2 * t * t * t


def clamp01(v):
    return max(0.0, min(1.0, v))


def lerp(a, b, t):
    return a + (b - a) * t


def blend(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def text(d, xy, s, f, fill, anchor="la", alpha=255):
    """알파를 받는 글자. 페이드 인에 쓴다."""
    if alpha <= 0:
        return
    d.text(xy, s, font=f, fill=fill if alpha >= 255 else fill + (alpha,),
           anchor=anchor)


def new_frame(bg=GROUND):
    im = Image.new("RGB", (W, H), bg)
    return im, ImageDraw.Draw(im, "RGBA")


def _add(a, b):
    """두 프레임을 더한다. 조명을 얹을 때 쓴다."""
    import numpy as np
    return np.clip(np.asarray(a, dtype=int) + np.asarray(b, dtype=int),
                   0, 255).astype("uint8")


def floodlight(im, box, color, blur=90):
    """플러드라이트 한 덩이를 얹는다."""
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=color)
    return Image.fromarray(_add(im, layer.filter(ImageFilter.GaussianBlur(blur))))


def fade_out(im, p, start):
    """장면 끝에서 지면색으로 잠근다."""
    if p <= start:
        return im
    return Image.blend(im, Image.new("RGB", (W, H), GROUND),
                       (p - start) / (1 - start))


_shot_cache = {}


def shot(name, height):
    """찍어 둔 화면. 상태바와 제스처바를 잘라내고 높이에 맞춘다."""
    key = (name, height)
    if key in _shot_cache:
        return _shot_cache[key]
    im = Image.open(os.path.join(SHOTS, name + ".png")).convert("RGB")
    im = im.crop((0, 72, im.width, im.height - 96))
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    _shot_cache[key] = im
    return im


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.width - 1, im.height - 1], radius=radius, fill=255)
    out = im.copy()
    out.putalpha(mask)
    return out


def phone(im, screen, cx, cy, h):
    """기기 목업 안에 화면을 넣는다."""
    s = shot(screen, h)
    pad = 14
    frame = Image.new("RGB", (s.width + pad * 2, s.height + pad * 2), (32, 41, 54))
    frame.paste(s, (pad, pad))
    frame = rounded(frame, 46)
    im.paste(frame, (int(cx - frame.width / 2), int(cy - frame.height / 2)), frame)


def head(d, t, num, line1, line2, sub):
    """장면 머리말 — 번호·두 줄 제목·설명."""
    a = int(255 * ease_out(clamp01(t / .5)))
    text(d, (80, 300), num, F_SMALL, BEAM2, "la", a)
    text(d, (80, 356), line1, F_BIG, INK, "la", a)
    text(d, (80, 452), line2, F_BIG, INK, "la", a)
    text(d, (80, 578), sub, F_BODY, INK2, "la",
         int(255 * ease_out(clamp01((t - .3) / .5))))


# ── 장면 ──────────────────────────────────────────────────

def scene_open(t, dur):
    """로고와 한 줄. 조명이 켜지듯 시작한다."""
    im, _ = new_frame()
    k = ease_out(clamp01(t / 1.2))
    im = floodlight(im, [W // 2 - 700, -300, W // 2 + 700, 900],
                    (int(10 * k), int(28 * k), int(58 * k)))
    d = ImageDraw.Draw(im, "RGBA")

    # 불꽃 마크 — 앱 아이콘과 같은 도형(불꽃 + 올라가는 막대)
    a = int(255 * ease_out(clamp01((t - .2) / .8)))
    cx, cy = W // 2, 690
    scale = lerp(.82, 1.0, ease_out(clamp01((t - .2) / .9)))
    fr = int(120 * scale)
    d.ellipse([cx - fr, cy - fr, cx + fr, cy + fr], fill=BEAM2 + (a,))
    for i, bh in enumerate((44, 74, 104)):
        bx = cx - 46 * scale + i * 40 * scale
        d.rounded_rectangle([bx, cy + 40 * scale - bh * scale,
                             bx + 20 * scale, cy + 40 * scale],
                            radius=7, fill=GROUND + (a,))

    text(d, (W // 2, 940), "엘리트 루틴 케어", F_BIG, INK, "ma",
         int(255 * ease_out(clamp01((t - .8) / .9))))
    text(d, (W // 2, 1046), "다치지 않고, 기록이 남고, 진학까지", F_BODY, INK2,
         "ma", int(255 * ease_out(clamp01((t - 1.15) / .9))))
    return fade_out(im, clamp01(t / dur), .86)


def scene_story(t, dur):
    """만든 이유. 지면이 석고(깁스)색으로 바뀐다."""
    im, d = new_frame(blend(GROUND, PLASTER, ease_in_out(clamp01(t / .5))))
    d = ImageDraw.Draw(im, "RGBA")

    y = 560
    for delay, s in ((0.55, "알람이 울리면"),
                     (0.95, "알아서 하길 바랐습니다."),
                     (2.10, "대충 하거나, 빼먹거나,"),
                     (2.50, "주말엔 아예 안 했습니다.")):
        k = ease_out(clamp01((t - delay) / .55))
        text(d, (100, y + int(26 * (1 - k))), s, F_MID, PLASTER_INK, "la",
             int(255 * k))
        y += 96

    # 전환 — 붉은 선 하나가 그어지고 그날 이야기가 나온다.
    a = int(255 * ease_out(clamp01((t - 4.0) / .6)))
    if a > 0:
        d.line([(100, 1080),
                (100 + int(880 * ease_out(clamp01((t - 4.0) / .8))), 1080)],
               fill=RISK + (a,), width=6)
        text(d, (100, 1130), "그러다 대회에서 다쳤습니다.", F_MID, PLASTER_INK, "la", a)
        a2 = int(255 * ease_out(clamp01((t - 4.6) / .7)))
        text(d, (100, 1240), "깁스를 하고 돌아온 아이를 보며", F_BODY,
             PLASTER_INK2, "la", a2)
        a3 = int(255 * ease_out(clamp01((t - 5.0) / .7)))
        text(d, (100, 1306), "지난 몇 주 훈련량을", F_BODY, PLASTER_INK2, "la", a3)
        text(d, (100, 1364), "제가 전혀 모르고 있었다는 걸 알았습니다.", F_BODY,
             PLASTER_INK2, "la", a3)
    return fade_out(im, clamp01(t / dur), .90)


def scene_load(t, dur):
    """훈련 부하 — 7주에 걸쳐 위험 구간으로 넘어가는 곡선."""
    im, d = new_frame()
    head(d, t, "01", "무리한 주를", "미리 짚어 줍니다",
         "이번 주 훈련량을 지난 4주 평균과 견줍니다")

    x0, x1, y0, y1 = 90, W - 90, 760, 1300
    vals = [0.92, 1.05, 0.98, 1.18, 1.34, 1.62, 1.71]

    def X(i):
        return x0 + (x1 - x0) * i / (len(vals) - 1)

    def Y(v):
        return y1 - (y1 - y0) * (v - 0.6) / (1.9 - 0.6)

    d.rectangle([x0, Y(1.3), x1, Y(0.8)], fill=SAFE + (26,))
    d.rectangle([x0, Y(1.5), x1, Y(1.3)], fill=WATCH + (30,))
    d.rectangle([x0, y0, x1, Y(1.5)], fill=RISK + (34,))
    for v in (0.8, 1.3, 1.5):
        d.line([(x0, Y(v)), (x1, Y(v))], fill=RULE, width=2)
        text(d, (x0 - 14, Y(v)), str(v), F_TINY, INK3, "rm")

    # 선을 왼쪽부터 그린다.
    n = ease_in_out(clamp01((t - .7) / 2.2)) * (len(vals) - 1)
    pts = [(X(i), Y(vals[i])) for i in range(len(vals)) if i <= n]
    if n > int(n) and int(n) + 1 < len(vals):
        i, f = int(n), n - int(n)
        pts.append((lerp(X(i), X(i + 1), f), lerp(Y(vals[i]), Y(vals[i + 1]), f)))
    if len(pts) > 1:
        d.line(pts, fill=BEAM2, width=7, joint="curve")

    for i, v in enumerate(vals):
        if i > n:
            continue
        c = RISK if v > 1.5 else (WATCH if v > 1.3 else SAFE)
        r = 15 if v > 1.5 else 11
        d.ellipse([X(i) - r, Y(v) - r, X(i) + r, Y(v) + r], fill=c)
        text(d, (X(i), y1 + 40), f"{i+1}주", F_TINY, INK3, "ma")

    a = int(255 * ease_out(clamp01((t - 3.0) / .6)))
    if a > 0:
        d.rounded_rectangle([80, 1420, W - 80, 1560], radius=24,
                            fill=PANEL + (a,), outline=RISK + (a,), width=3)
        text(d, (W // 2, 1470), "위험 구간 — 이번 주는 강도를 낮추세요",
             F_SMALL, RISK, "ma", a)
        text(d, (W // 2, 1520), "많이 튄 주에 부상이 몰립니다", F_TINY, INK2, "ma", a)
    return fade_out(im, clamp01(t / dur), .92)


def scene_pitch(t, dur):
    """투구 수 — 나이별 상한까지 차오르는 게이지."""
    im, d = new_frame()
    head(d, t, "02", "아이는 아프다고", "말하지 않습니다",
         "그래서 통증을 묻는 대신 공을 셉니다")

    cx, cy, r = W // 2, 1080, 300
    span, start = math.pi * 1.45, math.pi * 0.775
    d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(start),
          math.degrees(start + span), fill=RULE, width=52)

    k = ease_out(clamp01((t - .6) / 1.6))
    frac = 68 / 85 * k
    if frac > .01:
        d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(start),
              math.degrees(start + span * frac), fill=WATCH, width=52)
    text(d, (cx, cy - 30), str(int(68 * k)), F_HUGE, INK, "mm")
    text(d, (cx, cy + 70), "／ 85구 · 만 12세", F_SMALL, INK3, "mm")

    text(d, (cx, 1470), "다음 등판까지 2일 휴식", F_MID, WATCH, "ma",
         int(255 * ease_out(clamp01((t - 2.3) / .6))))
    text(d, (cx, 1560), "나이별 상한과 휴식일을 자동으로 계산합니다", F_TINY, INK2,
         "ma", int(255 * ease_out(clamp01((t - 2.6) / .6))))
    return fade_out(im, clamp01(t / dur), .92)


def scene_growth(t, dur):
    """성장 기록 — 키 곡선 위에 통증일과 훈련량을 겹친다."""
    im, d = new_frame()
    head(d, t, "03", "성장기에 무리했는지", "한 장에 보입니다",
         "키 성장 곡선 위에 통증일과 훈련량을 겹칩니다")

    x0, x1, y0, y1 = 100, W - 100, 780, 1240
    hs = [148, 149.2, 150.1, 151.6, 153.4, 155.1, 156.2, 156.8]
    pv = [180, 240, 320, 410, 520, 610, 430, 260]

    def X(i):
        return x0 + (x1 - x0) * i / (len(hs) - 1)

    def Yh(v):
        return y1 - (y1 - y0) * (v - 147) / (158 - 147)

    for i, p_ in enumerate(pv):
        k = ease_out(clamp01((t - .5 - i * .07) / .5))
        bh = p_ / 620 * 190 * k
        d.rounded_rectangle([X(i) - 30, 1440 - bh, X(i) + 30, 1440],
                            radius=8, fill=BEAM + (120,))

    n = ease_in_out(clamp01((t - .8) / 2.0)) * (len(hs) - 1)
    pts = [(X(i), Yh(hs[i])) for i in range(len(hs)) if i <= n]
    if n > int(n) and int(n) + 1 < len(hs):
        i, f = int(n), n - int(n)
        pts.append((lerp(X(i), X(i + 1), f), lerp(Yh(hs[i]), Yh(hs[i + 1]), f)))
    if len(pts) > 1:
        d.line(pts, fill=SAFE, width=7, joint="curve")

    # 통증이 기록된 달. 성장이 가장 가파른 구간과 겹친다.
    for j, idx in enumerate((4, 5)):
        a = int(255 * ease_out(clamp01((t - 2.6 - j * .18) / .5)))
        if a <= 0:
            continue
        d.ellipse([X(idx) - 18, Yh(hs[idx]) - 18, X(idx) + 18, Yh(hs[idx]) + 18],
                  fill=RISK + (a,))
        text(d, (X(idx), Yh(hs[idx]) - 54), "통증", F_TINY, RISK, "ma", a)

    a = int(255 * ease_out(clamp01(t / .5)))
    text(d, (100, 1500), "키", F_SMALL, SAFE, "la", a)
    text(d, (190, 1500), "주간 훈련량", F_SMALL, BEAM2, "la", a)
    text(d, (W // 2, 1620), "병원에 그대로 가져갈 수 있는 자료", F_SMALL, INK,
         "ma", int(255 * ease_out(clamp01((t - 3.2) / .6))))
    return fade_out(im, clamp01(t / dur), .92)


def scene_portfolio(t, dur):
    """진학 실적표 — 실제 미리보기 화면."""
    im, d = new_frame()
    head(d, t, "04", "3년 치 기록이", "A4 한 장으로",
         "대회가 끝나면 30초. 진학 때 버튼 하나로 뽑습니다.")
    k = ease_out(clamp01((t - .5) / 1.1))
    phone(im, "16_portfolio_pdf", W // 2, int(lerp(1300, 1180, k)),
          int(820 * lerp(.9, 1.0, k)))
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (W // 2, 1700), "인적사항 · 대회 실적 · 신체 기록 · 훈련 성실도",
         F_SMALL, INK2, "ma", int(255 * ease_out(clamp01((t - 2.2) / .6))))
    return fade_out(im, clamp01(t / dur), .92)


def scene_parent(t, dur):
    """학부모 화면 — 하루 1분."""
    im, d = new_frame()
    head(d, t, "05", "잔소리 대신", "하루 1분 확인",
         "오늘 훈련했는지, 어디가 아픈지 한 화면에.")
    k = ease_out(clamp01((t - .5) / 1.1))
    phone(im, "30_parent_today", W // 2, int(lerp(1300, 1180, k)), 820)
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (W // 2, 1700), "일지 내용과 AI 코치 대화는 부모에게 가지 않습니다",
         F_SMALL, INK2, "ma", int(255 * ease_out(clamp01((t - 2.2) / .6))))
    return fade_out(im, clamp01(t / dur), .92)


def scene_end(t, dur):
    """마무리."""
    im, _ = new_frame()
    im = floodlight(im, [W // 2 - 650, 500, W // 2 + 650, 1500], (10, 28, 58))
    d = ImageDraw.Draw(im, "RGBA")

    text(d, (W // 2, 780), "오늘의 루틴이", F_BIG, INK, "ma",
         int(255 * ease_out(clamp01(t / .7))))
    text(d, (W // 2, 890), "3년 뒤의 기록이 됩니다", F_BIG, INK, "ma",
         int(255 * ease_out(clamp01((t - .35) / .7))))

    a = int(255 * ease_out(clamp01((t - 1.0) / .7)))
    text(d, (W // 2, 1060), "엘리트 루틴 케어", F_MID, BEAM2, "ma", a)
    text(d, (W // 2, 1140), "초·중·고 엘리트 선수 · 38개 종목", F_SMALL, INK2, "ma", a)
    text(d, (W // 2, 1280), "k-elite.github.io", F_SMALL, INK3, "ma",
         int(255 * ease_out(clamp01((t - 1.5) / .7))))
    return fade_out(im, clamp01(t / dur), .88)


SCENES = [
    (scene_open, 3.2),
    (scene_story, 6.4),
    (scene_load, 5.2),
    (scene_pitch, 4.6),
    (scene_growth, 5.2),
    (scene_portfolio, 4.2),
    (scene_parent, 4.2),
    (scene_end, 3.6),
]


def main():
    total = sum(d for _, d in SCENES)
    nframes = int(total * FPS)
    print(f"길이 {total:.1f}초 · {nframes}프레임 · {W}x{H} @{FPS}fps")

    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y",
           "-f", "rawvideo", "-vcodec", "rawvideo",
           "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
           "-i", "-", "-an",
           "-vcodec", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "20",
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

    # 사이트에 박아 넣을 base64도 함께 만든다.
    with open(OUT, "rb") as f:
        b64 = "data:video/mp4;base64," + base64.b64encode(f.read()).decode()
    with open(OUT_B64, "w", encoding="utf-8") as f:
        f.write(b64)
    print("base64:", OUT_B64, len(b64) // 1024, "KB")


if __name__ == "__main__":
    main()
