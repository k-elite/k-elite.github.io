# -*- coding: utf-8 -*-
"""일러스트 작업 지시서 — 캐릭터를 움직이려면 어떤 그림이 더 필요한가."""
import base64
import io
import os

from PIL import Image

SRC = r"C:\github\k-elite\tools\manga\elite3.png"
OUT = r"C:\github\k-elite\pose_spec.html"

COLS = [(14, 382), (394, 762), (774, 1142), (1154, 1522)]
ROWS = [(66, 458), (476, 878)]


def panels():
    im = Image.open(SRC).convert("RGB")
    out = []
    for r0, r1 in ROWS:
        for c0, c1 in COLS:
            p = im.crop((c0, r0, c1, r1))
            w = 460
            p = p.resize((w, int(p.height * w / p.width)), Image.LANCZOS)
            buf = io.BytesIO()
            p.save(buf, "JPEG", quality=80, optimize=True)
            out.append("data:image/jpeg;base64,"
                       + base64.b64encode(buf.getvalue()).decode())
    return out


P = panels()

# (컷번호, 제목, 우선순위, [ (포즈코드, 무엇을 바꾸나, 왜) ])
JOBS = [
    (2, "부상 예방 — 튜빙 운동", 1, [
        ("p2_a", "밴드를 가슴 앞으로 모은 상태 (팔 굽힘)",
         "당기기 시작. 지금 그림은 다 편 상태뿐이라 움직임의 출발점이 없습니다."),
        ("p2_b", "중간 — 팔이 절반쯤 펴진 상태",
         "두 장만 오가면 뚝뚝 끊깁니다. 가운데 한 장이 있으면 부드럽습니다."),
        ("p2_c", "지금 그림 그대로 (팔 완전히 편 상태)",
         "이미 있습니다. 같은 규격으로 다시 주시면 맞춰 쓰기 쉽습니다."),
    ], "앞쪽 큰 소년과 <b>폰 화면 속 소년</b> 둘 다 필요합니다. "
       "둘이 같은 동작을 해야 'AI가 내 동작을 본다'가 성립합니다."),

    (1, "종목 선택 — 정보 입력", 2, [
        ("p1_a", "지금 그림 그대로 (검지를 세운 상태)", "말하는 자세."),
        ("p1_b", "그 손가락으로 폰 화면을 누르는 순간",
         "'다음'을 누르는 장면이 됩니다. 지금은 누르는 손이 없어 "
         "화면에 동그라미만 띄우고 있습니다."),
    ], "손가락 끝이 폰 화면 안(오른쪽 폰의 '다음' 버튼 근처)에 닿아야 합니다."),

    (3, "루틴 습관화 — 화이팅", 2, [
        ("p3_a", "지금 그림 그대로 (주먹이 가슴 옆)", ""),
        ("p3_b", "주먹을 위로 올린 상태",
         "알람을 켜고 '좋아, 하자' 하는 동작. 두 장이면 충분합니다."),
    ], ""),

    (4, "훈련 기록 — 필기", 2, [
        ("p4_a", "지금 그림 그대로 (펜이 공책 왼쪽)", ""),
        ("p4_b", "펜이 공책 오른쪽으로 이동한 상태",
         "손목과 펜만 움직이면 됩니다. 몸·얼굴은 그대로. "
         "두 장을 오가면 글씨 쓰는 것처럼 보입니다."),
    ], "고개도 아주 살짝(2~3도) 따라 움직이면 더 자연스럽습니다."),

    (8, "종합 리포트 — 함께 보기", 3, [
        ("p8_a", "지금 그림 그대로", ""),
        ("p8_b", "소년이 태블릿 화면을 손가락으로 가리키는 자세",
         "'이거 보세요' 하는 동작. 엄마 얼굴은 그대로 둬도 됩니다."),
    ], ""),

    (5, "분석 리포트 — 화면 넘기기", 3, [
        ("p5_a", "지금 그림 그대로", ""),
        ("p5_b", "엄지를 폰 화면 위로 올려 쓸어내리는 자세",
         "스크롤 동작. 우선순위는 낮습니다."),
    ], ""),

    (7, "학부모 — 화면 넘기기", 3, [
        ("p7_a", "지금 그림 그대로", ""),
        ("p7_b", "엄지로 화면을 쓸어내리는 자세", "위와 같습니다."),
    ], ""),

    (6, "성장 기록 — 시선", 3, [
        ("p6_a", "지금 그림 그대로 (옆모습)", ""),
        ("p6_b", "고개를 그래프 쪽으로 조금 더 돌린 모습",
         "그래프가 그려질 때 시선이 따라가면 살아납니다."),
    ], ""),
]

