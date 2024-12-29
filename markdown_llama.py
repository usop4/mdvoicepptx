#!python3

from icecream import ic

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2")

from langchain_core.messages import AIMessage

def make_comment(s):
    messages = [
        ("system","この文に含まれる韓国語の文を１〜５単語程度で区切って、それぞれをコンパクトに日本語で解説してください。文は数字やカッコは付けないでください。発音や日本語の読みについては解説しないでください。中国語、漢字語は書かないでください。",),
        ("human", s),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content

def make_comment_test(s):
    return ">>"+s

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
        lines = file.readlines()
    
    i = 0
    while i < len(lines):
        if is_korean(lines[i]):
            res = make_comment(lines[i])
            lines.insert(i + 1, " " + res.strip() + "\n")
            i += 1  # コメント行をスキップするためにインクリメント
        i += 1

    # 最後にfnameに書き込みする
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(lines)


