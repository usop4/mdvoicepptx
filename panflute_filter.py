#!/usr/bin/env python3

import panflute as pf
import csv

from icecream import ic
# ic.disable()

keywords = {}
keyword_stats = {}

def load_keywords(filepath):
    """Load keywords and their corresponding links from a CSV file."""
    global keywords
    with open(filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:  # 行が少なくとも2列あるか確認
                keywords[row[0]] = row[1]  # キーワードをキー、対応リンクを値としてdictに追加

def highlight_word(elem, doc):
    """Filter function to replace keywords with hyperlinks."""
    if isinstance(elem, pf.Str) and elem.text in keywords:
        url = keywords[elem.text]
        keyword_stats[elem.text] = keywords[elem.text]
        return pf.Link(pf.Str(elem.text), url=url)

def remove_voice_lines(elem, doc):
    """Filter function to remove lines starting with 'voice:'."""
    if isinstance(elem, pf.Para):
        # Convert the paragraph to plain text
        text = pf.stringify(elem)
        # Check if it starts with 'voice:'
        if text.startswith('voice:'):
            return []  # Remove this element

def duplicate_comment_lines(elem, doc):
    """Filter function to duplicate lines starting with '#'."""
    if isinstance(elem, pf.Header) and elem.level == 1:
        ic("duplicate_comment")
        return [elem, elem]  # Duplicate the element

def prepare(doc):
    """Load the keywords CSV during preparation."""
    load_keywords('keywords.csv')  # Replace 'keywords.csv' with the actual file path

def add_last_page(doc):
    """ドキュメントの最後に蓄積データを追加"""
    if keyword_stats:
        slide_break = pf.Header(pf.Str("Keyword Statistics"), level=1)
        data_paragraph = pf.Plain(
            *[
                pf.Str(f"{keyword}: {discription}, ") 
                for keyword, discription in keyword_stats.items()
            ]
        )
        doc.content.extend([slide_break, data_paragraph])

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filters([highlight_word, remove_voice_lines, duplicate_comment_lines], prepare=prepare, finalize=finalize, doc=doc)

if __name__ == "__main__":
    main()