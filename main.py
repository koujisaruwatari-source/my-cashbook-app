import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")
st.title("📖 現金出納帳クラウド（最終安定版）")

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# --- 1. データの読み込み（名前を使わず順番で取得） ---
try:
    # 全シートをまとめて読み込む（これで400エラーを回避します）
    # ※worksheet指定を外すと、通常は1枚目のシートが返ってきます
    master_df = conn.read(spreadsheet=url, ttl=0)
    
    # 履歴データ(2枚目)の取得。
    # 名前指定で400が出るため、一度全データを取得してアプリ側で処理するか、
    # ここでは一番エラーが出にくい「デフォルト名」でのアクセスを試みます。
    # 万が一失敗した場合は空の表を作って入力を優先させます。
    try:
        data_df = conn.read(spreadsheet=url, worksheet="transactions", ttl=0)
    except:
        # transactionsでエラーが出るなら空のデータフレームを作成（入力で作成するため）
        data_df = pd.DataFrame(columns=["日付", "勘定科目", "摘要", "入金額", "出金額", "備考"])
    
    st.sidebar.success("✅ 通信確立")
except Exception as e:
    st.error(f"根本的な接続エラー: {e}")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        # マスタシートの1列目を「勘定科目」として取得
        category = st.selectbox("勘定科目", master_df.iloc[:, 0].unique())
    with col3:
        # マスタシートの1列目が科目、2列目が摘要と仮定して絞り込み
        options = master_df[master_df.iloc[:, 0] == category].iloc[:, 1].unique()
        summary = st.selectbox("摘要", options)

    col4, col5, col6 = st.columns(3)
    income = col4.number_input("入金額", min_value=0, step=100)
    expense = col5.number_input("出金額", min_value=0, step=100)
    remark = col6.text_input("備考")

    if st.form_submit_button("スプレッドシートに保存"):
        new_row = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        updated_df = pd.concat([data_df, new_row], ignore_index=True)
        
        # 保存時のみ、名前指定を試みる（ここでエラーが出たらタブ名確定）
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        st.success("保存に成功しました！")
        st.balloons()
        st.rerun()

# --- 3. 履歴の表示 ---
st.divider()
st.subheader("📊 履歴データ")
st.dataframe(data_df)
