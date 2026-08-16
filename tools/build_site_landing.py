# -*- coding: utf-8 -*-
"""엘리트 루틴 케어 소개 사이트를 만든다.

앱 화면은 실제 기기에서 찍은 것을 base64 로 박아 넣는다. 외부 요청이
막혀 있어(CSP) 링크로는 못 부른다.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_head import CSS  # noqa: E402

CSS += """
/* ── 영상 ────────────────────────────────────────────── */
.filmwrap { display:grid; grid-template-columns: minmax(0,340px) minmax(0,1fr);
  gap: clamp(28px,5vw,64px); align-items:center; }
@media (max-width:820px){ .filmwrap{ grid-template-columns:1fr; } }
.film { position:relative; border-radius:30px; padding:10px;
  background: linear-gradient(160deg,#26313F,#0E1520);
  box-shadow: 0 40px 90px -30px #000, 0 0 0 1px var(--rule-2) inset; }
.film video { display:block; width:100%; border-radius:22px; background:#000; }
.film-cta { display:flex; gap:10px; flex-wrap:wrap; margin-top:16px; }
"""

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SP = HERE
# 영상은 파일로 둔다. base64 로 박으면 첫 화면이 8MB 를 넘게 받는다.
VIDEO = "intro.mp4"
MANGA = "manga.mp4"
MANGA_WIDE = "manga_wide.mp4"
IDX = json.load(io.open(os.path.join(SP, "shots_web", "index.json"),
                        encoding="utf-8"))


def S(key):
    return IDX.get(key, "")


# ─────────────────────────────────────────────────────────────
# 차트 — 값은 앱이 실제로 쓰는 규칙 그대로다
# ─────────────────────────────────────────────────────────────

def acwr_chart():
    """훈련 부하(이번 주 ÷ 지난 4주 평균)."""
    # 주차별 값. 마지막 두 주가 위험 구간으로 넘어간다.
    vals = [0.92, 1.05, 0.98, 1.18, 1.34, 1.62, 1.71]
    w, h = 560, 240
    pad_l, pad_r, pad_t, pad_b = 34, 14, 16, 28
    x0, x1 = pad_l, w - pad_r
    y0, y1 = pad_t, h - pad_b

    def X(i):
        return x0 + (x1 - x0) * i / (len(vals) - 1)

    def Y(v):
        lo, hi = 0.6, 1.9
        return y1 - (y1 - y0) * (v - lo) / (hi - lo)

    band = (f'<rect x="{x0}" y="{Y(1.3):.1f}" width="{x1-x0}" '
            f'height="{Y(0.8)-Y(1.3):.1f}" fill="var(--safe)" opacity=".10"/>'
            f'<rect x="{x0}" y="{Y(1.5):.1f}" width="{x1-x0}" '
            f'height="{Y(1.3)-Y(1.5):.1f}" fill="var(--watch)" opacity=".12"/>'
            f'<rect x="{x0}" y="{y0}" width="{x1-x0}" '
            f'height="{Y(1.5)-y0:.1f}" fill="var(--risk)" opacity=".13"/>')

    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    dots = "".join(
        f'<circle class="pop" style="animation-delay:{.9+i*.07:.2f}s" '
        f'cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{5 if v>1.5 else 3.5}" '
        f'fill="{"var(--risk)" if v > 1.5 else ("var(--watch)" if v > 1.3 else "var(--safe)")}"/>'
        for i, v in enumerate(vals))

    labels = "".join(
        f'<text class="tick" x="{X(i):.1f}" y="{h-9}" text-anchor="middle">{i+1}주</text>'
        for i in range(len(vals)))

    yticks = "".join(
        f'<text class="tick" x="{x0-8}" y="{Y(v)+3.5:.1f}" text-anchor="end">{v}</text>'
        f'<line class="gridline" x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}"/>'
        for v in (0.8, 1.3, 1.5))

    return f'''
<svg class="chart" viewBox="0 0 {w} {h}" role="img"
     aria-label="훈련 부하가 7주에 걸쳐 0.92에서 1.71로 올라 위험 구간에 들어간 그래프">
  {band}{yticks}
  <polyline class="draw" style="--len:900" points="{pts}" fill="none"
            stroke="var(--beam-2)" stroke-width="2.6"
            stroke-linecap="round" stroke-linejoin="round"/>
  {dots}{labels}
  <text class="tick" x="{x1}" y="{Y(1.71)-14:.1f}" text-anchor="end"
        fill="var(--risk)" style="font-weight:700">위험</text>
</svg>'''


def pitch_gauge():
    """투구 수 — 나이별 하루 상한 대비."""
    cur, cap = 68, 85
    r, cx, cy = 78, 110, 108
    import math
    span = math.pi * 1.45
    start = math.pi * 0.775

    def pt(frac):
        a = start + span * frac
        return cx + r * math.cos(a), cy + r * math.sin(a)

    def arc(f0, f1, color, width, cls="", delay=0):
        x0, y0 = pt(f0)
        x1, y1 = pt(f1)
        large = 1 if (f1 - f0) * span > math.pi else 0
        length = span * r * (f1 - f0)
        style = f'--len:{length:.0f};animation-delay:{delay}s' if cls else ''
        return (f'<path class="{cls}" style="{style}" d="M{x0:.1f},{y0:.1f} '
                f'A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f}" fill="none" '
                f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')

    frac = cur / cap
    return f'''
<svg class="chart" viewBox="0 0 220 190" role="img"
     aria-label="오늘 투구 수 68개, 나이별 상한 85개 게이지">
  {arc(0, 1, "var(--rule-2)", 13)}
  {arc(0, frac, "var(--watch)", 13, "draw", .25)}
  <text x="110" y="104" text-anchor="middle" fill="var(--ink)"
        style="font-size:44px;font-weight:900;letter-spacing:-.04em">{cur}</text>
  <text x="110" y="128" text-anchor="middle" class="tick">／ {cap}구 · 만 12세</text>
  <text x="110" y="168" text-anchor="middle" fill="var(--watch)"
        style="font-size:13px;font-weight:800">다음 등판까지 2일 휴식</text>
</svg>'''


def week_strip():
    """주간 목표 5일 — 회복일도 채운 날로 센다."""
    days = [("월", "done"), ("화", "done"), ("수", "rest"), ("목", "done"),
            ("금", "done"), ("토", "done"), ("일", "todo")]
    cells = []
    for i, (d, st) in enumerate(days):
        fill = {"done": "var(--beam)", "rest": "var(--watch)",
                "todo": "var(--panel-2)"}[st]
        mark = {"done": "✓", "rest": "🌙", "todo": ""}[st]
        cells.append(
            f'<g class="pop" style="animation-delay:{i*.08:.2f}s">'
            f'<rect x="{i*58}" y="0" width="46" height="46" rx="13" fill="{fill}"'
            f' opacity="{1 if st != "todo" else .9}"/>'
            f'<text x="{i*58+23}" y="30" text-anchor="middle" '
            f'style="font-size:18px" fill="#fff">{mark}</text>'
            f'<text x="{i*58+23}" y="66" text-anchor="middle" class="tick">{d}</text>'
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
            stroke="var(--safe)" stroke-width="2.6" stroke-linecap="round"/>
  {marks}{months}
  <text class="tick" x="{x0}" y="{y0-4}" fill="var(--safe)">키</text>
  <text class="tick" x="{x0+34}" y="{y0-4}" fill="var(--beam-2)">주간 투구량</text>
</svg>'''


def economy_diagram():
    """훈련 재화와 게임 재화의 한 방향 문."""
    return '''
<svg class="chart" viewBox="0 0 620 220" role="img"
     aria-label="훈련으로 얻은 포인트만 등급에 반영되고, 게임 코인은 꾸미기에만 쓰이는 구조도">
  <g class="reveal in-view">
    <rect x="4" y="26" width="240" height="168" rx="18" fill="var(--panel)"
          stroke="var(--beam)" stroke-width="1.5"/>
    <text x="24" y="58" fill="var(--beam-2)" style="font-size:11px;font-weight:800;letter-spacing:.12em">훈련으로만</text>
    <text x="24" y="88" fill="var(--ink)" style="font-size:19px;font-weight:900">🔥 불꽃 포인트</text>
    <text x="24" y="116" fill="var(--ink-2)" style="font-size:13px">루틴 · 일지 · 측정 · 회복일</text>
    <rect x="24" y="132" width="200" height="42" rx="10" fill="rgba(46,212,122,.12)"/>
    <text x="38" y="158" fill="var(--safe)" style="font-size:13px;font-weight:800">등급과 순위에 반영</text>
  </g>
  <g class="pop" style="animation-delay:.5s">
    <path d="M254,110 L358,110" stroke="var(--watch)" stroke-width="2.5"
          marker-end="url(#ah)" fill="none"/>
    <text x="306" y="94" text-anchor="middle" fill="var(--watch)"
          style="font-size:12px;font-weight:800">입장권</text>
    <text x="306" y="134" text-anchor="middle" class="tick">한 방향</text>
  </g>
  <g class="reveal in-view" style="animation-delay:.35s">
    <rect x="376" y="26" width="240" height="168" rx="18" fill="var(--panel)"
          stroke="var(--watch)" stroke-width="1.5"/>
    <text x="396" y="58" fill="var(--watch)" style="font-size:11px;font-weight:800;letter-spacing:.12em">게임으로만</text>
    <text x="396" y="88" fill="var(--ink)" style="font-size:19px;font-weight:900">🪙 게임 코인</text>
    <text x="396" y="116" fill="var(--ink-2)" style="font-size:13px">아케이드 6종</text>
    <rect x="396" y="132" width="200" height="42" rx="10" fill="rgba(255,90,82,.12)"/>
    <text x="410" y="158" fill="var(--risk)" style="font-size:13px;font-weight:800">등급에 1점도 반영 안 됨</text>
  </g>
  <defs>
    <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7"
            markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--watch)"/>
    </marker>
  </defs>
</svg>'''


def loop_diagram():
    """하루 3분 루프."""
    import math
    steps = [("아침", "오늘의 미션 확인"), ("훈련 후", "루틴 완료 · 불꽃"),
             ("저녁", "일지 · 컨디션"), ("보상", "아케이드 입장권")]
    cx, cy, r = 150, 150, 104
    out = []
    for i, (when, what) in enumerate(steps):
        a = -math.pi / 2 + i * math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(
            f'<g class="pop" style="animation-delay:{.2+i*.14:.2f}s">'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="30" fill="var(--panel)" '
            f'stroke="var(--beam)" stroke-width="1.5"/>'
            f'<text x="{x:.0f}" y="{y+4:.0f}" text-anchor="middle" '
            f'fill="var(--beam-2)" style="font-size:12px;font-weight:800">{when}</text>'
            f'<text x="{x:.0f}" y="{y+52 if i != 2 else y+52:.0f}" text-anchor="middle" '
            f'class="tick">{what}</text></g>')
    return f'''
<svg class="chart" viewBox="0 0 300 300" style="max-width:300px;margin-inline:auto"
     role="img" aria-label="아침 미션 확인, 훈련 후 루틴 완료, 저녁 일지, 보상 아케이드로 도는 하루 흐름도">
  <circle class="draw" style="--len:660" cx="{cx}" cy="{cy}" r="{r}" fill="none"
          stroke="var(--rule-2)" stroke-width="1.5" stroke-dasharray="660"/>
  {"".join(out)}
  <text x="150" y="144" text-anchor="middle" fill="var(--ink)"
        style="font-size:30px;font-weight:900;letter-spacing:-.04em">3분</text>
  <text x="150" y="166" text-anchor="middle" class="tick">하루에</text>
</svg>'''


# ─────────────────────────────────────────────────────────────
CORE = [
    ("부상 예방", "훈련 부하",
     "이번 주 훈련량을 지난 4주 평균과 견줍니다. 얼마나 했나보다 "
     "<b>얼마나 갑자기 늘렸나</b>가 부상을 부릅니다. 위험 구간에 들어가면 "
     "그 주에 알려 드립니다.", acwr_chart()),
    ("야구 전용", "투구 수 관리",
     "나이별 하루 상한과 필요한 휴식일을 자동으로 계산합니다. "
     "아이는 시합에서 빠질까 봐 아프다고 말하지 않습니다. "
     "그래서 <b>통증을 묻는 대신 공을 셉니다.</b>", pitch_gauge()),
    ("종단 기록", "성장·케어 타임라인",
     "키 성장 곡선 위에 통증일과 훈련량을 겹칩니다. 성장기에 무리했는지가 "
     "한 장에 보이고, <b>병원에 그대로 가져갈 수 있습니다.</b>", growth_timeline()),
    ("끊기지 않게", "회복일",
     "주 1회 쉬어도 연속 기록이 이어집니다. 기록 때문에 아파도 참고 훈련하는 "
     "일을 막으려고 넣은 장치입니다. 부상 중에는 제한이 풀립니다.", week_strip()),
]

MORE = [
    ("🎓", "진학 실적표 PDF", "대회 실적을 쌓아 A4 한 장으로. 학교에 그대로 냅니다."),
    ("🤖", "AI 코치", "종목·포지션·나이를 알고 답합니다. 통증엔 휴식을 먼저 권합니다."),
    ("👨‍👩‍👧", "학부모 연동", "6자리 코드 하나로. 오늘 훈련했는지, 어디가 아픈지."),
    ("📋", "지도자 평가", "감독이 종목별 역량을 점수로. 실적표 반영은 본인 동의로만."),
    ("📄", "주간 AI 리포트", "한 주를 스카우팅 리포트 형식으로 정리합니다."),
    ("📸", "자세 분석", "카메라로 폼을 보고 보완 루틴을 추천합니다. 영상은 저장 안 함."),
    ("💸", "훈련비 가계부", "레슨·대회·장비를 기록해 월·연 합계를 봅니다."),
    ("🔗", "실적표 공유 링크", "열어 봤는지 횟수만. 누가 열었는지는 기록하지 않습니다."),
    ("🗺️", "전국 랭킹", "시즌 점수로만. 서버에는 가린 이름(김**)만 남습니다."),
    ("🎮", "루틴 아케이드", "훈련으로 번 입장권으로만. 등급과는 무관합니다."),
    ("🎁", "후원 챌린지", "30일 완주하면 브랜드 상품. 결제·예치는 없습니다."),
    ("🎨", "테마 7종", "색만이 아니라 버튼과 카드 모양까지 바뀝니다."),
]


def cards_more():
    return "".join(
        f'<div class="card reveal" style="animation-delay:{i*.04:.2f}s">'
        f'<div style="font-size:26px;line-height:1">{ico}</div>'
        f'<h3>{name}</h3><p>{desc}</p></div>'
        for i, (ico, name, desc) in enumerate(MORE))


def cards_core():
    out = []
    for kicker, title, body, viz in CORE:
        out.append(f'''
<article class="core-card reveal">
  <div class="top">
    <div class="kicker" style="font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--beam-2)">{kicker}</div>
    <h3 style="margin-top:8px">{title}</h3>
    <p style="margin-top:10px;font-size:15.5px;line-height:1.7;color:var(--ink-2)">{body}</p>
  </div>
  <div class="viz">{viz}</div>
</article>''')
    return "".join(out)


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
      <a href="#core">핵심 기능</a>
      <a href="#more">전체 기능</a>
      <a href="#trust">정보 보호</a>
      <a href="#partners">제휴</a>
    </nav>
    <div class="progress" id="progress"></div>
  </div>
</header>

<!-- ── 히어로 ────────────────────────────────────────── -->
<section class="hero">
  <div class="beam"></div>
  <div class="wrap hero-grid">
    <div class="stack g24">
      <p class="eyebrow reveal">초 · 중 · 고 엘리트 선수 · 38개 종목</p>
      <h1 class="reveal" style="animation-delay:.08s">
        다치지 않고,<br>기록이 남고,<br><span class="hl">진학까지</span>
      </h1>
      <p class="lead reveal" style="animation-delay:.16s; max-width:52ch">
        아들이 대회에서 다쳐 깁스를 하던 날, 개발자인 아빠가 만들기 시작한
        앱입니다. 잔소리 대신 알림이, 걱정 대신 <b style="color:var(--ink)">숫자</b>가
        남게 하려고요.
      </p>
      <div class="badge-row reveal" style="animation-delay:.24s">
        <span class="badge">하루 3분</span>
        <span class="badge">기기 우선 저장</span>
        <span class="badge">게임으로 등급 안 오름</span>
        <span class="badge">월 9,900원</span>
      </div>
      <div class="cta-row reveal" style="animation-delay:.32s">
        <a class="btn btn-primary" href="#core">핵심 기능 보기</a>
        <a class="btn btn-ghost" href="#story">만든 이유 읽기</a>
      </div>
    </div>
    <div class="reveal" style="animation-delay:.2s">
      <div class="phone phone-float">
        <img src="{S('01_home_top')}" alt="앱 홈 화면 — 오늘의 루틴과 연속 달성 일수">
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

<!-- ── 영상 ──────────────────────────────────────────── -->
<section class="pad" id="film" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g48">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">영상으로 보기</p>
      <h2 class="reveal">두 편으로 정리했습니다</h2>
      <p class="lead reveal">
        나오는 화면은 전부 <b style="color:var(--ink)">실제 앱</b>입니다.
        이름·생년월일·학교는 예시 값으로 바꿔 두었습니다.
      </p>
    </div>

    <div class="cards c2">
      <div class="stack g16 reveal">
        <div class="film">
          <video controls playsinline preload="metadata"
                 aria-label="만화로 보는 사용법 56초">
            <source src="{MANGA_WIDE}" type="video/mp4">
            영상을 재생할 수 없는 환경입니다.
          </video>
        </div>
        <div>
          <h3>이렇게 사용하세요 · 56초</h3>
          <p style="margin-top:8px;font-size:15px;color:var(--ink-2)">
            처음 켜서 종합 리포트까지, 여덟 걸음을 만화로.
            <a href="{MANGA}" download>세로 버전</a>도 있습니다.
          </p>
        </div>
      </div>

      <div class="stack g16 reveal" style="animation-delay:.08s">
        <div class="film">
          <video controls playsinline preload="metadata"
                 aria-label="기능 소개 78초">
            <source src="{VIDEO}" type="video/mp4">
            영상을 재생할 수 없는 환경입니다.
          </video>
        </div>
        <div>
          <h3>기능 소개 · 78초</h3>
          <p style="margin-top:8px;font-size:15px;color:var(--ink-2)">
            훈련 부하부터 정보 공개 범위까지 17개 장면.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

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

<!-- ── 핵심 기능 ─────────────────────────────────────── -->
<section class="pad" id="core">
  <div class="wrap stack g48">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">핵심 기능</p>
      <h2 class="reveal">이 네 가지를 위해 만들었습니다</h2>
      <p class="lead reveal">나머지 기능은 전부 이 넷을 돕는 것들입니다.</p>
    </div>
    <div class="core">{cards_core()}</div>
  </div>
</section>

<!-- ── 하루 흐름 ─────────────────────────────────────── -->
<section class="pad" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap" style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,340px);gap:clamp(28px,5vw,64px);align-items:center">
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
</section>

<!-- ── 재화 구조 ─────────────────────────────────────── -->
<section class="pad">
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
<section class="pad" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">실제 화면</p>
      <h2 class="reveal">보이는 그대로입니다</h2>
      <p class="lead reveal">아래는 합성이 아니라 실제 기기에서 찍은 화면입니다.</p>
    </div>
    <div class="cards c4">
      <div class="reveal"><div class="phone" style="width:100%"><img src="{S('05_home_bottom')}" alt="훈련 부하와 개인 최고 기록 카드"></div></div>
      <div class="reveal" style="animation-delay:.06s"><div class="phone" style="width:100%"><img src="{S('13_ranking')}" alt="학부모 화면의 자녀 상태 보고"></div></div>
      <div class="reveal" style="animation-delay:.12s"><div class="phone" style="width:100%"><img src="{S('09_arcade')}" alt="진학 실적표 미리보기"></div></div>
      <div class="reveal" style="animation-delay:.18s"><div class="phone" style="width:100%"><img src="{S('10_more_sheet')}" alt="AI 코치 대화 화면"></div></div>
    </div>
  </div>
</section>

<!-- ── 전체 기능 ─────────────────────────────────────── -->
<section class="pad" id="more">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">전체 기능</p>
      <h2 class="reveal">그 밖에 들어 있는 것들</h2>
    </div>
    <div class="cards c3">{cards_more()}</div>
  </div>
</section>

<!-- ── 정보 보호 ─────────────────────────────────────── -->
<section class="pad" id="trust" style="background:var(--ground-2);border-block:1px solid var(--rule)">
  <div class="wrap stack g32">
    <div class="stack g16 narrow">
      <p class="eyebrow reveal">정보 보호</p>
      <h2 class="reveal">무엇이 누구에게 보이는지 적어 둡니다</h2>
      <p class="lead reveal">
        선수 대부분이 미성년자입니다. 기록은 <b style="color:var(--ink)">기기에 먼저</b>
        저장되고, 서버로 올리는 것도 보호자가 보는 것도 아이가 켜야 열립니다.
      </p>
    </div>
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
<section class="pad" id="partners">
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
        <p style="margin-top:8px;font-size:15px;color:var(--ink-2)">
          투구 수 상한과 복귀 판단 기준을 현장 기준과 맞추기 위한 자문.
        </p>
        <div class="slot">계약 후 로고·검토 의견 게재</div>
      </div>
      <div class="partner reveal" style="animation-delay:.08s">
        <span class="status">● 협의 중</span>
        <h3 style="margin-top:16px">정형외과 의료진</h3>
        <p style="margin-top:8px;font-size:15px;color:var(--ink-2)">
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
<section class="pad" style="text-align:center">
  <div class="beam" style="opacity:.55"></div>
  <div class="wrap stack g24" style="align-items:center">
    <h2 class="reveal" style="max-width:20ch">오늘의 루틴이<br>3년 뒤의 기록이 됩니다</h2>
    <p class="lead reveal" style="max-width:52ch">
      월 9,900원. 선수 한 명을 관리하고, 보호자 연결은 추가 비용 없이 됩니다.
    </p>
    <div class="cta-row reveal" style="justify-content:center">
      <a class="btn btn-primary" href="https://eliteroutine.github.io/beginner_guide.html">초보자 설명서</a>
      <a class="btn btn-ghost" href="https://eliteroutine.github.io/parent_guide.html">학부모 안내서</a>
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

  // 스크롤 등장 — 한 번만 켠다. 다시 사라졌다 나타나면 산만하다.
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (!e.isIntersecting) return;
      e.target.classList.add('in-view');
      io.unobserve(e.target);
    }});
  }}, {{ rootMargin: '0px 0px -12% 0px', threshold: 0.12 }});

  document.querySelectorAll('.reveal, .core-card, .chart').forEach(function (el) {{
    if (reduce) {{ el.classList.add('in-view'); return; }}
    io.observe(el);
  }});

  // 숫자 세기
  document.querySelectorAll('[data-count]').forEach(function (el) {{
    var target = parseInt(el.dataset.count, 10);
    var small = el.querySelector('small');
    var suffix = small ? small.outerHTML : '';
    if (reduce || target === 0) {{ el.innerHTML = target + suffix; return; }}
    var seen = new IntersectionObserver(function (es) {{
      if (!es[0].isIntersecting) return;
      seen.disconnect();
      var t0 = performance.now(), dur = 900;
      (function step(now) {{
        var p = Math.min(1, (now - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        el.innerHTML = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(step);
      }})(t0);
    }}, {{ threshold: 0.6 }});
    seen.observe(el);
  }});

  // 상단 바 + 진행 막대
  var bar = document.getElementById('topbar');
  var prog = document.getElementById('progress');
  function onScroll() {{
    var y = scrollY;
    bar.classList.toggle('solid', y > 12);
    var max = document.documentElement.scrollHeight - innerHeight;
    prog.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
  }}
  addEventListener('scroll', onScroll, {{ passive: true }});
  onScroll();
}})();
</script>
"""

out = os.path.join(ROOT, "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
io.open(out, "w", encoding="utf-8", newline="\n").write(HTML)
print("wrote", out, os.path.getsize(out) // 1024, "KB")
