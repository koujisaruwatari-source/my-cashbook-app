import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド")

# Secretsに登録したURLを使って接続
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # スプレッドシートを読み込む（マスタシートを指定する例）
    # ※シート名が「マスタ」なら worksheet="マスタ" と指定
    df = conn.read(spreadsheet=st.secrets["public_gsheets_url"])
    
    st.success("スプレッドシートへの接続に成功しました！")
    st.subheader("データプレビュー")
    st.dataframe(df)

except Exception as e:
    st.error(f"接続エラーが発生しました: {e}")
    st.info("Secretsに正しいURLが設定されているか、スプレッドシートの共有設定が『リンクを知っている全員』になっているか確認してください。")
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="現金出納帳アプリ", layout="wide")

st.title("📖 現金出納帳クラウド")

# 接続設定
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. マスタと既存データの読み込み ---
try:
    url = st.secrets["public_gsheets_url"]
    # マスタ情報を取得
    master_df = conn.read(spreadsheet=url, worksheet="master")
    # 履歴を取得
    data_df = conn.read(spreadsheet=url, worksheet="transactions")
    
    st.sidebar.success("接続済み")
except Exception as e:
    st.error(f"接続エラー: {e}")
    st.stop()

# --- 2. 入力フォーム ---
st.header("➕ 新規データ入力")
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("日付")
    with col2:
        category = st.selectbox("勘定科目", master_df["勘定科目"].unique())
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
        # 新しい行を作成
        new_row = pd.DataFrame([{
            "日付": date.strftime("%Y-%m-%d"),
            "勘定科目": category,
            "摘要": summary,
            "入金額": income,
            "出金額": expense,
            "備考": remark
        }])
        
        # 既存データと結合
        updated_df = pd.concat([data_df, new_row], ignore_index=True)
        
        # スプレッドシートを更新
        conn.update(spreadsheet=url, worksheet="transactions", data=updated_df)
        st.balloons()
        st.success("保存が完了しました！")
        # 再読み込み
        st.rerun()

# --- 3. 履歴の表示 ---
st.header("📊 入出金履歴")
# 最新のデータを表示
st.dataframe(data_df.sort_index(ascending=False), use_container_width=True)
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Secretsの確認用
if "public_gsheets_url" not in st.secrets:
    st.error("Secretsに 'public_gsheets_url' が見つかりません！")
else:
    url = st.secrets["public_gsheets_url"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # シート名を指定せずに一番左のシートを読み込む
    df = conn.read(spreadsheet=url)
    st.write("接続に成功しました！一番左のシートを表示します：")
    st.dataframe(df)
    
