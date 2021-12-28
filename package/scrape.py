from .page import HorsePage, RacePage, ShutubaPage, OddsPage
from pprint import pprint
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver


def scrape_odds(race_id: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(20)
    driver.get(f"https://race.netkeiba.com/odds/index.html?race_id={race_id}")
    odds_page = OddsPage(driver)
    try:
        print("win")
        win = odds_page.get_win()
        print("place")
        place = odds_page.get_place()
        print("exacta")
        exacta = odds_page.get_exacta()
        print("quinella")
        quinella = odds_page.get_quinella()
        print("quinella_place")
        quinella_place = odds_page.get_quinella_place()
        print("trifecta")
        trifecta = odds_page.get_trifecta()
        print("trio")
        trio = odds_page.get_trio()
        data = {"単勝": win, "複勝": place, "馬単": exacta, "馬連": quinella,
                "ワイド": quinella_place, "3連複": trio, "3連単": trifecta}
        return {"race_id": race_id, "data": data, "status": True}
    
    finally:
        driver.close()


def scrape_racehistory(horse_id: str):
    """馬の戦歴を取得する関数

    Args:
        horse_id (str): 馬のid

    Returns:
        dict: {"horse_id":int 馬のid, "data":pd.DataFrame 取得データ, "status":bool 取得成功失敗}
    """
    horse_page = HorsePage(f"https://db.netkeiba.com/horse/{horse_id}")
    race_history = horse_page.get_race_history()
    if race_history:
        df = race_history
        df["horse_id"] = str(horse_id)
        df["horse_title"] = str(horse_page.get_horse_title())
        return {"horse_id": horse_id, "data": df, "status": True}
    else:
        return {"horse_id": horse_id, "data": pd.DataFrame(), "status": False}


def scrape_racehistories(horse_id_list):
    """horse_id_list中のhorse_idに該当する競走馬のデータを
    スクレイピングしてDataFrame型で返すジェネレータ

    Args:
        horse_id_list ([List(int)]): horse_idのリスト

    Yields:
        [dict]: {"horse_id":int, "data":pd.DataFrame, "status":bool}
    """
    for horse_id in horse_id_list:
        yield scrape_racehistory(horse_id)
        time.sleep(1)


def scrape_race(race_id: str):
    """race_idに該当するレースの結果を取得する関数

    Args:
        race_id (str): レースのid

    Returns:
        dict: {"race_id":str, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    race_page = RacePage(f"https://db.netkeiba.com/race/{race_id}/")
    df_race = race_page.get_result_list()
    if len(df_race) > 0:
        course_info = race_page.get_course_info()
        title = race_page.get_title()
        race_info = race_page.get_race_info()
        info = {}
        # print(title, race_info, course_info)
        info.update(**title, **race_info, **course_info)
        df_race["race_id"] = str(race_id)
        for key, value in info.items():
            df_race[key] = str(value)
        return {"race_id": race_id, "data": df, "status": True}
    else:
        return {"race_id": race_id, "data": pd.DataFrame(), "status": False}


def scrape_races(race_id_list: list):
    """race_id_list中のrace_idに該当する
    レース情報をスクレイピングしてpd.DataFrame型で返す

    Args:
        race_id_list (list): race_idのリスト

    Yields:
        dict: {"race_id":int, "data":pd.DataFrame, "status":bool}
    """
    for race_id in race_id_list:
        yield scrape_race(race_id)


def scrape_shutuba(race_id):
    """race_idに該当するレースの出場場を取得する関数

    Args:
        race_id (str): レースのid

    Returns:
        dict: {"race_id":str, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}")
        shutuba_page = ShutubaPage(driver)
        df_horse = shutuba_page.get_horse_list()
        title = shutuba_page.get_title()
        date = shutuba_page.get_date()
        if len(df_horse) > 0:
            df_horse["race_id"] = str(race_id)
            return {"race_id": race_id, "title": title["title"], "date": date["date"], "data": df, "status": True}
        else:
            return {"race_id": race_id, "title": None, "date": None, "data": pd.DataFrame(), "status": False}
    finally:
        driver.close()

def scrape_return(race_id):
    """race_idに該当するレースの配当を取得する関数

    Args:
        race_id (str): レースのid

    Returns:
        dict: {"race_id":int, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    result_page = RacePage(f"https://db.netkeiba.com/race/{race_id}/")
    return_list = result_page.get_return_list()

    if return_list:
        df = pd.DataFrame(return_list, dtype=str)
        df["race_id"] = str(race_id)
        return {"race_id": race_id, "data": df, "status": True}
    else:
        return {"race_id": race_id, "data": pd.DataFrame(), "status": False}


def scrape_returns(race_id_list):
    """race_id_list中の各race_idに該当するレースの配当を取得するジェネレータ

    Args:
        race_id_list (List[int]): レースidのリスト

    Yields:
        dict: {"race_id":int, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    for race in race_id_list:
        yield scrape_return(race)


if __name__ == "__main__":
    path = "./tests/shutuba.csv"
    df = pd.read_csv(path, index_col=0)
    horse_id_list = df["horse_id"].unique()
