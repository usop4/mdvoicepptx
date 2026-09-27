# hangul スクリプト仕様

## 1. 目的

韓国語学習用の素材を作成するためのスクリプト群。主な処理は次の二つ。

1. YouTube動画から音声を取得し、韓国語の文字起こしを作成する。
2. `scenario.md` を整形し、日本語解説、音声、PowerPointを生成する。

## 2. よく使う実行フロー

### YouTubeから文字起こしを作る

```sh
source venv/bin/activate
./clean.sh
./yt_trans.py "https://www.youtube.com/watch?v=動画ID"
```

冒頭を除外して文字起こしする場合は、秒数を指定する。

```sh
./yt_trans.py "https://www.youtube.com/watch?v=動画ID" --trim_seconds 1
```

出力は `youtube/` に保存される。動画音声の `.mp3` と、Whisperのタイムスタンプ付き `.txt` が生成される。

### シナリオから教材を作る

履歴上は、次の順序で使われている。

```sh
./lines.py
./comment_from_llm.py
./pptx_from_scenario.sh
./audio_from_scenario.py
```

通常は `scenario.md` を入力として、整形、韓国語行への日本語解説追加、PowerPoint生成、音声生成を行う。

## 3. スクリプト仕様

### `clean.sh`

`youtube/*` と `cache/*` を削除する。YouTubeのダウンロード結果とLLM/TTSのキャッシュを一括して初期化するためのスクリプトで、削除前の確認は行わない。

### `yt_trans.py`

YouTube URLを受け取り、`yt-dlp` と `faster-whisper` で韓国語音声を文字起こしする。

- 入力: YouTube URL
- `--output_dir DIR`: 保存先。既定値は `/Users/user/Documents/hangul/youtube`
- `--trim_seconds SEC`: 音声の先頭から指定秒数だけを残したファイルを作る
- `--model SIZE`: Whisperモデル。既定値は `medium`
- 音声形式: mp3、品質192kbps
- Whisper: CPU、`int8`、韓国語 (`ko`)、beam size 5
- 出力: 入力音声と同名の `.txt`
- 文字起こしの各行: `[開始秒s -> 終了秒s] テキスト`

`--trim_seconds` を指定しない場合、音声のトリミングは行わない。

### `yt_trans.sh`

`yt_trans.py` を実行した後、`youtube/` 内の最新の `.txt` をエピソード検索へ渡すラッパー。文字起こしが失敗した場合は検索を実行しない。

### `yt_find_episode.py`

YouTubeの文字起こしテキストと `netflix/*.tsv` の韓国語字幕を比較し、対応するエピソードを検索する。

- 文字起こし側のタイムスタンプ、句読点、空白を除去して比較する
- 字幕TSVの韓国語列を比較対象、日本語列を結果表示に使う
- 10行単位、5行ずつ移動するスライディングウィンドウで類似度を計算する
- 全TSVをスコア順に並べ、最上位のファイルと一致箇所を最大5件表示する
- 字幕ファイルがない場合や入力ファイルがない場合はエラーを表示する

### `lines.py`

`scenario.md` の行をPandoc向けに整形する。引数を省略すると `scenario.md` を上書きする。

- 行の間に空行を追加し、連続する空行を一つにまとめる
- `1:01:45` など時刻だけの行を削除する。日付だけの行は削除しない
- タブを改行に変換する
- 全角空白、ゼロ幅文字、過剰な空白を整理する
- 一部の韓国語の感嘆表現と `[...]` 内の文字を削除する
- 韓国語を含み日本語文字を含まない行に `# ` を付ける（既定で有効）
- 先頭が `#` の行は通常の整形を行わず、先頭の `# #` のような重複マーカーだけを一つにまとめる
- `--sharp=False`: `# ` の追加を無効化
- `--note=True`: 空白で始まる行に `>` を付ける
- 韓国語でない本文行には先頭に空白を付ける

### `comment_from_llm.py`

`scenario.md` の韓国語行に対して、LLMで韓国語と日本語の逐語的な解説を生成し、直後の日本語行として挿入する。

- 対象: 韓国語行、かつ6文字以上、空白行でない行
- 生成単位: 2～4文程度の意味のある区切り
- 出力形式: 韓国語と日本語を1行ずつ並べる
- キャッシュ: `cache/` に入力文ごとの `.txt` を保存し、同じ文は再利用する
- `lang`: 既定値 `ko`
- `model`: 既定値 `gpt-5-mini`
- 利用可能なモデル種別: `ollama`、`openai`、`gpt-5-mini`、`gemini`

APIキーは `config.env` の `OPENAI_KEY` または `GOOGLE_KEY` から読み込む。LLMを再実行するときも、既存キャッシュは優先して利用される。

### `insert_comments.py`

`comment_from_llm.py` の代替。外部LLM APIを呼ばず、GitHub Copilotのエージェントモード（`hangul-comment` スキル）に対訳生成を任せる構成のうち、決定的な部分だけを担当する。

- 対象行の判定は `comment_from_llm.py` と同じ（韓国語行、6文字以上、空白行でない、日本語行でない）
- `cache/` に対応する `.txt` が既にあり、まだ `scenario.md` に挿入されていない見出しがあれば、その内容を直後の日本語行の下に挿入する
- `cache/` が無い見出しは対訳を生成せず、`cache_fname<TAB>本文` の一覧を標準出力に表示するだけ（生成は行わない）
- LLM呼び出しやAPIキーは不要。何度実行しても、既に挿入済みの行を重複挿入しない

`hangul-comment` スキル（`.github/skills/hangul-comment/SKILL.md`）が次の手順でこのスクリプトを使う。

