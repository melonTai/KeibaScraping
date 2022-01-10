import scrape_shutuba_related_info
from package import const, scrape
from package.page import RaceListPage, CalenderPage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import time
from datetime import datetime
import sys
import pathlib
import signal
from tqdm import tqdm
import re
from package import utils

def get_kaisai_race(kaisai_date):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(20)
    driver.get(f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}")
    page = RaceListPage(driver)
    race_id_list = page.get_race_id()
    driver.close()
    return race_id_list

def update_odds(shutuba_id):
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
        # # 出馬データ保存
        df = shutuba_res["data"]
        path = f"{root}/shutuba.csv"
        df.to_csv(path, encoding="utf_8_sig")
        # オッズ保存
        print("scrape odds")
        scrape_shutuba_related_info.scrape_odds_and_save(shutuba_id,odds_folder)

def update_odds_at_kaisai_date(kaisai_date):
    print("get_kaisai_race")
    race_id_list = get_kaisai_race(kaisai_date)
    print("start update")
    for race_id in tqdm(race_id_list):
        update_odds(race_id)

def main(kaisai_date):
    """kaisai_dateに渡された日程に開催されるレースの出馬表，および，指数算出に必要な関連レースを取得する

    Args:
        kaisai_date ([type]): [description]
    """
    race_id_list = get_kaisai_race(kaisai_date)
    try:
        for race_id in tqdm(race_id_list):
            scrape_shutuba_related_info.main(race_id)
    except Exception as e:
        print(race_id)
        raise Exception(e)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if len(sys.argv) < 2:
        print("引数が足りません")
        print("kaisai_date, ex.20210104")
        sys.exit()
    else:
        kaisai_date = sys.argv[1]
        if len(sys.argv) == 2:
            main(kaisai_date)
        elif len(sys.argv)>2:
            update_option = sys.argv[2]
            if update_option == "update_odds":
                update_odds_at_kaisai_date(kaisai_date)


    
    