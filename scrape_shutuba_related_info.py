from package import scrape, const, utils
from package.page import RacePage
from selenium import webdriver
import os
import time
import sys
import pandas as pd
import pathlib
import signal
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from datetime import datetime
import re

def scrape_odds_and_save(race_id, folder):
    res = scrape.scrape_odds(race_id)
    data = res["data"]
    for key, df in data.items():
        path = f"{folder}/{key}.csv"
        df = df.drop_duplicates()
        df.to_csv(path, encoding="utf_8_sig")

def scrape_related_racehistory(race_id):
    root_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\race')
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    race_const = const.Race(race_id)
    # フォルダ作成
    folder = f"{root_path}/{race_const.place}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    # 過去に同様のデータを取得済みの場合はスキップ
    file_path = f"{folder}/{race_const.year}_all.csv"
    if os.path.exists(file_path):
        df_b = pd.read_csv(file_path, index_col=0, dtype=str)
        if df_b["race_id"].isin([race_id]).any():
            return None
    res = scrape.scrape_race(race_id)
    if res["status"]:
        # 重複を避けて保存
        df = res["data"]
        if os.path.exists(file_path):
            df_b = df_b.append(df)
            df_b.drop_duplicates(inplace=True)
            df_b.to_csv(file_path, encoding="utf_8_sig")
        else:
            df.to_csv(file_path, encoding="utf_8_sig")

def main(race_id):
    shutuba_id = race_id
    print("scrape shutuba")
    shutuba_res = scrape.scrape_shutuba(shutuba_id)
    if shutuba_res["status"]:
        # フォルダ生成
        title = shutuba_res["title"]
        race_const = const.Race(shutuba_id)
        date = shutuba_res["date"]
        date = date.replace("/","月")
        date = date + "" if "日" in date else date + "日"
        date = re.sub("\(.*?\)","",date)
        date_datetime = datetime.strptime(f"{shutuba_id[0:4]}年{date}", '%Y年%m月%d日')
        shutuba_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\shutuba')
        place = utils.place_decoder(race_const.place)
        root = f"{shutuba_path}/{race_const.year}/{race_const.year}{date_datetime.month:02}{date_datetime.day:02}/{place}{race_const.r}R{race_const.kai}回{race_const.day}日目{title}"
        if not os.path.exists(root):
            os.makedirs(root)
        sub_folder = f"{root}/related_histories"
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        odds_folder = f"{root}/odds"
        if not os.path.exists(odds_folder):
            os.makedirs(odds_folder)
        # 出馬データ保存
        df = shutuba_res["data"]
        path = f"{root}/shutuba.csv"
        df.to_csv(path, encoding="utf_8_sig")
        # オッズ保存
        print("scrape odds")
        scrape_odds_and_save(shutuba_id,odds_folder)
        # 馬の戦歴をスクレイピング
        horse_id_list = df["horse_id"].unique()

        print("scrape race histories")
        for horse_id in tqdm(horse_id_list):
            res = scrape.scrape_racehistory(horse_id)
            if not res["status"]:
                print("race_histories_error")
            else:
                horse_id = res["horse_id"]
                # print(horse_id)
                df = res["data"]
                df["日付"] = pd.to_datetime(df["日付"], format="%Y/%m/%d")
                df = df[df["日付"] < date_datetime]
                df = df.sort_values("日付", ascending=False)
                #レース直前にスクレイプする場合は[0:3]つけたほうが効率よし
                for race_id in df["race_id"].tolist()[0:4]:
                    # print(f" {race_id}")
                    for r in range(1, 13):
                        race_const = const.Race(race_id)
                        related_race_id = f"{race_const.year}{race_const.place}{race_const.kai}{race_const.day}{r:02}"
                        # print(f"  {related_race_id}")
                        scrape_related_racehistory(related_race_id) 
                        time.sleep(1)
                path = f"{sub_folder}/{horse_id}.csv"
                df.to_csv(path, encoding="utf_8_sig")
            time.sleep(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if len(sys.argv) < 2:
        print("引数が足りません")
        print("raceid")
        sys.exit()
    shutuba_id = sys.argv[1]
    main(shutuba_id)