from selenium import webdriver
from mypackage.page import horse, result
from mypackage import const
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import glob
import time
import sys
import datetime

def scrape_horse(horse_id_list):
    driver = webdriver.Chrome()
    try:
        root_path = "./data/horse/race_history"
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        for horse_id in horse_id_list:
            print(horse_id)
            year = str(horse_id)[0:4]
            folder = f"{root_path}"
            if not os.path.exists(folder):
                os.makedirs(folder)
            file_path = f"{folder}/{horse_id}.csv"
            driver.get(f"https://db.netkeiba.com/horse/{horse_id}")
            horse_page = horse.HorsePage(driver)
            race_history = horse_page.get_race_history()
            df = pd.DataFrame(race_history)
            df["horse_id"] = horse_id
            df["horse_title"] = horse_page.get_horse_title()
            if os.path.exists(file_path):
                df_b = pd.read_csv(file_path, index_col=0)
                df_b = df_b.append(df)
                df_b.drop_duplicates(inplace=True)
                df_b.to_csv(file_path)
            else:
                df.to_csv(file_path)
            time.sleep(1)
    finally:
        driver.close()

def scrape_horse_in_year_place(year,place):
    now = datetime.datetime.now()
    if year < 2011:
        raise Exception("2011年より前は対応していません")
    elif year > now.year:
        raise Exception("未来の年は入力できません")
    
    if not place in [e.value for e in const.Place]:
        raise Exception("有効なレース場idではありません")
    driver = webdriver.Chrome()
    try:
        results_path = f"./data/results/{place:02}/{year}_all.csv"
        df_results = pd.read_csv(results_path, index_col=0)
        horse_id_list = df_results["horse_id"].unique()
        scrape_horse(driver, horse_id_list)

    finally:
        driver.close()



if __name__ == "__main__":
    path = "./tests/shutuba.csv"
    df = pd.read_csv(path, index_col=0)
    horse_id_list = df["horse_id"].unique()
    scrape_horse(horse_id_list)