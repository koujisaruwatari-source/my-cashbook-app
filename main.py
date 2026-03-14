import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド")

# 接続設定
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. データの読み込み ---
try:
    url = st.secrets["public_gsheets_url"]
    # スプレッドシートからマスタと履歴を読み込む
    master_df = conn.read(spreadsheet=url, worksheet="master")
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    st.sidebar.success("データ同期中")
except Exception as e:
    st.error(f"データの読み込みに失敗しました。シート名(master/transactions)を確認してください。: {e}")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        category_list = master_df["勘定科目"].unique()
        category = st.selectbox("勘定科目", category_list)
    with col3:
        filtered_summaries = master_df[master_df["勘定科目"] == category]["摘要"].tolist()
        summary = st.selectbox("摘要", filtered_summaries)
        
    col4, col5, col6 = st.columns(3)
    with col4:
        income = st.number_input("入金額", min_value=0, step=100)
    with col5:
        expense = st.number_input("出金額", min_value=0, step=100)
    with col6:
        remark = st.text_input("備考")
        
    submitted = st.form_submit_button("スプレッドシートに保存")

    if submitted:
        new_row = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        # 既存データと結合して更新
        updated_df = pd.concat([data_df, new_row], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        
        st.success("保存が完了しました！")
        st.balloons()
        st.rerun()

# --- 3. 履歴の表示 ---
st.divider()
st.header("📊 入出金履歴")
st.dataframe(data_df.sort_index(ascending=False), use_container_width=True)
