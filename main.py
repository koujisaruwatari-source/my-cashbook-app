import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")
st.title("📖 現金出納帳クラウド（シンプル版）")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    url = st.secrets["public_gsheets_url"]
    
    # 【変更点】worksheetの「名前」を指定せず、まず全部読み込む
    # とにかくスプレッドシート本体にアクセスする
    all_data = conn.read(spreadsheet=url, ttl=0)
    
    # 1枚目のシート（マスタ）として扱う
    master_df = all_data 
    
    # 2枚目のシート（履歴）を名前ではなく「内部ID（gid）」等で探すのは難しいため
    # ここでは「接続が生きていること」を最優先にフォームを表示します
    st.success("✅ 接続に成功しました。フォームを表示します。")

    with st.form("input_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("日付")
        with col2:
            # 1列目のデータを科目リストにする
            category = st.selectbox("勘定科目", master_df.iloc[:, 0].unique())
        with col3:
            # 科目に合う摘要を表示
            options = master_df[master_df.iloc[:, 0] == category].iloc[:, 1].unique()
            summary = st.selectbox("摘要", options)

        income = st.number_input("入金額", min_value=0)
        expense = st.number_input("出金額", min_value=0)
        remark = st.text_input("備考")

        if st.form_submit_button("保存"):
            # 保存先は一旦一番左のシートに追記するテスト
            st.warning("保存機能は読み込みが完全に安定してから有効化します。まずは表示を確認してください。")

    st.subheader("📊 現在のデータ（マスタ）")
    st.dataframe(master_df)

except Exception as e:
    st.error(f"エラー詳細: {e}")
    st.info("SecretsのURLが '/edit' で終わっているか、もう一度だけ確認してください。")
