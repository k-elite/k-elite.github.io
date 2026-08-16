# -*- coding: utf-8 -*-
"""엘리트 루틴 케어 소개 사이트를 만든다.

앱 화면은 실제 기기에서 찍은 것을 base64 로 박아 넣는다. 외부 요청이
막혀 있어(CSP) 링크로는 못 부른다.

## 지면 구성

숫자를 다루는 앱이라 지면도 숫자로 말한다. 문단보다 도식이 앞서고,
가장 중요한 지표 하나(훈련 부하)는 **스크롤에 물려** 크게 하나만 보여
준다. 나머지는 카드 안에 작게 접어 넣는다.

영상은 **가로 한 편만** 자동 재생한다. 소리 없는 영상이라 자동 재생이
막히지 않고, 두 편을 나란히 두면 어느 쪽을 보라는 건지 알 수 없다.
"""
import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_head import CSS  # noqa: E402

CSS += """
/* ── 이 페이지에서만 쓰는 것 ─────────────────────────── */
.flow { stroke-dasharray: 7 11; animation: dashmove 1.1s linear infinite; }
@keyframes dashmove { to { stroke-dashoffset: -36; } }
.two-up { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr);
  gap: clamp(28px,5vw,64px); align-items: center; }
@media (max-width: 900px) { .two-up { grid-template-columns: 1fr; } }
.side-360 { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,360px);
  gap: clamp(28px,5vw,64px); align-items: center; }
@media (max-width: 900px) { .side-360 { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) { .flow { animation: none; } }
"""

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SP = HERE
# 영상은 파일로 둔다. base64 로 박으면 첫 화면이 8MB 를 넘게 받는다.
MANGA_WIDE = "manga_wide.mp4"
IDX = json.load(io.open(os.path.join(SP, "shots_web", "index.json"),
                        encoding="utf-8"))


def S(key):
    return IDX.get(key, "")


# ─────────────────────────────────────────────────────────────
# 스크롤에 물린 큰 차트 — 훈련 부하
# ─────────────────────────────────────────────────────────────

ACWR = [0.92, 1.05, 0.98, 1.18, 1.34, 1.62, 1.71]


def acwr_big():
    """7주 훈련 부하. 선이 스크롤을 따라 그려지고 마커가 함께 간다.

    좌표 계산을 파이썬에서 해 두고, 자바스크립트는 `getPointAtLength`
    로 선 위를 따라가기만 한다. 값 배열도 함께 넘겨 큰 숫자를 맞춘다.
    """
    w, h = 640, 340
    x0, x1, y0, y1 = 52, 618, 26, 286
    lo, hi = 0.6, 1.9

    def X(i):
        return x0 + (x1 - x0) * i / (len(ACWR) - 1)

    def Y(v):
        return y1 - (y1 - y0) * (v - lo) / (hi - lo)

    bands = (
        f'<rect x="{x0}" y="{Y(1.3):.1f}" width="{x1-x0}" height="{Y(0.8)-Y(1.3):.1f}"'
        f' fill="var(--safe)" opacity=".15"/>'
        f'<rect x="{x0}" y="{Y(1.5):.1f}" width="{x1-x0}" height="{Y(1.3)-Y(1.5):.1f}"'
        f' fill="var(--watch)" opacity=".17"/>'
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{Y(1.5)-y0:.1f}"'
        f' fill="var(--risk)" opacity=".16"/>')

    rules = "".join(
        f'<line class="gridline" x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}"/>'
        f'<text class="tick" x="{x0-10}" y="{Y(v)+4:.1f}" text-anchor="end">{v}</text>'
        for v in (0.8, 1.3, 1.5, 1.8))

    zone_tags = (
        f'<text x="{x1-6}" y="{Y(1.68):.1f}" text-anchor="end" fill="var(--risk)"'
        f' style="font-size:12px;font-weight:800">위험</text>'
        f'<text x="{x1-6}" y="{Y(1.40):.1f}" text-anchor="end" fill="var(--watch)"'
        f' style="font-size:12px;font-weight:800">주의</text>'
        f'<text x="{x1-6}" y="{Y(1.05):.1f}" text-anchor="end" fill="var(--safe)"'
        f' style="font-size:12px;font-weight:800">안전</text>')

    d = "M" + " L".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ACWR))

    weeks = "".join(
        f'<text class="tick" x="{X(i):.1f}" y="{h-12}" text-anchor="middle">{i+1}주</text>'
        for i in range(len(ACWR)))

    xs = ",".join(f"{X(i):.1f}" for i in range(len(ACWR)))

    return f'''
<svg class="chart" id="acwrsvg" viewBox="0 0 {w} {h}" role="img"
     data-vals="{','.join(str(v) for v in ACWR)}" data-xs="{xs}"
     data-top="{y0}" data-bot="{y1}"
     aria-label="훈련 부하가 7주에 걸쳐 0.92에서 1.71까지 올라 위험 구간에 들어가는 그래프">
  {bands}{rules}{zone_tags}
  <line id="acwrguide" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"
        stroke="var(--ink-3)" stroke-width="1" stroke-dasharray="4 5" opacity="0"/>
  <path id="acwrline" d="{d}" fill="none" stroke="var(--beam-2)" stroke-width="3.4"
        stroke-linecap="round" stroke-linejoin="round"/>
  <circle id="acwrdot" cx="{X(0):.1f}" cy="{Y(ACWR[0]):.1f}" r="8"
          fill="var(--beam)" stroke="var(--ground)" stroke-width="3"/>
  {weeks}
</svg>'''


# ─────────────────────────────────────────────────────────────
# 카드 안에 들어가는 차트들
# ─────────────────────────────────────────────────────────────

