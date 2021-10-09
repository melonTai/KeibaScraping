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
    root_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\odds')
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    
    # レースid生成
    race_id_list = []
    place_list = [e.value for e in const.PlaceChuo] + [e.value for e in const.PlaceChiho] if place is None else [place]
    for place in place_list:
        for year in range(year_start, year_end + 1):
            for kai in range(1, 11):
                for day in range(1, 13):
                    for r in range(1, 13):         
                        race_id = f"{year}{place:02}{kai:02}{day:02}{r:02}"
                        race_id_list.append(race_id)

    # スクレイピング
    for race_id in race_id_list:
        try:
            print(race_id)
            race_const = const.Race(race_id)
            # フォルダ作成
            folder = f"{root_path}/{race_const.place}"
            if not os.path.exists(folder):
                os.makedirs(folder)
            # 過去に同様のデータを取得済みの場合はスキップ
            ticket_list = ["単勝", "複勝", "馬単", "馬連", "ワイド", "3連複", "3連単"]
            is_gotten = {}
            for ticket in ticket_list:
                file_path = f"{folder}/{race_const.year}_{ticket}.csv"
                if os.path.exists(file_path):
                    df_b = pd.read_csv(file_path, index_col=0)
                    if df_b["race_id"].isin([int(race_id)]).any():
                        is_gotten[ticket] = True
                    else:
                        is_gotten[ticket] = False
                else:
                    is_gotten[ticket] = False
            if not False in is_gotten.values():
                continue
            res = scrape.scrape_odds(race_id, "headless")
            if res["status"]:
                data = res["data"]
                for ticket, df in data.items():
                    file_path = f"{folder}/{race_const.year}_{ticket}.csv"
                    df["race_id"] = race_id
                    if os.path.exists(file_path):
                        df_b = pd.read_csv(file_path, index_col=0)
                        df_b = df_b.append(df)
                        df_b.drop_duplicates(inplace=True)
                        df_b.to_csv(file_path)
                    else:
                        df.to_csv(file_path)
            time.sleep(1)
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
