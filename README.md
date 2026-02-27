# 概要

このリポジトリは、天気、アメダス、潮汐などの情報を定期的に取得し、静的なWebページとして表示するためのプロジェクトです。
GitHub Actionsを利用して定期的にデータを取得・更新し、フロントエンド（`docs` ディレクトリ）用のJSONデータを自動生成します。

## 機能・データソース

GitHub Actionsの定期実行（cron）によって以下のデータを自動取得し、`docs/` 配下にJSONファイルとして保存します。

1. **気象庁 天気予報データ** (`docs/130000.json`)
   * **取得元:** 気象庁 (JMA) 天気予報API (`https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json`)
   * **対象地域:** 東京地方（130000）
   * **更新頻度:** 毎日 06:10 JST (21:10 UTC)
   * **ワークフロー:** `.github/workflows/daily-jma-fetch.yml`

2. **アメダス（AMeDAS）データ** (`docs/44132.json`)
   * **取得元:** 気象庁 アメダス最新データ
   * **対象観測所:** 観測所コード 44132（東京）
   * **更新頻度:** 毎時 5分 (JST)
   * **ワークフロー:** `.github/workflows/hourly-amedas-fetch.yml`
   * **スクリプト:** `scripts/amedas.py`

3. **潮汐・日の出・日の入りデータ** (`docs/tide.json`)
   * **取得元:** [tide736.net API](https://tide736.net/)（潮汐）、Pythonライブラリ `astral`（日の出・日の入り）
   * **対象地域:** 芝浦周辺（緯度: 35.6586, 経度: 139.7454）
   * **更新頻度:** 毎日 00:10 JST (15:10 UTC)
   * **ワークフロー:** `.github/workflows/daily-tide-fetch.yml`
   * **スクリプト:** `scripts/tide.py`

## ディレクトリ構成

* `docs/`: フロントエンドリソース（HTML、CSS、JS）および、自動取得されたJSONデータ。静的サイトホスティング（GitHub Pagesなど）のドキュメントルートとなります。
  * `index.html`: メインダッシュボード画面
  * `tide.html`: 潮汐情報画面
  * `*.json`: 取得済みの各種データ
* `scripts/`: データ取得用のPythonスクリプト
  * `amedas.py`: アメダスデータの取得・整形
  * `tide.py`: 潮汐データおよび日の出日の入り、月齢の計算・整形
  * `requirements-*.txt`: 各スクリプトで必要なPythonパッケージ一覧

## ローカルでの実行・開発

データ取得スクリプトをローカルでテストする場合は、以下のコマンドを実行します。

```bash
# アメダスデータの取得テスト
pip install -r scripts/requirements-amedas.txt
python scripts/amedas.py

# 潮汐データの取得テスト
pip install -r scripts/requirements-tide.txt
python scripts/tide.py
```

フロントエンドの確認は、ローカルサーバーを立ち上げて `docs/` ディレクトリを表示してください。

```bash
cd docs
python -m http.server 8000
# ブラウザで http://localhost:8000 にアクセス
```