def pitch_gauge():
    """투구 수 — 나이별 하루 상한 대비."""
    cur, cap = 68, 85
    r, cx, cy = 78, 110, 108
    span = math.pi * 1.45
    start = math.pi * 0.775

    def pt(frac):
        a = start + span * frac
        return cx + r * math.cos(a), cy + r * math.sin(a)

    def arc(f0, f1, color, width, cls="", delay=0):
        ax, ay = pt(f0)
        bx, by = pt(f1)
        large = 1 if (f1 - f0) * span > math.pi else 0
        length = span * r * (f1 - f0)
        style = f'--len:{length:.0f};animation-delay:{delay}s' if cls else ''
        return (f'<path class="{cls}" style="{style}" d="M{ax:.1f},{ay:.1f} '
                f'A{r},{r} 0 {large} 1 {bx:.1f},{by:.1f}" fill="none" '
                f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')

    return f'''
<svg class="chart" viewBox="0 0 220 190" role="img"
     aria-label="오늘 투구 수 68개, 나이별 상한 85개 게이지">
  {arc(0, 1, "var(--rule-2)", 14)}
  {arc(0, cur / cap, "var(--watch)", 14, "draw", .25)}
  <text x="110" y="104" text-anchor="middle" fill="var(--ink)"
        style="font-size:46px;font-weight:800;letter-spacing:-.05em">{cur}</text>
  <text x="110" y="128" text-anchor="middle" class="tick">／ {cap}구 · 만 12세</text>
  <text x="110" y="168" text-anchor="middle" fill="var(--watch)"
        style="font-size:13px;font-weight:800">다음 등판까지 2일 휴식</text>
</svg>'''


def week_strip():
    """주간 목표 5일 — 회복일도 채운 날로 센다."""
    days = [("월", "done"), ("화", "done"), ("수", "rest"), ("목", "done"),
            ("금", "done"), ("토", "done"), ("일", "todo")]
    cells = []
    for i, (day, st) in enumerate(days):
        fill = {"done": "var(--beam)", "rest": "var(--watch)",
                "todo": "var(--panel-2)"}[st]
        mark = {"done": "✓", "rest": "🌙", "todo": ""}[st]
        cells.append(
            f'<g class="pop" style="animation-delay:{i*.08:.2f}s">'
            f'<rect x="{i*58}" y="0" width="46" height="46" rx="13" fill="{fill}"/>'
            f'<text x="{i*58+23}" y="30" text-anchor="middle" '
            f'style="font-size:18px" fill="#fff">{mark}</text>'
            f'<text x="{i*58+23}" y="66" text-anchor="middle" class="tick">{day}</text>'
            f'</g>')
    return (f'<svg class="chart" viewBox="0 0 404 76" role="img" '
            f'aria-label="주 5일 목표를 수요일 회복일 포함해 달성한 한 주">'
            f'{"".join(cells)}</svg>')


def growth_timeline():
    """키 성장 곡선 + 통증일 + 주간 투구량."""
    w, h = 560, 260
    x0, x1, y0, y1 = 40, 546, 20, 200
    heights = [148, 149.2, 150.1, 151.6, 153.4, 155.1, 156.2, 156.8]
    pitch = [180, 240, 320, 410, 520, 610, 430, 260]
    pain = [4, 5]

    def X(i):
        return x0 + (x1 - x0) * i / (len(heights) - 1)

    def Yh(v):
        return y1 - (y1 - y0) * (v - 147) / (158 - 147)

    bars = "".join(
        f'<rect class="rise" style="animation-delay:{i*.05:.2f}s" '
        f'x="{X(i)-11:.1f}" y="{240 - p/620*36:.1f}" width="22" '
        f'height="{p/620*36:.1f}" rx="3" fill="var(--beam)" opacity=".45"/>'
        for i, p in enumerate(pitch))

    line = " ".join(f"{X(i):.1f},{Yh(v):.1f}" for i, v in enumerate(heights))

    marks = "".join(
        f'<g class="pop" style="animation-delay:{1.1+n*.12:.2f}s">'
        f'<line x1="{X(i):.1f}" y1="{Yh(heights[i]):.1f}" x2="{X(i):.1f}" '
        f'y2="240" stroke="var(--risk)" stroke-width="1.5" stroke-dasharray="3 3" opacity=".7"/>'
        f'<circle cx="{X(i):.1f}" cy="{Yh(heights[i]):.1f}" r="6.5" fill="var(--risk)"/>'
        f'<text x="{X(i):.1f}" y="{Yh(heights[i])-13:.1f}" text-anchor="middle" '
        f'fill="var(--risk)" style="font-size:11px;font-weight:800">통증</text></g>'
        for n, i in enumerate(pain))

    months = "".join(
        f'<text class="tick" x="{X(i):.1f}" y="256" text-anchor="middle">{3+i}월</text>'
        for i in range(len(heights)))

    return f'''
<svg class="chart" viewBox="0 0 {w} {h}" role="img"
     aria-label="키가 빠르게 자라는 구간에서 주간 투구량이 정점을 찍고 통증이 두 번 기록된 그래프">
  {bars}
  <polyline class="draw" style="--len:700" points="{line}" fill="none"
            stroke="var(--safe)" stroke-width="2.8" stroke-linecap="round"/>
  {marks}{months}
  <text class="tick" x="{x0}" y="{y0-4}" fill="var(--safe)">키</text>
  <text class="tick" x="{x0+34}" y="{y0-4}" fill="var(--beam-2)">주간 투구량</text>
</svg>'''


def radar_chart():
    """지도자 평가 — 종목별 역량을 오각형으로."""
    axes = [("파워", 4.2), ("스피드", 3.6), ("기술", 4.6),
            ("경기 이해", 3.9), ("태도", 4.8)]
    cx, cy, r = 150, 142, 92
    n = len(axes)

    def pt(i, frac):
        a = -math.pi / 2 + i * 2 * math.pi / n
        return cx + r * frac * math.cos(a), cy + r * frac * math.sin(a)

    rings = "".join(
        '<polygon points="' +
        " ".join(f"{pt(i, k/5)[0]:.1f},{pt(i, k/5)[1]:.1f}" for i in range(n)) +
        '" fill="none" stroke="var(--rule)" stroke-width="1"/>'
        for k in (1, 2, 3, 4, 5))

    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{pt(i,1)[0]:.1f}" y2="{pt(i,1)[1]:.1f}"'
        f' stroke="var(--rule)" stroke-width="1"/>' for i in range(n))

    shape = " ".join(f"{pt(i, v/5)[0]:.1f},{pt(i, v/5)[1]:.1f}"
                     for i, (_, v) in enumerate(axes))

    knobs = "".join(
        f'<circle class="pop" style="animation-delay:{.5+i*.07:.2f}s"'
        f' cx="{pt(i, v/5)[0]:.1f}" cy="{pt(i, v/5)[1]:.1f}" r="4.5" fill="var(--beam-2)"/>'
        for i, (_, v) in enumerate(axes))

    labels = ""
    for i, (name, v) in enumerate(axes):
        lx, ly = pt(i, 1.24)
        anchor = "middle"
        if lx > cx + 8:
            anchor = "start"
        elif lx < cx - 8:
            anchor = "end"
        labels += (f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="{anchor}"'
                   f' fill="var(--ink-2)" style="font-size:13px;font-weight:700">'
                   f'{name} <tspan fill="var(--beam-2)">{v}</tspan></text>')

    return f'''
<svg class="chart" viewBox="0 0 300 290" role="img"
     aria-label="파워 4.2, 스피드 3.6, 기술 4.6, 경기 이해 3.9, 태도 4.8 의 역량 오각형">
  {rings}{spokes}
  <polygon class="pop" style="animation-delay:.35s" points="{shape}"
           fill="var(--beam)" fill-opacity=".18" stroke="var(--beam-2)" stroke-width="2.4"/>
  {knobs}{labels}
  <text x="150" y="276" text-anchor="middle" class="tick">감독이 매긴 5점 척도 · 실적표 반영은 동의로만</text>
</svg>'''


