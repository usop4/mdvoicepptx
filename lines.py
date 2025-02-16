#!python3

# scenario.mdを読み込み、下記の調整を行う
# 1. 各行の間に1行ずつ空行を追加
# 2. 空の行が2つ以上続いた場合、1つにする

# --sharpオプションを指定すると、行頭に「#」を追加する
# --noteオプションを指定すると、行頭に「>」を追加する

import fire
from icecream import ic

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

def is_space(text):
    return text.startswith(' ')

def lines(note=False,sharp=False):

    fname = "scenario.md"
    with open(fname, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 各行の間に空行を追加
    new_lines = []
    for line in lines:

        # タブを改行に変換
        line = line.replace('\t', '\n')

        # noteがTrueの場合、行頭に「>」を追加
        if note:
            if line.startswith(' '):
                line = ">" + line

        # sharpがTrueの場合、行頭に「#」を追加
        if sharp:
            sharp_flag = False

            if start_with_korean(line):
                sharp_flag = True

            if sharp_flag:
                line = "# " + line

        if not is_space(line):
            if not is_korean(line):
                line = " " + line
        new_lines.append(line)

        new_lines.append("\n")

    # 空行が2つ以上続く場合、1つにまとめる
    i = 0
    previous_line_empty = False  # 前の行が空行かどうかを記録するフラグ

    while i < len(new_lines):
        current_line_empty = new_lines[i].strip() == ""  # 現在の行が空行かどうかを判定

        if previous_line_empty and current_line_empty:
            # 前の行と現在の行が両方とも空行の場合、現在の行を削除
            del new_lines[i]
        else:
            # 前の行が空行でないか、現在の行が空行でない場合、次の行へ進む
            previous_line_empty = current_line_empty
            i += 1

    # 処理結果をファイルに書き込む
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


if __name__ == "__main__":
    fire.Fire(lines)