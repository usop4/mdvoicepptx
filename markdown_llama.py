#!python3

from icecream import ic

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2")

from langchain_core.messages import AIMessage

def make_comment(s):
    messages = [
        ("system","この文に含まれる韓国語の文法をコンパクトに日本語で解説してください",),
        ("human", s),
    ]
    ai_msg = llm.invoke(messages)

    return ai_msg.content

def is_korean(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if '\uAC00' <= char <= '\uD7A3':
            return True
    return False

if __name__ == "__main__":

    temp = ""
    fname = "scenario.md"
    with open(fname, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file, start=1):
            line = line.strip()
            #ic(line)
            if is_korean(line):
                res = make_comment(line)
                print(line)
                print(res.strip())

