from scrapenetkeiba import scrape
import pandas as pd

def main():
    dst = r"D:\Keiba\data\raw\jockey\jockey_list.pkl"
    df_jockey = scrape.scrape_jockey_list()
    df_jockey.to_pickle(dst)
    print(df_jockey)

if __name__ == '__main__':
    main()