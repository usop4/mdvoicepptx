#!python3

import os
import sys
import re

import fire

from icecream import ic

from konlpy.tag import Okt

def extract_verb_stems(text):
    """
    動詞の原型を出力する
    """

    okt = Okt()
    
    # そのままの形を取得
    original_morphs = okt.pos(text, stem=False)
    
    # 原形を取得
    stem_morphs = okt.pos(text, stem=True)
    
    verbs = []
    for original, stem in zip(original_morphs, stem_morphs):
        original_word, original_pos = original
        stem_word, stem_pos = stem
        
        # 動詞であるかを確認
        if original_pos == 'Verb' and stem_pos == 'Verb':
            verbs.append(f"{original_word} ({stem_word})")  # (そのままの形, 原形)
    
    return "\n".join(verbs)

def is_korean(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if '\uAC00' <= char <= '\uD7A3':
            return True
    return False

def is_space(text):
    return text.startswith(' ')

def is_comment(text):
    return text.startswith('#')

def insert_space(text):
    lines = text.split('\n')
    lines = [" " + line for line in lines]
    return '\n'.join(lines)

def command(lang="ko"):
    print(f"lang={lang}")

    temp = ""
    fname = "scenario.md"
    with open(fname, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    i = 0
    while i < len(lines):
        flag = False

        if lang=="ko" and is_korean(lines[i]):
            flag = True

        if is_space(lines[i]):
            flag = False
        if is_comment(lines[i]):
            flag = False

        if flag:
            res = extract_verb_stems(lines[i])
            res = insert_space(res)
            lines.insert(i + 1,res+'\n')
            i += 1
        i += 1

    # 最後にfnameに書き込みする
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == "__main__":

    fire.Fire(command)
