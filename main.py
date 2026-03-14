import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 接続診断モード")

# SecretsからURLを取得
try:
    url = st.secrets["public_gsheets_url"]
    st.write(f"読み込んでいるURL: `{url}`")
except:
    st.error("Secretsに 'public_gsheets_url' が設定されていません。")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # URLを取得
    url = st.secrets["public_gsheets_url"]
    
    # シート名指定を「変数」にして分かりやすくする
    MASTER_SHEET = "master"        # ←スプレッドシートのタブ名と一致させる
    DATA_SHEET = "transactions"    # ←スプレッドシートのタブ名と一致させる

    # 読み込み実行
    master_df = conn.read(spreadsheet=url, worksheet=MASTER_SHEET)
    data_df = conn.read(spreadsheet=url, worksheet=DATA_SHEET)
    # シート名（worksheet）を指定せずに、まず「本体」を読み込む
    # これで失敗する場合はURL自体の不備です
    df = conn.read(spreadsheet=url)
    st.success("🎉 スプレッドシート本体への接続に成功しました！")
    st.write("一番左にあるシートの内容を表示します:")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"接続エラー詳細: {e}")
    st.info("URLを https://docs.google.com/spreadsheets/d/ID/edit の形式に直して再試行してください。")
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド（完成版）")

# 接続設定
conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# --- 1. データの読み込み ---
try:
    # シート名は実際のものに合わせてください（ここでは master / transactions と仮定）
    master_df = conn.read(spreadsheet=url, worksheet="master")
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    st.sidebar.success("データ同期中")
except Exception as e:
    st.error(f"シートの読み込みに失敗しました。シート名を確認してください。: {e}")
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
        # マスタから選んだ科目に紐づく摘要だけを表示
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
        # 保存用の新しい行を作成
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
st.header("📊 入出金履歴（最新10件）")
# 逆順にして新しいデータを上に表示
st.dataframe(data_df.sort_index(ascending=False).head(10), use_container_width=True)
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 シート名確認モード")

url = st.secrets["public_gsheets_url"]
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # シート全体を読み込んでみる
    df = conn.read(spreadsheet=url)
    st.success("接続自体は成功しています！")
    
    st.write("読み込まれたデータのプレビュー（最初のシート）:")
    st.dataframe(df.head())
    
    st.info("【ヒント】もし上の表がマスタなら、プログラムの worksheet='master' を worksheet='シート1' など、現在表示されているシートの正式名に直す必要があります。")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    
