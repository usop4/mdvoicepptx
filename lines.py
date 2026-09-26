#!python3

# scenario.mdを読み込み、下記の調整を行う
# 1. 各行の間に1行ずつ空行を追加
# 2. 空の行が2つ以上続いた場合、1つにする

# --sharpオプションを指定すると、行頭に「#」を追加する
# --noteオプションを指定すると、行頭に「>」を追加する

import re
import fire

from icecream import ic

from mylib import *

TIME_ONLY_PATTERN = re.compile(r'^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}(?::\d{2})?\s*$')


def is_time_only(line):
    return TIME_ONLY_PATTERN.fullmatch(line) is not None


def is_korean_only(line):
    return is_korean(line) and not is_japanese(line)


def lines(fname="scenario.md",note=False,sharp=True):

    #fname = "scenario.md"
    with open(fname, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    front_matter = []
    if lines and lines[0].strip() == '---':
        for index in range(1, len(lines)):
            if lines[index].strip() == '---':
                front_matter = lines[:index + 1]
                lines = lines[index + 1:]
                break

    # 各行の間に空行を追加
    new_lines = []
    for line in lines:

        if line.startswith('#'):
            line = re.sub(r'^#[ \t　]+#(?:[ \t　]+#)*[ \t　]*', '# ', line)
            new_lines.append(line)
            new_lines.append("\n")
            continue

        if is_time_only(line):
            continue

        line = line.replace('3級', ' 3級')

        # タブを改行に変換
        line = line.replace('\t', '\n')

        # ゼロ幅スペースを削除
        line = line.replace('\u200e', '')

        # 空白２つ以上を１つに変換
        line = line.replace('　', ' ')
        while '  ' in line:  # 空白2つが存在する間繰り返す
            line = line.replace('  ', ' ')

        # 感嘆など削除
        line = line.replace('아, ', '')
        line = line.replace('아휴, ', '')
        line = line.replace('야, ', '')
        line = line.replace('아이, ', '')


        # []で囲まれた文字を削除
        line = re.sub(r'\[.*?\]', '', line)


        # noteがTrueの場合、行頭に「>」を追加
        if note:
            if line.startswith(' '):
                line = ">" + line

        # sharpがTrueで韓国語の場合、行頭に「#」を追加
        if sharp:
            if is_korean_only(line):
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

    new_lines = front_matter + new_lines

    # 処理結果をファイルに書き込む
    with open(fname, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


if __name__ == "__main__":
    fire.Fire(lines)