#!python3

import os
import sys
import re

import fire

from icecream import ic

from langchain_ollama import ChatOllama
import os
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
この韓国語の文を１〜５単語程度で区切って、韓国語と日本語をそれぞれをコンパクトに解説してください。
解説には数字やカッコ、ハイフン、コロンは付けないでください。

* 出力の例
살짝 少し
웜톤으로 暖かい色調で  
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

def make_comment_test(s,model_type):
    return ">>"+s

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

def command(lang="ko", model="ollama"):
    print(f"lang={lang}, model={model}")

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
        if is_cached(lines[i]):
            flag = False

        if flag:
            res = make_comment(lines[i],model)
            res = insert_space(res)
            lines.insert(i + 1,res+'\n')
            i += 1
        i += 1

    # 最後にfnameに書き込みする
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == "__main__":

    fire.Fire(command)
