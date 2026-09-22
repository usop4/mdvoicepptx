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
韓国語の学習者にとって、理解しやすいように
この韓国語の文を２〜４センテンスごとに意味のある区切りで分割し、
出力例のように、それぞれ１行ごとに直訳し韓国語と日本語で表記してください
元の文に含まれていない韓国語を追加しないでください。
カッコや数字、ハイフン、箇条書きは付けないでください。

* 出力例
살짝 웜톤으로 少し暖かい色調で  
보이면서 見えながら  
아무래도 やはり 
예뻐 보이고 きれいに見える
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