def loop_diagram():
    """하루 3분 루프."""
    steps = [("아침", "오늘의 미션 확인"), ("훈련 후", "루틴 완료 · 불꽃"),
             ("저녁", "일지 · 컨디션"), ("보상", "아케이드 입장권")]
    cx, cy, r = 150, 150, 104
    out = []
    for i, (when, what) in enumerate(steps):
        a = -math.pi / 2 + i * math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(
            f'<g class="pop" style="animation-delay:{.2+i*.14:.2f}s">'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="31" fill="var(--panel)" '
            f'stroke="var(--beam)" stroke-width="1.6"/>'
            f'<text x="{x:.0f}" y="{y+4:.0f}" text-anchor="middle" '
            f'fill="var(--beam-2)" style="font-size:12px;font-weight:800">{when}</text>'
            f'<text x="{x:.0f}" y="{y+53:.0f}" text-anchor="middle" '
            f'class="tick">{what}</text></g>')
    return f'''
<svg class="chart" viewBox="0 0 300 300" style="max-width:320px;margin-inline:auto"
     role="img" aria-label="아침 미션 확인, 훈련 후 루틴 완료, 저녁 일지, 보상 아케이드로 도는 하루 흐름도">
  <circle class="draw" style="--len:660" cx="{cx}" cy="{cy}" r="{r}" fill="none"
          stroke="var(--rule-2)" stroke-width="1.6" stroke-dasharray="660"/>
  <circle class="flow" cx="{cx}" cy="{cy}" r="{r}" fill="none"
          stroke="var(--beam)" stroke-width="2.4" opacity=".55"/>
  {"".join(out)}
  <text x="150" y="144" text-anchor="middle" fill="var(--ink)"
        style="font-size:34px;font-weight:800;letter-spacing:-.05em">3분</text>
  <text x="150" y="167" text-anchor="middle" class="tick">하루에</text>
</svg>'''


def economy_diagram():
    """훈련 재화와 게임 재화의 한 방향 문."""
    return '''
<svg class="chart" viewBox="0 0 640 230" role="img"
     aria-label="훈련으로 얻은 포인트만 등급에 반영되고, 게임 코인은 꾸미기에만 쓰이는 구조도">
  <g class="reveal in-view">
    <rect x="4" y="26" width="252" height="176" rx="20" fill="var(--panel)"
          stroke="var(--beam)" stroke-width="1.8"/>
    <text x="26" y="58" fill="var(--beam-2)" style="font-size:11px;font-weight:800;letter-spacing:.14em">훈련으로만</text>
    <text x="26" y="90" fill="var(--ink)" style="font-size:21px;font-weight:800">🔥 불꽃 포인트</text>
    <text x="26" y="118" fill="var(--ink-2)" style="font-size:14px">루틴 · 일지 · 측정 · 회복일</text>
    <rect x="26" y="136" width="208" height="46" rx="11" fill="var(--safe)" opacity=".12"/>
    <text x="42" y="164" fill="var(--safe)" style="font-size:14px;font-weight:800">등급과 순위에 반영</text>
  </g>
  <g>
    <path class="flow" d="M266,114 L370,114" stroke="var(--watch)" stroke-width="3" fill="none"/>
    <path d="M266,114 L374,114" stroke="var(--watch)" stroke-width="3"
          marker-end="url(#ah)" fill="none" opacity="0"/>
    <polygon points="374,114 362,108 362,120" fill="var(--watch)"/>
    <text x="318" y="96" text-anchor="middle" fill="var(--watch)"
          style="font-size:13px;font-weight:800">입장권</text>
    <text x="318" y="140" text-anchor="middle" class="tick">한 방향 · 되돌아오지 않음</text>
  </g>
  <g class="reveal in-view" style="animation-delay:.35s">
    <rect x="388" y="26" width="248" height="176" rx="20" fill="var(--panel)"
          stroke="var(--watch)" stroke-width="1.8"/>
    <text x="410" y="58" fill="var(--watch)" style="font-size:11px;font-weight:800;letter-spacing:.14em">게임으로만</text>
    <text x="410" y="90" fill="var(--ink)" style="font-size:21px;font-weight:800">🪙 게임 코인</text>
    <text x="410" y="118" fill="var(--ink-2)" style="font-size:14px">아케이드 6종 · 겉모습 상점</text>
    <rect x="410" y="136" width="204" height="46" rx="11" fill="var(--risk)" opacity=".12"/>
    <text x="426" y="164" fill="var(--risk)" style="font-size:14px;font-weight:800">등급에 1점도 반영 안 됨</text>
  </g>
  <defs>
    <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7"
            markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--watch)"/>
    </marker>
  </defs>
</svg>'''


def flow_diagram():
    """기록이 어디까지 가는지."""
    return '''
<svg class="chart" viewBox="0 0 660 300" role="img"
     aria-label="기록은 기기에 먼저 저장되고, 동의를 켠 항목만 서버를 거쳐 보호자와 지도자에게 간다는 흐름도">
  <!-- 기기 -->
  <g class="reveal in-view">
    <rect x="6" y="60" width="180" height="140" rx="18" fill="var(--panel)"
          stroke="var(--beam)" stroke-width="1.8"/>
    <text x="26" y="90" fill="var(--beam-2)" style="font-size:11px;font-weight:800;letter-spacing:.14em">1단계</text>
    <text x="26" y="118" fill="var(--ink)" style="font-size:19px;font-weight:800">📱 아이 기기</text>
    <text x="26" y="146" fill="var(--ink-2)" style="font-size:13px">모든 기록이 먼저</text>
    <text x="26" y="166" fill="var(--ink-2)" style="font-size:13px">여기에 저장됩니다</text>
    <text x="26" y="188" fill="var(--safe)" style="font-size:12px;font-weight:800">인터넷 없어도 동작</text>
  </g>

  <!-- 동의 문 -->
  <path class="flow" d="M192,130 L246,130" stroke="var(--beam)" stroke-width="3" fill="none"/>
  <polygon points="250,130 238,124 238,136" fill="var(--beam)"/>
  <g class="reveal in-view" style="animation-delay:.2s">
    <rect x="256" y="86" width="140" height="88" rx="16" fill="var(--panel-2)"
          stroke="var(--beam-2)" stroke-width="1.8" stroke-dasharray="6 5"/>
    <text x="326" y="118" text-anchor="middle" fill="var(--ink)"
          style="font-size:16px;font-weight:800">🔓 동의 스위치</text>
    <text x="326" y="142" text-anchor="middle" fill="var(--ink-2)" style="font-size:12.5px">항목별로 아이가 켭니다</text>
    <text x="326" y="160" text-anchor="middle" fill="var(--ink-3)" style="font-size:12px">끄면 즉시 멈춥니다</text>
  </g>
  <path class="flow" d="M402,110 L462,84" stroke="var(--beam)" stroke-width="3" fill="none"/>
  <polygon points="466,82 452,80 456,92" fill="var(--beam)"/>
  <path class="flow" d="M402,152 L462,178" stroke="var(--beam)" stroke-width="3" fill="none"/>
  <polygon points="466,180 452,182 456,170" fill="var(--beam)"/>

  <!-- 받는 쪽 -->
  <g class="reveal in-view" style="animation-delay:.4s">
    <rect x="472" y="42" width="182" height="82" rx="16" fill="var(--panel)" stroke="var(--rule-2)"/>
    <text x="492" y="72" fill="var(--ink)" style="font-size:17px;font-weight:800">👨‍👩‍👧 보호자</text>
    <text x="492" y="96" fill="var(--ink-2)" style="font-size:12.5px">훈련 여부 · 연속 일수 · 신체</text>
    <text x="492" y="114" fill="var(--ink-3)" style="font-size:12px">일지 본문은 못 봅니다</text>

    <rect x="472" y="140" width="182" height="82" rx="16" fill="var(--panel)" stroke="var(--rule-2)"/>
    <text x="492" y="170" fill="var(--ink)" style="font-size:17px;font-weight:800">🧑‍🏫 감독 · 코치</text>
    <text x="492" y="194" fill="var(--ink-2)" style="font-size:12.5px">출석 · 통증 있다/없다</text>
    <text x="492" y="212" fill="var(--ink-3)" style="font-size:12px">키·기록은 안 보입니다</text>
  </g>

  <!-- 나가지 않는 것 -->
  <g class="reveal in-view" style="animation-delay:.55s">
    <rect x="6" y="226" width="390" height="66" rx="16" fill="var(--risk)" fill-opacity=".08"
          stroke="var(--risk)" stroke-width="1.6" stroke-dasharray="7 5"/>
    <text x="26" y="254" fill="var(--risk)" style="font-size:14px;font-weight:800">기기 밖으로 나가지 않는 것</text>
    <text x="26" y="278" fill="var(--ink-2)" style="font-size:13px">훈련 일지 본문 · AI 코치 대화 · 카메라 자세 영상</text>
  </g>
  <g class="reveal in-view" style="animation-delay:.65s">
    <rect x="412" y="226" width="242" height="66" rx="16" fill="var(--panel)" stroke="var(--rule)"/>
    <text x="432" y="254" fill="var(--ink)" style="font-size:14px;font-weight:800">랭킹 서버에 남는 것</text>
    <text x="432" y="278" fill="var(--ink-2)" style="font-size:13px">가린 이름(김**) · 시즌 점수뿐</text>
  </g>
</svg>'''


