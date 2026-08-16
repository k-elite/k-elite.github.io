# -*- coding: utf-8 -*-
"""화면 사진에서 개인정보를 데모 값으로 바꾼다.

## 왜 필요한가

앱 화면에는 실제로 쓰는 계정의 이름·생년월일·소속 학교가 그대로 찍힌다.
소개 사이트와 영상은 공개되므로 그대로 쓸 수 없다. 선수는 대부분
미성년자다.

**화면 자체는 진짜다.** 사람을 가리키는 글자만 데모 값으로 덮는다.
없는 기능을 그려 넣거나 성적을 부풀리지 않는다.

## 데모 값

    이름 이엘리트 · 소속 엘리트초등학교 · 생년월일 2015-01-01

## 실행

    python tools/mask_pii.py

`shots_raw/` 의 원본을 읽어 `shots/` 에 덮어쓴다. 원본에는 실제 개인정보가
들어 있으므로 저장소에 넣지 않는다(.gitignore).

## 좌표를 다시 잡아야 할 때

앱 UI가 바뀌면 글자 위치가 달라진다. 원본을 잘라 보며 상자를 맞춘다.
글자가 상자보다 넓으면 실행할 때 경고가 찍힌다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "shots_raw")
OUT = os.path.join(HERE, "shots")

FONT_DIR = r"C:\Windows\Fonts"
_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(
            os.path.join(FONT_DIR, "malgunbd.ttf" if bold else "malgun.ttf"),
            size)
    return _fonts[key]


PAPER = (252, 251, 248)   # 리포트 종이. 테마와 무관하게 고정인 색이다.
CARD = (18, 34, 74)       # 실적 카드 남색
DARK = (16, 23, 36)       # 앱 배경(루카 나이트)
WHITE = (255, 255, 255)

# 덮어쓸 자리.
#   (상자, 배경색, 조각들, 크기, 글자색, 베이스라인 y)
# 조각들은 (글자, 굵게) 목록 — 굵은 라벨과 보통 본문을 한 줄에 이어 그린다.
JOBS = {
    "16_portfolio_pdf": [
        ((104, 548, 620, 596), WHITE, [("이엘리트  야구", True)], 40,
         (20, 33, 61), 588),
        ((258, 652, 620, 686), WHITE, [("2015-01-01", False)], 24,
         (25, 30, 40), 680),
        ((258, 700, 620, 734), WHITE, [("엘리트초등학교", False)], 24,
         (25, 30, 40), 728),
    ],
    "21_result_card": [
        # 아래 획이 상자 밖으로 삐져나오므로 넉넉히 잡는다.
        ((120, 868, 720, 974), CARD, [("이엘리트 선수", True)], 62,
         WHITE, 955),
        ((120, 986, 810, 1050), CARD,
         [("엘리트초등학교 · 야구 · 투수, 외야수", False)], 30,
         (168, 181, 214), 1034),
    ],
    "06_calendar": [
        ((110, 425, 960, 495), DARK,
         [("이엘리트 선수, 이번 주 목표까지 3일 남았어요!", False)], 30,
         (150, 164, 186), 478),
    ],
    "19_report_detail": [
        ((110, 582, 460, 648), PAPER, [("선수: 이엘리트", True)], 44,
         (20, 23, 28), 634),
        ((110, 1068, 930, 1136), PAPER,
         [("선수명: ", True), ("이엘리트 선수 (우투우타 / 주 포지션:", False)],
         40, (20, 23, 28), 1122),
    ],
    "08_aicoach": [
        # 다음 줄이 "라 더 높이…" 로 이어지므로 끝을 '아니' 로 맞춘다.
        ((205, 1330, 1000, 1394), DARK,
         [("이엘리트야, 쉬어가는 단계는 후퇴가 아니", False)], 40,
         (200, 208, 220), 1382),
    ],
}


def apply(name, jobs):
    src = os.path.join(RAW, name + ".png")
    if not os.path.exists(src):
        print(f"  skip (no raw): {name}")
        return

    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for box, bg, parts, size, color, baseline in jobs:
        d.rectangle(box, fill=bg)
        x = box[0] + 4
        for s, bold in parts:
            f = font(size, bold)
            d.text((x, baseline), s, font=f, fill=color, anchor="ls")
            x += d.textlength(s, font=f)
        # 넘치면 원래 글자가 잘려 보인다. 조용히 지나가지 않게 알린다.
        if x > box[2] + 2:
            print(f"    ! {name}: text overflows box by {int(x - box[2])}px")

    im.save(os.path.join(OUT, name + ".png"))
    print(f"  {name}: {len(jobs)} replaced")


def main():
    os.makedirs(OUT, exist_ok=True)
    print("demo: 이엘리트 / 엘리트초등학교 / 2015-01-01"
          .encode("ascii", "backslashreplace").decode())
    for name, jobs in JOBS.items():
        apply(name, jobs)


if __name__ == "__main__":
    main()
