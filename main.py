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
    # シート名（worksheet）を指定せずに、まず「本体」を読み込む
    # これで失敗する場合はURL自体の不備です
    df = conn.read(spreadsheet=url)
    st.success("🎉 スプレッドシート本体への接続に成功しました！")
    st.write("一番左にあるシートの内容を表示します:")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"接続エラー詳細: {e}")
    st.info("URLを https://docs.google.com/spreadsheets/d/ID/edit の形式に直して再試行してください。")
