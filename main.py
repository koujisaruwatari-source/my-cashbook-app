import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📖 現金出納帳クラウド")

# スプレッドシートへの接続設定（後ほどGUIで設定します）
conn = st.connection("gsheets", type=GSheetsConnection)

st.write("接続テスト中...")
