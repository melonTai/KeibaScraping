from selenium import webdriver
import selenium
from .page import horse, race, shutuba
from . import const
from pprint import pprint
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
import time
import datetime

def scrape_horse_racehistories(horse_id_list):
    """horse_id_list中のhorse_idに該当する競走馬のデータを
    スクレイピングしてDataFrame型で返すジェネレータ

    Args:
        horse_id_list ([List(int)]): horse_idのリスト

    Yields:
        [dict]: {"horse_id":int, "data":pd.DataFrame, "status":bool}
    """
    driver = webdriver.Chrome()
    try:
        for horse_id in horse_id_list:
            try:
                print(horse_id)
                driver.get(f"https://db.netkeiba.com/horse/{horse_id}")
                horse_page = horse.HorsePage(driver)
                race_history = horse_page.get_race_history()
                df = pd.DataFrame(race_history)
                df["horse_id"] = horse_id
                df["horse_title"] = horse_page.get_horse_title()
                yield {"horse_id":horse_id, "data":df, "status":True}
                time.sleep(1)
            except selenium.common.exceptions.TimeoutException as e:
                yield {"horse_id":horse_id, "data":pd.DataFrame(), "status":False}
                time.sleep(10)
            
    finally:
        driver.close()

def scrape_races(race_id_list:list):
    """race_id_list中のrace_idに該当する
    レース情報をスクレイピングしてpd.DataFrame型で返す

    Args:
        race_id_list (list): race_idのリスト

    Yields:
        dict: {"race_id":int, "data":pd.DataFrame, "status":bool}
    """
    driver = webdriver.Chrome()
    try:
        for race_id in race_id_list:
            try:
                print(race_id)
                driver.get(f"https://db.netkeiba.com/race/{race_id}/")
                race_page = race.RacePage(driver)
                race_list = race_page.get_result_list()

                if race_list:
                    course_info = race_page.get_course_info()
                    title = race_page.get_title()
                    race_info = race_page.get_date()
                    info = {}
                    info.update(**title, **race_info, **course_info)
                    df = pd.DataFrame(race_list)
                    df["race_id"] = race_id
                    for key, value in info.items():
                        df[key] = value
                    yield {"race_id":race_id, "data":df, "status":True}
                else:
                    yield {"race_id":race_id, "data":pd.DataFrame(), "status":False}

                time.sleep(1)
            except selenium.common.exceptions.TimeoutException:
                yield {"race_id":race_id, "data":pd.DataFrame(), "status":False}
                time.sleep(10)
    finally:
        driver.close()

def scrape_shutuba(race_id):
    driver = webdriver.Chrome()
    try:
        print(race_id)
        driver.get(f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}")
        shutuba_page = shutuba.ShutubaPage(driver)
        horse_list = shutuba_page.get_horse_list()
        title = shutuba_page.get_title()
        if horse_list:
            df = pd.DataFrame(horse_list)
            df["race_id"] = race_id
            return {"race_id":race_id, "title":title["title"], "data":df, "status":True}
        else:
            return {"race_id":race_id, "title":None, "data":pd.DataFrame(), "status":False}

    except selenium.common.exceptions.TimeoutException:
        return {"race_id":race_id, "title":None, "data":pd.DataFrame(), "status":False}

    finally:
        driver.close()



if __name__ == "__main__":
    path = "./tests/shutuba.csv"
    df = pd.read_csv(path, index_col=0)
    horse_id_list = df["horse_id"].unique()
    