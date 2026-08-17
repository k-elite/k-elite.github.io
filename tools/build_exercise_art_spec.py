# -*- coding: utf-8 -*-
"""운동 일러스트 작업 지시서를 만든다.

## 왜 스크립트로 만드나

앱에는 케어 운동 14가지와 자세 점검 7가지가 들어 있고, 각각 **엔진이
재는 관절과 각도**가 정해져 있다. 그 숫자를 손으로 발주서에 옮겨 적으면
앱을 한 번 고칠 때마다 어긋난다. 그림은 165도로 그렸는데 앱은 150도를
정점으로 세는 일이 생긴다.

그래서 `care_exercise.dart` 와 `sport_form.dart` 를 **직접 읽어서**
만든다. 앱을 고치고 이 스크립트를 다시 돌리면 발주서도 같이 바뀐다.

    python tools/build_exercise_art_spec.py

앱 저장소 경로는 [APP] 에 있다.
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
APP = r"C:\github\elite_routine_care"
OUT = os.path.join(ROOT, "exercise_art_spec.html")

SOURCES = [
    (os.path.join(APP, "lib", "models", "care_exercise.dart"), "케어 운동"),
    (os.path.join(APP, "lib", "models", "sport_form.dart"), "자세 점검"),
]

# 관절별로 어느 방향에서 그려야 각도가 보이는가.
#
# 카메라(그리고 그림)가 관절이 도는 평면과 나란하면 각도가 안 보인다.
# 팔꿈치 굽힘은 옆에서, 어깨 벌림은 앞에서 봐야 한다.
VIEW = {
    "elbow": ("측면", "팔꿈치가 접히는 각도는 옆에서 봐야 보입니다. "
                     "정면에서 그리면 팔이 겹쳐 각도가 사라집니다."),
    "shoulder": ("정면", "팔을 몸에서 벌리는 각도라 앞에서 봐야 벌어진 폭이 "
                        "보입니다."),
    "hip": ("측면", "상체와 허벅지가 이루는 각도라 옆에서 봐야 합니다."),
    "knee": ("측면", "앉는 깊이는 옆에서만 보입니다."),
    "trunkTilt": ("정면", "좌우 어깨가 이루는 기울기라 앞에서 봐야 합니다."),
}

JOINT_KR = {
    "elbow": "팔꿈치 (어깨—팔꿈치—손목)",
    "shoulder": "어깨 (골반—어깨—팔꿈치)",
    "hip": "고관절 (어깨—골반—무릎)",
    "knee": "무릎 (골반—무릎—발목)",
    "trunkTilt": "몸통 기울기 (좌우 어깨를 잇는 선)",
}

# 기본으로 먼저 뜨는 운동. 아픈 곳이 없을 때 모두가 보는 넷이라 먼저 필요하다.
FIRST = {
    "shoulder_ytw", "core_dead_bug", "hip_glute_bridge", "ankle_calf_raise",
}

# 야구 아이가 가장 자주 보게 되는 것들.
SECOND = {
    "elbow_band_wrist_curl", "elbow_band_pronation",
    "shoulder_external_rotation", "shoulder_sleeper_stretch",
    "form_wall_slide", "form_rotation_symmetry", "form_overhead_squat",
}


def parse(path):
    """Dart 소스에서 운동 정의를 뽑는다.

    정규식으로 읽는다. Dart 파서를 붙일 만한 일이 아니고, 형식이 깨지면
    개수가 안 맞아 바로 드러난다([main] 의 검사).
    """
    src = io.open(path, encoding="utf-8").read()
    out = []

    for block in re.findall(r"CareExercise\((.*?)\n    \),", src, re.S):
        def one(key, cast=str, default=None):
            m = re.search(r"\b%s:\s*('((?:[^'\\]|\\.)*)'|[\d.]+|true|false)"
                          % key, block)
            if not m:
                return default
            raw = m.group(2) if m.group(2) is not None else m.group(1)
            return cast(raw)

        # 여러 줄로 이어 붙인 문자열('가' \n '나')을 하나로 만든다.
        def joined(key):
            m = re.search(r"\b%s:\s*((?:'(?:[^'\\]|\\.)*'\s*)+)" % key, block)
            if not m:
                return ""
            return "".join(re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1)))

        spec_m = re.search(r"spec:\s*PoseSpec\((.*?)\),\s*$", block, re.S)
        spec = spec_m.group(1) if spec_m else ""

        def sp(key, cast=str, default=None):
            m = re.search(r"\b%s:\s*(PoseJoint\.(\w+)|'([^']*)'|[\d.]+|true|false)"
                          % key, spec)
            if not m:
                return default
            raw = m.group(2) or m.group(3) or m.group(1)
            return cast(raw)

        eid = one("id")
        if not eid:
            continue

        out.append({
            "id": eid,
            "area": one("area"),
            "name": one("name"),
            "why": joined("why"),
            "how": joined("how"),
            "tool": one("tool"),
            "level": one("level"),
            "reps": one("baseReps", int, 0),
            "hold": one("baseHoldSeconds", int, 0),
            "sets": one("baseSets", int, 0),
            "joint": sp("joint"),
            "contracted": sp("contractedAngle", float, 0.0),
            "extended": sp("extendedAngle", float, 0.0),
            "peakHold": sp("holdSeconds", float, 0.0),
            "cue": re.sub(r"'\s*'", "", (re.search(
                r"cue:\s*((?:'(?:[^'\\]|\\.)*'\s*)+)", spec) or
                type("m", (), {"group": lambda *_: "''"})()).group(1))
                .strip().strip("'"),
            "symmetry": sp("watchSymmetry", lambda v: v == "true", True),
        })
    return out


def tier(eid):
    if eid in FIRST:
        return 1
    if eid in SECOND:
        return 2
    return 3


def dose(e):
    if e["hold"]:
        return "%d초 × %d세트" % (e["hold"], e["sets"])
    return "%d회 × %d세트" % (e["reps"], e["sets"])


def frames(e):
    """이 운동에 필요한 그림 목록."""
    lo, hi = e["contracted"], e["extended"]
    mid = (lo + hi) / 2
    hold = e["peakHold"]

    if e["hold"]:
        # 버티는 동작은 오가지 않는다. 자세 하나와 틀린 자세 하나.
        return [
            ("hold", "버티는 자세", "%d°" % round(lo),
             "이 각도로 %d초를 버팁니다. 힘이 들어가는 곳이 보이게 그려 "
             "주세요." % e["hold"]),
            ("wrong", "흔한 오류", "—", e["cue"]),
        ]

    return [
        ("start", "시작 자세", "%d°" % round(hi),
         "동작을 시작하는 자리. 앱에서 0회로 세는 지점입니다."),
        ("mid", "중간", "%d°" % round(mid),
         "두 장만 오가면 뚝뚝 끊깁니다. 가운데 한 장이 있으면 부드럽습니다."),
        ("peak", "정점", "%d°" % round(lo),
         "여기까지 와야 한 개로 셉니다."
         + (" 정점에서 %d초 버팁니다." % round(hold) if hold >= 1 else "")),
        ("wrong", "흔한 오류", "—", e["cue"]),
    ]


CSS = """
@font-face { font-family:"Pretendard"; src:url("fonts/Pretendard-Regular.woff2") format("woff2");
  font-weight:400; font-display:swap; }
