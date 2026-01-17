# 📊 Stock Monthly Low Data Extractor

証券コードを入力するだけで、株探から月間安値データを自動抽出し、Excelファイルで出力するWebアプリケーションです。

## 🎯 機能

- **簡単入力**: 証券コード（4桁）を入力するだけ
- **自動スクレイピング**: 株探から月足の時系列データを自動取得
- **柔軟な期間設定**: 取得開始日と終上日をカレンダーで選択可能
- **Excel出力**: A列に日付、B列に安値を配置したファイルをダウンロード
- **統計情報表示**: 最高値、最安値、平均値などを自動計算

## 📋 必要な環境

- Python 3.8以上
- pip（Pythonパッケージマネージャー）

## 🚀 ローカルでの実行方法

### 1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/stock_data_extractor.git
cd stock_data_extractor
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run app.py
