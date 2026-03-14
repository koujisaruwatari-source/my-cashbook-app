import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")
st.title("📖 現金出納帳クラウド")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    url = st.secrets["public_gsheets_url"]
    
    # 読み込みテスト
    st.write("🔄 データを読み込み中...")
    master_df = conn.read(spreadsheet=url, worksheet="master")
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    
    st.success("✅ 接続成功！入力フォームを表示します。")

    # --- 入力フォーム ---
    with st.form("input_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("日付")
        with col2:
            # マスタの1列目を科目として使用
            category = st.selectbox("勘定科目", master_df.iloc[:, 0].unique())
        with col3:
            # 科目に合う摘要を表示
            options = master_df[master_df.iloc[:, 0] == category].iloc[:, 1].unique()
            summary = st.selectbox("摘要", options)

        col4, col5 = st.columns(2)
        income = col4.number_input("入金額", min_value=0)
        expense = col5.number_input("出金額", min_value=0)
        remark = st.text_input("備考")

        if st.form_submit_button("スプレッドシートに保存"):
            new_row = pd.DataFrame([{"日付": str(date), "勘定科目": category, "摘要": summary, "入金額": income, "出金額": expense, "備考": remark}])
            updated_df = pd.concat([data_df, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
            st.balloons()
            st.rerun()

    st.divider()
    st.subheader("📊 履歴")
    st.dataframe(data_df)

except Exception as e:
    st.error(f"⚠️ エラーが発生しました: {e}")
    if "400" in str(e):
        st.warning("【解決策】スプレッドシートのタブ名が 'master' と 'transactions' になっているか、URLの末尾に #gid=... が残っていないか再確認してください。")
    st.stop()
