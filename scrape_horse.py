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

def main():
    if len(sys.argv) < 4:
        raise Exception("引数が足りません")
    root_path = "./data/results"
    year_start = int(sys.argv[1])
    year_end = int(sys.argv[2])
    place = int(sys.argv[3])
    now = datetime.datetime.now()

    if year_start < 2011:
        raise Exception("2011年より前は対応していません")
    elif year_start > year_end:
        raise Exception("終了年には開始年より大きな値を設定してください")
    elif year_end > now.year:
        raise Exception("未来の年は入力できません")
    
    if not place in [e.value for e in const.Place]:
        raise Exception("有効なレース場idではありません")
    root_path = "./data/horse/race_history"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        for place in [e.value for e in const.Place]:
            for year in range(year_start, year_end + 1):
                results_path = f"./data/results/{place:02}/{year}_all.csv"
                df_results = pd.read_csv(results_path, index_col=0)
                horse_id_list = df_results["horse_id"].unique()
                driver = webdriver.Chrome()
                for horse_id in horse_id_list:
                    year = str(horse_id)[0:4]
                    file_path = f"{root_path}/{year}_all.csv"
                    print(horse_id)
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


if __name__ == "__main__":
    main()
