#!python3

import os
import sys
import re

import fire

from icecream import ic

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv('config.env')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_KEY')

from langchain_core.messages import AIMessage

def make_safe_fname(text):
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}.txt"

def model_init(model_type):
    if model_type == "ollama":
        return ChatOllama(model="llama3.2")
    elif model_type == "openai":
        return ChatOpenAI(model="gpt-4o-mini", max_tokens=200)
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
この韓国語の文を２〜５センテンス程度で区切って、それぞれをコンパクトに解説してください。
出力は出力例のように書いてください。日本語は韓国語と語順を変えず直訳してください。
カッコや数字、ハイフン、箇条書きは付けないでください。

* 出力例
살짝 웜톤으로 少し暖かい色調で  
보이면서 見えながら  
아무래도 やはり 
예뻐 보이고 きれいに見える
"""

        messages = [
            ("system",system_message),
            ("human", s),
        ]
        ai_msg = llm.invoke(messages)
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(ai_msg.content)
        return ai_msg.content

def is_korean(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if '\uAC00' <= char <= '\uD7A3':
            return True
    return False

def start_with_korean(text):
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

def is_comment(text):
    return text.startswith('#')

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

def command(lang="ko", model="openai"):
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

        if koflag:
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
