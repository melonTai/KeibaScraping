import os
import glob
import pandas as pd

def reformat_result(path):
    df = pd.read_csv(path, index_col=0)
    race_id = os.path.splitext(os.path.basename(path))[0]
    df["race_id"] = race_id
    df.to_csv(path)

def reformat_race_history(path):
    df = pd.read_csv(path, index_col=0)
    horse_id = os.path.splitext(os.path.basename(path))[0]
    df["horse_id"] = horse_id
    df.to_csv(path)

def main():
    pattern_result = "./data/results/**/*.csv"
    pattern_race_history = "./data/horse/race_history/*.csv"
    path_result_list = glob.glob(pattern_result, recursive=True)
    path_rh_list = glob.glob(pattern_race_history, recursive=True)
    for path in path_result_list:
        print(path)
        reformat_result(path)
    for path in path_rh_list:
        print(path)
        reformat_race_history(path)


if __name__ == '__main__':
    main()