HEAT = [
    "3222031322123", "2331120223313", "1232303122231", "3123210331222",
    "2213331202133", "3321122313021",
]


def heatmap():
    """지난 6주 활동. 0은 안 한 날, 3은 루틴·일지·측정을 다 한 날."""
    tone = {"0": "var(--panel-2)", "1": "rgba(22,104,240,.30)",
            "2": "rgba(22,104,240,.60)", "3": "var(--beam)"}
    cells = []
    n = 0
    for row in HEAT:
        for ch in row:
            cells.append(f'<i style="background:{tone[ch]};'
                         f'animation-delay:{n*.008:.3f}s"></i>')
            n += 1
    return (f'<div class="heat" role="img" aria-label="지난 6주 78일 중 활동한 날을 '
            f'진하기로 표시한 격자">{"".join(cells)}</div>'
            f'<div class="heat-key"><span>적게</span>'
            f'<i style="background:var(--panel-2)"></i>'
            f'<i style="background:rgba(22,104,240,.30)"></i>'
            f'<i style="background:rgba(22,104,240,.60)"></i>'
            f'<i style="background:var(--beam)"></i>'
            f'<span>많이</span></div>')


SPORTS = [
    ("⚽", "축구"), ("⚾", "야구"), ("🥋", "태권도"), ("🏃", "육상"),
    ("🏊", "수영"), ("🥎", "소프트볼"), ("⛳", "골프"), ("🏸", "배드민턴"),
    ("🤼", "유도"), ("🏀", "농구"), ("🏐", "배구"), ("🎽", "검도"),
    ("🏓", "탁구"), ("🤼", "씨름"), ("🎾", "테니스"), ("🥊", "복싱"),
    ("🤸", "기계체조"), ("🎗️", "리듬체조"), ("🤼", "레슬링"), ("🤺", "펜싱"),
    ("🏹", "양궁"), ("🎯", "사격"), ("🤾", "핸드볼"), ("🏋️", "역도"),
    ("⛸️", "쇼트트랙"), ("⛸️", "피겨"), ("⛸️", "스피드스케이팅"), ("🚴", "사이클"),
    ("🏑", "하키"), ("🛼", "인라인"), ("🎳", "볼링"), ("🏅", "근대5종"),
    ("🚣", "조정/카누"), ("🏒", "아이스하키"), ("🥌", "컬링"), ("🎿", "스키"),
    ("🏂", "스노우보드"), ("🧗", "클라이밍"),
]


def sport_tiles():
    return '<div class="sports">' + "".join(
        f'<span style="animation-delay:{i*.016:.3f}s">{e}<br>{n}</span>'
        for i, (e, n) in enumerate(SPORTS)) + '</div>'


# ─────────────────────────────────────────────────────────────
CORE = [
    ("야구 전용", "투구 수 관리",
     "나이별 하루 상한과 필요한 휴식일을 자동으로 계산합니다. "
     "아이는 시합에서 빠질까 봐 아프다고 말하지 않습니다. "
     "그래서 <b>통증을 묻는 대신 공을 셉니다.</b>", pitch_gauge()),
    ("종단 기록", "성장·케어 타임라인",
     "키 성장 곡선 위에 통증일과 훈련량을 겹칩니다. 성장기에 무리했는지가 "
     "한 장에 보이고, <b>병원에 그대로 가져갈 수 있습니다.</b>", growth_timeline()),
    ("끊기지 않게", "회복일",
     "주 1회 쉬어도 연속 기록이 이어집니다. 기록 때문에 아파도 참고 훈련하는 "
     "일을 막으려고 넣은 장치입니다. <b>부상 중에는 제한이 풀립니다.</b>", week_strip()),
    ("객관화", "지도자 평가",
     "감독이 종목별 역량을 5점 척도로 남깁니다. 부모의 눈과 현장의 눈이 "
     "다를 때 기준이 됩니다. <b>실적표 반영은 본인 동의로만.</b>", radar_chart()),
]

MORE = [
    ("🎓", "진학 실적표 PDF", "대회 실적을 쌓아 A4 한 장으로. 학교에 그대로 냅니다."),
    ("🤖", "AI 코치", "종목·포지션·나이를 알고 답합니다. 통증엔 휴식을 먼저 권합니다."),
    ("👨‍👩‍👧", "학부모 연동", "6자리 코드 하나로. 오늘 훈련했는지, 어디가 아픈지."),
    ("📄", "주간 AI 리포트", "한 주를 스카우팅 리포트 형식으로 정리합니다."),
    ("📸", "자세 분석", "카메라로 폼을 보고 보완 루틴을 추천합니다. 영상은 저장 안 함."),
    ("💸", "훈련비 가계부", "레슨·대회·장비를 기록해 월·연 합계를 봅니다."),
    ("🔗", "실적표 공유 링크", "열어 봤는지 횟수만. 누가 열었는지는 기록하지 않습니다."),
    ("🗺️", "전국 랭킹", "시즌 점수로만. 서버에는 가린 이름(김**)만 남습니다."),
    ("🏆", "개인 최고 기록", "대회 결과를 읽어 자기 최고 기록을 스스로 갱신합니다."),
    ("🎮", "루틴 아케이드", "훈련으로 번 입장권으로만. 등급과는 무관합니다."),
    ("🎁", "후원 챌린지", "30일 완주하면 브랜드 상품. 결제·예치는 없습니다."),
    ("🎨", "테마 7종", "색만이 아니라 버튼과 카드 모양까지 바뀝니다."),
]

