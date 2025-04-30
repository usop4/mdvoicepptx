from konlpy.tag import Okt

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