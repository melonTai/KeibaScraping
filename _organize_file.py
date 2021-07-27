import os
import shutil
import glob
import pandas as pd

def organize_race_history():
    root = "./data/horse/race_history"
    path_list = glob.glob(f"{root}/*.csv")
    for path in path_list:
        print(path)
        year = os.path.splitext(os.path.basename(path))[0][0:4]
        folder = f"{root}/{year}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        shutil.move(path, folder)

def delete_except_all():
    pattern = "./data/**/*.csv"
    path_list = glob.glob(pattern, recursive=True)
    for path in path_list:
        if not "all" in path:
            print(path)
            os.remove(path)

def drop_unnamed():
    pattern = "./data/**/*.csv"
    path_list = glob.glob(pattern, recursive=True)
    for path in path_list:
        df = pd.read_csv(path, index_col=0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.to_csv(path)

if __name__ == '__main__':
    #organize_race_history()
    #delete_except_all()
    drop_unnamed()