1. `python3 insert_comments.py` を実行し、「未生成の行」一覧を得る
2. 一覧の各文について、Copilotがスキルに書かれた対訳フォーマットのルールに従って自分で対訳を生成する
3. 生成結果を、一覧に出力された `cache_fname` にそのまま書き込む
4. 再度 `python3 insert_comments.py` を実行し、`scenario.md` へ反映する
5. 「未生成の行はありません。」と表示されるまで2〜4を繰り返す

エージェントモードで「hangul-comment スキルを使って scenario.md の対訳コメントを埋めて」のように頼むと、この手順が実行される。

### `pptx_from_scenario.sh`

`scenario.md` を `panflute_filter.py` で変換し、Pandocで `scenario.pptx` を生成して開く。

- 入力: `scenario.md`
- フィルター: `panflute_filter.py`
- PowerPointテンプレート: `template.pptx`
- 出力: `scenario.pptx`
- 前提: Pandoc、PowerPointテンプレート、macOSの `open` コマンド

### `audio_from_scenario.py`

`scenario.md` の韓国語行をOpenAI TTSで読み上げ、教材用の音声ファイルを生成する。

- 韓国語行だけを読み上げる
- `voice:` 行で音声を変更できる。既定値は `alloy`
- 各行の音声は `cache/` に保存し、再利用する
- 行ごとに一定の無音を挿入する
- 各韓国語音声を2回再生する
- 冒頭に `material/決定ボタンを押す3.mp3` を配置する
- 出力: `scenario/audio.mp3`
- `--fire=True` を指定すると生成後に再生する

OpenAI APIキーは `config.env` の `OPENAI_KEY` から読み込む。音声処理にはFFmpegが必要になる場合がある。

### `trial/test_rag.ipynb`

`../netflix/` の字幕TSVを分割・ベクトル化してChromaDBに登録し、質問文に類似する字幕テキストを検索する実験用ノートブック。

- `search_and_display(query, n_results=5)` が質問を表示し、ChromaDBの検索結果を上位から出力する
- 各結果の先頭行を字幕TSVと照合し、元ファイル名とタイムスタンプを結果本文の前に表示する
- 照合時は空白を除去して比較する。一致する字幕がない場合はその旨を表示する
- 関数はChromaDBの検索結果も返すため、後続セルで利用できる

### `mylib.py`

各スクリプトから共通で使われるユーティリティ関数をまとめたモジュール。`from mylib import *` で読み込む。

- 韓国語・日本語の文字種判定: `is_korean`、`is_start_with_korean`、`is_japanese`
- `scenario.md` の整形補助: `is_space`、`is_start_with_sharp`、`replace_start_with`
- `insert_comments.py`・`comment_from_llm.py` 共通のキャッシュ処理: `make_safe_fname`（入力文からcache/以下の`.txt`パスを作る）、`insert_space`（各行の先頭に空白を付けて`scenario.md`の注釈行の書式に合わせる）
- 形態素解析（`konlpy`のOkt）を使った韓国語処理: `convert_to_stem_sentence`、`convert_to_stem_sentence_simple`、`extract_verbs_with_stems`、`generate_conjugations`、`analyze_text`
- ハングルのパッチム（終声）・字母分解: `checkPatchim`、`is_hangul_syllable`、`get_vowel`、`get_initial_and_vowel`

## 4. 共通ファイルと依存関係

- 入力シナリオ: `scenario.md`
- YouTube出力: `youtube/`
- LLM/TTSキャッシュ: `cache/`
- Netflix字幕: `netflix/*.tsv`
- 効果音: `material/決定ボタンを押す3.mp3`
- 環境設定: `config.env`
- Python依存関係: `requirements.txt`
- PowerPoint変換: Pandoc、Panflute、`template.pptx`
- 外部サービス: YouTube、OpenAI、必要に応じてGoogle GeminiまたはOllama

## 5. 現在の注意点

- `clean.sh` は `youtube/` と `cache/` の内容を無条件に削除する。
- `yt_trans.sh` は現在 `find_episode.py` を呼び出すが、リポジトリ内の検索スクリプト名は `yt_find_episode.py` である。ラッパーを使う場合は、このファイル名を一致させる必要がある。
- `yt_trans.sh` の `find` はGNU形式の `-printf` を使用しているため、macOS標準の `find` では動かない可能性がある。
- `scenario.md`、`cache/`、`youtube/` の既存内容を前提にした固定パスが多いため、別環境ではパスやテンプレートを調整する。

## 6. Marp画像からMP4を作る

`scenario.md` をMarpでPNGに変換し、`#` 見出しごとのタイトル音声と組み合わせてYouTube向け動画を生成する。

```sh
marp scenario.md --images png --output ./scenario/scenario.png
venv/bin/python make_mp4_from_scenario.py
```

Marpの出力画像は `scenario/` 内のPNGを自然順で読み込み、`#` 見出しと1対1で対応付ける。既定の出力は `scenario/scenario.mp4`。

タイトル音声は `audio_from_scenario.py` と同じOpenAI TTSキャッシュを利用する。各タイトルを2回読み上げ、最初のスライドには `material/決定ボタンを押す3.mp3` を追加する。

主な引数:

- `--scenario`: 入力Markdown。既定値は `scenario.md`
- `--image_dir`: Marp画像のディレクトリ。既定値は `scenario`
- `--output`: MP4出力先。既定値は `scenario/scenario.mp4`
- `--cache_dir`: TTSキャッシュのディレクトリ。既定値は `cache`
- `--interval_ms`: 音声の基準間隔。既定値は `1875`

FFmpegとFFprobeが必要。画像数と `#` 見出し数が一致しない場合、動画生成前にエラーになる。
