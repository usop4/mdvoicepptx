#!/Users/user/Documents/hangul/venv/bin/python3

import glob
import os
import re
import sys

def normalize_text(text):
    """
    比較のためにテキストを正規化します。
    - 空白を除去
    - 句読点を除去
    """
    # 韓国語の文字と英数字以外を除去
    return re.sub(r'[^\w\s]', '', text).replace(' ', '')

def parse_timestamp_whisper(timestamp_str):
    """
    Whisperのタイムスタンプ形式 [0.00s -> 2.00s] をパースして開始時刻（秒）を返す
    """
    match = re.search(r'\[(\d+\.\d+)s', timestamp_str)
    if match:
        return float(match.group(1))
    return 0.0

def parse_timestamp_netflix(timestamp_str):
    """
    NetflixのTSVタイムスタンプ形式 00:00:00,000 をパースして秒を返す
    """
    parts = timestamp_str.split(':')
    if len(parts) >= 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_ms = parts[2].replace(',', '.')
        seconds = float(seconds_ms)
        return hours * 3600 + minutes * 60 + seconds
    return 0.0

def get_block_id(time_seconds, block_size=60):
    """
    時間から1分単位のブロックIDを取得
    """
    return int(time_seconds // block_size)

def get_block_id_from_line_number(line_num, block_size=10):
    """
    行番号から10行単位のブロックIDを取得
    """
    return line_num // block_size

def get_sliding_windows(total_lines, window_size=10, step=5):
    """
    スライディングウィンドウの位置を取得（5行ずつずらす）
    """
    windows = []
    for start in range(0, total_lines - window_size + 1, step):
        windows.append((start, start + window_size))
    # 最後の窓が足りない場合は調整
    if total_lines % step != 0 and (total_lines - window_size) % step != 0:
        windows.append((total_lines - window_size, total_lines))
    return windows

def calculate_similarity(text1, text2):
    """
    2つの正規化テキスト間の類似度を計算（0.0～1.0）
    共通文字数の比率を使用
    """
    if not text1 or not text2:
        return 0.0
    
    # 共通文字を数える
    common = sum(1 for c in text1 if c in text2)
    max_len = max(len(text1), len(text2))
    
    return common / max_len if max_len > 0 else 0.0

def get_seconds_from_timestamp(time_str):
    """
    タイムスタンプを秒に変換（"1:19" または "48s" 形式）
    """
    if 's' in str(time_str):
        try:
            return float(str(time_str).replace('s', ''))
        except:
            return 0.0
    else:
        # "mm:ss" または "h:mm:ss" 形式
        parts = str(time_str).split(':')
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except:
            return 0.0
        return 0.0

def search_episode2(target_text_path):
    """
    改良版：タイムスタンプで1分毎にブロック化して類似度で比較
    """
    netflix_dir = "/Users/user/Documents/hangul/netflix"
    tsv_files = glob.glob(os.path.join(netflix_dir, "*.tsv"))
    
    if not tsv_files:
        print("Error: No subtitle files found in", netflix_dir)
        return

    # ターゲットテキスト（Whisper）をスライディングウィンドウで処理
    target_blocks = {}
    target_blocks_raw = {}  # 正規化前のテキスト用
    try:
        with open(target_text_path, 'r', encoding='utf-8') as f:
            whisper_lines = f.readlines()
            
            # テキスト行のみフィルタリング（フィルタ条件を満たすもの）
            filtered_whisper = []
            for line in whisper_lines:
                clean_line = re.sub(r'\[.*?\]', '', line).strip().rstrip()
                if clean_line and len(clean_line) > 5:
                    norm_text = normalize_text(clean_line)
                    if len(norm_text) >= 3:
                        filtered_whisper.append((clean_line, norm_text))
            
            # スライディングウィンドウで処理
            windows = get_sliding_windows(len(filtered_whisper), window_size=10, step=5)
            for window_id, (start, end) in enumerate(windows):
                # ウィンドウ内のテキストを連結
                norm_texts = [text[1] for text in filtered_whisper[start:end]]
                raw_texts = [text[0] for text in filtered_whisper[start:end]]
                
                if norm_texts:
                    target_blocks[window_id] = ''.join(norm_texts)
                    target_blocks_raw[window_id] = ' / '.join(raw_texts)
    except FileNotFoundError:
        print(f"Error: File not found: {target_text_path}")
        return

    all_matches = []
    print(f"Searching {len(tsv_files)} episodes (sliding-window block matching)...")

    for tsv_path in tsv_files:
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # タイトル行（1行目）
                title_line = lines[0].strip() if lines else "Unknown"
                
                # NetflixのTSVをスライディングウィンドウで処理
                netflix_lines_filtered = []
                for line in lines[2:]:  # 3行目以降を対象（1行目はタイトル、2行目はヘッダー）
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        time_str = parts[0]
                        korean_text = parts[1]  # 韓国語（マッチング用）
                        japanese_text = parts[2]  # 日本語翻訳（表示用）
                        norm_text = normalize_text(korean_text)  # 韓国語で正規化
                        if len(norm_text) >= 3:
                            netflix_lines_filtered.append((time_str, korean_text, japanese_text, norm_text, line))
                
                # スライディングウィンドウで処理
                netflix_windows = get_sliding_windows(len(netflix_lines_filtered), window_size=10, step=5)
                netflix_blocks = {}
                netflix_blocks_raw = {}
                
                for window_id, (start, end) in enumerate(netflix_windows):
                    norm_texts = [text[3] for text in netflix_lines_filtered[start:end]]  # 正規化されたテキスト
                    raw_texts = [(text[0], text[2]) for text in netflix_lines_filtered[start:end]]  # 時刻と日本語
                    
                    if norm_texts:
                        netflix_blocks[window_id] = ''.join(norm_texts)
                        netflix_blocks_raw[window_id] = raw_texts
                
                # ウィンドウ単位で類似度を計算
                total_similarity = 0.0
                block_details = []  # ブロック単位の詳細情報
                
                for target_wid, target_text in target_blocks.items():
                    max_similarity = 0.0
                    best_netflix_wid = None
                    
                    # 各Targetウィンドウに対して、最も類似度の高いNetflixウィンドウを探す
                    for netflix_wid, netflix_text in netflix_blocks.items():
                        similarity = calculate_similarity(target_text, netflix_text)
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_netflix_wid = netflix_wid
                    
                    if best_netflix_wid is not None and max_similarity > 0:
                        total_similarity += max_similarity
                        
                        # Netflix側の詳細情報を取得
                        netflix_lines_text = netflix_blocks_raw.get(best_netflix_wid, [])
                        block_text_lines = [f"[{ts}] {text}" for ts, text in netflix_lines_text[:3]]
                        
                        block_details.append({
                            'similarity': max_similarity,
                            'target_wid': target_wid,
                            'netflix_wid': best_netflix_wid,
                            'target_text': target_blocks_raw[target_wid],
                            'netflix_lines': block_text_lines
                        })
                
                score = total_similarity / len(target_blocks) if target_blocks else 0.0
                
                # すべてのエピソードをスコア記録（上位用語の選別は後で行う）
                all_matches.append({
                    'path': tsv_path,
                    'title': title_line,
                    'score': score,
                    'matched_blocks': len(block_details),
                    'total_blocks': len(target_blocks),
                    'block_details': block_details
                })

        except Exception as e:
            print(f"Error reading {tsv_path}: {e}")

    if all_matches:
        # スコアでソート（降順）
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        # 上位1件だけ表示
        result = all_matches[0]
        print(f"\nFile: {os.path.basename(result['path'])}")
        print(f"Match Score: {result['score']:.2%}")
        
        # 最もマッチしているブロック（類似度が高い順）を表示
        if result['block_details']:
            block_details = sorted(result['block_details'], key=lambda x: x['similarity'], reverse=True)
            for j, block in enumerate(block_details[:5], 1):  # 最大5つの一致箇所を表示
                for line in block['netflix_lines']:
                    print(f"  {line}")
    else:
        print("❌ No matching episode found.")

def search_episode(target_text_path):
    netflix_dir = "/Users/user/Documents/hangul/netflix"
    tsv_files = glob.glob(os.path.join(netflix_dir, "*.tsv"))
    
    if not tsv_files:
        print("Error: No subtitle files found in", netflix_dir)
        return

    # ターゲットテキストの読み込み
    target_lines = []
    try:
        with open(target_text_path, 'r', encoding='utf-8') as f:
            for line in f:
                # タイムスタンプ [0.00s -> 1.66s] を除去
                clean_line = re.sub(r'\[.*?\]', '', line).strip()
                clean_line = clean_line.rstrip()
                # 3文字以内は相槌のようなフィラーワードとしてスキップ
                if clean_line and len(clean_line) > 5:
                    target_lines.append(clean_line)
    except FileNotFoundError:
        print(f"Error: File not found: {target_text_path}")
        return

    all_matches = []

    print(f"Searching {len(tsv_files)} episodes...")

    for tsv_path in tsv_files:
        current_score = 0
        current_matches = []
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # タイトル行（1行目）
                title_line = lines[0].strip() if lines else "Unknown"
                
                # 字幕本文（2行目以降）をリスト化
                subtitle_data = []
                for line in lines[1:]:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        time = parts[0]
                        korean_text = parts[1]  # 韓国語（マッチング用）
                        japanese_text = parts[2]  # 日本語翻訳（表示用）
                        norm_text = normalize_text(korean_text)  # 韓国語で正規化
                        subtitle_data.append({'time': time, 'korean': korean_text, 'japanese': japanese_text, 'norm': norm_text})

                # 各ターゲット行に対してマッチング
                for target_line in target_lines:
                    # 前処理：文末の空白を除去
                    target_line = target_line.rstrip()
                    norm_target = normalize_text(target_line)
                    if len(norm_target) < 3: continue # 短すぎる行はスキップ

                    for sub in subtitle_data:
                        # 部分一致判定（正規化後）
                        if norm_target in sub['norm'] or sub['norm'] in norm_target:
                            current_score += 1
                            current_matches.append(f"[{sub['time']}] {sub['japanese']}")
                            break # 1つのターゲット行につき1回カウント

            if current_score > 0:
                all_matches.append({
                    'path': tsv_path,
                    'title': title_line,
                    'score': current_score,
                    'matches': current_matches
                })

        except Exception as e:
            print(f"Error reading {tsv_path}: {e}")

    if all_matches:
        # スコアでソート（降順）
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        print("\n" + "="*40)
        print(f"✅ FOUND {len(all_matches)} MATCHING EPISODE(S)")
        print("="*40)
        
        for result in all_matches:
            print(f"\n{os.path.basename(result['path'])}")
            print(f"Title: {result['title']}")
            print(f"Score: {result['score']} lines matched")
            
            # 重複を除去してタイムラインでソート
            unique_matches = {}
            for m in result['matches']:
                # タイムスタンプを抽出 [1:19] or [48s]
                time_match = re.match(r'\[([^\]]+)\]', m)
                if time_match:
                    time_str = time_match.group(1)
                    # 同じタイムスタンプは後ろのものが上書きされる（重複除去）
                    unique_matches[time_str] = m
            
            # タイムラインでソート
            sorted_matches = sorted(unique_matches.items(), key=lambda x: get_seconds_from_timestamp(x[0]))
            for _, m in sorted_matches:
                print(m)
    else:
        print("❌ No matching episode found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # ファイル名が指定されない場合、youtube ディレクトリから最も新しいテキストファイルを使用
        youtube_dir = "/Users/user/Documents/hangul/youtube"
        text_files = glob.glob(os.path.join(youtube_dir, "*.txt"))
        
        if not text_files:
            print("Error: No text files found in", youtube_dir)
            sys.exit(1)
        
        # 最も新しいファイルを取得
        target_text_path = max(text_files, key=os.path.getmtime)
        print(f"Using the latest file: {os.path.basename(target_text_path)}")
        use_v2 = True  # デフォルトはv2を使用
    else:
        target_text_path = sys.argv[1]
        use_v2 = '--v2' in sys.argv or '-2' in sys.argv
    
    if use_v2:
        search_episode2(target_text_path)
    else:
        search_episode(target_text_path)
