# -*- coding: utf-8 -*-
"""찍은 화면을 문서에 넣을 수 있게 다듬는다.

- 상단 상태바(시계·배터리)와 하단 내비게이션 바를 잘라낸다. 설명서에
  필요한 것은 앱 화면이지 기기 상태가 아니다.
- 문서 폭에 맞게 줄이고 JPEG 로 저장한다. 원본 1080x2400 을 그대로 넣으면
  한 장에 1MB 가 넘어 문서가 열리지 않는다.
- base64 로 박아 넣어 파일 하나로 끝나게 한다.
"""
import base64
import io as _io
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "shots")
OUT = os.path.join(HERE, "shots_web")

# 1080x2400 기준. 상태바 72px, 하단 제스처바 96px.
TOP_CROP = 72
BOTTOM_CROP = 96
WIDTH = 420   # 문서에서 실제로 보이는 최대 폭의 2배(레티나)
QUALITY = 74


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {}

    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".png"):
            continue
        im = Image.open(os.path.join(SRC, name)).convert("RGB")
        im = im.crop((0, TOP_CROP, im.width, im.height - BOTTOM_CROP))
        h = int(im.height * WIDTH / im.width)
        im = im.resize((WIDTH, h), Image.LANCZOS)

        buf = _io.BytesIO()
        im.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        data = buf.getvalue()

        key = name[:-4]
        index[key] = "data:image/jpeg;base64," + base64.b64encode(data).decode()
        im.save(os.path.join(OUT, key + ".jpg"), "JPEG", quality=QUALITY)
        print(f"  {key:26} {len(data)//1024:>4} KB  {im.size}")

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f)

    total = sum(len(v) for v in index.values())
    print(f"\n{len(index)}장 · base64 합계 {total//1024} KB")


if __name__ == "__main__":
    main()
