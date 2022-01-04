import scrape_shutuba_related_info
from package import const, scrape
from package.page import RaceListPage, CalenderPage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import time
import datetime
import sys
import pathlib
import signal
from tqdm import tqdm

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

def main(kaisai_date):
    """kaisai_dateに渡された日程に開催されるレースの出馬表，および，指数算出に必要な関連レースを取得する

    Args:
        kaisai_date ([type]): [description]
    """
    race_id_list = get_kaisai_race(kaisai_date)
    for race_id in tqdm(race_id_list):
        scrape_shutuba_related_info.main(race_id)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if len(sys.argv) < 2:
        print("引数が足りません")
        print("kaisai_date, ex.20210104")
        sys.exit()
    kaisai_date = sys.argv[1]
    main(kaisai_date)