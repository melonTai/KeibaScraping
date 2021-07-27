import os
import glob
import pandas as pd
"""年ごとにcsvをまとめる関数"""

def bind_csv(path_list, output_path):
    df_all = pd.read_csv(path_list[0], index_col=0)
    for path in path_list[1::]:
        print(path)
        df = pd.read_csv(path, index_col=0)
        df_all = df_all.append(df)
    df_all.to_csv(output_path)

def bind_result_csv():
    print("bind result")
    for year in range(2008,2021):
        pattern_result = f"./data/results/05/{year}/*.csv"
        path_result_list = glob.glob(pattern_result, recursive=True)
        print(year)
        bind_csv(path_result_list, f"./data/results/05/{year}/{year}_all.csv")

def bind_race_history_csv():
    print("bind race history")
    path = "./data/horse/race_history"
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    for directory in files_dir:
        print(directory)
        path_list = glob.glob(f"{path}/{directory}/*.csv")
        bind_csv(path_list, f"{path}/{directory}/{directory}_all.csv")

def main():
    #bind_result_csv()
    bind_race_history_csv()

if __name__ == '__main__':
    main()