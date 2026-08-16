# -*- coding: utf-8 -*-
"""엘리트 루틴 케어 소개 사이트 — CSS.

## 지면

흰 바탕에 블루. 아이의 기록을 다루는 앱이라 지면은 밝고 정직해야 한다.
파랑은 브랜드 하나만 쓰고, 부상 신호 삼색(안전·주의·위험)은 장식이 아니라
훈련 부하 구간 그 자체라 따로 둔다.

밝은 지면 하나로 간다. 대신 **스토리와 마무리 두 구간만 짙은 남색으로
뒤집는다** — 이야기가 꺾이는 자리라 지면도 함께 꺾인다.

## 글꼴

Pretendard 를 저장소에 함께 두고 직접 물린다. 외부 CDN 은 막혀 있고,
시스템 기본 글꼴로는 큰 제목이 버티지 못한다. 라이선스가 OFL 이라 함께
배포해도 된다(`fonts/OFL.txt`). 2.3MB 라 `font-display: swap` 으로
글자가 먼저 뜨게 한다.
"""

CSS = r"""
@font-face {
  font-family: "Pretendard";
  src: url("fonts/Pretendard-Regular.woff2") format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Pretendard";
  src: url("fonts/Pretendard-SemiBold.woff2") format("woff2");
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Pretendard";
  src: url("fonts/Pretendard-ExtraBold.woff2") format("woff2");
  font-weight: 800; font-style: normal; font-display: swap;
}

/* ───────────────────────────────────────────────────────────
   토큰
   ─────────────────────────────────────────────────────────── */
:root {
  --ground: #FFFFFF;
  --ground-2: #F3F7FF;      /* 살짝 푸른 기가 도는 면. 순회색은 무성의하다 */
  --panel: #FFFFFF;
  --panel-2: #EDF3FF;
  --rule: #DEE7F5;
  --rule-2: #C7D6EE;

  --ink: #0A1730;
  --ink-2: #3D4A60;
  --ink-3: #5F6E86;   /* 흰 바탕에서 4.24 라 기준(4.5)에 못 미쳤다 */

  --beam: #1668F0;          /* 브랜드 파랑 */
  --beam-2: #0B4FC0;        /* 진한 쪽 — 흰 바탕 위 글자용 */
  --beam-3: #5AA0FF;        /* 밝은 쪽 — 어두운 면 위 */
  --beam-wash: #E7F0FF;
  --beam-glow: rgba(22,104,240,.16);

  --deep: #061B3D;          /* 뒤집는 구간(스토리·마무리) */
  --deep-2: #0C2A5A;
  --on-deep: #FFFFFF;
  --on-deep-2: #A9C2E8;

  --safe: #097C42;    /* 라벨 글자로 쓰므로 흰 바탕에서 읽혀야 한다 */
  --watch: #9A6100;
  --risk: #CF3327;   /* 살짝 띄운 바탕(#EDF3FF) 위에서도 4.5 를 넘겨야 한다 */

  --sans: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI",
    "Malgun Gothic", "Apple SD Gothic Neo", system-ui, sans-serif;
  --mono: ui-monospace, "Cascadia Mono", Consolas, monospace;

  --max: 1200px;
  --gut: 24px;
  --shadow: 0 1px 2px rgba(10,30,70,.05), 0 12px 32px rgba(10,30,70,.07);
  --shadow-lg: 0 2px 6px rgba(10,30,70,.06), 0 28px 64px rgba(10,30,70,.12);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }

body {
  margin: 0;
  background: var(--ground);
  color: var(--ink-2);
  font-family: var(--sans);
  font-size: 19px;
  line-height: 1.75;
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.wrap { max-width: var(--max); margin: 0 auto; padding: 0 var(--gut); }
.narrow { max-width: 820px; }

/* 세로로 쌓고 사이를 띄운다. h1·p 의 margin 을 0 으로 둔 대신
   간격은 전부 여기서 준다 — 안 그러면 제목과 본문이 달라붙는다. */
.stack { display: flex; flex-direction: column; align-items: stretch; }
.g8 { gap: 8px; } .g16 { gap: 16px; } .g24 { gap: 24px; }
.g32 { gap: 32px; } .g40 { gap: 40px; } .g48 { gap: 48px; }
.stack > * { max-width: 100%; }

h1, h2, h3, h4 { color: var(--ink); margin: 0; text-wrap: balance; }
h1 {
  font-size: clamp(46px, 8.6vw, 104px); line-height: 0.98;
  letter-spacing: -0.05em; font-weight: 800;
}
h2 {
  font-size: clamp(34px, 5.4vw, 62px); line-height: 1.08;
  letter-spacing: -0.042em; font-weight: 800;
}
h3 {
  font-size: clamp(22px, 2.8vw, 30px); line-height: 1.22;
  letter-spacing: -0.028em; font-weight: 800;
}
p { margin: 0; }
a { color: var(--beam-2); }

.eyebrow {
  font-family: var(--mono); font-size: 13px; letter-spacing: 0.2em;
  text-transform: uppercase; color: var(--beam); font-weight: 600;
}
.lead { font-size: clamp(19px, 2.2vw, 24px); line-height: 1.65; color: var(--ink-2); }

section { position: relative; }
.pad { padding: clamp(84px, 12vw, 172px) 0; }

/* ── 상단 바 ─────────────────────────────────────────── */
.topbar {
  position: fixed; inset: 0 0 auto 0; z-index: 60;
  backdrop-filter: blur(16px) saturate(150%);
  background: rgba(255,255,255,.82);
  border-bottom: 1px solid transparent;
  transition: border-color .3s, box-shadow .3s;
}
.topbar.solid {
  border-bottom-color: var(--rule);
  box-shadow: 0 6px 24px rgba(10,30,70,.05);
}
.topbar .row {
  max-width: var(--max); margin: 0 auto; padding: 15px var(--gut);
  display: flex; align-items: center; gap: 18px;
}
.brand {
  display: flex; align-items: center; gap: 11px; font-weight: 800;
  color: var(--ink); letter-spacing: -.03em; font-size: 18px;
}
.brand svg { width: 30px; height: 30px; flex: none; }
.topbar nav { margin-left: auto; display: flex; gap: 26px; }
.topbar nav a {
  color: var(--ink-3); text-decoration: none; font-size: 16px; font-weight: 600;
  transition: color .16s;
}
.topbar nav a:hover { color: var(--beam-2); }
@media (max-width: 860px) { .topbar nav { display: none; } }
.progress { position: absolute; left: 0; bottom: -1px; height: 3px; background: var(--beam); width: 0; }

/* ── 히어로 ──────────────────────────────────────────── */
.hero { position: relative; padding: clamp(140px, 18vw, 210px) 0 clamp(64px, 9vw, 110px); overflow: hidden; }
.hero > .wrap { position: relative; z-index: 2; }
.hero-grid {
  display: grid; grid-template-columns: minmax(0,1.08fr) minmax(0,.92fr);
  gap: clamp(36px, 5vw, 80px); align-items: center;
}
@media (max-width: 940px) { .hero-grid { grid-template-columns: 1fr; } }

.beam {
  position: absolute; inset: -30% -20% auto -20%; height: 130%;
  background:
    radial-gradient(46% 40% at 18% 6%, var(--beam-glow), transparent 68%),
    radial-gradient(38% 32% at 86% 26%, rgba(90,160,255,.16), transparent 70%);
  pointer-events: none;
  animation: drift 24s ease-in-out infinite alternate;
}
@keyframes drift { to { transform: translate3d(2.5%, 1.5%, 0) scale(1.05); } }

.hero h1 span.hl { color: var(--beam); }

.badge-row { display: flex; flex-wrap: wrap; gap: 10px; }
.badge {
  font-size: 15px; font-weight: 600; padding: 9px 16px; border-radius: 999px;
  border: 1px solid var(--rule-2); color: var(--ink-2); background: var(--panel);
}
.cta-row { display: flex; flex-wrap: wrap; gap: 14px; }
.btn {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 18px 30px; border-radius: 16px; font-weight: 800; font-size: 18px;
  text-decoration: none; border: 1px solid transparent; cursor: pointer;
  letter-spacing: -.02em;
  transition: transform .18s cubic-bezier(.2,.8,.3,1), box-shadow .18s, background .18s;
}
.btn-primary {
  background: var(--beam); color: #fff;
  box-shadow: 0 12px 30px -10px rgba(22,104,240,.65);
}
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 22px 44px -12px rgba(22,104,240,.7); }
.btn-ghost { border-color: var(--rule-2); color: var(--ink); background: var(--panel); }
.btn-ghost:hover { transform: translateY(-3px); border-color: var(--beam); color: var(--beam-2); }

/* 기기 목업 */
.phone {
  position: relative; width: min(320px, 78vw); margin-inline: auto;
  border-radius: 38px; padding: 10px;
  background: linear-gradient(160deg, #dbe6f7, #f7fafe);
  box-shadow: var(--shadow-lg), 0 0 0 1px var(--rule) inset;
}
.phone img { display: block; width: 100%; border-radius: 29px; }
.phone::after {
  content: ""; position: absolute; left: 50%; top: 17px; transform: translateX(-50%);
  width: 74px; height: 5px; border-radius: 3px; background: rgba(10,23,48,.14);
}
.phone-float { animation: float 7s ease-in-out infinite; }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }

/* ── 지표 띠 ─────────────────────────────────────────── */
.metrics { background: var(--ground-2); border-block: 1px solid var(--rule); }
.metrics .row { display: grid; grid-template-columns: repeat(4, 1fr); }
.metric { padding: 44px 26px; border-right: 1px solid var(--rule); }
.metric:last-child { border-right: 0; }
.metric .n {
  font-size: clamp(40px, 5.4vw, 64px); font-weight: 800; color: var(--beam-2);
  letter-spacing: -.055em; font-variant-numeric: tabular-nums; line-height: 1;
}
.metric .n small { font-size: .42em; font-weight: 700; color: var(--ink-3); margin-left: 4px; }
.metric .l { font-size: 16px; color: var(--ink-3); margin-top: 12px; font-weight: 600; }
@media (max-width: 800px) {
  .metrics .row { grid-template-columns: repeat(2, 1fr); }
  .metric:nth-child(2) { border-right: 0; }
  .metric:nth-child(-n+2) { border-bottom: 1px solid var(--rule); }
}

/* ── 스토리 — 여기만 어둡게 뒤집는다 ─────────────────── */
.plaster { background: var(--deep); color: var(--on-deep-2); position: relative; overflow: hidden; }
.plaster h2, .plaster h3, .plaster strong { color: var(--on-deep); }
.plaster .eyebrow { color: var(--beam-3); }
.plaster::before {
  content: ""; position: absolute; inset: -40% -20% auto -20%; height: 120%;
  background: radial-gradient(42% 40% at 22% 10%, rgba(90,160,255,.20), transparent 70%);
  pointer-events: none;
}
.story-grid { display: grid; grid-template-columns: 84px minmax(0,1fr); gap: clamp(20px,4vw,48px); }
@media (max-width: 760px) { .story-grid { grid-template-columns: 1fr; } }
.story-rail { position: relative; }
.story-rail .line { position: absolute; left: 15px; top: 8px; bottom: 8px; width: 2px; background: rgba(169,194,232,.28); }
.story-beat { position: relative; padding-left: 52px; }
.story-beat + .story-beat { margin-top: 48px; }
.story-beat .dot {
  position: absolute; left: 5px; top: 9px; width: 22px; height: 22px; border-radius: 50%;
  background: var(--deep); border: 3px solid var(--beam-3);
}
.story-beat.turn .dot { background: var(--risk); border-color: var(--risk); }
.story-beat .when {
  font-family: var(--mono); font-size: 13px; letter-spacing: .18em;
  color: var(--beam-3); text-transform: uppercase; font-weight: 600;
}
.story-beat p { margin-top: 10px; font-size: clamp(18px, 2.1vw, 22px); line-height: 1.75; }
.pull {
  margin: 48px 0 0; padding: 0 0 0 30px; border-left: 5px solid var(--beam-3);
  font-size: clamp(24px, 3.6vw, 40px); line-height: 1.35; font-weight: 800;
  color: var(--on-deep); letter-spacing: -.035em;
}
.sign { margin-top: 18px; font-size: 16px; color: var(--on-deep-2); }

/* ── 카드 ────────────────────────────────────────────── */
.cards { display: grid; gap: 20px; }
.cards.c3 { grid-template-columns: repeat(3, 1fr); }
.cards.c2 { grid-template-columns: repeat(2, 1fr); }
.cards.c4 { grid-template-columns: repeat(4, 1fr); }
@media (max-width: 1000px) { .cards.c3, .cards.c4 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 660px) { .cards.c2, .cards.c3, .cards.c4 { grid-template-columns: 1fr; } }

.card {
  background: var(--panel);
  border: 1px solid var(--rule); border-radius: 22px; padding: 32px;
  position: relative; overflow: hidden; box-shadow: var(--shadow);
  transition: transform .22s cubic-bezier(.2,.8,.3,1), box-shadow .22s, border-color .22s;
}
.card:hover { transform: translateY(-5px); box-shadow: var(--shadow-lg); border-color: var(--rule-2); }
.card .kicker {
  font-family: var(--mono); font-size: 12px; letter-spacing: .16em;
  text-transform: uppercase; color: var(--beam); font-weight: 600;
}
.card p { margin-top: 12px; font-size: 17px; line-height: 1.7; color: var(--ink-2); }
.card h3 { margin-top: 12px; }

/* 핵심 기능 대형 카드 */
.core { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 22px; }
@media (max-width: 900px) { .core { grid-template-columns: 1fr; } }
.core-card {
  border: 1px solid var(--rule); border-radius: 26px; overflow: hidden;
  background: var(--panel); box-shadow: var(--shadow);
  display: grid; grid-template-rows: auto 1fr;
  transition: transform .22s cubic-bezier(.2,.8,.3,1), box-shadow .22s;
}
.core-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-lg); }
.core-card .top { padding: 36px 36px 0; }
.core-card .viz { padding: 22px 30px 32px; }

/* ── 차트 ────────────────────────────────────────────── */
.chart { width: 100%; height: auto; display: block; overflow: visible; }
.tick { fill: var(--ink-3); font-size: 12px; font-family: var(--mono); }
.gridline { stroke: var(--rule); stroke-width: 1; stroke-dasharray: 3 5; }
.draw { stroke-dasharray: var(--len); stroke-dashoffset: var(--len); }
.in-view .draw { animation: draw 1.6s cubic-bezier(.4,0,.2,1) forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
.rise { transform: scaleY(0); transform-origin: bottom; }
.in-view .rise { animation: rise .85s cubic-bezier(.3,1.2,.4,1) forwards; }
@keyframes rise { to { transform: scaleY(1); } }
.pop { opacity: 0; transform: scale(.4); transform-origin: center; }
.in-view .pop { animation: pop .5s cubic-bezier(.2,1.4,.4,1) forwards; }
@keyframes pop { to { opacity: 1; transform: scale(1); } }

/* ── 스크롤 등장 ─────────────────────────────────────── */
.reveal { opacity: 0; transform: translateY(30px); }
.reveal.in-view { animation: reveal .78s cubic-bezier(.2,.8,.3,1) forwards; }
@keyframes reveal { to { opacity: 1; transform: none; } }

@media (prefers-reduced-motion: reduce) {
  .reveal, .reveal.in-view { opacity: 1; transform: none; animation: none; }
  .draw, .rise, .pop { animation: none !important; stroke-dashoffset: 0 !important; transform: none !important; opacity: 1 !important; }
  .phone-float, .beam { animation: none; }
}

/* ── 표 ──────────────────────────────────────────────── */
.tablewrap {
  overflow-x: auto; border: 1px solid var(--rule); border-radius: 20px;
  background: var(--panel); box-shadow: var(--shadow);
}
table { border-collapse: collapse; width: 100%; min-width: 620px; font-size: 18px; }
th, td { text-align: left; padding: 20px 24px; border-bottom: 1px solid var(--rule); }
thead th {
  font-family: var(--mono); font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--ink-3); background: var(--panel-2); font-weight: 600;
}
tbody tr:last-child td { border-bottom: 0; }
td:first-child { color: var(--ink); font-weight: 700; }
.yes { color: var(--safe); font-weight: 800; }
.no { color: var(--risk); font-weight: 800; }
.partial { color: var(--watch); font-weight: 800; }

/* ── 영상 ────────────────────────────────────────────── */
.film {
  border-radius: 24px; padding: 10px; background: var(--panel-2);
  border: 1px solid var(--rule); box-shadow: var(--shadow);
}
.film video { display: block; width: 100%; border-radius: 16px; background: #061B3D; }
.film-cta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
.filmwrap { display: grid; grid-template-columns: minmax(0,340px) minmax(0,1fr);
  gap: clamp(28px,5vw,64px); align-items: center; }
@media (max-width: 820px) { .filmwrap { grid-template-columns: 1fr; } }

/* ── 제휴 ────────────────────────────────────────────── */
.partners { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
@media (max-width: 760px) { .partners { grid-template-columns: 1fr; } }
.partner {
  border: 2px dashed var(--rule-2); border-radius: 22px; padding: 32px;
  background: var(--ground-2);
}
.partner .status {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  color: var(--watch); border: 1px solid rgba(192,122,0,.3); background: #FFF6E5;
  padding: 7px 14px; border-radius: 999px;
}
.partner .slot {
  margin-top: 22px; height: 76px; border-radius: 14px; background: var(--panel);
  border: 1px solid var(--rule);
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-3); font-size: 15px; font-weight: 600;
}

/* ── 마무리 — 여기도 뒤집는다 ────────────────────────── */
.finale { background: var(--deep); color: var(--on-deep-2); overflow: hidden; }
.finale h2 { color: var(--on-deep); }
.finale .lead { color: var(--on-deep-2); }
.finale .btn-ghost {
  background: transparent; border-color: rgba(169,194,232,.42); color: var(--on-deep);
}
.finale .btn-ghost:hover { border-color: var(--beam-3); color: var(--beam-3); }
.finale::before {
  content: ""; position: absolute; inset: -50% -20% auto -20%; height: 140%;
  background: radial-gradient(40% 44% at 50% 10%, rgba(90,160,255,.24), transparent 68%);
  pointer-events: none;
}

/* ── 푸터 ────────────────────────────────────────────── */
footer { border-top: 1px solid var(--rule); background: var(--ground-2); }
footer .row { display: flex; flex-wrap: wrap; gap: 28px 56px; padding: 56px 0; }
footer a { color: var(--ink-2); text-decoration: none; font-size: 17px; font-weight: 600; }
footer a:hover { color: var(--beam-2); }
.fine { font-size: 15px; color: var(--ink-3); line-height: 1.7; }

:focus-visible { outline: 3px solid var(--beam); outline-offset: 3px; border-radius: 6px; }

/* ═══════════════════════════════════════════════════════════
   브랜드 지면 장치 — 여기부터는 "보여 주기" 위한 것들
   ═══════════════════════════════════════════════════════════ */

/* ── 히어로 배경: 천천히 도는 색 덩어리 + 격자 ──────────── */
.mesh { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.mesh i { position: absolute; display: block; border-radius: 50%; filter: blur(72px); opacity: .5; }
.mesh i:nth-child(1) { width: 46vw; height: 46vw; left: -9vw; top: -13vw;
  background: radial-gradient(circle, #9CC4FF, transparent 66%); animation: blob1 26s ease-in-out infinite alternate; }
.mesh i:nth-child(2) { width: 38vw; height: 38vw; right: -7vw; top: -7vw;
  background: radial-gradient(circle, #C7DDFF, transparent 66%); animation: blob2 32s ease-in-out infinite alternate; }
.mesh i:nth-child(3) { width: 34vw; height: 34vw; left: 42vw; top: 24vw; opacity: .34;
  background: radial-gradient(circle, #B7F0DA, transparent 66%); animation: blob3 38s ease-in-out infinite alternate; }
@keyframes blob1 { to { transform: translate3d(7vw, 5vw, 0) scale(1.16); } }
@keyframes blob2 { to { transform: translate3d(-6vw, 7vw, 0) scale(1.10); } }
@keyframes blob3 { to { transform: translate3d(-9vw,-6vw, 0) scale(1.20); } }

.grid-bg {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(to right, rgba(10,30,70,.055) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(10,30,70,.055) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(72% 62% at 50% 32%, #000 28%, transparent 76%);
  -webkit-mask-image: radial-gradient(72% 62% at 50% 32%, #000 28%, transparent 76%);
}

/* ── 제목이 한 줄씩 밀려 올라온다 ────────────────────── */
.rise-line { display: block; overflow: hidden; }
.rise-line > span { display: block; transform: translateY(114%);
  animation: riseUp .95s cubic-bezier(.16,1,.3,1) forwards; }
@keyframes riseUp { to { transform: none; } }

/* ── 떠 있는 상태 칩 ─────────────────────────────────── */
.float-chip {
  position: absolute; z-index: 3; background: var(--panel);
  border: 1px solid var(--rule); border-radius: 18px; padding: 13px 18px;
  box-shadow: var(--shadow-lg); display: flex; align-items: center; gap: 12px;
  animation: bob 6s ease-in-out infinite;
}
.float-chip .live { width: 10px; height: 10px; border-radius: 50%; background: var(--safe);
  flex: none; animation: pulse 2.2s infinite; }
.float-chip b { display: block; color: var(--ink); font-size: 16px; font-weight: 800; letter-spacing: -.02em; }
.float-chip span { display: block; color: var(--ink-3); font-size: 13px; font-weight: 600; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-11px); } }
@keyframes pulse {
  0%   { box-shadow: 0 0 0 0 rgba(9,124,66,.45); }
  70%  { box-shadow: 0 0 0 13px rgba(9,124,66,0); }
  100% { box-shadow: 0 0 0 0 rgba(9,124,66,0); }
}

/* ── 영상 — 어두운 지면에 크게 하나 ──────────────────── */
.showreel { background: var(--deep); overflow: hidden; }
.showreel h2, .showreel h3, .showreel .bigval { color: var(--on-deep); }
.showreel .lead, .showreel p { color: var(--on-deep-2); }
.showreel .eyebrow { color: var(--beam-3); }
.showreel .eyebrow::before { background: var(--beam-3); }
.reelframe {
  position: relative; border-radius: 24px; overflow: hidden;
  border: 1px solid rgba(169,194,232,.22);
  box-shadow: 0 44px 110px -44px rgba(0,0,0,.75);
  background: #061B3D;
}
.reelframe video { display: block; width: 100%; height: auto; }
.reel-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.reel-meta span {
  font-size: 14px; font-weight: 600; padding: 9px 15px; border-radius: 999px;
  border: 1px solid rgba(169,194,232,.28); color: var(--on-deep-2);
}

/* ── 기능이 흘러가는 띠 ──────────────────────────────── */
.marquee {
  overflow: hidden; border-block: 1px solid var(--rule);
  background: var(--panel); padding: 24px 0;
  mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent);
}
.marquee .track { display: flex; gap: 16px; width: max-content; animation: slide 46s linear infinite; }
.marquee:hover .track { animation-play-state: paused; }
.marquee .chip {
  display: inline-flex; align-items: center; gap: 10px; white-space: nowrap;
  font-size: 17px; font-weight: 700; color: var(--ink-2);
  border: 1px solid var(--rule); border-radius: 999px; padding: 12px 22px; background: var(--ground);
}
.marquee .chip i { width: 8px; height: 8px; border-radius: 50%; background: var(--beam); flex: none; }
@keyframes slide { to { transform: translateX(-50%); } }

/* ── 스크롤에 물린 큰 차트 ───────────────────────────── */
.pin { position: relative; }
.pin .rail { height: 260vh; }
.pin .sticky {
  position: sticky; top: 92px; padding: clamp(24px,4vw,48px) 0;
  display: grid; grid-template-columns: minmax(0,.82fr) minmax(0,1.18fr);
  gap: clamp(28px,5vw,72px); align-items: center;
}
@media (max-width: 980px) {
  .pin .rail { height: auto; }
  .pin .sticky { position: static; grid-template-columns: 1fr; }
}
.zone-legend { display: flex; flex-direction: column; gap: 11px; margin-top: 28px; }
.zone {
  display: flex; align-items: center; gap: 15px; padding: 15px 18px;
  border-radius: 15px; border: 1px solid var(--rule); background: var(--panel);
  opacity: .4; transition: opacity .32s, border-color .32s, transform .32s, box-shadow .32s;
}
.zone.on { opacity: 1; border-color: currentColor; transform: translateX(7px); box-shadow: var(--shadow); }
.zone .sw { width: 13px; height: 36px; border-radius: 5px; flex: none; background: currentColor; }
.zone b { display: block; font-size: 18px; color: var(--ink); font-weight: 800; letter-spacing: -.02em; }
.zone span { display: block; font-size: 15px; color: var(--ink-3); }
.zone.z1 { color: var(--safe); } .zone.z2 { color: var(--watch); } .zone.z3 { color: var(--risk); }

.bigval {
  font-size: clamp(50px, 8.4vw, 96px); font-weight: 800; letter-spacing: -.06em;
  line-height: 1; font-variant-numeric: tabular-nums; color: var(--ink);
}
.bigval small { font-size: .26em; font-weight: 700; color: var(--ink-3); margin-left: 10px; letter-spacing: -.02em; }
.showreel .bigval small { color: var(--on-deep-2); }

/* ── 카드에 커서 불빛 ────────────────────────────────── */
.spot { position: relative; }
.spot::after {
  content: ""; position: absolute; inset: 0; border-radius: inherit;
  background: radial-gradient(240px circle at var(--mx,50%) var(--my,0%), rgba(22,104,240,.11), transparent 62%);
  opacity: 0; transition: opacity .28s; pointer-events: none;
}
.spot:hover::after { opacity: 1; }

/* ── 오른쪽 구간 표시 ────────────────────────────────── */
.dots { position: fixed; right: 20px; top: 50%; transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 13px; z-index: 60; }
@media (max-width: 1240px) { .dots { display: none; } }
.dots a { width: 10px; height: 10px; border-radius: 50%; background: var(--rule-2);
  transition: background .25s, transform .25s; position: relative; }
.dots a.on { background: var(--beam); transform: scale(1.5); }
.dots a::after {
  content: attr(data-label); position: absolute; right: 22px; top: 50%;
  transform: translateY(-50%) translateX(6px);
  background: var(--ink); color: #fff; font-size: 13px; font-weight: 600;
  padding: 6px 12px; border-radius: 8px; white-space: nowrap;
  opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s;
}
.dots a:hover::after { opacity: 1; transform: translateY(-50%); }

/* ── 종목 타일 ───────────────────────────────────────── */
.sports { display: grid; grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); gap: 9px; }
.sports span {
  padding: 15px 6px; border-radius: 13px; background: var(--panel);
  border: 1px solid var(--rule); text-align: center;
  font-size: 15px; font-weight: 700; color: var(--ink-2);
  opacity: 0; transform: scale(.84);
}
.in-view .sports span { animation: tilePop .48s cubic-bezier(.2,1.35,.4,1) forwards; }
@keyframes tilePop { to { opacity: 1; transform: none; } }

/* ── 히트맵 ──────────────────────────────────────────── */
.heat { display: grid; grid-template-columns: repeat(14, 1fr); gap: 6px; }
.heat i { aspect-ratio: 1; border-radius: 5px; display: block; opacity: 0; transform: scale(.5); }
.in-view .heat i { animation: tilePop .4s cubic-bezier(.2,1.35,.4,1) forwards; }
.heat-key { display: flex; align-items: center; gap: 9px; margin-top: 18px;
  font-size: 14px; color: var(--ink-3); font-weight: 600; }
.heat-key i { width: 15px; height: 15px; border-radius: 4px; display: block; }

/* ── 큰 인용 ─────────────────────────────────────────── */
.bigquote {
  font-size: clamp(30px, 4.4vw, 58px); line-height: 1.2; font-weight: 800;
  letter-spacing: -.045em; color: var(--ink); text-wrap: balance;
}
.showreel .bigquote, .plaster .bigquote, .finale .bigquote { color: var(--on-deep); }

@media (prefers-reduced-motion: reduce) {
  .mesh i, .float-chip, .float-chip .live, .marquee .track { animation: none !important; }
  .rise-line > span { transform: none; animation: none; }
  .sports span, .heat i { opacity: 1; transform: none; animation: none; }
}
"""
