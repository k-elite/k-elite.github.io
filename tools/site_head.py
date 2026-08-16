# -*- coding: utf-8 -*-
"""엘리트 루틴 케어 소개 사이트 — CSS."""

CSS = r"""
/* ───────────────────────────────────────────────────────────
   토큰
   지면은 야간 훈련장. 데이터 삼색(안전·주의·위험)은 장식이 아니라
   훈련 부하 구간 그 자체라 액센트와 따로 둔다.
   ─────────────────────────────────────────────────────────── */
:root {
  --ground: #070C14;
  --ground-2: #0C131E;
  --panel: #111A28;
  --panel-2: #16202F;
  --rule: #1E2A3C;
  --rule-2: #2A374B;

  --ink: #EEF3FA;
  --ink-2: #A9B8CC;
  --ink-3: #6D7F97;

  --beam: #2E7DF6;
  --beam-2: #63A4FF;
  --beam-glow: rgba(46,125,246,.22);

  --safe: #2ED47A;
  --watch: #FFB020;
  --risk: #FF5A52;

  --plaster: #F1ECE2;
  --plaster-2: #E4DCCD;
  --plaster-ink: #1A1610;
  --plaster-ink-2: #564E40;

  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Malgun Gothic",
    "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
  --mono: ui-monospace, "Cascadia Mono", Consolas, "D2Coding", monospace;

  --max: 1160px;
  --gut: 24px;
}

/* 이 사이트는 하나의 시각 세계(야간 훈련장)에 의도적으로 고정한다.
   그래서 테마 전환을 두지 않되, 배경과 글자색을 전부 명시해
   어떤 지면 위에 얹혀도 그대로 읽히게 한다. */

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }

body {
  margin: 0;
  background: var(--ground);
  color: var(--ink-2);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.wrap { max-width: var(--max); margin: 0 auto; padding: 0 var(--gut); }
.narrow { max-width: 760px; }

h1, h2, h3, h4 { color: var(--ink); margin: 0; text-wrap: balance; }
h1 { font-size: clamp(38px, 7.2vw, 78px); line-height: 1.02; letter-spacing: -.045em; font-weight: 900; }
h2 { font-size: clamp(28px, 4.6vw, 46px); line-height: 1.12; letter-spacing: -.035em; font-weight: 900; }
h3 { font-size: clamp(19px, 2.4vw, 24px); line-height: 1.25; letter-spacing: -.02em; font-weight: 800; }
p { margin: 0; }
a { color: var(--beam-2); }

.eyebrow {
  font-family: var(--mono);
  font-size: 11.5px;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--ink-3);
}
.lead { font-size: clamp(17px, 2.1vw, 20px); line-height: 1.7; color: var(--ink-2); }
.stack { display: flex; flex-direction: column; }
.g8 { gap: 8px; } .g12 { gap: 12px; } .g16 { gap: 16px; }
.g24 { gap: 24px; } .g32 { gap: 32px; } .g48 { gap: 48px; }

section { position: relative; }
.pad { padding: clamp(72px, 11vw, 148px) 0; }

/* ── 상단 바 ─────────────────────────────────────────── */
.topbar {
  position: fixed; inset: 0 0 auto 0; z-index: 60;
  backdrop-filter: blur(14px);
  background: rgba(7,12,20,.72);
  border-bottom: 1px solid transparent;
  transition: border-color .3s, background .3s;
}
.topbar.solid { border-bottom-color: var(--rule); }
.topbar .row {
  max-width: var(--max); margin: 0 auto; padding: 13px var(--gut);
  display: flex; align-items: center; gap: 18px;
}
.brand { display: flex; align-items: center; gap: 10px; font-weight: 900; color: var(--ink); letter-spacing: -.02em; }
.brand svg { width: 26px; height: 26px; flex: none; }
.topbar nav { margin-left: auto; display: flex; gap: 22px; }
.topbar nav a { color: var(--ink-3); text-decoration: none; font-size: 14px; font-weight: 700; }
.topbar nav a:hover { color: var(--ink); }
@media (max-width: 780px) { .topbar nav { display: none; } }
.progress { position: absolute; left: 0; bottom: -1px; height: 2px; background: var(--beam); width: 0; }

/* ── 히어로 ──────────────────────────────────────────── */
.hero { padding: clamp(120px, 17vw, 190px) 0 clamp(56px, 8vw, 92px); overflow: hidden; }
.hero-grid { display: grid; grid-template-columns: minmax(0,1.05fr) minmax(0,.95fr); gap: clamp(32px, 5vw, 72px); align-items: center; }
@media (max-width: 900px) { .hero-grid { grid-template-columns: 1fr; } }

.beam {
  position: absolute; inset: -20% -30% auto -10%; height: 120%;
  background:
    radial-gradient(58% 42% at 22% 8%, var(--beam-glow), transparent 70%),
    radial-gradient(40% 34% at 82% 22%, rgba(99,164,255,.10), transparent 72%);
  pointer-events: none;
  animation: drift 22s ease-in-out infinite alternate;
}
@keyframes drift { to { transform: translate3d(3%, 2%, 0) scale(1.06); } }

.hero h1 span.hl {
  background: linear-gradient(180deg, var(--ink) 62%, var(--beam-2) 62%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.badge-row { display: flex; flex-wrap: wrap; gap: 8px; }
.badge {
  font-family: var(--mono); font-size: 11.5px; letter-spacing: .08em;
  padding: 6px 11px; border-radius: 999px;
  border: 1px solid var(--rule-2); color: var(--ink-2); background: var(--panel);
}
.cta-row { display: flex; flex-wrap: wrap; gap: 12px; }
.btn {
  display: inline-flex; align-items: center; gap: 9px;
  padding: 14px 22px; border-radius: 12px; font-weight: 800; font-size: 15.5px;
  text-decoration: none; border: 1px solid transparent; cursor: pointer;
  transition: transform .18s cubic-bezier(.2,.8,.3,1), box-shadow .18s, background .18s;
}
.btn-primary { background: var(--beam); color: #fff; box-shadow: 0 10px 30px -10px var(--beam); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 18px 40px -12px var(--beam); }
.btn-ghost { border-color: var(--rule-2); color: var(--ink); background: var(--panel); }
.btn-ghost:hover { transform: translateY(-2px); border-color: var(--beam); }

/* 기기 목업 */
.phone {
  position: relative; width: min(300px, 78vw); margin-inline: auto;
  border-radius: 34px; padding: 9px;
  background: linear-gradient(160deg, #26313F, #0E1520);
  box-shadow: 0 40px 90px -30px #000, 0 0 0 1px var(--rule-2) inset;
}
.phone img { display: block; width: 100%; border-radius: 26px; }
.phone::after {
  content: ""; position: absolute; left: 50%; top: 15px; transform: translateX(-50%);
  width: 72px; height: 5px; border-radius: 3px; background: #0A0F17;
}
.phone-float { animation: float 7s ease-in-out infinite; }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }

/* ── 지표 띠 ─────────────────────────────────────────── */
.metrics { border-block: 1px solid var(--rule); background: var(--ground-2); }
.metrics .row { display: grid; grid-template-columns: repeat(4, 1fr); }
.metric { padding: 30px 22px; border-right: 1px solid var(--rule); }
.metric:last-child { border-right: 0; }
.metric .n {
  font-size: clamp(28px, 4vw, 40px); font-weight: 900; color: var(--ink);
  letter-spacing: -.04em; font-variant-numeric: tabular-nums; line-height: 1;
}
.metric .n small { font-size: .46em; font-weight: 800; color: var(--ink-3); margin-left: 3px; }
.metric .l { font-size: 13.5px; color: var(--ink-3); margin-top: 8px; }
@media (max-width: 760px) {
  .metrics .row { grid-template-columns: repeat(2, 1fr); }
  .metric:nth-child(2) { border-right: 0; }
  .metric:nth-child(-n+2) { border-bottom: 1px solid var(--rule); }
}

/* ── 석고(스토리) ───────────────────────────────────── */
.plaster {
  background: var(--plaster);
  color: var(--plaster-ink-2);
  position: relative;
}
.plaster h2, .plaster h3, .plaster strong { color: var(--plaster-ink); }
.plaster .eyebrow { color: #8A7F6C; }
.plaster::before, .plaster::after {
  content: ""; position: absolute; left: 0; right: 0; height: 26px;
  background: repeating-linear-gradient(90deg, var(--plaster) 0 14px, var(--plaster-2) 14px 28px);
  opacity: .55;
}
.plaster::before { top: 0; }
.plaster::after { bottom: 0; }
.story-grid { display: grid; grid-template-columns: 92px minmax(0,1fr); gap: clamp(20px,4vw,44px); }
@media (max-width: 720px) { .story-grid { grid-template-columns: 1fr; } }
.story-rail { position: relative; }
.story-rail .line { position: absolute; left: 15px; top: 6px; bottom: 6px; width: 2px; background: var(--plaster-2); }
.story-beat { position: relative; padding-left: 46px; }
.story-beat + .story-beat { margin-top: 40px; }
.story-beat .dot {
  position: absolute; left: 6px; top: 7px; width: 20px; height: 20px; border-radius: 50%;
  background: var(--plaster); border: 3px solid var(--plaster-ink);
}
.story-beat.turn .dot { background: var(--risk); border-color: var(--risk); }
.story-beat .when {
  font-family: var(--mono); font-size: 11.5px; letter-spacing: .14em;
  color: #8A7F6C; text-transform: uppercase;
}
.story-beat p { margin-top: 6px; font-size: 16.5px; line-height: 1.8; }
.pull {
  margin: 34px 0 0; padding: 26px 30px; border-left: 4px solid var(--plaster-ink);
  font-size: clamp(19px, 2.6vw, 26px); line-height: 1.5; font-weight: 800;
  color: var(--plaster-ink); letter-spacing: -.02em;
}
.sign { margin-top: 14px; font-size: 14px; color: #8A7F6C; font-family: var(--mono); }

/* ── 카드 ────────────────────────────────────────────── */
.cards { display: grid; gap: 16px; }
.cards.c3 { grid-template-columns: repeat(3, 1fr); }
.cards.c2 { grid-template-columns: repeat(2, 1fr); }
.cards.c4 { grid-template-columns: repeat(4, 1fr); }
@media (max-width: 940px) { .cards.c3, .cards.c4 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .cards.c2, .cards.c3, .cards.c4 { grid-template-columns: 1fr; } }

.card {
  background: linear-gradient(180deg, var(--panel), var(--ground-2));
  border: 1px solid var(--rule); border-radius: 18px; padding: 26px;
  position: relative; overflow: hidden;
  transition: transform .22s cubic-bezier(.2,.8,.3,1), border-color .22s;
}
.card:hover { transform: translateY(-4px); border-color: var(--rule-2); }
.card .kicker {
  font-family: var(--mono); font-size: 11px; letter-spacing: .16em;
  text-transform: uppercase; color: var(--beam-2);
}
.card p { margin-top: 10px; font-size: 15px; line-height: 1.7; color: var(--ink-2); }
.card h3 { margin-top: 10px; }

.feature { display: grid; gap: 14px; }
.feature .glyph { width: 44px; height: 44px; }

/* 핵심 기능 대형 카드 */
.core { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px; }
@media (max-width: 860px) { .core { grid-template-columns: 1fr; } }
.core-card {
  border: 1px solid var(--rule); border-radius: 22px; overflow: hidden;
  background: linear-gradient(180deg, var(--panel), var(--ground-2));
  display: grid; grid-template-rows: auto 1fr;
}
.core-card .top { padding: 28px 28px 0; }
.core-card .viz { padding: 18px 28px 28px; }
.core-card.tall { grid-row: span 2; }

/* ── 차트 공통 ───────────────────────────────────────── */
.chart { width: 100%; height: auto; display: block; overflow: visible; }
.axis { stroke: var(--rule-2); stroke-width: 1; }
.gridline { stroke: var(--rule); stroke-width: 1; stroke-dasharray: 3 5; }
.tick { fill: var(--ink-3); font-size: 10.5px; font-family: var(--mono); }
.draw { stroke-dasharray: var(--len); stroke-dashoffset: var(--len); }
.in-view .draw { animation: draw 1.5s cubic-bezier(.4,0,.2,1) forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
.rise { transform: scaleY(0); transform-origin: bottom; }
.in-view .rise { animation: rise .8s cubic-bezier(.3,1.2,.4,1) forwards; }
@keyframes rise { to { transform: scaleY(1); } }
.pop { opacity: 0; transform: scale(.4); transform-origin: center; }
.in-view .pop { animation: pop .5s cubic-bezier(.2,1.4,.4,1) forwards; }
@keyframes pop { to { opacity: 1; transform: scale(1); } }

/* ── 스크롤 등장 ─────────────────────────────────────── */
.reveal { opacity: 0; transform: translateY(26px); }
.reveal.in-view { animation: reveal .72s cubic-bezier(.2,.8,.3,1) forwards; }
@keyframes reveal { to { opacity: 1; transform: none; } }

@media (prefers-reduced-motion: reduce) {
  .reveal, .reveal.in-view { opacity: 1; transform: none; animation: none; }
  .draw, .rise, .pop { animation: none !important; stroke-dashoffset: 0 !important; transform: none !important; opacity: 1 !important; }
  .phone-float, .beam { animation: none; }
}

/* ── 표 ──────────────────────────────────────────────── */
.tablewrap { overflow-x: auto; border: 1px solid var(--rule); border-radius: 16px; }
table { border-collapse: collapse; width: 100%; min-width: 560px; font-size: 15px; }
th, td { text-align: left; padding: 15px 18px; border-bottom: 1px solid var(--rule); }
thead th {
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--ink-3); background: var(--panel-2);
}
tbody tr:last-child td { border-bottom: 0; }
td:first-child { color: var(--ink); font-weight: 700; }
.yes { color: var(--safe); font-weight: 800; }
.no { color: var(--risk); font-weight: 800; }
.partial { color: var(--watch); font-weight: 800; }

/* ── 제휴 ────────────────────────────────────────────── */
.partners { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
@media (max-width: 720px) { .partners { grid-template-columns: 1fr; } }
.partner {
  border: 1px dashed var(--rule-2); border-radius: 18px; padding: 26px;
  background: repeating-linear-gradient(45deg, transparent 0 12px, rgba(255,255,255,.012) 12px 24px);
}
.partner .status {
  display: inline-flex; align-items: center; gap: 7px;
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--watch); border: 1px solid rgba(255,176,32,.35); background: rgba(255,176,32,.07);
  padding: 5px 10px; border-radius: 999px;
}
.partner .slot {
  margin-top: 18px; height: 62px; border-radius: 10px; background: var(--panel-2);
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-3); font-size: 13px; font-family: var(--mono); letter-spacing: .08em;
}

/* ── 푸터 ────────────────────────────────────────────── */
footer { border-top: 1px solid var(--rule); background: var(--ground-2); }
footer .row { display: flex; flex-wrap: wrap; gap: 24px 48px; padding: 44px 0; }
footer a { color: var(--ink-2); text-decoration: none; font-size: 15px; }
footer a:hover { color: var(--ink); }
.fine { font-size: 13px; color: var(--ink-3); line-height: 1.7; }

:focus-visible { outline: 2px solid var(--beam-2); outline-offset: 3px; border-radius: 4px; }
"""
