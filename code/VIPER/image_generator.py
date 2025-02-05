# SAMPLE USAGE:
# python3 image_generator.py < mychars.txt my_output

import os
import sys
from PIL import Image, ImageDraw, ImageFont

width, height = 24, 24
font_size = 22
font_color = (255, 255, 255)  # 흰색 글자 (검정 배경에 대비)
font_dir = "multilingual_mixed_fonts"  # 폰트 파일 경로

# 사용자 지정 결과 저장 디렉토리
if len(sys.argv) != 2:
    print("Usage: python3 image_generator.py < mychars.txt [output_directory]")
    sys.exit(1)

output_root = sys.argv[1]  # 사용자 입력으로 받은 저장 디렉토리 이름
output_dir = os.path.join(output_root, "images")  # 이미지 저장 경로
missing_chars_file = os.path.join(output_root, "missing_chars.txt")  # 지원되지 않는 문자를 기록할 파일

# 결과 저장 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 폰트 파일 불러오기
font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith((".ttf", ".otf"))]
if not font_files:
    raise RuntimeError(f"No font files found in directory: {font_dir}")

# 표준 입력에서 문자 읽기
for line in sys.stdin:
    unicode_text = line.strip()  # 문자 추출
    if not unicode_text:
        continue

    codepoint = ord(unicode_text)
    print(f"Processing character: {unicode_text} (U+{codepoint:X})")

    # 검정 배경의 새 이미지 생성
    im = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(im)

    # 폰트 지원 여부 확인 및 적용
    font_supported = False
    for font_path in font_files:
        try:
            unicode_font = ImageFont.truetype(font_path, font_size)
            # 테스트로 문자를 폰트에 그려봄 (지원 여부 확인)
            draw.text((2, 0), unicode_text, font=unicode_font, fill=font_color)
            font_supported = True
            break  # 지원 가능한 폰트를 찾으면 루프 종료
        except Exception:
            continue

    # 지원되지 않는 경우, missing_chars.txt에 기록
    if not font_supported:
        with open(missing_chars_file, "a", encoding="utf-8") as missing_file:
            missing_file.write(f"{unicode_text};U+{codepoint:X}\n")
        print(f"Character not supported: {unicode_text} (U+{codepoint:X})")
        continue

    # 이미지 저장
    image_path = os.path.join(output_dir, f"text-other_{codepoint}.png")
    im.save(image_path)

    print(f"Saved image: {image_path}")

print(f"Images have been saved in '{output_dir}' directory.")
print(f"Characters not supported are logged in '{missing_chars_file}'.")