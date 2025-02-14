# SAMPLE USAGE:
# python3 vec_generator_dino.py images_dir saving_chars.txt vec_dino.normalized

import os
import sys
import numpy as np
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModel

# Hugging Face에서 DINOv2 ViT-B/14 모델 로드
processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
model = AutoModel.from_pretrained("facebook/dinov2-base")

# GPU 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

model.to(device)
model.eval()  # 평가 모드

def extract_embedding(image_path):
    """이미지를 DINOv2 ViT-B/14로 변환하여 embedding 추출"""
    image = Image.open(image_path).convert("RGB")  # RGB 변환
    # 이미지 텐서를 GPU로 이동
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)  # DINOv2에서 feature 추출
        embedding = outputs.last_hidden_state.mean(dim=1)  # 평균 풀링 적용 (768-d vector)
    
    return embedding.squeeze().cpu().numpy()  # NumPy 배열로 변환

def generate_vectors(image_dir, saving_chars_file, output_file):
    """
    이미지를 벡터로 변환하여 vec_dino.normalized 파일로 저장 (Word2Vec 형식).
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
    vector_dimension = 768  # DINOv2 ViT-B/14의 embedding 차원

    # 결과 파일 초기화 및 헤더 작성 (Word2Vec 포맷 유지)
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
            # DINOv2 임베딩 추출
            vector = extract_embedding(image_path)

            # 벡터를 문자열로 변환
            vector_str = " ".join(map(str, vector))

            # 결과 파일에 저장 (Word2Vec 포맷 유지)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{char} {vector_str}\n")

        except Exception as e:
            print(f"Error processing image {image_name}: {e}")

    print(f"Vector file '{output_file}' has been created in Word2Vec format.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 vec_generator_dino.py [images_dir] [saving_chars.txt] [output_file]")
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