BLINK = [
    (1, "소년 (모자, 정면)"),
    (2, "앞쪽 소년 (옆모습) · 폰 속 소년 (정면)"),
    (3, "소년 (정면)"),
    (4, "소년 (살짝 아래를 봄)"),
    (5, "소년 (정면)"),
    (6, "소년 (옆모습)"),
    (7, "어머니 (정면)"),
    (8, "소년 · 어머니 (둘 다)"),
]


def job_html():
    out = []
    for num, title, pri, poses, note in JOBS:
        rows = "".join(
            f'<tr><td><code>{code}</code></td><td>{what}</td>'
            f'<td class="why">{why or "—"}</td></tr>'
            for code, what, why in poses)
        out.append(f'''
<article class="job pri{pri}">
  <div class="shot"><img src="{P[num - 1]}" alt="{num}번 컷"></div>
  <div class="body">
    <div class="head">
      <span class="num">{num}번 컷</span>
      <span class="tag t{pri}">{["", "1순위 · 꼭 필요", "2순위 · 있으면 좋음", "3순위 · 여유 있으면"][pri]}</span>
    </div>
    <h3>{title}</h3>
    <table><thead><tr><th>파일명</th><th>포즈</th><th>왜 필요한가</th></tr></thead>
      <tbody>{rows}</tbody></table>
    {f'<p class="note">{note}</p>' if note else ""}
  </div>
</article>''')
    return "".join(out)


def blink_html():
    return "".join(
        f'<tr><td><code>p{n}_blink</code></td><td>{n}번 컷</td><td>{who}</td></tr>'
        for n, who in BLINK)


