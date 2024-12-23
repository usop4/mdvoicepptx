# mdvoicepptx

## 概要
`mdvoicepptx` は、Markdownファイルを元に音声ファイルやPowerPointプレゼンテーションを生成するためのPythonツール集です。このツールを使用することで、簡単にテキストから音声やスライドを作成できます。

音声はOpenAIのAPIを使っているため、APIキーが必要です。PowerPointの生成にはpandocを使っているため、別途インストールが必要です。

作者は主に韓国語の例文を覚えるために使っています。


## インストール

必要なPythonパッケージをインストールするには、以下のコマンドを実行してください：

```sh
pip install -r requirements.txt
```

pandocをインストールするには、以下のコマンドを実行してください：

### macOS

```sh
brew install pandoc
```

### Linux (Debian/Ubuntu)

```sh
sudo apt-get install pandoc
```

## 環境変数

音声合成エンジンを使用するために、`config.env` ファイルにAPIキーを設定してください。

```sh
OPENAI_KEY=your_openai_api_key
```

## 使い方

### 音声ファイルの生成
[`audio_from_scenario.py`](audio_from_scenario.py ) を使用して、Markdownファイルから音声ファイルを生成します。

```sh
python audio_from_scenario.py
```

### PowerPointの生成
[`pptx_from_scenario.sh`](pptx_from_scenario.sh ) を使用して、MarkdownファイルからPowerPointプレゼンテーションを生成します。

```sh
sh pptx_from_scenario.sh
```


## ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細については、`LICENSE` ファイルを参照してください。

## 貢献
バグ報告や機能リクエストは、Issueを通じて行ってください。プルリクエストも歓迎します。

