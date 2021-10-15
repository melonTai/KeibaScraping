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
from tqdm import tqdm

def main():
    # フォルダ生成
    root_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\race')
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    df_missing_race = pd.read_pickle(f"{root_path}/missing_race.pkl")
    # 過去レースから馬のidリストを取得
    race_id_list = df_missing_race["race_id"].unique()

    # スクレイピング
    for race_id in tqdm(race_id_list):
        print(race_id)
        race_const = const.Race(race_id)
        # フォルダ作成
        folder = f"{root_path}/{race_const.place}"
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        # 過去に同様のデータを取得済みの場合はスキップ
        file_path = f"{folder}/{race_const.year}_all.csv"
        if os.path.exists(file_path):
            df_b = pd.read_csv(file_path, index_col=0, dtype=str)

        res = scrape.scrape_race(race_id)
        if res["status"]:
            # 重複を避けて保存
            df = res["data"]
            print(df.head())
            if os.path.exists(file_path):
                indexer = df_b["race_id"] == race_id
                df_old = df_b[~indexer]
                df_b = pd.concat([df_old, df])
                df_b.to_csv(file_path, encoding="utf_8_sig")
            else:
                df.to_csv(file_path, encoding="utf_8_sig")
        time.sleep(1)
                
        
            

   


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
