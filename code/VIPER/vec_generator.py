# SAMPLE USAGE:
# python3 vec_generator.py images_dir saving_chars.txt vec.normalized

import os
import sys
import numpy as np
from PIL import Image

def generate_vectors(image_dir, saving_chars_file, output_file):
    """
    이미지를 벡터로 변환하여 vec.normalized 파일로 저장 (Word2Vec 형식).

    :param image_dir: 이미지가 저장된 디렉토리 경로
    :param saving_chars_file: saving_chars.txt 파일 경로 (문자 정보 포함)
    :param output_file: 벡터 데이터를 저장할 파일 경로
    """
    # saving_chars.txt 읽기
    char_mapping = {}
    with open(saving_chars_file, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" ")
            if len(parts) == 3:  # unicode_text;U+codepoint;image_name
                unicode_text, _, image_name = parts
                char_mapping[image_name] = unicode_text

    image_files = [f for f in sorted(os.listdir(image_dir)) if f.endswith(".png")]
    number_of_vectors = len(image_files)
    vector_dimension = 24 * 24  # 이미지 크기 (24x24 픽셀)

    # 결과 파일 초기화 및 헤더 작성
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{number_of_vectors} {vector_dimension}\n")  # 헤더 작성

    # 이미지 파일 처리
    for image_name in image_files:
        image_path = os.path.join(image_dir, image_name)
        char = char_mapping.get(image_name)
        if not char:
            print(f"Warning: Character not found for image {image_name}. Skipping.")
            continue

        try:
            # 이미지 로드 및 그레이스케일 변환
            with Image.open(image_path) as img:
                img = img.convert("L")  # Grayscale로 변환

                # 이미지 데이터를 1D 벡터로 변환
                vector = np.array(img).flatten() / 255.0  # 0-1로 정규화

                # 벡터를 문자열로 변환
                vector_str = " ".join(map(str, vector))

                # 결과 파일에 저장 (char를 첫 필드로)
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"{char} {vector_str}\n")

        except Exception as e:
            print(f"Error processing image {image_name}: {e}")

    print(f"Vector file '{output_file}' has been created in Word2Vec format.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 vec_generator.py [images_dir] [saving_chars.txt] [output_file]")
        sys.exit(1)

    image_dir = sys.argv[1]  # 이미지 디렉토리 경로
    saving_chars_file = sys.argv[2]  # saving_chars.txt 경로
    output_file = sys.argv[3]  # 결과 파일 경로

    if not os.path.exists(image_dir):
        print(f"Error: Image directory '{image_dir}' does not exist.")
        sys.exit(1)

    if not os.path.exists(saving_chars_file):
        print(f"Error: Saving chars file '{saving_chars_file}' does not exist.")
        sys.exit(1)

    generate_vectors(image_dir, saving_chars_file, output_file)
