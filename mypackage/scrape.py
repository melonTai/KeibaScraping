from .page import horse, race, shutuba
from pprint import pprint
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time

def scrape_racehistory(horse_id:int):
    """馬の戦歴を取得する関数

    Args:
        horse_id (int): 馬のid

    Returns:
        dict: {"horse_id":int 馬のid, "data":pd.DataFrame 取得データ, "status":bool 取得成功失敗}
    """
    horse_page = horse.HorsePage(f"https://db.netkeiba.com/horse/{horse_id}")
    race_history = horse_page.get_race_history()
    if race_history:
        df = pd.DataFrame(race_history)
        df["horse_id"] = horse_id
        df["horse_title"] = horse_page.get_horse_title()
        return {"horse_id":horse_id, "data":df, "status":True}
    else:
        return {"horse_id":horse_id, "data":pd.DataFrame(), "status":False}

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

def scrape_race(race_id:int):
    """race_idに該当するレースの結果を取得する関数

    Args:
        race_id (int): レースのid

    Returns:
        dict: {"race_id":int, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    race_page = race.RacePage(f"https://db.netkeiba.com/race/{race_id}/")
    race_list = race_page.get_result_list()
    if race_list:
        course_info = race_page.get_course_info()
        title = race_page.get_title()
        race_info = race_page.get_race_info()
        info = {}
        info.update(**title, **race_info, **course_info)
        df = pd.DataFrame(race_list)
        df["race_id"] = race_id
        for key, value in info.items():
            df[key] = value
        return {"race_id":race_id, "data":df, "status":True}
    else:
        return {"race_id":race_id, "data":pd.DataFrame(), "status":False}

def scrape_races(race_id_list:list):
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
        race_id (int): レースのid

    Returns:
        dict: {"race_id":int, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    shutuba_page = shutuba.ShutubaPage(f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}")
    horse_list = shutuba_page.get_horse_list()
    title = shutuba_page.get_title()
    if horse_list:
        df = pd.DataFrame(horse_list)
        df["race_id"] = race_id
        return {"race_id":race_id, "title":title["title"], "data":df, "status":True}
    else:
        return {"race_id":race_id, "title":None, "data":pd.DataFrame(), "status":False}

def scrape_return(race_id):
    """race_idに該当するレースの配当を取得する関数

    Args:
        race_id (int): レースのid

    Returns:
        dict: {"race_id":int, "data":pd.DataFrame 取得したデータ, "status":bool 取得成功失敗}
    """
    result_page = race.RacePage(f"https://db.netkeiba.com/race/{race_id}/")
    return_list = result_page.get_return_list()

    if return_list:
        df = pd.DataFrame(return_list)
        df["race_id"] = race_id
        return {"race_id":race_id, "data":df, "status":True}
    else:
        return {"race_id":race_id, "data":pd.DataFrame(), "status":False}

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
    