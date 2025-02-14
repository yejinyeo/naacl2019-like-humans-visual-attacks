# SAMPLE USAGE:
# python3 image_generator_embedding.py < mychars.txt output_directory

# VIPER embedding 개선용.py
# glyph가 잘림 현상 없이 가운데 정렬된 버전을 default로 함 

import os
import sys
from PIL import Image, ImageDraw, ImageFont

width, height = 56, 56
font_size = int(width * 0.85)
font_color = (255, 255, 255)  # 흰색 글자 (검정 배경에 대비)
font_dir = "multilingual_mixed_fonts"  # 폰트 파일 경로

# 사용자 지정 결과 저장 디렉토리
if len(sys.argv) != 2:
    print("Usage: python3 image_generator_embedding.py < mychars.txt [output_directory]")
    sys.exit(1)

output_root = sys.argv[1]  # 사용자 입력으로 받은 저장 디렉토리 이름
output_dir = os.path.join(output_root, "images")  # 이미지 저장 경로
missing_chars_file = os.path.join(output_root, "missing_chars.txt")  # 지원되지 않는 문자를 기록할 파일
saving_chars_file = os.path.join(output_root, "saving_chars.txt")  # 지원된 문자를 기록할 파일

# 결과 저장 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 초기화: 파일 비우기
open(missing_chars_file, "w", encoding="utf-8").close()
open(saving_chars_file, "w", encoding="utf-8").close()

# 폰트 파일 불러오기
font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith((".ttf", ".otf"))]
if not font_files:
    raise RuntimeError(f"No font files found in directory: {font_dir}")

# 지원 여부 확인 함수
def is_char_supported(font_path, char):
    """
    특정 font에서 문자가 지원되는지 확인
    :param font_path: 폰트 경로
    :param char: 확인할 문자
    :return: 지원 여부 (True/False)
    """
    txt_path = f"{os.path.splitext(font_path)[0]}.txt"  # 폰트와 동일한 이름의 .txt 파일
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Glyph file not found: {txt_path}")
    
    with open(txt_path, "r", encoding="utf-8") as file:
        glyphs = file.read()
    
    return char in glyphs

# 표준 입력에서 문자 읽기
for line in sys.stdin:
    unicode_text = line.strip()  # 문자 추출
    if not unicode_text:
        continue

    codepoint = ord(unicode_text)
    print(f"Processing character: {unicode_text} (U+{codepoint:X})")

    # 폰트 지원 여부 확인 및 선택
    selected_font = None
    for font_path in font_files:
        if is_char_supported(font_path, unicode_text):
            selected_font = font_path
            break

    # 지원되지 않는 경우, missing_chars.txt에 기록
    if not selected_font:
        with open(missing_chars_file, "a", encoding="utf-8") as missing_file:
            missing_file.write(f"{unicode_text} U+{codepoint:X}\n")
        print(f"Character not supported: {unicode_text} (U+{codepoint:X})")
        continue

    # 이미지 생성
    im = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(im)
    try:
        # 선택된 폰트 로드
        unicode_font = ImageFont.truetype(selected_font, font_size)

        # 텍스트 크기 계산 (textbbox 사용)
        bbox = draw.textbbox((0, 0), unicode_text, font=unicode_font) # bbox = (left, top, right, bottom)
        text_width = bbox[2] - bbox[0]  # 텍스트의 폭
        text_height = bbox[3] - bbox[1]  # 텍스트의 높이

        # 폰트의 ascent와 descent 가져오기
        ascent, descent = unicode_font.getmetrics()

        # 중앙 정렬을 위한 오프셋 계산
        x_offset = (width - text_width) // 2
        bbox_center_y = (bbox[1] + bbox[3]) / 2
        image_center_y = height / 2
        y_offset = int(image_center_y - bbox_center_y)

        # 텍스트를 이미지 중앙에 배치
        draw.text((x_offset, y_offset), unicode_text, font=unicode_font, fill=font_color)

        # 이미지 저장
        image_name = f"text-other_{codepoint:X}.png"
        image_path = os.path.join(output_dir, image_name)
        im.save(image_path)
        print(f"Saved image: {image_path}")

        # saving_chars.txt에 기록
        with open(saving_chars_file, "a", encoding="utf-8") as saving_file:
            saving_file.write(f"{unicode_text} U+{codepoint:X} {image_name}\n")

    except Exception as e:
        print(f"Error rendering {unicode_text} with {selected_font}: {e}")
        with open(missing_chars_file, "a", encoding="utf-8") as missing_file:
            missing_file.write(f"{unicode_text} U+{codepoint:X} Error: {str(e)}\n")

# 총 문자 개수 계산
def count_lines(file_path):
    """파일의 줄 수를 계산"""
    if not os.path.exists(file_path):
        return 0
    with open(file_path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

missing_count = count_lines(missing_chars_file)
saving_count = count_lines(saving_chars_file)

# 결과 출력
print(f"Images have been saved in '{output_dir}' directory.")
print(f"Characters not supported are logged in '{missing_chars_file}' ({missing_count} characters).")
print(f"Characters supported and saved are logged in '{saving_chars_file}' ({saving_count} characters).")
