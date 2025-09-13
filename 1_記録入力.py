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

def save_data(record_to_add):
    new_df = pd.DataFrame(record_to_add)

    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE)>0:
        new_df.to_csv(CSV_FILE,mode = "a", header=False,index=False)
    else:
        new_df.to_csv(CSV_FILE,index=False)  
    st.success("戦績を記録しました")

#----------------------メイン機能-----------------------------
st.title('麻雀戦績記録アプリ')

#過去のプレイヤーリストを取得
player_list = get_player_list()
player_list_with_new = ["(新規プレイヤー)"]+player_list

#タブを作成
tab1,tab2 = st.tabs(["詳細入力","簡易入力"])

#------------------詳細入力タブ----------------------
with tab1:
    #入力フォーム
    with st.form(key='detail_form'):
        st.header("新規対戦記録")
        #ゲーム全体の設定
        badai =st.number_input("このゲームの場代(円)",min_value=0,value=1000,step=100)
        start_score = st.number_input("配給原点",value = 25000, step = 10000)
        num_players = st.number_input("プレイ人数",min_value=3,max_value=4,value=4,step=1)

        #順位ごとの場代負担率
        st.subheader("順位ごとの場代負担率(%)")
        cols = st.columns(num_players)
        payment_ratios = []
        # デフォルトの負担率を設定
        default_ratios = {4:[0,25,25,50], 3:[0,25,75]}

        for i in range(num_players):
            with cols[i]:
                # 順位の添字 (例: 4人なら 0,1,2,3 -> 1位,2位,3位,4位)
                rank_display = i + 1
                ratio = st.number_input(f'{rank_display}位の負担率',min_value = 0, max_value = 100, value = default_ratios[num_players][i], step = 5, key = f"ratio_{i}")
                payment_ratios.append(ratio)
        # プレイヤー情報とスコアを格納するリスト
        players_data = []

        # 選択された人数分だけ入力欄を動的に生成
        for i in range(num_players):
            st.markdown(f"---")#区切り線

            # 既存プレイヤー選択 or 新規プレイヤー入力
            selected_player = st.selectbox(f"プレイヤー{i+1}",player_list_with_new,key=f"player_select_{i}")

            player_name = ""
            if selected_player == "(新規プレイヤー)":
                player_name = st.text_input("新しいプレイヤー名を入力",key=f"player_new_{i}")
            else:
                player_name = selected_player

            score = st.number_input(f"スコア{i+1}",value=start_score,step=1000,key=f"score_{i}")
            if player_name:
                players_data.append({"name":player_name,"score":score})
        submit_button = st.form_submit_button(label='この内容で記録する')

    #データ保存処理
    if submit_button:
        #4人の麻雀のスコア合計チェック
        total_score = sum(p["score"]for p in players_data)
        is_total_ok = (num_players == 4 and total_score == start_score*4) or (num_players == 3 and total_score == start_score*3)

        if not is_total_ok:
            st.error(f"4人の麻雀の合計が{start_score*4}になっていません。")
        elif len(players_data) != num_players:
            st.error("プレイヤー名が入力されていない欄があります。")
        else:
            #順位を決定
            players_data.sort(key = lambda p_n: p_n["score"], reverse =True)
            for rank,p_data in enumerate (players_data,1):
                p_data["rank"] = rank
            
            game_id = int(datetime.now().timestamp())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

            record_to_add = []
            for rank_index, p in enumerate(players_data):
                rank = rank_index + 1
                #各プレイヤーの収支を計算
                badai_payment = badai*(payment_ratios[rank_index]/100.0)

                record_to_add.append({
                    "ゲームID":game_id,
                    "記録日時":timestamp,
                    "プレイヤー名":p["name"],
                    "順位":p["rank"],
                    "場代":badai,
                    "収支":badai_payment, 
                })
            save_data(record_to_add)

# ----------------- 簡易入力タブ -----------------
with tab2:
    with st.form(key = "quick_form"):
        st.header("新規対戦記録")
        #ゲーム設定
        q_badai = st.number_input("このゲームの場代(円)", min_value=0, value=1000, step=100, key='q_badai')
        q_num_players = st.number_input("プレイ人数", min_value=3, max_value=4, value=4, step=1, key='q_num_players')
    
        #順位ごとの場代負担率
        st.subheader("順位ごとの場代負担率(%)")
        q_cols = st.columns(q_num_players)
        q_payment_ratios = []
        
        # デフォルトの負担率を設定
        q_default_ratios = {4:[0,25,25,50], 3:[0,25,75]}
        for i in range(q_num_players):
            with q_cols[i]:
                # 順位の添字 (例: 4人なら 0,1,2,3 -> 1位,2位,3位,4位)
                q_rank_display = i + 1
                q_ratio = st.number_input(f'{q_rank_display}位の負担率',min_value = 0, max_value = 100, value = default_ratios[num_players][i], step = 5, key = f"q_ratio_{i}")
                q_payment_ratios.append(q_ratio)
        # プレイヤー情報とスコアを格納するリスト
        players_data = []

        # 選択された人数分だけ入力欄を動的に生成
        for i in range(q_num_players):
            st.markdown(f"---")#区切り線

            # 既存プレイヤー選択 or 新規プレイヤー入力
            selected_player = st.selectbox(f"プレイヤー{i+1}",player_list_with_new,key=f"q_player_select_{i}")

            player_name = ""
            if selected_player == "(新規プレイヤー)":
                player_name = st.text_input("新しいプレイヤー名を入力",key=f"q_player_new_{i}")
            else:
                player_name = selected_player

            rank = st.number_input("順位",min_value = 1, max_value = q_num_players ,value=1,step=1,key=f"rank_{i}")
            ranks = [p["rank"] for p in players_data]
            if player_name:
                players_data.append({"name":player_name,"rank":rank})
        q_submit_button = st.form_submit_button(label='この内容で記録する')

#データ保存処理
if q_submit_button:
    if len(players_data) != q_num_players:
        st.error("プレイヤー名が入力されていない欄があります。")

    elif len(ranks) != len(set(ranks)): 
        st.error("順位が重複しています。") 
    else:
        game_id = int(datetime.now().timestamp())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        record_to_add = []
        for p in players_data:
            #各プレイヤーの収支を計算
            q_badai_payment = q_badai*(q_payment_ratios[rank-1]/100.0)

            record_to_add.append({
                "ゲームID":game_id,
                "記録日時":timestamp,
                "プレイヤー名":p["name"],
                "順位":p["rank"],
                "場代":badai,
                "収支":q_badai_payment, 
            })
        save_data(record_to_add)
