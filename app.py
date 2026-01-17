import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="Stock Monthly Low Data Extractor",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# スタイル設定
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .input-section {
        background-color: #f9fafb;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .success-message {
        color: #10b981;
        font-weight: bold;
    }
    .error-message {
        color: #ef4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# タイトル
st.markdown('<div class="main-title">📊 Stock Monthly Low Data Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">証券コードを入力して、月間安値データを自動抽出</div>', unsafe_allow_html=True)

def scrape_kabutan_data(code: str, start_date: datetime, end_date: datetime):
    """株探からデータをスクレイピングする関数"""
    all_data = []
    page = 1
    max_pages = 10
    
    while page <= max_pages:
        try:
            url = f"https://kabutan.jp/stock/kabuka?code={code}&ashi=mon&page={page}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                st.error(f"❌ ページ取得エラー: ステータスコード {response.status_code}")
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            if len(tables) < 6:
                break
            
            # Table 4と5からデータを抽出
            page_data = []
            for table_idx in [4, 5]:
                if table_idx < len(tables):
                    table = tables[table_idx]
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        ths = row.find_all('th')
                        tds = row.find_all('td')
                        
                        if len(ths) == 1 and len(tds) == 7:
                            date_str = ths[0].get_text(strip=True)
                            low_str = tds[2].get_text(strip=True).replace(',', '')
                            
                            # 日付フォーマットのチェック
                            if '/' in date_str and len(date_str) == 8:
                                try:
                                    yy, mm, dd = map(int, date_str.split('/'))
                                    year = 2000 + yy
                                    dt = datetime(year, mm, dd)
                                    
                                    if start_date <= dt <= end_date:
                                        page_data.append({
                                            'date': dt.strftime('%Y/%m/%d'),
                                            'low': int(low_str)
                                        })
                                except (ValueError, TypeError):
                                    continue
            
            if not page_data:
                break
            
            all_data.extend(page_data)
            page += 1
            time.sleep(1)  # サーバー負荷軽減
            
        except Exception as e:
            st.warning(f"⚠️ ページ {page} の処理中にエラーが発生しました: {str(e)}")
            break
    
    return all_data

def get_company_name(code: str):
    """企業名を取得する関数"""
    try:
        url = f"https://kabutan.jp/stock/?code={code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 企業名を取得（複数の方法を試す）
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # 「企業名（企業名）【コード】」形式から企業名を抽出
            if '【' in title_text:
                company_name = title_text.split('【')[0].strip().split('（')[0].strip()
                return company_name
        
        return f"Stock_{code}"
    except:
        return f"Stock_{code}"

# 入力セクション
st.markdown('<div class="input-section">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    code = st.text_input(
        "証券コード",
        placeholder="例: 1443",
        max_chars=4,
        help="4桁の証券コードを入力してください"
    )

with col2:
    st.write("")
    st.write("")
    if st.button("📥 データを取得", use_container_width=True):
        if not code or len(code) != 4 or not code.isdigit():
            st.error("❌ 有効な4桁の証券コードを入力してください")
        else:
            st.session_state.code = code

st.markdown('</div>', unsafe_allow_html=True)

# 日付範囲設定
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "開始日",
        value=datetime(2019, 1, 1),
        help="データ取得の開始日を選択"
    )
with col2:
    end_date = st.date_input(
        "終了日",
        value=datetime.now(),
        help="データ取得の終了日を選択"
    )

# データ取得処理
if 'code' in st.session_state:
    code = st.session_state.code
    
    with st.spinner("📊 データを取得中..."):
        # 企業名を取得
        company_name = get_company_name(code)
        
        # データをスクレイピング
        data = scrape_kabutan_data(code, start_date, end_date)
    
    if data:
        # データフレームを作成
        df = pd.DataFrame(data)
        df = df.sort_values('date').reset_index(drop=True)
        
        st.success(f"✅ {len(df)}件のデータを取得しました")
        
        # データプレビュー
        st.subheader("📋 データプレビュー")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Excel出力
        st.subheader("💾 ファイルをダウンロード")
        
        # Excelファイルをメモリに作成
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='月間安値', index=False)
        output.seek(0)
        
        # ダウンロードボタン
        filename = f"{company_name}_{code}_月間安値.xlsx"
        st.download_button(
            label="📥 Excelファイルをダウンロード",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # 統計情報
        st.subheader("📊 統計情報")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("最高値", f"¥{df['low'].max()}")
        with col2:
            st.metric("最安値", f"¥{df['low'].min()}")
        with col3:
            st.metric("平均値", f"¥{df['low'].mean():.0f}")
        with col4:
            st.metric("データ件数", len(df))
        
        # 削除
        del st.session_state.code
    else:
        st.error(f"❌ 証券コード {code} のデータが見つかりませんでした。コードを確認してください。")
        if 'code' in st.session_state:
            del st.session_state.code

# フッター
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #9ca3af; font-size: 0.875rem;">
    <p>📊 Stock Monthly Low Data Extractor | データ出典: <a href="https://kabutan.jp" target="_blank">株探</a></p>
    <p>このツールは教育目的で作成されています。投資判断の参考にはしないでください。</p>
    </div>
""", unsafe_allow_html=True)