TICKER = [
    "훈련 부하 경고", "투구 수 상한", "성장 타임라인", "회복일", "지도자 평가",
    "진학 실적표 PDF", "AI 코치", "학부모 연동", "주간 리포트", "자세 분석",
    "훈련비 가계부", "공유 링크", "전국 랭킹", "개인 최고 기록", "루틴 알람",
    "후원 챌린지", "테마 7종", "38개 종목",
]


def ticker():
    one = "".join(f'<span class="chip"><i></i>{t}</span>' for t in TICKER)
    return f'<div class="marquee" aria-hidden="true"><div class="track">{one}{one}</div></div>'


def cards_more():
    return "".join(
        f'<div class="card spot reveal" style="animation-delay:{i*.035:.2f}s">'
        f'<div style="font-size:28px;line-height:1">{ico}</div>'
        f'<h3>{name}</h3><p>{desc}</p></div>'
        for i, (ico, name, desc) in enumerate(MORE))


def cards_core():
    out = []
    for kicker, title, body, viz in CORE:
        out.append(f'''
<article class="core-card spot reveal">
  <div class="top">
    <div class="kicker" style="font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--beam-2)">{kicker}</div>
    <h3 style="margin-top:8px">{title}</h3>
    <p style="margin-top:12px;font-size:16.5px;line-height:1.72;color:var(--ink-2)">{body}</p>
  </div>
  <div class="viz">{viz}</div>
</article>''')
    return "".join(out)


DOTS = [("hero", "처음"), ("film", "영상"), ("story", "만든 이유"),
        ("load", "훈련 부하"), ("core", "핵심 기능"), ("rhythm", "하루 3분"),
        ("economy", "재화 구조"), ("screens", "실제 화면"),
        ("more", "전체 기능"), ("trust", "정보 보호"), ("partners", "제휴")]


def dots_nav():
    return ('<nav class="dots" aria-label="구간 이동">' + "".join(
        f'<a href="#{i}" data-label="{lab}" aria-label="{lab}"></a>'
        for i, lab in DOTS) + '</nav>')


