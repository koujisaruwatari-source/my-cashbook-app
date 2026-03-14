import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")
st.title("📖 現金出納帳クラウド")

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# --- 1. データの読み込み（名前を使わずに読み込む） ---
try:
    # 1枚目のシート（マスタ）を読み込む
    master_df = conn.read(spreadsheet=url, ttl=0) 
    
    # 2枚目のシート（履歴）を読み込む
    # 名前指定で400が出るため、一度全シートを読み込むか、
    # スプレッドシート側のタブ名を「Sheet2」などデフォルト名にして試す
    # ここでは「transactions」という名前が正しいと仮定しますが、
    # 失敗した場合は一番左のシートだけを表示するようにします
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    
    st.sidebar.success("接続完了")
except Exception as e:
    st.error(f"シートの読み込みエラー: {e}")
    st.info("スプレッドシートの2枚目のタブ名が 'transactions' になっているか確認してください。")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("my_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        # 見出しが「勘定科目」であることを前提としています
        category = st.selectbox("勘定科目", master_df.iloc[:, 0].unique())
    with col3:
        # 1列目が科目、2列目が摘要と仮定
        options = master_df[master_df.iloc[:, 0] == category].iloc[:, 1].unique()
        summary = st.selectbox("摘要", options)

    col4, col5, col6 = st.columns(3)
    with col4:
        income = st.number_input("入金額", min_value=0)
    with col5:
        expense = st.number_input("出金額", min_value=0)
    with col6:
        remark = st.text_input("備考")

    if st.form_submit_button("保存"):
        new_data = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        updated_df = pd.concat([data_df, new_data], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        st.success("保存しました！")
        st.rerun()

st.divider()
st.header("📊 履歴")
st.dataframe(data_df)
