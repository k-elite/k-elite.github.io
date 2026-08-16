# tools

사이트와 소개 영상을 만드는 생성기. 저장소 안에서 그대로 돌아갑니다.

```
pip install pillow numpy imageio-ffmpeg
```

`imageio-ffmpeg` 가 ffmpeg 실행 파일을 함께 받아 오므로 시스템에 따로 설치할
필요가 없습니다. 글꼴은 윈도우의 맑은 고딕을 씁니다.

## 앱 화면을 바꿨을 때

앱 UI가 바뀌면 화면을 다시 찍어 `tools/shots/` 의 PNG를 덮어씁니다.
파일명은 그대로 두세요 — 생성기가 이름으로 찾습니다.

```
# 갤럭시 기준. 상태바·제스처바는 생성기가 알아서 잘라냅니다.
adb exec-out screencap -p > tools/shots/01_home_top.png
```

| 파일 | 쓰이는 곳 |
| --- | --- |
| `01_home_top.png` | 사이트 히어로 |
| `05_home_bottom.png` | 사이트 화면 모음 |
| `08_aicoach.png` | 사이트 화면 모음 |
| `16_portfolio_pdf.png` | 사이트 · **영상 4번 장면** |
| `30_parent_today.png` | 사이트 · **영상 5번 장면** |

## 다시 만들기

순서대로 돌립니다.

```
python tools/prep_shots.py          # PNG → 문서용 JPEG + base64 (shots_web/)
python tools/make_video.py          # intro.mp4 + tools/video_b64.txt
python tools/build_site_landing.py  # index.html
```

영상을 안 바꿨으면 `make_video.py` 는 건너뛰어도 됩니다 —
`tools/video_b64.txt` 가 이미 있으면 사이트가 그걸 씁니다.

## 파일

| 파일 | 하는 일 |
| --- | --- |
| `site_head.py` | 사이트 CSS. 팔레트와 모션이 여기 있습니다 |
| `build_site_landing.py` | 사이트 본문·차트를 그려 `index.html` 을 씁니다 |
| `make_video.py` | 소개 영상 8장면을 프레임 단위로 그려 MP4로 인코딩합니다 |
| `prep_shots.py` | 화면 PNG를 문서용 크기로 줄이고 base64로 바꿉니다 |
| `shots/` | 실제 기기에서 찍은 앱 화면 |
| `video_b64.txt` | 사이트에 박아 넣을 영상 (생성물) |

## 지키는 것

- **앱 화면은 실제로 찍은 것만 씁니다.** 없는 화면을 그려 넣지 않습니다.
  소개 자료에 실물과 다른 화면이 나오면 설치한 사람이 속았다고 느낍니다.
- **차트 값은 앱이 실제로 쓰는 규칙 그대로입니다.** 훈련 부하 구간(0.8~1.3
  안전 / 1.5 초과 위험), 나이별 투구 수 상한이 그렇습니다.
- **체결되지 않은 제휴는 만들지 않습니다.** 제휴 자리는 '협의 중' 상태로
  비워 두고, 실제 자문이 시작되면 그때 채웁니다.