HTML = f"""<title>만화 캐릭터 포즈 의뢰서</title>
<style>
:root {{
  --paper: #FBFAF7; --card: #FFFFFF; --alt: #F2F4F8;
  --line: #DCE1E9; --ink: #16202E; --ink2: #46536A; --ink3: #7A879C;
  --brand: #17408B; --gold: #C98A08; --stop: #B3261E;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Malgun Gothic",
    "Apple SD Gothic Neo", system-ui, sans-serif;
  --mono: ui-monospace, "Cascadia Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #0B1017; --card: #131B26; --alt: #19222F;
    --line: #26313F; --ink: #EEF3F9; --ink2: #B7C3D3; --ink3: #7F8DA1;
    --brand: #7BA7F5; --gold: #E8B34A; --stop: #FF9A90;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #0B1017; --card: #131B26; --alt: #19222F;
  --line: #26313F; --ink: #EEF3F9; --ink2: #B7C3D3; --ink3: #7F8DA1;
  --brand: #7BA7F5; --gold: #E8B34A; --stop: #FF9A90;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--paper); color: var(--ink2);
  font-family: var(--sans); font-size: 16px; line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}
.doc {{ max-width: 940px; margin: 0 auto; padding: 0 22px 90px; }}
header {{ padding: 56px 0 24px; border-bottom: 3px solid var(--ink); }}
.eyebrow {{
  font-family: var(--mono); font-size: 11.5px; letter-spacing: .18em;
  text-transform: uppercase; color: var(--ink3); margin: 0 0 12px;
}}
h1 {{
  margin: 0; font-size: clamp(28px, 5vw, 42px); line-height: 1.1;
  letter-spacing: -.03em; font-weight: 850; color: var(--ink);
}}
.lede {{ margin: 14px 0 0; max-width: 62ch; font-size: 17.5px; }}
h2 {{
  font-size: clamp(21px, 3.4vw, 27px); margin: 0 0 12px; color: var(--ink);
  letter-spacing: -.02em; font-weight: 800;
}}
h3 {{ font-size: 19px; margin: 4px 0 12px; color: var(--ink); font-weight: 800; }}
section {{ padding: 44px 0 0; }}
p {{ margin: 0 0 14px; max-width: 66ch; }}
strong {{ color: var(--ink); font-weight: 700; }}
code {{
  font-family: var(--mono); font-size: .86em; background: var(--alt);
  padding: 2px 7px; border-radius: 5px; color: var(--ink); white-space: nowrap;
}}
ol, ul {{ margin: 0 0 16px; padding-left: 22px; }}
li {{ margin-bottom: 9px; max-width: 66ch; }}

.callout {{
  border-radius: 14px; padding: 20px 22px; margin: 0 0 22px;
  background: var(--card); border: 1px solid var(--line);
  border-left: 5px solid var(--brand);
}}
.callout.warn {{ border-left-color: var(--gold); }}
.callout h3 {{ margin-top: 0; }}
.callout p:last-child {{ margin-bottom: 0; }}

.job {{
  display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 24px;
  background: var(--card); border: 1px solid var(--line);
  border-radius: 16px; padding: 22px; margin: 0 0 18px;
}}
@media (max-width: 760px) {{ .job {{ grid-template-columns: 1fr; }} }}
.job .shot img {{
  width: 100%; height: auto; display: block; border-radius: 10px;
  border: 1px solid var(--line);
}}
.head {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.num {{
  font-family: var(--mono); font-size: 12px; letter-spacing: .1em;
  color: var(--ink3);
}}
.tag {{
  font-size: 11.5px; font-weight: 800; padding: 3px 10px; border-radius: 999px;
  font-family: var(--mono); letter-spacing: .04em;
}}
.t1 {{ background: rgba(179,38,30,.12); color: var(--stop); }}
.t2 {{ background: rgba(201,138,8,.14); color: var(--gold); }}
.t3 {{ background: var(--alt); color: var(--ink3); }}

table {{ border-collapse: collapse; width: 100%; font-size: 14.5px; }}
th, td {{
  text-align: left; padding: 10px 12px 10px 0; vertical-align: top;
  border-bottom: 1px solid var(--line);
}}
thead th {{
  font-family: var(--mono); font-size: 10.5px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--ink3); font-weight: 700;
}}
tbody tr:last-child td {{ border-bottom: 0; }}
td .why, .why {{ color: var(--ink3); }}
.note {{
  margin: 12px 0 0; padding: 12px 14px; background: var(--alt);
  border-radius: 10px; font-size: 14px; color: var(--ink2); max-width: none;
}}

.check {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 22px; }}
.check li {{ list-style: none; position: relative; padding-left: 30px; }}
.check ul {{ padding-left: 0; margin-bottom: 0; }}
.check li::before {{
  content: ""; position: absolute; left: 0; top: 6px;
  width: 17px; height: 17px; border: 2px solid var(--ink3); border-radius: 4px;
}}
footer {{
  margin-top: 56px; padding-top: 22px; border-top: 1px solid var(--line);
  font-size: 13px; color: var(--ink3); font-family: var(--mono);
}}
@media print {{
  :root {{ --paper: #fff; --card: #fff; --alt: #F2F4F8; --ink: #16202E; }}
  .job {{ break-inside: avoid; }}
  body {{ font-size: 11pt; }}
}}
:focus-visible {{ outline: 2px solid var(--brand); outline-offset: 3px; }}
</style>

<div class="doc">
<header>
  <p class="eyebrow">일러스트 작업 의뢰 · 엘리트 루틴 케어</p>
  <h1>만화 캐릭터 포즈 추가 요청</h1>
  <p class="lede">
    이미 그려 주신 8컷 인포그래픽으로 사용법 영상을 만들었습니다.
    <strong>캐릭터가 실제로 움직이게</strong> 하려면 포즈 그림이 몇 장 더
    필요합니다. 무엇이 왜 필요한지 컷별로 적었습니다.
  </p>
</header>

<section>
  <h2>왜 추가 그림이 필요한가</h2>
  <p>
    지금 있는 것은 <strong>완성된 그림 한 장</strong>입니다. 여기서 팔만
    오려내 움직이면 팔이 있던 자리에 <strong>구멍</strong>이 생깁니다.
    뒤에 무엇이 있었는지 그림에 없기 때문입니다.
  </p>
  <p>
    그래서 <strong>같은 컷을 포즈만 바꿔 2~3장</strong> 그려 주시면 됩니다.
    그걸 번갈아 보여 주면 움직임이 됩니다. 애니메이션 경험이 없어도
    되는 방식으로 골랐습니다.
  </p>

  <div class="callout">
    <h3>전달 방법 — 이것만 지켜 주세요</h3>
    <ol>
      <li><strong>캔버스 크기와 캐릭터 위치를 똑같이.</strong> 같은 파일을
        복사해서 포즈만 고쳐 주시는 게 가장 확실합니다. 한 장이라도 캐릭터가
        옆으로 밀리면 화면이 덜컹거립니다.</li>
      <li><strong>배경·말풍선·폰 화면 UI는 그대로 두세요.</strong> 바꾸는
        것은 캐릭터 포즈뿐입니다.</li>
      <li><strong>PNG, 컷 하나당 최소 1200×1280px.</strong> 지금 받은
        파일은 8컷이 한 장에 들어 있어 컷당 368×392입니다. 영상에서 키우면
        흐려집니다. <strong>컷별로 크게 주시면 화질이 크게 좋아집니다.</strong></li>
      <li><strong>파일명은 아래 표의 코드 그대로.</strong>
        <code>p2_a.png</code> 처럼요. 이름이 다르면 제가 순서를 잘못 붙입니다.</li>
    </ol>
  </div>

  <div class="callout warn">
    <h3>레이어 파일이 있으시면 더 좋습니다</h3>
    <p>
      원본이 PSD·AI 같은 레이어 파일이라면, <strong>캐릭터 레이어와 배경
      레이어를 나눠서</strong> 주셔도 됩니다(캐릭터는 투명 배경 PNG, 배경은
      캐릭터를 지운 상태로 한 장). 그러면 포즈를 여러 장 그리지 않아도
      제가 팔 각도를 조금씩 움직일 수 있습니다.
      <strong>둘 중 편한 쪽으로 주시면 됩니다.</strong>
    </p>
  </div>
</section>

<section>
  <h2>컷별 요청</h2>
  <p>
    우선순위를 붙였습니다. <strong>1순위만 해 주셔도 영상이 확 달라집니다.</strong>
    2·3순위는 여유가 있을 때만 부탁드립니다.
  </p>
  {job_html()}
</section>

<section>
  <h2>눈 깜빡임 — 가장 적은 품으로 가장 큰 차이</h2>
  <p>
    포즈 전체를 다시 그리지 않아도 됩니다. <strong>눈 감은 얼굴만</strong>
    투명 배경 PNG로 주시면, 제가 몇 초에 한 번씩 얹어 깜빡이게 만듭니다.
    캐릭터가 살아 있는 느낌이 확 달라집니다.
  </p>
  <p>
    얼굴 부분만 잘라 주셔도 되고, 컷 전체에서 눈만 감은 버전을 주셔도
    됩니다. <strong>얼굴만 주실 경우 원본 컷에서 어느 위치인지</strong>
    (좌표 또는 같은 캔버스에 얹은 상태) 알려 주세요.
  </p>
  <table>
    <thead><tr><th>파일명</th><th>컷</th><th>대상</th></tr></thead>
    <tbody>{blink_html()}</tbody>
  </table>
</section>

<section>
  <h2>정리 — 최소 / 권장</h2>
  <div class="callout">
    <h3>최소로 하신다면 (그림 5장)</h3>
    <p>
      <code>p2_a</code> <code>p2_b</code> <code>p2_c</code> — 튜빙 동작 3장<br>
      <code>p2_blink</code> <code>p3_blink</code> — 눈 깜빡임 2장
    </p>
    <p style="margin-top:10px">
      튜빙 컷은 이 앱이 무엇을 하는지 가장 잘 보여 주는 장면이라
      여기부터 부탁드립니다.
    </p>
  </div>
  <div class="callout">
    <h3>권장 (그림 15장 안팎)</h3>
    <p>
      1순위 3장 + 2순위 6장 + 눈 깜빡임 8장.<br>
      여기까지면 8컷 전부에서 캐릭터가 움직입니다.
    </p>
  </div>
</section>

<section>
  <h2>보내실 때 확인</h2>
  <div class="check">
    <ul>
      <li>모든 파일의 <strong>캔버스 크기가 같은가</strong></li>
      <li>포즈만 다르고 <strong>배경·말풍선·폰 UI는 그대로인가</strong></li>
      <li>파일명이 <code>p2_a.png</code> 형식인가</li>
      <li>컷 하나당 <strong>1200×1280px 이상</strong>인가</li>
      <li>눈 감은 그림은 <strong>위치를 알 수 있게</strong> 되어 있는가</li>
      <li>2번 컷은 <strong>앞쪽 소년과 폰 속 소년 둘 다</strong> 그렸는가</li>
    </ul>
  </div>
</section>

<footer>엘리트 루틴 케어 · 만화 포즈 의뢰서 · 문의 64723b@gmail.com</footer>
</div>
"""

io.open(OUT, "w", encoding="utf-8", newline="\n").write(HTML)
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
