import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# アプリのレイアウト設定
st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド")

# スプレッドシートへの接続
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み
try:
    url = st.secrets["public_gsheets_url"]
    # masterシートとtransactionsシートを読み込む
    # ※スプレッドシートのタブ名がこれと違う場合は書き換えてください
    master_df = conn.read(spreadsheet=url, worksheet="master")
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    st.sidebar.success("スプレッドシートに接続中")
except Exception as e:
    st.error(f"接続エラー: {e}")
    st.info("SecretsのURL設定や、シート名（master, transactions）を確認してください。")
    st.stop()

# --- 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        # マスタから勘定科目のリストを取得
        category_list = master_df["勘定科目"].unique()
        category = st.selectbox("勘定科目", category_list)
    with col3:
        # 選んだ科目に合う摘要だけを絞り込む
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
        # 新しい行の作成
        new_row = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        # 既存データに新しい行をくっつける
        updated_df = pd.concat([data_df, new_row], ignore_index=True)
        
        # スプレッドシートの transactions シートを更新
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        st.success("保存しました！")
        st.balloons()
        # 画面を更新して最新の履歴を表示
        st.rerun()

# --- 履歴の表示 ---
st.divider()
st.header("📊 入出金履歴")
# 履歴を新しい順に表示
st.dataframe(data_df.sort_index(ascending=False), use_container_width=True)
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 スプレッドシート診断")

url = st.secrets["public_gsheets_url"]
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # シート名を指定せずに、まず接続できるか確認
    df = conn.read(spreadsheet=url)
    st.success("スプレッドシート本体への接続は成功しました！")
    
    # 実際のスプレッドシートにあるタブ名（シート名）を表示させたいですが、
    # 簡易的に最初の5行を表示して構造を確認します
    st.write("現在読み込めているデータ（一番左のシート）:")
    st.dataframe(df.head())
    
    st.info("この表が『マスタ』の内容なら、プログラムの worksheet='master' を worksheet='(このシートの名前)' に書き換えてください。")

except Exception as e:
    st.error(f"接続そのものに失敗しています: {e}")
    st.warning("スプレッドシートの共有設定を『リンクを知っている全員』＋『編集者』にしているか再確認してください。")
