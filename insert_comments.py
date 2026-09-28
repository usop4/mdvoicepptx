#!python3
"""cache/ の対訳を scenario.md に挿入し、未生成（cache無し）の見出しを一覧表示する。

comment_from_llm.py と異なり、対訳の生成自体は行わない。
生成は .github/skills/hangul-comment スキルを通じて Copilot(エージェント)自身が行い、
cache/ に書き込んだ後、このスクリプトを再実行して scenario.md へ反映する。
"""

import os

from mylib import is_korean, is_japanese, is_space, make_safe_fname, insert_space

FNAME = "scenario.md"


def is_heading(line):
    if not is_korean(line) or is_japanese(line) or is_space(line):
        return False
    return len(line) >= 6


def already_has_comment(lines, ja_index):
    return ja_index + 1 < len(lines) and is_space(lines[ja_index + 1])


def main():
    with open(FNAME, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pending = []
    i = 0
    while i < len(lines):
        if is_heading(lines[i]):
            text = lines[i].replace('# ', '').strip()
            cache_fname = make_safe_fname(text)

            # 見出しの次から次の見出しまでを検索範囲にする
            j = i + 1
            while j < len(lines) and not is_heading(lines[j]) and not is_japanese(lines[j]):
                j += 1

            has_japanese_line = j < len(lines) and is_japanese(lines[j])
            if not os.path.exists(cache_fname):
                pending.append((cache_fname, text))
            elif has_japanese_line:
                if not already_has_comment(lines, j):
                    with open(cache_fname, 'r', encoding='utf-8') as cf:
                        comment = cf.read()
                    lines.insert(j + 1, insert_space(comment) + '\n')
            else:
                with open(cache_fname, 'r', encoding='utf-8') as cf:
                    comment = cf.read()
                lines[i + 1:i + 1] = ['\n', insert_space(comment) + '\n']
        i += 1

    with open(FNAME, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    if pending:
        print("未生成の行:")
        for cache_fname, text in pending:
            print(f"{cache_fname}\t{text}")
    else:
        print("未生成の行はありません。")


if __name__ == "__main__":
    main()
