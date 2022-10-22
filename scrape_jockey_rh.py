from scrapenetkeiba import scrape
import pandas as pd
from tqdm import tqdm
import os

def main():
    path = r'D:\Keiba\data\raw\jockey\jockey_list.pkl'
    df_jockey_list = pd.read_pickle(path)
    jockey_id_list = df_jockey_list['jockey_id'].unique()
    dst_folder = r'D:\Keiba\data\raw\jockey\race_history'
    search_params = []
    for year in range(2010, 2022):
        for field in ['te', 'de']:
            search_params.append((year, field))
    for jockey_id in tqdm(jockey_id_list):
        print(jockey_id)
        dst = os.path.join(dst_folder, f'{jockey_id}.pkl')
        if os.path.exists(dst):
            continue
        df_jockey_rh = pd.DataFrame()
        for year, field in tqdm(search_params):
            df = scrape.scrape_jockey_race_history(jockey_id, year, field)
            df_jockey_rh = pd.concat([df_jockey_rh, df])
        df_jockey_rh['jockey_id'] = jockey_id
        df_jockey_rh.to_pickle(dst)
# 478まで回した
if __name__ == '__main__':
    main()