@font-face { font-family:"Pretendard"; src:url("fonts/Pretendard-SemiBold.woff2") format("woff2");
  font-weight:600; font-display:swap; }
@font-face { font-family:"Pretendard"; src:url("fonts/Pretendard-ExtraBold.woff2") format("woff2");
  font-weight:800; font-display:swap; }
:root{
  --ground:#FFFFFF; --panel:#FFFFFF; --panel-2:#EDF3FF; --ground-2:#F3F7FF;
  --rule:#DEE7F5; --rule-2:#C7D6EE;
  --ink:#0A1730; --ink-2:#3D4A60; --ink-3:#5F6E86;
  --beam:#1668F0; --beam-2:#0B4FC0;
  --warn:#9A6100; --warn-bg:#FFF6E5;
  --stop:#CF3327; --stop-bg:#FEF2F1;
  --good:#097C42; --good-bg:#E8F6EE;
  --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;
  --sans:"Pretendard",-apple-system,"Malgun Gothic",system-ui,sans-serif;
  --shadow:0 1px 2px rgba(10,30,70,.05),0 12px 32px rgba(10,30,70,.07);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
.page{max-width:1080px;margin:0 auto;padding:0 24px 100px}
header.top{padding:72px 0 30px;
  background:radial-gradient(58% 120% at 12% 0%,rgba(90,160,255,.16),transparent 62%);
  margin:0 -24px 8px;padding-left:24px;padding-right:24px;border-radius:0 0 28px 28px}
.eyebrow{font-family:var(--mono);font-size:13px;letter-spacing:.2em;color:var(--beam);
  font-weight:600;margin:0 0 16px}
h1{margin:0;font-size:clamp(34px,5.6vw,58px);line-height:1.04;letter-spacing:-.045em;
  font-weight:800}
.lede{margin:20px 0 0;max-width:62ch;color:var(--ink-2);font-size:19px}
section{padding:52px 0 8px;border-bottom:1px solid var(--rule)}
section:last-of-type{border-bottom:0}
h2{font-family:var(--mono);font-size:12.5px;letter-spacing:.18em;color:var(--beam);
  margin:0 0 8px;font-weight:600}
h3{font-size:clamp(24px,3.4vw,34px);margin:0 0 16px;letter-spacing:-.03em;font-weight:800}
p{margin:0 0 14px;max-width:70ch;color:var(--ink-2)}
strong{color:var(--ink);font-weight:700}
code{font-family:var(--mono);font-size:.9em;background:var(--panel-2);padding:2px 7px;
  border-radius:6px;color:var(--beam-2)}
.board{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1px;
  background:var(--rule);border:1px solid var(--rule);border-radius:18px;overflow:hidden;
  margin:26px 0 0;box-shadow:var(--shadow)}
.board div{background:var(--panel);padding:20px}
.board dt{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--ink-3);
  margin:0 0 8px}