HTML = f"""<title>엘리트 루틴 케어</title>
<style>{CSS}</style>

<header class="topbar" id="topbar">
  <div class="row">
    <div class="brand">
      <svg viewBox="0 0 32 32" aria-hidden="true">
        <path d="M16.5 1.5c1.6 4.6.2 7-2.4 9.4-2.6 2.4-4.6 4.3-4.6 8.2 0 5 3.9 8.9 8.7 8.9s8.3-3.9 8.3-8.9c0-4.6-2.3-6.6-4.1-9.7-1.1 2.2-2.6 2.8-3.6 1.6-1.4-1.7-1.7-5.2-2.3-9.5z"
              fill="var(--beam-2)"/>
        <rect x="12" y="17" width="2.8" height="5" rx="1.2" fill="var(--ground)"/>
        <rect x="16" y="14" width="2.8" height="8" rx="1.2" fill="var(--ground)"/>
        <rect x="20" y="11" width="2.8" height="11" rx="1.2" fill="var(--ground)"/>
      </svg>
      엘리트 루틴 케어
    </div>
    <nav>
      <a href="#story">만든 이유</a>
      <a href="#load">훈련 부하</a>
      <a href="#core">핵심 기능</a>
      <a href="#more">전체 기능</a>
      <a href="#trust">정보 보호</a>
    </nav>
    <div class="progress" id="progress"></div>
  </div>
</header>

{dots_nav()}

<!-- ── 히어로 ────────────────────────────────────────── -->
<section class="hero" id="hero">
  <div class="mesh" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="grid-bg" aria-hidden="true"></div>
  <div class="wrap hero-grid">
    <div class="stack g24">
      <p class="eyebrow reveal">초 · 중 · 고 엘리트 선수 · 38개 종목</p>
      <h1>
        <span class="rise-line"><span style="animation-delay:.05s">다치지 않고,</span></span>
        <span class="rise-line"><span style="animation-delay:.16s">기록이 남고,</span></span>
        <span class="rise-line"><span style="animation-delay:.27s" class="hl">진학까지</span></span>
      </h1>
      <p class="lead reveal" style="animation-delay:.34s; max-width:52ch">
        아들이 대회에서 다쳐 깁스를 하던 날, 개발자인 아빠가 만들기 시작한
        앱입니다. 잔소리 대신 알림이, 걱정 대신 <b style="color:var(--ink)">숫자</b>가
        남게 하려고요.
      </p>
      <div class="badge-row reveal" style="animation-delay:.42s">
        <span class="badge">하루 3분</span>
        <span class="badge">기기 우선 저장</span>
        <span class="badge">게임으로 등급 안 오름</span>
        <span class="badge">월 9,900원</span>
      </div>
      <div class="cta-row reveal" style="animation-delay:.5s">
        <a class="btn btn-primary" href="#film">1분 영상 보기</a>
        <a class="btn btn-ghost" href="#story">만든 이유 읽기</a>
      </div>
    </div>
    <div class="reveal" style="animation-delay:.24s;position:relative">
      <div class="phone phone-float">
        <img src="{S('01_home_top')}" alt="앱 홈 화면 — 오늘의 루틴과 연속 달성 일수">
      </div>
      <div class="float-chip" style="left:-6%;top:16%;animation-delay:.4s">
        <span class="live"></span>
        <span><b>오늘 루틴 완료</b><span>불꽃 +12</span></span>
      </div>
      <div class="float-chip" style="right:-8%;bottom:14%;animation-delay:1.6s">
        <span><b style="color:var(--watch)">부하 1.62</b><span>이번 주 주의</span></span>
      </div>
    </div>
  </div>
</section>

<!-- ── 지표 ──────────────────────────────────────────── -->
<section class="metrics">
  <div class="wrap row">
    <div class="metric"><div class="n" data-count="38">0</div><div class="l">지원 종목</div></div>
    <div class="metric"><div class="n" data-count="3">0<small>분</small></div><div class="l">하루 사용 설계</div></div>
    <div class="metric"><div class="n" data-count="4">0<small>주</small></div><div class="l">부하 비교 기준</div></div>
    <div class="metric"><div class="n" data-count="0">0</div><div class="l">게임이 올리는 등급</div></div>
  </div>
</section>

<!-- ── 영상 — 가로 한 편만, 자동 재생 ─────────────────── -->
<section class="pad showreel" id="film">
  <div class="wrap stack g40">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">움직이는 화면으로</p>
      <h2 class="reveal">처음 켜서 리포트까지, 여덟 걸음</h2>
      <p class="lead reveal">
        나오는 화면은 전부 <b style="color:var(--on-deep)">실제 앱</b>입니다.
        이름·생년월일·학교는 예시 값으로 바꿔 두었습니다.
      </p>
    </div>
    <div class="reelframe reveal">
      <video autoplay muted loop playsinline controls preload="auto"
             aria-label="만화로 보는 사용법 — 종목 선택부터 종합 리포트까지 여덟 장면">
        <source src="{MANGA_WIDE}" type="video/mp4">
        영상을 재생할 수 없는 환경입니다.
      </video>
    </div>
    <div class="reel-meta reveal">
      <span>① 종목 선택</span><span>② 부상 예방</span><span>③ 루틴 습관화</span>
      <span>④ 훈련 기록</span><span>⑤ 분석 리포트</span><span>⑥ 성장 기록</span>
      <span>⑦ 학부모 화면</span><span>⑧ 종합 리포트</span>
    </div>
  </div>
</section>

{ticker()}

<!-- ── 스토리 ────────────────────────────────────────── -->
<section class="plaster pad" id="story">
  <div class="wrap story-grid">
    <div class="story-rail" aria-hidden="true"><div class="line"></div></div>
    <div>
      <p class="eyebrow">왜 만들었나</p>
      <h2 style="margin-top:10px;max-width:18ch">아이를 위한 앱이 아니라,<br>아이를 보는 부모의 앱</h2>

      <div style="margin-top:44px">
        <div class="story-beat reveal">
          <span class="dot"></span>
          <div class="when">Before</div>
          <p>알람이 울리면 알아서 튜빙을, 밴드를, 유연성 루틴을 하는 모습을
            보고 싶었습니다. 현실은 대충 하거나 빼먹는 날이 대부분이었고,
            주말엔 아예 안 했습니다. 그때마다 잔소리를 했고,
            <strong>잔소리를 한 날은 저도 아이도 기분이 나빴습니다.</strong></p>
        </div>

        <div class="story-beat reveal turn">
          <span class="dot"></span>
          <div class="when">그날</div>
          <p>대회를 뛰다 아이가 다쳤습니다. 깁스를 하고 돌아온 아이를 보면서,
            지난 몇 주 동안 훈련량이 어땠는지 <strong>제가 아무것도 모르고
            있었다</strong>는 걸 알았습니다. 수첩에도 기억에도 남은 게 없었습니다.</p>
        </div>

        <div class="story-beat reveal">
          <span class="dot"></span>
          <div class="when">After</div>
          <p>그래서 기록을 습관으로 만들고, 쉬는 것도 훈련으로 인정하고,
            무리한 주를 미리 짚어 주는 앱을 만들었습니다. 잔소리를 대신할
            알림, 걱정을 대신할 숫자를 남기려고요.</p>
        </div>
      </div>

      <blockquote class="pull">
        “다치고 나서 아는 것과, 다치기 전에 아는 것의 차이.<br>
        그 하나를 위해 만들었습니다.”
      </blockquote>
      <div class="sign">— 만든 사람, 엘리트 선수의 아빠</div>
    </div>
  </div>
</section>

<!-- ── 훈련 부하 — 스크롤에 물린 큰 차트 ──────────────── -->
<section class="pin" id="load" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="rail" id="loadrail">
    <div class="sticky wrap" id="loadsticky">
      <div class="stack g16">
        <p class="eyebrow">핵심 기능 ①</p>
        <h2 style="max-width:14ch">무너지기 전에<br>먼저 알려 드립니다</h2>
        <p class="lead" style="max-width:44ch">
          이번 주 훈련량을 지난 4주 평균과 견줍니다.
          얼마나 했나보다 <b style="color:var(--ink)">얼마나 갑자기 늘렸나</b>가
          부상을 부릅니다.
        </p>
        <div style="margin-top:8px">
          <div class="bigval"><span id="acwrnum">0.92</span><small id="acwrweek">1주차</small></div>
        </div>
        <div class="zone-legend">
          <div class="zone z1 on" data-zone="1"><span class="sw"></span>
            <span><b>0.8 – 1.3 · 안전</b><span>지금 페이스를 유지하세요</span></span></div>
          <div class="zone z2" data-zone="2"><span class="sw"></span>
            <span><b>1.3 – 1.5 · 주의</b><span>다음 주 증량은 멈추세요</span></span></div>
          <div class="zone z3" data-zone="3"><span class="sw"></span>
            <span><b>1.5 초과 · 위험</b><span>부상 확률이 뚜렷하게 올라갑니다</span></span></div>
        </div>
        <p class="fine" style="margin-top:14px">
          급성:만성 훈련 부하비(ACWR). 스포츠 의학에서 널리 쓰는 지표를
          아이의 종목·나이에 맞춰 계산합니다.
        </p>
      </div>
      <div>{acwr_big()}</div>
    </div>
  </div>
</section>

<!-- ── 핵심 기능 나머지 ──────────────────────────────── -->
<section class="pad" id="core">
  <div class="wrap stack g48">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">핵심 기능 ② – ⑤</p>
      <h2 class="reveal">나머지 넷도 같은 이유로 있습니다</h2>
      <p class="lead reveal">전부 “다치기 전에 알기”와 “남은 기록으로 증명하기”를 돕습니다.</p>
    </div>
    <div class="core">{cards_core()}</div>
  </div>
</section>

<!-- ── 하루 흐름 ─────────────────────────────────────── -->
<section class="pad" id="rhythm" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g48">
    <div class="side-360">
      <div class="stack g16">
        <p class="eyebrow reveal">하루 사용</p>
        <h2 class="reveal">오래 붙잡아 두지 않습니다</h2>
        <p class="lead reveal">
          아이가 앱을 오래 쓰게 만드는 것이 목적이 아닙니다. 하루 3분이면 끝나고,
          <b style="color:var(--ink)">저녁에 미션을 이미 다 끝냈으면 알림도 보내지 않습니다.</b>
          할 일을 다 한 아이에게 잔소리하는 알림은 곧 꺼지니까요.
        </p>
        <div class="badge-row reveal" style="margin-top:6px">
          <span class="badge">무한 스크롤 없음</span>
          <span class="badge">연속 보상 루프 없음</span>
          <span class="badge">푸시 하루 1회</span>
        </div>
      </div>
      <div class="reveal">{loop_diagram()}</div>
    </div>

    <div class="two-up">
      <div class="reveal">{heatmap()}</div>
      <div class="stack g16">
        <p class="eyebrow reveal">쌓이는 방식</p>
        <h2 class="reveal" style="font-size:clamp(28px,3.6vw,44px)">3분이 6주가 되면<br>이런 모양이 됩니다</h2>
        <p class="lead reveal" style="font-size:18px">
          진한 칸은 루틴·일지·측정을 모두 마친 날입니다. 빈칸이 이어지면
          앱이 먼저 묻습니다 — <b style="color:var(--ink)">혼내는 대신, 어디가 불편한지를요.</b>
        </p>
      </div>
    </div>
  </div>
</section>

<!-- ── 재화 구조 ─────────────────────────────────────── -->
<section class="pad" id="economy">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">부모님이 가장 걱정하는 것</p>
      <h2 class="reveal">게임은 훈련과 경쟁하지 않습니다</h2>
      <p class="lead reveal">
        앱 안에 미니게임이 있습니다. 구조를 그대로 공개합니다 —
        입장권은 <b style="color:var(--ink)">훈련으로만</b> 생기고, 게임을 아무리
        잘해도 등급은 오르지 않으며, 코인으로는 <b style="color:var(--ink)">겉모습만</b> 삽니다.
      </p>
    </div>
    <div class="reveal">{economy_diagram()}</div>
  </div>
</section>

<!-- ── 화면 ──────────────────────────────────────────── -->
<section class="pad" id="screens" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">실제 화면</p>
      <h2 class="reveal">보이는 그대로입니다</h2>
      <p class="lead reveal">아래는 합성이 아니라 실제 기기에서 찍은 화면입니다.</p>
    </div>
    <div class="cards c4">
      <div class="reveal"><div class="phone" data-par="0.03" style="width:100%"><img src="{S('05_home_bottom')}" alt="훈련 부하와 개인 최고 기록 카드"></div></div>
      <div class="reveal" style="animation-delay:.06s"><div class="phone" data-par="0.06" style="width:100%"><img src="{S('13_ranking')}" alt="학부모 화면의 자녀 상태 보고"></div></div>
      <div class="reveal" style="animation-delay:.12s"><div class="phone" data-par="0.03" style="width:100%"><img src="{S('09_arcade')}" alt="진학 실적표 미리보기"></div></div>
      <div class="reveal" style="animation-delay:.18s"><div class="phone" data-par="0.06" style="width:100%"><img src="{S('10_more_sheet')}" alt="AI 코치 대화 화면"></div></div>
    </div>
  </div>
</section>

<!-- ── 종목 ──────────────────────────────────────────── -->
<section class="pad" id="sports">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">지원 종목</p>
      <h2 class="reveal">38개 종목이 서로 다른 앱을 씁니다</h2>
      <p class="lead reveal">
        종목을 고르면 <b style="color:var(--ink)">주요 기록 항목, 포지션, 통증 부위,
        진학 경로</b>가 통째로 바뀝니다. 수영에 투구 수가 뜨지 않고,
        야구에 50m 자유형이 뜨지 않습니다.
      </p>
    </div>
    <div class="reveal">{sport_tiles()}</div>
  </div>
</section>

<!-- ── 전체 기능 ─────────────────────────────────────── -->
<section class="pad" id="more" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">전체 기능</p>
      <h2 class="reveal">그 밖에 들어 있는 것들</h2>
    </div>
    <div class="cards c3">{cards_more()}</div>
  </div>
</section>

<!-- ── 정보 보호 ─────────────────────────────────────── -->
<section class="pad" id="trust">
  <div class="wrap stack g40">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">정보 보호</p>
      <h2 class="reveal">무엇이 누구에게 보이는지 적어 둡니다</h2>
      <p class="lead reveal">
        선수 대부분이 미성년자입니다. 기록은 <b style="color:var(--ink)">기기에 먼저</b>
        저장되고, 서버로 올리는 것도 보호자가 보는 것도 아이가 켜야 열립니다.
      </p>
    </div>
    <div class="reveal">{flow_diagram()}</div>
    <div class="tablewrap reveal">
      <table>
        <thead><tr><th>항목</th><th>보호자에게</th><th>감독·코치에게</th></tr></thead>
        <tbody>
          <tr><td>오늘 훈련했는지</td><td class="yes">보임</td><td class="yes">보임</td></tr>
          <tr><td>연속 달성 일수</td><td class="yes">보임</td><td class="yes">보임</td></tr>
          <tr><td>키·몸무게·기록</td><td class="yes">보임</td><td class="no">안 보임</td></tr>
          <tr><td>아픈 부위</td><td class="partial">아이가 보낼 때만</td><td class="partial">‘있다/없다’만</td></tr>
          <tr><td>훈련 일지 내용</td><td class="no">안 보임</td><td class="no">안 보임</td></tr>
          <tr><td>AI 코치 대화</td><td class="no">안 보임</td><td class="no">안 보임</td></tr>
          <tr><td>지도자 평가의 실적표 반영</td><td class="partial">본인·보호자가 켜야</td><td class="no">켤 수 없음</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- ── 제휴 ──────────────────────────────────────────── -->
<section class="pad" id="partners" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">제휴</p>
      <h2 class="reveal">의료 자문을 붙이는 중입니다</h2>
      <p class="lead reveal">
        부상 판정 기준은 공개된 스포츠 의학 자료(MLB Pitch Smart, 급성:만성
        훈련 부하비, 질병관리청 성장도표)를 근거로 만들었습니다. 여기에 현장
        의료진의 검토를 더하려고 협의하고 있습니다.
      </p>
    </div>
    <div class="partners">
      <div class="partner reveal">
        <span class="status">● 협의 중</span>
        <h3 style="margin-top:16px">프로 구단 팀 닥터</h3>
        <p style="margin-top:8px;font-size:16px;color:var(--ink-2)">
          투구 수 상한과 복귀 판단 기준을 현장 기준과 맞추기 위한 자문.
        </p>
        <div class="slot">계약 후 로고·검토 의견 게재</div>
      </div>
      <div class="partner reveal" style="animation-delay:.08s">
        <span class="status">● 협의 중</span>
        <h3 style="margin-top:16px">정형외과 의료진</h3>
        <p style="margin-top:8px;font-size:16px;color:var(--ink-2)">
          성장기 부상 관리와 재활 복귀 프로토콜 검토.
        </p>
        <div class="slot">계약 후 로고·검토 의견 게재</div>
      </div>
    </div>
    <p class="fine reveal" style="max-width:70ch">
      아직 체결된 제휴가 없어 위 자리는 비워 두었습니다. 실제 자문이 시작되면
      기관명과 검토 의견을 이 자리에 그대로 싣습니다. 없는 추천을 지어내지
      않는 것이 이 앱을 만든 이유와 같은 원칙입니다.
    </p>
  </div>
</section>

<!-- ── 마무리 ────────────────────────────────────────── -->
<section class="pad finale" style="text-align:center">
  <div class="wrap stack g32" style="align-items:center">
    <p class="bigquote reveal" style="max-width:20ch">오늘의 루틴이<br>3년 뒤의 기록이 됩니다</p>
    <p class="lead reveal" style="max-width:52ch">
      월 9,900원. 선수 한 명을 관리하고, 보호자 연결은 추가 비용 없이 됩니다.
    </p>
    <div class="cta-row reveal" style="justify-content:center">
      <a class="btn btn-primary" href="https://eliteroutine.github.io/beginner_guide.html">초보자 설명서 보기</a>
      <a class="btn btn-ghost" href="https://eliteroutine.github.io/parent_guide.html">학부모 안내서 보기</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap row">
    <div class="stack g8" style="min-width:230px">
      <div class="brand" style="font-size:15px">엘리트 루틴 케어</div>
      <p class="fine">초·중·고 엘리트 선수의<br>훈련 루틴과 성장 기록</p>
    </div>
    <div class="stack g8">
      <a href="https://eliteroutine.github.io/beginner_guide.html">초보자 설명서</a>
      <a href="https://eliteroutine.github.io/parent_guide.html">학부모 안내서</a>
    </div>
    <div class="stack g8">
      <a href="https://eliteroutine.github.io/privacy_policy.html">개인정보 처리방침</a>
      <a href="https://eliteroutine.github.io/legal_review.html">법률 검토 메모</a>
    </div>
    <p class="fine" style="max-width:44ch">
      화면 사진은 실제 앱을 찍은 것입니다. 부상 판정은 참고 자료이며
      의학적 진단이 아닙니다. 통증이 있으면 병원 진료를 받으세요.
    </p>
  </div>
</footer>

<script>
(function () {{
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── 스크롤 등장 — 한 번만 켠다. 다시 사라졌다 나타나면 산만하다.
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (!e.isIntersecting) return;
      e.target.classList.add('in-view');
      io.unobserve(e.target);
    }});
  }}, {{ rootMargin: '0px 0px -12% 0px', threshold: 0.1 }});

  document.querySelectorAll('.reveal, .core-card, .chart').forEach(function (el) {{
    if (reduce) {{ el.classList.add('in-view'); return; }}
    io.observe(el);
  }});

  // ── 숫자 세기
  document.querySelectorAll('[data-count]').forEach(function (el) {{
    var target = parseInt(el.dataset.count, 10);
    var small = el.querySelector('small');
    var suffix = small ? small.outerHTML : '';
    if (reduce || target === 0) {{ el.innerHTML = target + suffix; return; }}
    var seen = new IntersectionObserver(function (es) {{
      if (!es[0].isIntersecting) return;
      seen.disconnect();
      var t0 = performance.now(), dur = 1000;
      (function step(now) {{
        var p = Math.min(1, (now - t0) / dur);
        el.innerHTML = Math.round(target * (1 - Math.pow(1 - p, 3))) + suffix;
        if (p < 1) requestAnimationFrame(step);
      }})(t0);
    }}, {{ threshold: 0.6 }});
    seen.observe(el);
  }});

  // ── 카드 위 커서 불빛
  document.querySelectorAll('.spot').forEach(function (el) {{
    el.addEventListener('pointermove', function (e) {{
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }});
  }});

  // ── 훈련 부하 차트 — 스크롤이 선을 그린다
  //
  // 파이썬이 넘겨준 값과 x 좌표를 그대로 쓴다. 선 위 좌표는 SVG 가
  // 계산해 주므로(getPointAtLength) 여기서 다시 구하지 않는다.
  var rail = document.getElementById('loadrail');
  var stick = document.getElementById('loadsticky');
  var svg = document.getElementById('acwrsvg');
  var line = document.getElementById('acwrline');
  var dot = document.getElementById('acwrdot');
  var guide = document.getElementById('acwrguide');
  var num = document.getElementById('acwrnum');
  var wk = document.getElementById('acwrweek');
  var zones = [].slice.call(document.querySelectorAll('.zone'));
  var vals = svg.dataset.vals.split(',').map(Number);
  var LEN = line.getTotalLength();
  line.style.strokeDasharray = LEN;

  function paintLoad(p) {{
    line.style.strokeDashoffset = LEN * (1 - p);
    var pt = line.getPointAtLength(LEN * p);
    dot.setAttribute('cx', pt.x);
    dot.setAttribute('cy', pt.y);
    guide.setAttribute('x1', pt.x);
    guide.setAttribute('x2', pt.x);
    guide.setAttribute('opacity', p > 0.02 ? 0.5 : 0);

    var f = p * (vals.length - 1);
    var i = Math.min(vals.length - 2, Math.floor(f));
    var v = vals[i] + (vals[i + 1] - vals[i]) * (f - i);
    num.textContent = v.toFixed(2);
    wk.textContent = (Math.round(f) + 1) + '주차';

    var live = v > 1.5 ? 3 : (v > 1.3 ? 2 : 1);
    var color = live === 3 ? 'var(--risk)' : (live === 2 ? 'var(--watch)' : 'var(--safe)');
    dot.setAttribute('fill', color);
    num.style.color = color;
    zones.forEach(function (z) {{
      z.classList.toggle('on', Number(z.dataset.zone) === live);
    }});
  }}

  var loose = matchMedia('(max-width: 980px)');
  function loadScroll() {{
    if (reduce || loose.matches) {{ paintLoad(1); return; }}
    var travel = rail.offsetHeight - stick.offsetHeight;
    if (travel <= 0) {{ paintLoad(1); return; }}
    var p = (-rail.getBoundingClientRect().top + 92) / travel;
    paintLoad(Math.max(0, Math.min(1, p)));
  }}

  // ── 오른쪽 구간 표시
  var dots = [].slice.call(document.querySelectorAll('.dots a'));
  var marks = dots.map(function (a) {{
    return document.getElementById(a.getAttribute('href').slice(1));
  }});

  // ── 시차 이동 — 폰이 스크롤보다 조금 늦게 따라온다
  var pars = [].slice.call(document.querySelectorAll('[data-par]'));

  var bar = document.getElementById('topbar');
  var prog = document.getElementById('progress');
  var queued = false;

  function frame() {{
    queued = false;
    var y = scrollY;
    bar.classList.toggle('solid', y > 12);
    var max = document.documentElement.scrollHeight - innerHeight;
    prog.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';

    loadScroll();

    var cur = 0;
    marks.forEach(function (m, i) {{
      if (m && m.getBoundingClientRect().top <= innerHeight * 0.42) cur = i;
    }});
    dots.forEach(function (a, i) {{ a.classList.toggle('on', i === cur); }});

    if (!reduce) {{
      var mid = innerHeight / 2;
      pars.forEach(function (el) {{
        var r = el.getBoundingClientRect();
        var off = (r.top + r.height / 2 - mid) * parseFloat(el.dataset.par);
        el.style.transform = 'translate3d(0,' + (-off).toFixed(1) + 'px,0)';
      }});
    }}
  }}
  function onScroll() {{
    if (queued) return;
    queued = true;
    requestAnimationFrame(frame);
  }}
  addEventListener('scroll', onScroll, {{ passive: true }});
  addEventListener('resize', onScroll);
  frame();
}})();
</script>
"""

out = os.path.join(ROOT, "index.html")
io.open(out, "w", encoding="utf-8", newline="\n").write(HTML)
print("wrote", out, os.path.getsize(out) // 1024, "KB")
