from scrapenetkeiba import const, scrape
from scrapenetkeiba.page import RaceListPage, CalenderPage
import pandas as pd
import os
import time
import datetime
import sys
import pathlib
import signal
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def main():
    # 入力チェック
    if len(sys.argv) < 3:
        raise Exception("引数が足りません\nstart_year end_year [place]")
    
    # 入力格納 
    year_start = int(sys.argv[1])
    year_end = int(sys.argv[2])
    place = sys.argv[3] if len(sys.argv) > 3 else None

    # 入力チェック
    now = datetime.datetime.now()
    if year_start < 2008:
        raise Exception("2008年より前は対応していません")
    elif year_start > year_end:
        raise Exception("終了年には開始年より大きな値を設定してください")
    elif year_end > now.year:
        raise Exception("未来の年は入力できません")
    if place is not None and not place in [e.value for e in const.PlaceChuo]+[e.value for e in const.PlaceChiho] + ["chuo"] + ["chiho"]:
        raise Exception("有効なレース場idではありません")
    
    # フォルダ生成
    root_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\race')
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    
    # place_list
    place_list = []
    if place is None:
        place_list = [e.value for e in const.PlaceChuo] + [e.value for e in const.PlaceChiho]
    elif place is not None:
        if place == "chuo":
            place_list = [e.value for e in const.PlaceChuo]
        elif place == "chiho":
            place_list = [e.value for e in const.PlaceChiho]
        else:
            place_list =[int(place)]
    
    race_id_folder = "./race_id"
    if not os.path.exists(race_id_folder):
        os.makedirs(race_id_folder)

    year_list = list(range(int(year_start), int(year_end+1), 1))

    # レースid生成
    race_id_list = []
    for year in tqdm(year_list):
        path = f"{race_id_folder}/race_id_{year}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0, dtype=str)
            race_id_list.extend(df["race_id"].values.tolist())
        else:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('log-level=2')
            race_list_driver = webdriver.Chrome(options=options)
            race_list_driver.implicitly_wait(20)
            race_list_driver.get(f"https://race.netkeiba.com/top/race_list.html")
            race_list_page = RaceListPage(race_list_driver)
            for month in tqdm(range(1, 13)):
                calender_driver = webdriver.Chrome(options=options)
                calender_driver.implicitly_wait(20)
                calender_driver.get(f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}")
                calender_page = CalenderPage(calender_driver)
                kaisai_dates = calender_page.get_kaisai_date_list()
                calender_page.close()
                for kaisai_date in tqdm(kaisai_dates):
                    race_list_page.update_url(f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}")
                    _race_id_list = race_list_page.get_race_id()
                    if os.path.exists(path):
                        df_race_id = pd.read_csv(path, index_col=0)
                        df = pd.DataFrame(_race_id_list, columns=["race_id"], dtype=str)
                        df_race_id = df_race_id.append(df)
                        df_race_id.to_csv(path)
                    else:
                        df_race_id = pd.DataFrame(_race_id_list, columns=["race_id"], dtype=str)
                        df_race_id.to_csv(path)
                    race_id_list.extend(_race_id_list)
                    time.sleep(1)
            race_list_page.close()

    race_id_list = list(filter(lambda race_id : int(const.Race(race_id).place) in place_list, race_id_list))

    # スクレイピング
    for race_id in tqdm(race_id_list):
        # print(race_id)
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
                continue
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
        time.sleep(1)
   


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
