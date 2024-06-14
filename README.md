# Nyantter
猫たちの、猫たちによる、猫たちのためのSNS
## How to Build
### 前提
- Python 3.11.9 (それ以外のバージョンで動くかの確証はありません)
### リポジトリのクローン・依存関係のインストール
(仮想環境を作りたい場合は、作っておく)
```
git clone https://github.com/nennneko5787/Nyantter.git
cd Nyantter
pip install -r requirements.txt
```

### 環境変数の設定
以下のような.envファイルを作成するか、環境変数を設定してください。
```ini
dsn=postgres://~~~~~~
turnstile_sitekey=0x~~~~~~~~~~~~~~~~~~~~~~
turnstile_secret=0x~~~~~~~~~~~~~~~~~~~~~~
```

### 実行
```
uvicorn main:app --host 0.0.0.0 --port 10000
```