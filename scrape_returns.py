from selenium import webdriver
from mypackage.page import result
from mypackage import const
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import time
import datetime
import sys

def main():
    if len(sys.argv) < 4:
        raise Exception("引数が足りません")
    root_path = "./data/returns"
    year_start = int(sys.argv[1])
    year_end = int(sys.argv[2])
    place = int(sys.argv[3])
    now = datetime.datetime.now()

    if year_start < 2008:
        raise Exception("2008年より前は対応していません")
    elif year_start > year_end:
        raise Exception("終了年には開始年より大きな値を設定してください")
    elif year_end > now.year:
        raise Exception("未来の年は入力できません")
    
    if not place in [e.value for e in const.Place]:
        raise Exception("有効なレース場idではありません")

    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        race_id_list = []
        driver = webdriver.Chrome()
        for place in [e.value for e in const.PlaceChuo]:
            for year in range(year_start, year_end + 1):
                for kai in range(1, 11):
                    for day in range(1, 13):
                        for r in range(1, 13):
                            race_id = f"{year}{place:02}{kai:02}{day:02}{r:02}"
                            race_id_list.append(race_id)

        for race_id in race_id_list:
            print(race_id)
            race = const.Race(race_id)
            folder = f"{root_path}/{race.place}"
            if not os.path.exists(folder):
                os.makedirs(folder)
            file_path = f"{folder}/{race.year}_all.csv"
            if os.path.exists(file_path):
                df_b = pd.read_csv(file_path, index_col=0)
                if df_b["race_id"].isin([int(race_id)]).any():
                    continue
            driver.get(f"https://db.netkeiba.com/race/{race_id}/")
            result_page = result.ResultPage(driver)
            return_list = result_page.get_return_list()

            if return_list:
                df = pd.DataFrame(return_list)
                df["race_id"] = race_id
                if os.path.exists(file_path):
                    if not race_id in df["race_id"]:
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
