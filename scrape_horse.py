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
    # 入力チェック
    if len(sys.argv) < 3:
        raise Exception("引数が足りません\nstart_year end_year [place]")
    
    # 入力格納 
    year_start = int(sys.argv[1])
    year_end = int(sys.argv[2])
    place = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # 入力チェック
    now = datetime.datetime.now()
    if year_start < 2008:
        raise Exception("2008年より前は対応していません")
    elif year_start > year_end:
        raise Exception("終了年には開始年より大きな値を設定してください")
    elif year_end > now.year:
        raise Exception("未来の年は入力できません")
    if place is not None and not place in [e.value for e in const.PlaceChuo]+[e.value for e in const.PlaceChiho]:
        raise Exception("有効なレース場idではありません")
    
    # フォルダ生成
    root_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data')
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    
    # レースid生成
    race_path_list = []
    place_list = [e.value for e in const.PlaceChuo] + [e.value for e in const.PlaceChiho] if place is None else [f"{place:02}"]
    for place in place_list:
        for year in range(year_start, year_end + 1):
            race_path = f"{root_path}/race/{place:02}/{year}_all.csv"
            race_path_list.append(race_path)

    # 過去レース取得
    df_race = pd.DataFrame()
    for race_path in race_path_list:
        if os.path.exists(race_path):
            df = pd.read_csv(race_path, index_col=0, dtype=str)
            df_race = df_race.append(df)
    
    # 過去レースから馬のidリストを取得
    horse_id_list = df_race["horse_id"].unique()

    # 各馬の過去戦歴をスクレイピング
    for horse_id in tqdm(horse_id_list):
        print(horse_id)
        # フォルダ作成
        folder = f"{root_path}/horse/race_history2"
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 過去に同様のデータを取得済みの場合はスキップ
        file_path = f"{folder}/{horse_id}.csv"
        time.sleep(1)
        print(file_path)
        res = scrape.scrape_racehistory(horse_id)
        if res["status"]:
            df = res["data"]
            if not os.path.exists(file_path):
                df.to_csv(file_path, encoding="utf_8_sig")
                continue

            # 重複を避けて保存
            df_b = pd.read_csv(file_path, index_col=0, dtype=str, encoding='utf_8')
            df_old = df_b[~df_b["race_id"].isin(df["race_id"])]
            df_b = pd.concat([df_old, df])
            df_b.to_csv(file_path,encoding="utf_8_sig")
            
                
        
            

   


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
