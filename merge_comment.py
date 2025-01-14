#!python3

import os
import sys
import re

import fire
import pyperclip

from icecream import ic

from langchain_ollama import ChatOllama
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv('config.env')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_KEY')

from langchain_core.messages import AIMessage

def model_init(model_type):
    if model_type == "ollama":
        return ChatOllama(model="llama3.2")
    elif model_type == "openai":
        return ChatOpenAI(model="gpt-4o-mini", max_tokens=200)
    else:
        raise ValueError("Unsupported model type. Use 'ollama' or 'openai'.")

def merge_comment(s,model_type):

    llm = model_init(model_type)

    system_message = """
入力例のように複数の行で構成されている韓国語と日本語を出力例のように１つの文にまとめてください

* 入力例
보신 見た（敬語）  
적이 ことが  
있으실 あるでしょう  
겁니다 と思います

* 出力例
보신 적이 있으실 겁니다 見たことがあるでしょう
"""

    messages = [
        ("system",system_message),
        ("human", s),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content

def command(lang="ko", model="openai"):
    print(f"lang={lang}, model={model}")

    content = pyperclip.paste()
    res = merge_comment(content,model)
    print(res)

if __name__ == "__main__":

    fire.Fire(command)
