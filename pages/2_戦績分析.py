import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSVファイルパス
CSV_FILE = 'mahjong_scores.csv'

# ---関数定義----
def get_player_list():
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        df=pd.read_csv(CSV_FILE)
        return sorted(df["プレイヤー名"].unique())
    return[]

#データを全消去
def reset_all_records():
    """全記録（CSVファイル）を削除する関数"""
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        return True
    return False

def delete_last_game():
    """直前のゲーム記録（同じゲームIDを持つ全ての行）を削除する関数"""
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return False
    
    df = pd.read_csv(CSV_FILE)

    #記録されているゲームが一つしかない場合、ファイルを空にする
    if df["ゲームID"].nunique() <= 1:
        #ファイルを空にする
        pd.DataFrame(columns = df.columns).to_csv(CSV_FILE,index = False)

    else:
        #最新のゲームIDを特定
        last_game_id = df["ゲームID"].max()
        # 最新のゲームIDを持つ行以外を新しいデータフレームとして残す
        df_new = df[df["ゲームID"] != last_game_id]
        # 新しいデータフレームでCSVファイルを上書き保存
        df_new.to_csv(CSV_FILE, index = False)
    return True

#収支分析セクション
st.header("個人別 収支分析")
player_list_for_analysis = get_player_list()
if player_list_for_analysis :
    #分析対象のプレイヤーを選択
    selected_player = st.selectbox("分析するプレイヤーを選択",player_list_for_analysis)

    df = pd.read_csv(CSV_FILE)
    player_df = df[df["プレイヤー名"] == selected_player].copy()
    if not player_df.empty:
        try:
            # 1. 平均場代を計算
            # ゲームIDで重複を削除してから場代の平均を計算
            unique_games = df.drop_duplicates(subset=["ゲームID"])
            avg_badai = unique_games["場代"].mean()

            # 2. 選択されたプレイヤーのデータを抽出
            player_df["記録日時"] = pd.to_datetime(player_df["記録日時"])
            player_df = player_df.sort_values("記録日時")

            #3.損得を計算
            # 各ゲームのプレイヤー数を計算
            player_counts= df.groupby("ゲームID")["プレイヤー名"].transform("count")
            df["人数"] = player_counts
            # プレイヤーごとのデータに人数をマージ
            player_df = pd.merge(player_df, df[["ゲームID","人数"]].drop_duplicates(), on="ゲームID")

            # 損得 = 収支 - (個人の場代負担額)
            player_df['損得'] = -(player_df['収支'] - (player_df['場代'] / player_df['人数']))

            # 4. 累計収支を計算
            player_df["累計収支"] = player_df["損得"].cumsum()

            # 5. 結果を表示
            col1,col2 = st.columns(2)
            col1.metric("累計収支", f"{player_df['収支'].mean():.0f}円")
            avg_rank = player_df["順位"].mean()
            col2.metric("平均順位",f"{avg_rank:.2f}位")

            st.write(f"{selected_player}さんの累計収支の推移")
            #グラフ表示用にデータを整形
            chart_data = player_df[["記録日時","累計収支"]].set_index("記録日時")
            st.line_chart(chart_data)

            st.write("###対戦履歴（収支詳細")
            st.dataframe(player_df[["記録日時","順位","場代","損得","累計収支"]].sort_values("記録日時",ascending=False))
        except FileNotFoundError:
            st.warning("記録ファイルが見つかりません。記録ページからデータを入力してください。")
        except Exception as e:
            st.error("データの分析中にエラーが発生しました。CSVファイルに問題がある可能性があります。")
            st.error(f"エラー詳細:{e}")
        else:
            st.info("選択されたプレイヤーの記録がありません")
else: 
    st.info("分析できるデータがまだ記録されていません")

# --- サイドバーにリセット機能を追加 ---
st.sidebar.header("⚙️設定")

# --- 直前の記録を削除 ---
with st.sidebar.expander("直前の対戦記録を削除"):
    st.warning("注意：この操作は元に戻せません！")
    st.write("最後に入力した1ゲーム分の記録が削除されます。")
    
    if st.button("はい、直前の記録を削除します"):
        if delete_last_game():
            st.success("直前の記録を削除しました。ページを更新します。")
            st.rerun()
        else:
            st.info("削除する記録がありませんでした。")

# st.expanderで折りたたみメニューを作成し、危険な操作を隠す
with st.sidebar.expander("全記録をリセットする"):
    st.warning("注意:この操作は元に戻せません！")
    st.write("すべての対戦記録が完全に削除されます。本当によろしいですか？")

    #確認用のテキスト入力を追加
    confirmation_text = st.text_input("上記を理解した上で、「リセット」と入力してください")

    # 入力されたテキストが"リセット"と一致するかどうかでボタンを無効化
    is_button_disabled = (confirmation_text != "リセット")    

    #確認用のボタン
    if st.button("はい、すべての記録を削除します", disabled = is_button_disabled):
        if reset_all_records():
            st.success("全記録をリセットしました。ページを更新します。")
            #ページを強制的にリロードして表示をクリアする
            st.rerun()
        else:
            st.info("削除する記録はありませんでした。")