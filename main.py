import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド")

# Secretsに登録したURLを使って接続
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # スプレッドシートを読み込む（マスタシートを指定する例）
    # ※シート名が「マスタ」なら worksheet="マスタ" と指定
    df = conn.read(spreadsheet=st.secrets["public_gsheets_url"])
    
    st.success("スプレッドシートへの接続に成功しました！")
    st.subheader("データプレビュー")
    st.dataframe(df)

except Exception as e:
    st.error(f"接続エラーが発生しました: {e}")
    st.info("Secretsに正しいURLが設定されているか、スプレッドシートの共有設定が『リンクを知っている全員』になっているか確認してください。")
