from selenium import webdriver
from mypackage.page import race
from mypackage import const, scrape
import pandas as pd
import os
import time
import datetime
import sys
import pathlib
import signal

def main():
    # フォルダ生成
    root_path = pathlib.WindowsPath(r'D:\マイドライブ\Keiba\data')
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    df_missing_horse = pd.read_csv(f"{root_path}/horse/race_history/missing_horse.csv")
    # 過去レースから馬のidリストを取得
    horse_id_list = df_missing_horse["horse_id"].unique()

    # 各馬の過去戦歴をスクレイピング
    for horse_id in horse_id_list:
        print(horse_id)
        # フォルダ作成
        folder = f"{root_path}/horse/race_history"
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 過去に同様のデータを取得済みの場合はスキップ
        file_path = f"{folder}/{str(horse_id)[0:4]}_all.csv"
        time.sleep(1)
        print(file_path)
        res = scrape.scrape_racehistory(horse_id)
        if res["status"]:
            df = res["data"]
            if not os.path.exists(file_path):
                df.to_csv(file_path, encoding="utf_8_sig")
                continue

            df_b = pd.read_csv(file_path, index_col=0, dtype=str, encoding='utf_8')
            # 重複を避けて保存
            for index, row in df.iterrows():
                print(f" {row['race_id']}")
                is_same_race_and_horse_with_df_b = (df_b["horse_id"] == str(row["horse_id"])) & (df_b["race_id"] == str(row["race_id"]))
                if not is_same_race_and_horse_with_df_b.any():
                    print(" append")
                    df_b = df_b.append(row)
                df_b.to_csv(file_path,encoding="utf_8_sig")
                
        
            

   


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
