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
import selenium

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

    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        race_id_list = []
        driver = webdriver.Chrome()
        for place in [e.value for e in const.Place]:
            for year in range(year_start, year_end + 1):
                for kai in range(1, 11):
                    for day in range(1, 13):
                        for r in range(1, 13):         
                            race_id = f"{year}{place:02}{kai:02}{day:02}{r:02}"
                            race_id_list.append(race_id)

        for race_id in race_id_list:
            try:
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
                result_list = result_page.get_result_list()

                if result_list:
                    course_info = result_page.get_course_info()
                    title = result_page.get_title()
                    date = result_page.get_date()
                    print(title, date, course_info)
                    #print(course_info,title,date)
                    info = {}
                    info.update(**title, **date, **course_info)
                    df = pd.DataFrame(result_list)
                    df["race_id"] = race_id
                    for key, value in info.items():
                        df[key] = value
                    if os.path.exists(file_path):
                        df_b = df_b.append(df)
                        df_b.drop_duplicates(inplace=True)
                        df_b.to_csv(file_path)
                    else:
                        df.to_csv(file_path)
                time.sleep(1)
            except selenium.common.exceptions.TimeoutException:
                time.sleep(10)




    finally:
        driver.close()


if __name__ == "__main__":
    main()
