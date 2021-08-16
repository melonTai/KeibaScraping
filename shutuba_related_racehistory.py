from mypackage import scrape
import os
import time

def main():
    shutuba_id = 202101020211
    shutuba_res = scrape.scrape_shutuba(shutuba_id)
    root = f"./data/shutuba/{shutuba_id}"
    if not os.path.exists(root):
        os.makedirs(root)
    sub_folder = f"{root}/related_histories"
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
    if shutuba_res["status"]:
        df = shutuba_res["data"]
        path = f"{root}/shutuba.csv"
        df.to_csv(path)
        horse_id_list = df["horse_id"].unique()
        for res in scrape.scrape_horse_racehistories(horse_id_list):
            if res["status"]:
                df = res["data"]
                horse_id = res["horse_id"]
                path = f"{sub_folder}/{horse_id}.csv"
                df.to_csv(path)
            time.sleep(1)

if __name__ == '__main__':
    main()