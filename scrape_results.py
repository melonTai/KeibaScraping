from selenium import webdriver
from mypackage.page import result, const
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options


def main():
    root_path = "./data/results"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        race_id_list = []
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
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
            folder = f"{root_path}/{race.place}/{race.year}"
            if not os.path.exists(folder):
                os.makedirs(folder)
            file_path = f"{folder}/{race_id}.csv"
            if os.path.exists(file_path):
                continue
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
                for key, value in info.items():
                    df[key] = value
                df.to_csv(file_path)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
