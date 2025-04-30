from konlpy.tag import Okt
import re

def hello():
    """
    Hello Worldを出力する関数
    """
    print("Hello World")

def convert_to_stem_sentence(text):
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
            verbs.append(f"　{stem_word} -> {original_word}")  # (そのままの形, 原形)
    
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
