#!/bin/bash

# yt_trans.pyを実行
python3 /Users/user/Documents/hangul/yt_trans.py "$@"

# yt_trans.pyが成功した場合のみfind_episode.pyを実行
if [ $? -eq 0 ]; then
    # yt_trans.pyの出力ディレクトリから最新の.txtファイルを見つけてfind_episode.pyに渡す
    LATEST_TXT=$(find /Users/user/Documents/hangul/youtube -name "*.txt" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -n "$LATEST_TXT" ]; then
        echo "Running find_episode.py with $LATEST_TXT"
        python3 /Users/user/Documents/hangul/find_episode.py "$LATEST_TXT"
    else
        echo "No transcript file found."
    fi
else
    echo "yt_trans.py failed, skipping find_episode.py"
fi