.board dd{margin:0;font-size:24px;font-weight:800;letter-spacing:-.03em}
.note{border-radius:14px;padding:16px 20px;margin:0 0 18px;max-width:74ch}
.note.warn{background:var(--warn-bg);color:var(--warn)}
.note.stop{background:var(--stop-bg);color:var(--stop)}
.note.good{background:var(--good-bg);color:var(--good)}
.ex{border:1px solid var(--rule);border-radius:20px;padding:24px;margin:0 0 18px;
  background:var(--panel);box-shadow:var(--shadow)}
.ex-head{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline}
.ex-head h4{margin:0;font-size:23px;font-weight:800;letter-spacing:-.02em}
.pill{font-size:12px;font-weight:800;padding:4px 11px;border-radius:999px;
  background:var(--panel-2);color:var(--beam-2)}
.pill.t1{background:#FFE9E7;color:var(--stop)}
.pill.t2{background:var(--warn-bg);color:var(--warn)}
.pill.t3{background:var(--panel-2);color:var(--beam-2)}
.meta{margin:12px 0 0;font-size:14.5px;color:var(--ink-3)}
.meta b{color:var(--ink-2)}
.why{margin:14px 0 0;font-size:15.5px;color:var(--ink-2);background:var(--ground-2);
  padding:14px 16px;border-radius:12px}
.frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;
  margin:16px 0 0}
.frame{border:1px solid var(--rule);border-radius:14px;padding:14px;background:var(--ground-2)}
.frame.wrong{background:var(--stop-bg);border-color:rgba(207,51,39,.25)}
.frame .fn{font-family:var(--mono);font-size:11.5px;color:var(--beam-2);word-break:break-all}
.frame .ft{font-size:15px;font-weight:800;margin:6px 0 2px}
.frame .fa{font-size:26px;font-weight:800;letter-spacing:-.03em;color:var(--beam);
  font-variant-numeric:tabular-nums}
.frame.wrong .fa{color:var(--stop)}
.frame .fd{font-size:13px;color:var(--ink-3);line-height:1.55;margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:16px;margin:8px 0 20px}
th,td{text-align:left;padding:13px 16px 13px 0;border-bottom:1px solid var(--rule);
  vertical-align:top;color:var(--ink-2)}
th{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--ink-3);
  font-weight:600}
td:first-child{color:var(--ink);font-weight:700;white-space:nowrap}
ol,ul{max-width:70ch;color:var(--ink-2)}
li{margin-bottom:8px}
footer{padding-top:36px;font-size:14px;color:var(--ink-3);font-family:var(--mono)}
"""


def card(e):
    t = tier(e["id"])
    view, why_view = VIEW.get(e["joint"], ("정면", ""))
    fs = frames(e)

    frames_html = "".join(
        '<div class="frame{cls}">'
        '<div class="fn">{eid}_{code}.png</div>'
        '<div class="ft">{title}</div>'
        '<div class="fa">{angle}</div>'
        '<div class="fd">{desc}</div>'
        '</div>'.format(
            cls=" wrong" if code == "wrong" else "",
            eid=e["id"], code=code, title=title, angle=angle, desc=desc)
        for code, title, angle, desc in fs)

    return """
