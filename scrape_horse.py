from selenium import webdriver
from mypackage.page import horse, const, result
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import glob
import time
import sys

def main():
    root_path = "./data/horse/race_history"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    try:
        results_path = "./data/results/**/*.csv"
        csv_path_list = glob.glob(results_path)
        df_results = pd.read_csv(csv_path_list[0], index_col=0)
        for path in csv_path_list[1::]:
            print(path)
            df = pd.read_csv(path, index_col=0)
            df_results = df_results.append(df)
        df_results.reset_index()
        horse_id_list = df_results["horse_id"].unique()
        #print(horse_id_list)
        # options = Options()
        # options.add_argument('--headless')
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
