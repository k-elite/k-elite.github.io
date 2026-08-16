# -*- coding: utf-8 -*-
"""만화 컷 안의 UI를 실제로 움직이게 한다.

## 왜 이렇게 하나

평면 그림 한 장을 잘라 팔을 휘두르게 만들 수는 없다. 팔을 옮기면 팔이
있던 자리에 구멍이 남는다. 그건 캐릭터를 레이어로 다시 그려야 하는 일이다.

대신 **와이프 리빌**을 쓴다. 움직이게 하고 싶은 요소를 그 자리의 배경색으로
덮었다가 서서히 걷어낸다. 게이지가 차오르고, 토글이 켜지고, 그래프가
그려지고, 체크가 하나씩 붙는 것처럼 보인다. 그리는 것은 배경색 사각형뿐이라
이음매도 색 어긋남도 생기지 않는다.

여기에 손가락 탭과 강조 링을 얹으면 "무엇을 눌러야 하는지"가 보인다.
영상의 목적이 사용법이므로 그게 핵심이다.

좌표는 모두 **컷 좌표계**(368x392)다.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

TAP = (255, 190, 60)      # 손가락·강조. 만화의 금색과 맞춘다.
RING = (255, 190, 60)


def _ease(t):
    return 1 - (1 - t) ** 3


def _clamp(v):
    return max(0.0, min(1.0, v))


def _phase(t, at, dur):
    """이 시각에 이 동작이 얼마나 진행됐나. 0이면 아직, 1이면 끝."""
    if dur <= 0:
        return 1.0 if t >= at else 0.0
    return _clamp((t - at) / dur)


def _bg(im, spec):
    """배경색. 좌표를 주면 그 픽셀을 뽑는다 — 손으로 색을 적으면 어긋난다."""
    if isinstance(spec, tuple) and len(spec) == 3:
        return spec
    return im.getpixel(spec)


# ── 동작 ──────────────────────────────────────────────────

def op_wipe(im, d, t, box, at, dur, bg, dir="r"):
    """덮개를 걷어 요소를 드러낸다. dir 은 걷히는 방향."""
    p = _ease(_phase(t, at, dur))
    if p >= 1:
        return
    x0, y0, x1, y1 = box
    c = _bg(im, bg)
    if dir == "r":      # 왼쪽부터 드러난다
        d.rectangle([x0 + (x1 - x0) * p, y0, x1, y1], fill=c)
    elif dir == "l":
        d.rectangle([x0, y0, x1 - (x1 - x0) * p, y1], fill=c)
    elif dir == "u":    # 아래부터 드러난다
        d.rectangle([x0, y0, x1, y1 - (y1 - y0) * p], fill=c)
    else:               # "d" — 위부터
        d.rectangle([x0, y0 + (y1 - y0) * p, x1, y1], fill=c)


def op_circle(im, d, t, c, r, at, dur, bg):
    """덮개 원이 줄어들며 안의 그림이 드러난다."""
    p = _ease(_phase(t, at, dur))
    if p >= 1:
        return
    rr = r * (1 - p)
    if rr <= 0.5:
        return
    d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=_bg(im, bg))


def op_pie(im, d, t, c, r, at, dur, bg, start=-90):
    """게이지가 돌아가며 채워지는 것처럼 보이게 한다."""
    p = _ease(_phase(t, at, dur))
    if p >= 1:
        return
    box = [c[0] - r, c[1] - r, c[0] + r, c[1] + r]
    d.pieslice(box, start + 360 * p, start + 360, fill=_bg(im, bg))


def op_tap(im, d, t, p, at, dur=0.9):
    """손가락이 내려와 누르고 파문이 퍼진다."""
    k = _phase(t, at, dur)
    if k <= 0 or k >= 1:
        return
    x, y = p
    # 내려오는 손가락
    drop = _ease(_clamp(k / 0.35))
    fy = y - 26 * (1 - drop)
    a = int(230 * min(1.0, k / 0.2))
    d.ellipse([x - 11, fy - 11, x + 11, fy + 11], fill=TAP + (a,))
    d.ellipse([x - 5, fy - 5, x + 5, fy + 5], fill=(255, 255, 255, a))
    # 파문
    if k > 0.35:
        w = _ease(_clamp((k - 0.35) / 0.65))
        rr = 12 + 26 * w
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  outline=TAP + (int(200 * (1 - w)),), width=3)


def op_ring(im, d, t, box, at, dur=1.0):
    """무엇을 보라는 강조 링."""
    k = _phase(t, at, dur)
    if k <= 0 or k >= 1:
        return
    a = int(230 * math.sin(math.pi * k))
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], radius=8,
                        outline=RING + (a,), width=3)


def op_glow(im, d, t, p, at, dur=1.0, r=9):
    """관절·아이콘이 살아 있는 것처럼 뛴다."""
    k = _phase(t, at, dur)
    if k <= 0 or k >= 1:
        return
    a = int(220 * math.sin(math.pi * k))
    rr = r * (1 + 0.5 * math.sin(math.pi * k))
    d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr],
              outline=TAP + (a,), width=3)


def op_focus(im, d, t, box, at, dur):
    """흐릿한 상태에서 또렷해진다.

    배경이 그라데이션인 곳에서는 덮개 색을 맞출 수 없다. 한 가지 색으로
    덮으면 그 자리만 판판해져 티가 난다. 그래서 그 자리 그림 자체를 흐리게
    만들었다가 되돌린다.
    """
    p = _ease(_phase(t, at, dur))
    if p >= 1:
        return
    x0, y0, x1, y1 = (int(v) for v in box)
    region = im.crop((x0, y0, x1, y1))
    blurred = region.filter(ImageFilter.GaussianBlur(7 * (1 - p) + 0.5))
    im.paste(Image.blend(blurred, region, p), (x0, y0))


OPS = {"wipe": op_wipe, "circle": op_circle, "pie": op_pie,
       "focus": op_focus, "tap": op_tap, "ring": op_ring,
       "glow": op_glow}


# ── 컷별 각본 ─────────────────────────────────────────────
#
# 좌표는 컷 좌표계(368x392). 배경색은 색을 적는 대신 **뽑을 좌표**를 준다.

SCRIPT = {
    0: [  # 종목 선택 및 선수 정보 입력
        ("wipe", dict(box=(222, 98, 352, 272), at=.4, dur=1.8,
                      bg=(240, 92), dir="d")),
        ("ring", dict(box=(224, 100, 350, 128), at=.9, dur=.8)),
        ("ring", dict(box=(224, 186, 350, 214), at=1.7, dur=.8)),
        ("wipe", dict(box=(226, 284, 350, 316), at=2.6, dur=.5,
                      bg=(240, 278), dir="r")),
        ("tap", dict(p=(288, 300), at=3.3)),
    ],
    1: [  # 부상 예방 — 모션 인식
        ("glow", dict(p=(205, 177), at=.6, dur=1.0, r=8)),
        ("glow", dict(p=(322, 161), at=1.0, dur=1.0, r=8)),
        ("glow", dict(p=(313, 262), at=1.4, dur=1.0, r=8)),
        ("wipe", dict(box=(188, 272, 292, 322), at=1.9, dur=.6,
                      bg=(196, 282), dir="r")),
        ("circle", dict(c=(313, 300), r=34, at=2.5, dur=.9, bg=(330, 300))),
    ],
    2: [  # 루틴 습관화 — 알람 켜기, 미션 체크
        ("wipe", dict(box=(300, 136, 336, 156), at=.6, dur=.5,
                      bg=(292, 146), dir="r")),
        ("tap", dict(p=(318, 146), at=.5)),
        ("wipe", dict(box=(300, 179, 336, 199), at=1.3, dur=.5,
                      bg=(292, 189), dir="r")),
        ("tap", dict(p=(318, 189), at=1.2)),
        ("wipe", dict(box=(186, 264, 340, 284), at=2.2, dur=.45,
                      bg=(230, 258), dir="r")),
        ("wipe", dict(box=(186, 290, 340, 310), at=2.7, dur=.45,
                      bg=(230, 258), dir="r")),
        ("ring", dict(box=(180, 316, 342, 340), at=3.4, dur=1.0)),
    ],
    3: [  # 훈련 기록 — 컨디션, 피로도
        ("wipe", dict(box=(220, 196, 344, 240), at=.5, dur=.9,
                      bg=(250, 205), dir="r")),
        ("circle", dict(c=(318, 180), r=15, at=1.4, dur=.6, bg=(250, 205))),
        ("tap", dict(p=(318, 180), at=1.5)),
        ("wipe", dict(box=(220, 214, 300, 234), at=2.3, dur=1.3,
                      bg=(250, 205), dir="r")),
        ("ring", dict(box=(216, 206, 348, 242), at=3.5, dur=1.0)),
    ],
    4: [  # 분석 리포트 — 점수 링, 가이드
        ("focus", dict(box=(238, 138, 344, 244), at=.5, dur=1.5)),
        ("ring", dict(box=(238, 140, 344, 242), at=1.8, dur=.9)),
        ("focus", dict(box=(222, 210, 350, 326), at=2.2, dur=1.4)),
        ("tap", dict(p=(284, 228), at=3.6)),
    ],
    5: [  # 성장 기록 — 그래프가 그려진다
        ("wipe", dict(box=(228, 38, 354, 124), at=.4, dur=1.6,
                      bg=(340, 44), dir="r")),
        ("wipe", dict(box=(228, 146, 354, 248), at=1.9, dur=1.3,
                      bg=(340, 152), dir="u")),
        ("wipe", dict(box=(214, 276, 354, 340), at=3.2, dur=.9,
                      bg=(330, 282), dir="r")),
    ],
    6: [  # 학부모 대시보드 — 카드가 차례로
        ("wipe", dict(box=(232, 152, 344, 208), at=.5, dur=.8,
                      bg=(300, 160), dir="d")),
        ("wipe", dict(box=(232, 216, 344, 290), at=1.3, dur=.8,
                      bg=(300, 225), dir="d")),
        ("wipe", dict(box=(232, 298, 344, 356), at=2.1, dur=.7,
                      bg=(300, 300), dir="d")),
        ("wipe", dict(box=(250, 322, 348, 356), at=2.8, dur=1.0,
                      bg=(300, 300), dir="u")),
    ],
    7: [  # 종합 리포트 — 항목이 붙고 버튼을 누른다
        ("wipe", dict(box=(220, 132, 344, 300), at=.5, dur=1.8,
                      bg=(340, 140), dir="d")),
        ("wipe", dict(box=(220, 302, 342, 334), at=2.5, dur=.5,
                      bg=(230, 340), dir="r")),
        ("ring", dict(box=(218, 300, 344, 336), at=3.0, dur=.9)),
        ("tap", dict(p=(281, 318), at=3.8)),
    ],
}


def animate(panel, idx, t):
    """컷 하나에 그 시각의 동작을 얹어 돌려준다."""
    ops = SCRIPT.get(idx)
    if not ops:
        return panel

    im = panel.copy()
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d_solid = ImageDraw.Draw(im)          # 덮개는 불투명하게
    d_over = ImageDraw.Draw(layer, "RGBA")  # 손가락·링은 반투명하게

    for kind, kw in ops:
        fn = OPS[kind]
        d = d_over if kind in ("tap", "ring", "glow") else d_solid
        fn(im, d, t, **kw)

    if layer.getbbox():
        im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
    return im
