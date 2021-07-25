from selenium import webdriver
from mypackage.page import horse, const, result
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import glob
import time

def main():
    root_path = "./data/horse/race_history"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        results_path = "./data/results/05/**/*.csv"
        csv_path_list = glob.glob(results_path)
        df_results = pd.read_csv(csv_path_list[0], index_col=0)
        for path in csv_path_list[1::]:
            print(path)
            df = pd.read_csv(path, index_col=0)
            df_results = df_results.append(df)
        df_results.reset_index()
        horse_id_list = df_results["horse_id"].unique()
        print(horse_id_list)
        # options = Options()
        # options.add_argument('--headless')
        driver = webdriver.Chrome()
        for horse_id in horse_id_list:
            file_path = f"{root_path}/{horse_id}.csv"
            print(horse_id)
            if not os.path.exists(file_path):
                driver.get(f"https://db.netkeiba.com/horse/{horse_id}")
                horse_page = horse.HorsePage(driver)
                race_history = horse_page.get_race_history()
                df = pd.DataFrame(race_history)
                df.to_csv(file_path)
                time.sleep(1)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
