import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")

st.title("📖 現金出納帳クラウド")

# 接続設定
conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# --- 1. データの読み込み ---
try:
    # シート名を指定して読み込み
    master_df = conn.read(spreadsheet=url, worksheet="master")
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
except Exception as e:
    st.error("データの読み込みに失敗しました。")
    st.info("スプレッドシートのタブ名が 'master' と 'transactions' になっているか確認してください。")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
# フォームを使うことで、ボタンを押すまで送信されないようにします
with st.form("my_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        category = st.selectbox("勘定科目", master_df["勘定科目"].unique())
    with col3:
        # 選んだ科目に合う摘要だけをリストにする
        options = master_df[master_df["勘定科目"] == category]["摘要"].unique()
        summary = st.selectbox("摘要", options)

    col4, col5, col6 = st.columns(3)
    with col4:
        income = st.number_input("入金額", min_value=0, step=100)
    with col5:
        expense = st.number_input("出金額", min_value=0, step=100)
    with col6:
        remark = st.text_input("備考")

    submitted = st.form_submit_button("スプレッドシートに保存")

    if submitted:
        # 新しい行の作成
        new_data = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        # 既存データと結合
        updated_df = pd.concat([data_df, new_data], ignore_index=True)
        
        # スプレッドシートを更新（書き込み）
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        
        st.success("保存しました！")
        st.balloons()
        st.rerun() # 画面を更新して最新の表を表示

# --- 3. 履歴の表示 ---
st.divider()
st.header("📊 入出金履歴")
# 最新の10件を上に表示
st.dataframe(data_df.sort_index(ascending=False).head(10), use_container_width=True)
