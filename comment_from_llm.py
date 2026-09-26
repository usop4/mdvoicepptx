#!python3

import os
import sys
import re

import fire

from icecream import ic

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv('config.env')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_KEY')

from langchain_core.messages import AIMessage

from mylib import *

def make_safe_fname(text):
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}.txt"

def model_init(model_type):
    if model_type == "ollama":
        return ChatOllama(model="llama3.2")
    elif model_type == "openai":
        return ChatOpenAI(model="gpt-4o-mini", max_tokens=200)
    elif model_type == "gpt-5-mini":
        return ChatOpenAI(model="gpt-5.4-mini")
    elif model_type == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    else:
        raise ValueError("Unsupported model type. Use 'ollama' or 'openai'.")

def make_comment(s,model_type):

    fname = make_safe_fname(s)
    if is_cached(s):
        with open(fname, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        llm = model_init(model_type)

        system_message = """
あなたは韓国語学習用の対訳を作成します。入力は韓国語の一文です。
入力文を、韓国語の文法と意味が自然につながる３〜４個のまとまりに分け、各まとまりを１行で対訳してください。

必ず次の規則に従ってください。

１．各行は「韓国語のまとまり 日本語のまとまり」の順にする。
２．韓国語を行の左側にまとめ、日本語を行の右側にまとめる。韓国語と日本語を交互に並べたり、単語ごとに韓国語と日本語を交互に置いたりしない。
３．韓国語のまとまりと日本語のまとまりは、入力文の語順を保つ。日本語はそのまとまりの意味が自然に伝わる訳にする。
４．単語数ではなく、意味と文法のまとまりで区切る。特に次を途中で分けない。
    - 名詞と助詞・助詞相当語
    - 動詞・形容詞の語幹と語尾
    - 目的語と、それに続く動作
    - 「나 보러 온 거예요?」のような「見に来たんですか」に相当する連続した表現
    - 「'전설의 고향' 만들어서」のような「『伝説の故郷』を作って」に相当する名詞と動作
    - 「내 질문은」のような「私の質問は」に相当する名詞句
５．入力文にない韓国語を追加しない。入力文の韓国語は漏らさず、順番も変えない。
６．直訳にこだわりすぎず、文脈上自然な日本語にする。ただし、意訳で元の意味を追加しない。
７．入力文全体の日本語訳、説明、見出し、ラベル、箇条書き、括弧、番号、ハイフンは出力しない。
８．各行の間は空行を１行入れる。

出力例１：
입력: 저 이 색깔 안 좋아하고요 꽃신 안 신고요 홍시 안 먹고요
出力:
저 이 색깔 안 좋아하고요 私は この 色が 好きではなくて

꽃신 안 신고요 花の靴を 履かなくて

홍시 안 먹고요 熟した柿を 食べなくて

出力例２：
입력: 미치겠다 그런 되지도 않는 '전설의 고향' 만들어서 나 보러 온 거예요?
出力:
미치겠다 그런 参った そんな

되지도 않는 '전설의 고향' 만들어서 できもしない 「伝説の故郷」を作って

나 보러 온 거예요? 私を 見に 来た んですか？

出力例３：
입력: 나는 다 말했는데 넌 왜 비밀이야?
出力:
나는 다 私は すべて

말했는데 넌 言ったのに 君は

왜 비밀이야? なぜ 秘密なの？
"""

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=s),
        ]
        ai_msg = llm.invoke(messages)
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(ai_msg.content)
        return ai_msg.content

def is_cached(text):
    fname = make_safe_fname(text)
    if os.path.exists(fname):
        return True
    else:
        return False

def insert_space(text):
    lines = text.split('\n')
    lines = [" " + line for line in lines]
    return '\n'.join(lines)

def command(lang="ko", model="gpt-5-mini"):
    print(f"lang={lang}, model={model}")

    temp = ""
    fname = "scenario.md"
    with open(fname, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    i = 0
    res = ""
    while i < len(lines):
        koflag = False
        jaflag = False

        if lang=="ko":
            if is_korean(lines[i]):
                koflag = True
            if is_japanese(lines[i]):
                koflag = False
                jaflag = True

        if is_space(lines[i]):
            koflag = False
        if is_cached(lines[i]):
            koflag = False

        if len(lines[i]) < 6:
            koflag = False

        if koflag:
            print(lines[i])
            res = make_comment(lines[i].replace('# ',''),model)

        if jaflag and res != "":
            res = insert_space(res)
            lines.insert(i + 1,res+'\n')
            res = ""
            i += 1
        i += 1

    # 最後にfnameに書き込みする
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == "__main__":

    fire.Fire(command)
