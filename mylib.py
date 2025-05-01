import hanja

import re

from konlpy.tag import Okt
from hanja import hangul


def hello():
    """
    Hello Worldを出力する関数
    """
    print("Hello World")

def convert_to_stem_sentence(text,debug=False):
    patchim_list=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㅐ','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

    okt = Okt()
    original_morphs = okt.pos(text, stem=False)
    stem_morphs = okt.pos(text, stem=True)
    
    s = ""
    verbs = []
    for original, stem in zip(original_morphs, stem_morphs):
        original_word, original_pos = original
        stem_word, stem_pos = stem

        if original_pos in ['Verb', 'Adjective']:
            try:
                temp = original_word.replace(stem_word[:-1], "")
                if debug:
                    print(original_word)
                    print(stem_word)
                    print(temp)
                if temp:  # 残りの文字がある場合のみ処理
                    separated = hangul.separate(temp[0])
                    if len(separated) > 2:
                        patchim = patchim_list[separated[2]]
                        if patchim == 'ㄴ':
                            temp_word = f"{stem_word}/ㄴ{temp[1:]}"
                            text = text.replace(original_word, temp_word)
                        elif patchim == 'ㄹ':
                            temp_word = f"{stem_word}/ㄹ{temp[1:]}"
                            text = text.replace(original_word, temp_word)
                        elif patchim == 'ㅁ':
                            temp_word = f"{stem_word}/ㅁ{temp[1:]}"
                            text = text.replace(original_word, temp_word)
                        else:
                            text = text.replace(original_word, stem_word)
                    else:
                        text = text.replace(original_word, stem_word)
                else:
                    text = text.replace(original_word, stem_word)

            except Exception as e:
                print(f"Error processing word '{original_word}': {e}")
                continue

    return text

def convert_to_stem_sentence_simple(text):
    """
    文を形態素解析し、動詞や形容詞を原型に変換した文を生成する
    """
    okt = Okt()
    
    # 原型を取得
    morphs = okt.pos(text, stem=True)
    
    # 原型に変換した文を生成
    stem_sentence = ' '.join(word for word, pos in morphs)
    
    return stem_sentence

def extract_verbs_with_stems(text):
    """
    入力されたテキストから動詞のそのままの形と原形を抽出し、改行区切りの文字列として返す関数。

    Args:
        text (str): 動詞を抽出するための韓国語のテキスト。

    Returns:
        str: 動詞のそのままの形と原形を改行区切りで含む文字列。
             例: "먹었어요 (먹다)\n했어요 (하다)"
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
            verbs.append(f" {stem_word} -> {original_word}")  # (そのままの形, 原形)
    
    return "\n".join(verbs)

def is_korean(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if '\uAC00' <= char <= '\uD7A3':
            return True
    return False

def is_start_with_korean(text):
    if len(text) > 0:
        first_char = text[0]
        # Check if the first character is in the Hangul unicode range
        if '\uAC00' <= first_char <= '\uD7A3':
            return True
    return False

def is_japanese(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if ('\u3040' <= char <= '\u309F') or ('\u30A0' <= char <= '\u30FF') or ('\u4E00' <= char <= '\u9FFF'):
            return True
    return False

def is_space(text):
    return text.startswith(' ')

def is_start_with_sharp(text):
    return text.startswith('#')

def checkPatchim(s,sub):
  patchim_list=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㅐ','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
  if " " in sub:
    patchim,sub2 = sub.split(" ")
    pos = s.find(sub2)
    if pos > 2:
      prev = s[pos-2:pos-1]
    else:
      return False
    result = hangul.separate(prev)
    if len(result) > 2:
      if patchim_list[result[2]] == patchim:
        return True
  else:
    return False

def replace_start_with(origin, prefix, replacement=''):
    """
    文字列の先頭が指定された文字列で始まる場合に置換する関数。

    Args:
        origin (str): 元の文字列。
        prefix (str): 置換対象の先頭文字列。
        replacement (str): 置換後の文字列（デフォルトは空文字列）。

    Returns:
        str: 置換後の文字列。
    """
    if origin.startswith(prefix):
        return origin.replace(prefix, replacement, 1)  # 先頭の1回だけ置換
    return origin