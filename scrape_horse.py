from selenium import webdriver
from mypackage.page import horse, const, result
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options


def main():
    root_path = "./data/horse/race_history"
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
            driver.get(f"https://db.netkeiba.com/race/{race_id}/")
            result_page = result.ResultPage(driver)
            result_list = result_page.get_result_list()
            if result_list:
                horse_id_list = [res["horse_id"] for res in result_list]
                for horse_id in horse_id_list:
                    file_path = f"{root_path}/{horse_id}.csv"
                    if not os.path.exists(file_path):
                        print(horse_id)
                        driver.get(f"https://db.netkeiba.com/horse/{horse_id}")
                        horse_page = horse.HorsePage(driver)
                        race_history = horse_page.get_race_history()
                        df = pd.DataFrame(race_history)
                        df.to_csv(file_path)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
