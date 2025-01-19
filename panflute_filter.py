#!/usr/bin/env python3

import panflute as pf
import csv

from icecream import ic
# ic.disable()

keywords = {}
keyword_stats = {}
timeline = []

def load_keywords(filepath):
    """Load keywords and their corresponding links from a CSV file."""
    global keywords
    with open(filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            if len(row) >= 2:  # 行が少なくとも2列あるか確認
                keywords[row[0]] = row[1]  # キーワードをキー、対応リンクを値としてdictに追加

def highlight_word(elem, doc):
    """Filter function to replace keywords with hyperlinks and add matched keyword line."""
    if isinstance(elem, pf.Para):
        new_elems = []
        matched_keywords = []
        for subelem in elem.content:
            if isinstance(subelem, pf.Str) and subelem.text in keywords:
                url = keywords[subelem.text]
                keyword_stats[subelem.text] = keywords[subelem.text]
                new_elems.append(pf.Link(pf.Str(subelem.text), url=url))
                matched_keywords.append((subelem.text, keywords[subelem.text]))
            else:
                new_elems.append(subelem)
        
        # Add matched keywords as a new line
        if matched_keywords:
            new_elems.append(pf.LineBreak())
            for keyword, meaning in matched_keywords:
                new_elems.append(pf.Str(f"({keyword}:{meaning})"))
        
        return pf.Para(*new_elems)


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
        return [elem, elem]  # Duplicate the element

def gather_time(elem, doc):
    if isinstance(elem, pf.Header) and elem.level == 1:
        text = pf.stringify(elem)
        #ic(text)
        timeline.append(text)

def prepare(doc):
    """Load the keywords CSV during preparation."""
    load_keywords('keywords.csv')  # Replace 'keywords.csv' with the actual file path

def add_keyword_page(doc):
    if keyword_stats:
        slide_break = pf.Header(pf.Str("Keyword Statistics"), level=1)
        data_paragraph = []
        for keyword, description in keyword_stats.items():
            data_paragraph.append(pf.Str(f"{keyword}: {description}"))
            data_paragraph.append(pf.LineBreak())
        doc.content.extend([slide_break, pf.Plain(*data_paragraph)])

def add_timeline_page(doc):
    """ドキュメントの最後に蓄積データを追加"""
    if timeline:
        
        slide_break = pf.Header(pf.Str("Timeline"), level=1)
        data_paragraph = pf.Plain(
            *[
                pf.Str(f"{time}, ") 
                for time in timeline
            ]
        )
        doc.content.extend([slide_break, data_paragraph])

def finalize(doc):
    add_keyword_page(doc)
    add_timeline_page(doc)

def main(doc=None):
    return pf.run_filters(
        [highlight_word, remove_voice_lines,gather_time], 
        #[highlight_word, remove_voice_lines, duplicate_comment_lines], 
        prepare=prepare, 
        finalize=finalize, 
        doc=doc)

if __name__ == "__main__":
    main()