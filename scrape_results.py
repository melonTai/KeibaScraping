from selenium import webdriver
from mypackage.page import result, const
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import time

def main():
    root_path = "./data/results"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        race_id_list = []
        driver = webdriver.Chrome()
        for year in range(2008, 2021):
            for place in range(5, 6):
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
            driver.get(f"https://db.netkeiba.com/race/{race_id}/")
            result_page = result.ResultPage(driver)
            result_list = result_page.get_result_list()

            if result_list:
                course_info = result_page.get_course_info()
                title = result_page.get_title()
                date = result_page.get_date()
                print(course_info,title,date)
                info = {}
                info.update(**title, **date, **course_info)
                df = pd.DataFrame(result_list)
                df["race_id"] = race_id
                for key, value in info.items():
                    df[key] = value
                if os.path.exists(file_path):
                    df_b = pd.read_csv(file_path, index_col=0)
                    df_b.append(df, inplace=True)
                    df_b.drop_duplicates(inplace=True)
                    df_b.to_csv(file_path)
                else:
                    df.to_csv(file_path)
            time.sleep(1)


    finally:
        driver.close()


if __name__ == "__main__":
    main()
