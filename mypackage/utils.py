from selenium.webdriver.remote.webdriver import WebDriver
from . import const
from .page import race
import pandas as pd
import numpy as np
import re
def __place2int(num):
    try:
        return int(num)
    except ValueError:
        return 1e3
def place_decoder(num):
    num = __place2int(num)
    if num == 1:
        return "札幌"
    elif num == 2:
        return "函館"
    elif num == 3:
        return "福島"
    elif num == 4:
        return "新潟"
    elif num == 5:
        return "東京"
    elif num == 6:
        return "中山"
    elif num == 7:
        return "中京"
    elif num == 8:
        return "京都"
    elif num == 9:
        return "阪神"
    elif num == 10:
        return "小倉"
    elif num == 42:
        return "浦和"
    elif num == 43:
        return "船橋"
    elif num == 44:
        return "大井"
    elif num == 45:
        return "川崎"
    elif num == 46:
        return "門別"
    elif num == 47:
        return "盛岡"
    elif num == 48:
        return "水沢"
    elif num == 49:
        return "金沢"
    elif num == 50:
        return "笠松"
    elif num == 51:
        return "名古屋"
    elif num == 52:
        return "園田"
    elif num == 53:
        return "姫路"
    elif num == 54:
        return "高知"
    elif num == 55:
        return "佐賀"
    elif num == 56:
        return "帯広"
    else:
        return "その他"
def get_ref_time(race_id):
    race_const = const.Race(race_id)
    ref_result_list = []
    for i in range(1,4):
        year = int(race_const.year) - i
        past_race_id = f"{year}{race_const.place}{race_const.kai}{race_const.day}{race_const.r}"
        race_page = race.RacePage(f"https://db.netkeiba.com/race/{past_race_id}/")
        result_list = race_page.get_result_list()
        ref_result_list.extend(result_list)
    df = pd.DataFrame(ref_result_list)
    def convert_time(x:str):
        pattern = "(\d*):(\d{2}.\d{1})"
        match = re.findall(pattern, x)
        if match:
            min, sec= match[0]
            return float(min)*60 + float(sec)
        return np.nan
    df["time"] = df["タイム"].apply(convert_time)
    return df["time"].mean()