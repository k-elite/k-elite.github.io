# k-elite

엘리트 루틴 케어 소개 사이트.

주소: https://k-elite.github.io

`index.html` 한 장이 전부입니다. 외부 요청이 막힌 환경에서도 그대로 뜨도록
앱 화면을 base64 로 박아 넣었습니다.

다시 만들려면 `tools/build_site_landing.py` 를 돌립니다.

## 다시 만들기

생성기는 `tools/` 에 있습니다. 자세한 건 [tools/README.md](tools/README.md).

```
pip install pillow numpy imageio-ffmpeg
python tools/make_video.py          # intro.mp4
python tools/build_site_landing.py  # index.html
```
