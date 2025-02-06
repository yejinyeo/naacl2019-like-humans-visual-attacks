import argparse
import random
import sys

import numpy as np

from perturbations_store import PerturbationsStorage

from gensim.models import KeyedVectors as W2Vec


parser = argparse.ArgumentParser()
parser.add_argument('-e', action="store", dest="embed")
parser.add_argument("-p", action="store", dest="prob")
parser.add_argument('-s', action="store", dest="seed", type=int, default=42)
parser.add_argument('--perturbations-file', action="store", dest='perturbations_file')
parser.add_argument('--transformed-file', action="store", dest='transformed_file', default="transformed_words.txt")
parser.add_argument('--linked-file', action="store", dest='linked_file', default="linked_words.txt")

parsed_args = parser.parse_args(sys.argv[1:])
seed = parsed_args.seed
random.seed(seed)
np.random.seed(seed)

emb = parsed_args.embed
prob = float(parsed_args.prob)
perturbations_file = PerturbationsStorage(parsed_args.perturbations_file)

transformed_lines_file = parsed_args.transformed_file
linked_lines_file = parsed_args.linked_file

open(transformed_lines_file, "w", encoding="utf-8").close()
open(linked_lines_file, "w", encoding="utf-8").close()

# SAMPLE USAGE:
# python3 viper_ices.py -e ../embeddings/efile.norm -p 0.4 -s 123 --perturbations-file dummy_store.txt --transformed-file output_transformed_lines.txt --linked-file output_linked_lines.txt < unsafe_raw_words.txt

model = W2Vec.load_word2vec_format(emb)

isOdd, isEven = False, False

topn = 20

mydict = {}

for line in sys.stdin:
    original_line = line.strip()  # 원본 라인
    transformed_line = []  # 변형된 라인

    # 단어 단위 처리
    for word in original_line.split():
        transformed_word = []  # 변형된 단어

        # 문자 단위 처리
        for char in word:
            if char not in mydict:
                # 유사한 문자 계산
                similar = model.most_similar(char, topn=topn)
                if isOdd:
                    similar = [similar[iz] for iz in range(1, len(similar), 2)]
                elif isEven:
                    similar = [similar[iz] for iz in range(0, len(similar), 2)]
                words, probs = [x[0] for x in similar], np.array([x[1] for x in similar])
                probs /= np.sum(probs)
                mydict[char] = (words, probs)
            else:
                words, probs = mydict[char]

            # 확률에 따라 변형 적용
            if random.random() < prob:
                transformed_char = np.random.choice(words, 1, replace=True, p=probs)[0]
                perturbations_file.add(char, transformed_char)
            else:
                transformed_char = char
            transformed_word.append(transformed_char)

        # 변형된 단어 추가
        transformed_line.append("".join(transformed_word))

    # 변형된 라인 생성
    transformed_line_str = " ".join(transformed_line)

    # 변형된 텍스트 저장
    with open(transformed_lines_file, "a", encoding="utf-8") as transformed_file:
        transformed_file.write(transformed_line_str + "\n")

    # 변형 전후 텍스트 연결 저장
    with open(linked_lines_file, "a", encoding="utf-8") as linked_file:
        linked_file.write(f"{original_line}||{transformed_line_str}\n")

# 변형 로그 저장
perturbations_file.maybe_write()
