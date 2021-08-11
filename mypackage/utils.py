from selenium.webdriver.remote.webdriver import WebDriver
from . import const
from .page import result
import pandas as pd
import numpy as np
import re
def get_ref_time(driver:WebDriver, race_id):
    race = const.Race(race_id)
    ref_result_list = []
    for i in range(1,4):
        year = int(race.year) - i
        past_race_id = f"{year}{race.place}{race.kai}{race.day}{race.r}"
        driver.get(f"https://db.netkeiba.com/race/{past_race_id}/")
        result_page = result.ResultPage(driver)
        result_list = result_page.get_result_list()
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