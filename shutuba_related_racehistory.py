from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from mypackage import scrape
from mypackage.page import race
import os
import time
import sys
import pandas as pd
import pathlib

def main():
    if len(sys.argv) < 2:
        print("引数が足りません")
        print("raceid")
        sys.exit()
    shutuba_id = int(sys.argv[1])
    shutuba_res = scrape.scrape_shutuba(shutuba_id)
    if shutuba_res["status"]:
        # フォルダ生成
        title = shutuba_res["title"]
        shutuba_path = pathlib.WindowsPath(r'G:\マイドライブ\Keiba\data\shutuba')
        root = f"{shutuba_path}/{title}"
        if not os.path.exists(root):
            os.makedirs(root)
        sub_folder = f"{root}/related_histories"
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        # 出馬データ保存
        df = shutuba_res["data"]
        path = f"{root}/shutuba.csv"
        df.to_csv(path)
        # 馬の戦歴をスクレイピング
        horse_id_list = df["horse_id"].unique()
        race_driver = webdriver.Chrome()
        for res in scrape.scrape_horse_racehistories(horse_id_list):
            if res["status"]:
                df = res["data"]
                race_info_list = []
                for race_id in df["race_id"].tolist():
                    race_driver.get(f"https://db.netkeiba.com/race/{race_id}/")
                    race_page = race.RacePage(race_driver)
                    race_info = race_page.get_race_info()
                    race_info_list.append(race_info)
                df_race_info = pd.DataFrame(race_info_list)
                df = pd.concat([df, df_race_info], axis = 1)
                horse_id = res["horse_id"]
                path = f"{sub_folder}/{horse_id}.csv"
                df.to_csv(path)
            time.sleep(1)
        race_driver.close()

if __name__ == '__main__':
    main()