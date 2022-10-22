from .page import HorsePage, JockeyResultPage, JockeySearchResultPage, RacePage, ShutubaPage, OddsPage, JockeySearchDetailPage, JockeySearchResultPageLocators
from pprint import pprint
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

def scrape_jockey_race_history(jockey_id, year, field):
    """jockey_idに指定された騎手のyear年に開催されたfield(芝|ダート)のレース戦績を取得する．

    Args:
        jockey_id (str): 騎手id
        year (int): レース開催年
        field (str): 'te'(芝), 'de'(ダート)
    """
    url = f'https://db.netkeiba.com/?pid=jockey_select&id={jockey_id}&year={year}&mode={field}&course=&page=1'
    jockey_result_page = JockeyResultPage(url)
    num = jockey_result_page.get_result_num()
    loop_num = int(num/20)+1
    df_jockey_rh = pd.DataFrame()
    for i in range(loop_num):
        try:
            url = f'https://db.netkeiba.com/?pid=jockey_select&id={jockey_id}&year={year}&mode={field}&course=&page={i+1}'
            jockey_result_page = JockeyResultPage(url)
            df = jockey_result_page.get_result_list()
            df_jockey_rh = pd.concat([df_jockey_rh, df])
        except Exception as e:
            continue
    return df_jockey_rh

def scrape_jockey_list():
    url = 'https://db.netkeiba.com/?pid=jockey_search_detail'
    jockey_search_detail_page = JockeySearchDetailPage(url)
    jockey_search_result_page = jockey_search_detail_page.move_to_jockey_search_result_page()
    i=1
    df_jockey = pd.DataFrame()
    for i in tqdm(range(30)):
        df = jockey_search_result_page.get_jockey_list()
        i+=1
        jockey_search_result_page = jockey_search_result_page.paging(i)
        df_jockey = pd.concat([df_jockey, df])
        if len(df)==0:
            break
    return df_jockey

def scrape_odds(race_id: str):
    """レースIDに該当するレースの全オッズを取得する．

    Args:
        race_id (str): レースid

    Returns:
        pandas.DataFrame: オッズのデータフレーム
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
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
    except Exception as e:
        print(e)
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
    if len(race_history) > 0:
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
    try:
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
            return {"race_id": race_id, "data": df_race, "status": True}
        else:
            return {"race_id": race_id, "data": pd.DataFrame(), "status": False}
    except Exception as e:
        print(race_id)
        raise Exception(e)


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
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    try:
        driver.get(f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}")
        shutuba_page = ShutubaPage(driver)
        df_horse = shutuba_page.get_horse_list()
        title = shutuba_page.get_title()
        date = shutuba_page.get_date()
        race_info = shutuba_page.get_race_info()
        index_list = race_info.index
        for ind in index_list:
            df_horse[ind] = race_info[ind]
        if len(df_horse) > 0:
            df_horse["race_id"] = str(race_id)
            return {"race_id": race_id, "title": title["title"], "date": date["date"], "data": df_horse, "status": True}
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
