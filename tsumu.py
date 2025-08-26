import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 定数 ---
# データを保存するCSVファイルの名前
CSV_FILE = 'tsum_coin_log.csv'

# --- 関数の定義 ---

def initialize_data():
    """
    データファイルが存在しない場合に、見出し(ヘッダー)だけのファイルを作成する関数
    """
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            '日付', 'プレイ前コイン', 'プレイ後コイン', '獲得コイン', 'プレイ回数', '使用ツム', 'メモ'
        ])
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def load_data():
    """
    CSVファイルからデータを読み込む関数
    """
    return pd.read_csv(CSV_FILE)

def save_data(df):
    """
    DataFrameをCSVファイルに保存する関数
    """
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

# --- Streamlitアプリのメイン処理 ---

def main():
    # ページの基本設定
    st.set_page_config(page_title="ツムツム コイン記録アプリ", layout="wide")

    st.title('🪙 ツムツム コイン記録アプリ')
    st.caption('日々のコイン獲得を記録し、グラフで可視化しましょう。')

    # データファイルの初期化（初回起動時のみ実行される）
    initialize_data()

    # --- サイドバー (入力フォーム) ---
    st.sidebar.header('今日のコインを記録')
    # st.formを使うと、中の要素をまとめて送信できる
    with st.sidebar.form(key='record_form', clear_on_submit=True):
        date = st.date_input('日付', datetime.today())
        before_coins = st.number_input('プレイ前コイン', min_value=0, step=1000)
        after_coins = st.number_input('プレイ後コイン', min_value=0, step=1000)
        plays = st.number_input('プレイ回数（任意）', min_value=0, step=1)
        used_tsum = st.text_input('メイン使用ツム（任意）')
        memo = st.text_area('メモ（任意）')
        submit_button = st.form_submit_button('✨ 記録する')

    # 「記録する」ボタンが押されたときの処理
    if submit_button:
        if after_coins < before_coins:
            st.sidebar.error('プレイ後コインはプレイ前コインより少なくすることはできません。')
        else:
            # 獲得コインを計算
            earned_coins = after_coins - before_coins
            # 新しい記録を作成
            new_data = pd.DataFrame({
                '日付': [date.strftime('%Y-%m-%d')],
                'プレイ前コイン': [int(before_coins)],
                'プレイ後コイン': [int(after_coins)],
                '獲得コイン': [int(earned_coins)],
                'プレイ回数': [int(plays)],
                '使用ツム': [used_tsum],
                'メモ': [memo]
            })
            # 既存のデータを読み込み、新しいデータを追加
            df = load_data()
            df_updated = pd.concat([df, new_data], ignore_index=True)
            # 保存
            save_data(df_updated)
            st.sidebar.success('記録しました！')
            st.balloons()


    # --- メイン画面 (データ表示・可視化) ---
    df = load_data()

    if df.empty:
        st.info('まだ記録がありません。左のサイドバーから今日のコインを記録しましょう！')
    else:
        st.header('📊 ダッシュボード')

        # 総獲得コインをメトリックで表示
        total_earned_coins = df['獲得コイン'].sum()
        st.metric(label="総獲得コイン枚数", value=f"{total_earned_coins:,.0f} コイン")

        # 可視化のために日付データを変換
        df_chart = df.copy()
        df_chart['日付'] = pd.to_datetime(df_chart['日付'])

        # --- グラフ表示 ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('日別のコイン獲得数')
            # 日付でグループ化して獲得コインを合計
            daily_earned_coins = df_chart.groupby(df_chart['日付'].dt.date)['獲得コイン'].sum()
            st.bar_chart(daily_earned_coins)

        with col2:
            st.subheader('月別のコイン獲得数')
            # 月でグループ化して獲得コインを合計
            df_chart['月'] = df_chart['日付'].dt.to_period('M').astype(str)
            monthly_earned_coins = df_chart.groupby('月')['獲得コイン'].sum()
            st.bar_chart(monthly_earned_coins)

        #test
        st.header('📖 記録一覧')
        # 日付の降順（新しいものが上）で表示
        st.dataframe(df.sort_values(by='日付', ascending=False), use_container_width=True)


if __name__ == '__main__':
    main()