<div class="ex">
  <div class="ex-head">
    <h4>{name}</h4>
    <span class="pill t{tier}">{tier}순위</span>
    <span class="pill">{area}</span>
    <span class="pill">{tool}</span>
  </div>
  <div class="meta">
    <b>파일 접두어</b> <code>{eid}</code> ·
    <b>분량</b> {dose} ·
    <b>그릴 각도</b> {view} ·
    <b>강조할 관절</b> {joint}{sym}
  </div>
  <div class="why"><b>왜 하는 운동인가</b> — {why}<br>
    <b>동작</b> — {how}</div>
  <div class="frames">{frames}</div>
  <p style="margin:14px 0 0;font-size:14px;color:var(--ink-3)">{why_view}</p>
</div>""".format(
        name=e["name"], tier=t, area=e["area"], tool=e["tool"], eid=e["id"],
        dose=dose(e), view=view, joint=JOINT_KR.get(e["joint"], e["joint"]),
        sym="" if e["symmetry"] else " · <b>한쪽만</b> 쓰는 동작",
        why=e["why"], how=e["how"], frames=frames_html, why_view=why_view)


def main():
    groups = []
    total = 0
    images = 0
    for path, label in SOURCES:
        items = parse(path)
        assert items, "%s 에서 운동을 하나도 못 읽었다" % path
        groups.append((label, items))
        total += len(items)
        images += sum(len(frames(e)) for e in items)

    by_tier = {1: 0, 2: 0, 3: 0}
    for _, items in groups:
        for e in items:
            by_tier[tier(e['id'])] += 1

    body = []
    for label, items in groups:
        items = sorted(items, key=lambda e: (tier(e["id"]), e["area"]))
        body.append(
            '<section><h2>{n}가지</h2><h3>{label}</h3>{cards}</section>'.format(
                n=len(items), label=label,
                cards="".join(card(e) for e in items)))

    html = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>운동 일러스트 작업 지시서 — 엘리트 루틴 케어</title>
<style>{css}</style></head><body>
<div class="page">

<header class="top">
  <p class="eyebrow">일러스트 작업 지시서</p>
  <h1>운동 {total}가지,<br>그림 {images}장</h1>
  <p class="lede">
    앱이 카메라로 자세를 보며 횟수를 셉니다. 지금은 막대 도형이 대신
    움직이고 있는데, 도구를 어떻게 잡는지·손 모양이 어떤지까지는
    도형으로 보여 줄 수 없습니다. 그 자리를 채울 그림입니다.
  </p>
  <div class="board">
    <div><dt>운동</dt><dd>{total}가지</dd></div>
    <div><dt>그림</dt><dd>{images}장</dd></div>
    <div><dt>1순위</dt><dd>{t1}가지</dd></div>
    <div><dt>2순위</dt><dd>{t2}가지</dd></div>
    <div><dt>3순위</dt><dd>{t3}가지</dd></div>
  </div>
</header>

<section>
  <h2>먼저 읽어 주세요</h2>
  <h3>각도가 이 일의 전부입니다</h3>
  <p>
    보통의 운동 일러스트와 다른 점이 하나 있습니다. 이 그림들은 <strong>앱이
    실제로 재는 각도와 같아야</strong> 합니다. 앱은 카메라로 관절 각도를
    재서, 정해진 각도까지 와야 한 개로 셉니다. 그림이 165도로 팔을 펴는데
    앱이 150도를 정점으로 세면, 아이는 그림대로 했는데 숫자가 안 올라갑니다.
  </p>
  <p>
    그래서 각 그림마다 <strong>몇 도인지</strong>를 적어 두었습니다. 그
    숫자에 맞춰 주세요. ±5도까지는 괜찮습니다.
  </p>

  <div class="note warn">
    <strong>각도를 재는 법</strong> — 관절을 가운데 두고 이어진 두 뼈가
    이루는 각입니다. 예를 들어 팔꿈치 각도는 <b>어깨—팔꿈치—손목</b> 세 점이
    이루는 각이고, 팔을 다 폈을 때가 180도에 가깝습니다. 각 운동의
    ‘강조할 관절’ 칸에 어느 세 점인지 적어 두었습니다.
  </div>

  <h3 style="margin-top:40px">그림 규격</h3>
  <table>
    <tr><th>항목</th><th>내용</th></tr>
    <tr><td>크기</td><td>1200 × 1200 px, 정사각. 앱에서 최대 320px로 줄여 씁니다.</td></tr>
    <tr><td>형식</td><td>PNG, <strong>배경 투명</strong>. 앱 테마가 7가지라
      배경을 칠하면 어느 테마에선가 튑니다.</td></tr>
    <tr><td>여백</td><td>인물이 캔버스의 80% 안에 들어오게. 사방 10% 는 비워 주세요.</td></tr>
    <tr><td>선</td><td>굵기 일정한 라인 아트 + 단색 면. 그라데이션·질감은 빼 주세요.
      작게 줄이면 지저분해집니다.</td></tr>
    <tr><td>색</td><td>인물은 <code>#3D4A60</code> 계열 한 가지 톤.
      <strong>움직이는 관절과 그 관절이 잇는 두 뼈만</strong>
      <code>#1668F0</code> 으로 강조. 도구(밴드 등)는 <code>#9A6100</code>.</td></tr>
    <tr><td>틀린 자세</td><td>같은 규격에 강조색만 <code>#CF3327</code> 으로.</td></tr>
    <tr><td>인물</td><td>초·중등 남녀 어느 쪽으로도 읽히는 중립적인 체형.
      얼굴은 이목구비 없이 단순하게. <strong>실존 인물을 닮게 그리지 마세요.</strong></td></tr>
    <tr><td>파일명</td><td>아래 각 카드에 적힌 대로. 예: <code>elbow_band_wrist_curl_peak.png</code></td></tr>
  </table>

  <div class="note stop">
    <strong>하지 말아야 할 것</strong> — 실제 선수 사진을 참고해 그대로
    옮기지 마세요(초상권). 통증을 참는 표정, 무거운 중량, 성인용 보디빌딩
    자세도 넣지 마세요. 성장기 아이가 따라 하는 그림입니다.
  </div>

  <h3 style="margin-top:40px">순위</h3>
  <p>
    <b>1순위</b>는 아픈 곳이 없을 때 모두에게 뜨는 넷입니다. 이것만 있어도
    앱이 돌아갑니다. <b>2순위</b>는 야구 아이가 가장 자주 보는 것들,
    <b>3순위</b>는 나머지 부위입니다. 순위대로 나눠 주셔도 됩니다.
  </p>
</section>

{body}

<section>
  <h2>납품</h2>
  <h3>이렇게 주시면 바로 붙입니다</h3>
  <ol>
    <li>파일명은 카드에 적힌 그대로. 폴더는 나누지 않아도 됩니다.</li>
    <li>PNG 원본과 함께, 수정용 원본(AI·SVG·PSD)도 주시면 좋겠습니다.
      각도를 조금 고칠 일이 생깁니다.</li>
    <li>1순위 넷을 먼저 주시면 그걸로 앱에 붙여 보고, 크기·강조색이
      화면에서 어떻게 보이는지 확인한 뒤 나머지를 진행하겠습니다.</li>
  </ol>
  <div class="note good">
    <strong>참고</strong> — 지금 앱에서는 막대 도형이 같은 각도로 움직이고
    있습니다. 실제 화면에서 어떻게 보이는지 보시려면 앱의 <b>루틴</b> 탭 →
    운동 카드를 열어 보세요. 그 자리에 이 그림이 들어갑니다.
  </div>
</section>

<footer>
  이 문서는 앱 소스(<code>care_exercise.dart</code>,
  <code>sport_form.dart</code>)에서 자동으로 만들어집니다.
  각도가 바뀌면 문서도 함께 바뀝니다 —
  <code>python tools/build_exercise_art_spec.py</code>
</footer>

</div></body></html>""".format(
        css=CSS, total=total, images=images,
        t1=by_tier[1], t2=by_tier[2], t3=by_tier[3],
        body="".join(body))

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)
    print("wrote", OUT)
    print("  운동 %d가지 · 그림 %d장 (1순위 %d · 2순위 %d · 3순위 %d)"
          % (total, images, by_tier[1], by_tier[2], by_tier[3]))


if __name__ == "__main__":
    main()
