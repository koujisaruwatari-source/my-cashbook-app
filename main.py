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
    st.info("SecretsのURLが '/edit' で終わっているか、もう一度だけ確認してください。")import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳", layout="wide")
st.title("📖 現金出納帳クラウド")

conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# --- 1. データの読み込み ---
try:
    # 1枚目のマスタを読み込む
    master_df = conn.read(spreadsheet=url, worksheet="master", ttl=0)
    # 2枚目の履歴を読み込む
    data_df = conn.read(spreadsheet=url, worksheet="transactions", ttl=0)
    st.sidebar.success("✅ データ同期中")
except Exception as e:
    st.error(f"シートの読み込みでエラーが発生しました。タブ名が 'master' と 'transactions' になっているか確認してください。: {e}")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        category = st.selectbox("勘定科目", master_df.iloc[:, 0].unique())
    with col3:
        options = master_df[master_df.iloc[:, 0] == category].iloc[:, 1].unique()
        summary = st.selectbox("摘要", options)

    col4, col5, col6 = st.columns(3)
    income = col4.number_input("入金額", min_value=0, step=100)
    expense = col5.number_input("出金額", min_value=0, step=100)
    remark = col6.text_input("備考")

    if st.form_submit_button("スプレッドシートに保存"):
        # 新しいデータを作成
        new_row = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        # 既存のデータに結合
        updated_df = pd.concat([data_df, new_row], ignore_index=True)
        
        # 保存実行
        try:
            conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
            st.success("スプレッドシートへの保存に成功しました！")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"保存に失敗しました。共有設定が『編集者』になっているか確認してください。: {e}")

# --- 3. 履歴の表示 ---
st.divider()
st.subheader("📊 直近の履歴")
st.dataframe(data_df.sort_index(ascending=False).head(10), use_container_width=True)
