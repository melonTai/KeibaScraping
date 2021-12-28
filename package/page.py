# selenium
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# beautifulsoup
from bs4 import BeautifulSoup
import bs4

# request
import requests

# 標準モジュール
import time
import re

# pandas
import pandas as pd

# 各ページの各要素にアクセスするためのロケーター(xpathやcssセレクタ等)の定義
from .locators import CalenderPageLocators
from .locators import HorsePageLocators
from .locators import OddsPageLocators
from .locators import RaceListPageLocators
from .locators import RacePageLocators
from .locators import ResultPageLocators
from .locators import ShutubaPageLocators


class BasePageRequest(object):
    """
    各ページクラスのベース
    特に，UI操作を必要としない(seleniumを使わない)，値を取得するだけのページのベースとして用いる
    """                         
    def __init__(self,url:str):
        """request用のベースクラス

        Args:
            url (str): url
        """
        self.url = url
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        header = {
            'User-Agent': user_agent
        }
        try:
            res = requests.get(self.url, headers=header, timeout=30)
        except requests.exceptions.ConnectionError as e:
            time.sleep(30)
            res = requests.get(self.url, headers=header, timeout=30)
        self.soup = BeautifulSoup(res.content.decode("euc-jp", "ignore"), 'html.parser')

class BasePageSelenium(object):
    """
    各ページクラスのベース
    特に，UI操作を必要とする(seleniumを使う)，ページのベースとして用いる

    Args:
        object ([type]): [description]
    """
    def __init__(self, driver:WebDriver):
        """selenium用ベースクラスのコンストラクタ

        Args:
            driver (WebDriver): webDriver
        """
        self.driver = driver
        self.url = driver.current_url
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def update_url(self, url:str):
        self.driver.implicitly_wait(20)
        self.driver.get(url)
        self.url = self.driver.current_url
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def close(self):
        self.driver.close()

class CalenderPage(BasePageSelenium):
    """ページ例：https://race.netkeiba.com/top/calendar.html?year=2020&month=7
    """
    def is_url_matches(self):
        cur_url = self.url
        return "calendar.html" in cur_url
    
    def get_kaisai_date_list(self):
        kaisai_date_elements = self.soup.select(CalenderPageLocators.KAISAI_DATE[1])
        pattern = "race_list.html\?kaisai_date=(\d*)"
        kaisai_dates = []
        for element in kaisai_date_elements:
            url = element.attrs["href"]
            matches = re.findall(pattern, url)
            if matches:
                kaisai_date = matches[0]
                kaisai_dates.append(kaisai_date)
        return kaisai_dates

class HorsePage(BasePageRequest):
    """ページ例：https://db.netkeiba.com/horse/2019105283/
    """

    def is_url_matches(self):
        cur_url = self.url
        return "horse" in cur_url
    
    def __get_id(self, element:bs4.element, pattern):
        atag_elements = element.select("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.attrs["href"]
            match = re.findall(pattern, url)
            if match:
                jockey_id = match[0]
                return jockey_id
        return None


    def get_race_history(self):
        dfs = pd.read_html(str(self.soup), match="レース名")
        if dfs:
            df = dfs[0]
            racename_elements = self.soup.select(HorsePageLocators.RACE_HISTORY_RACENAME[1])
            jockeyname_elements = self.soup.select(HorsePageLocators.RACE_HISTORY_JOCKEYNAME[1])
            df["race_id"] = list(map(lambda x:self.__get_id(x, "race/(.*?)/"), racename_elements))
            df["jockey_id"] = list(map(lambda x:self.__get_id(x, "jockey/(.*?)/"), jockeyname_elements))
            df = df.astype(str)
            return df
        else:
            return []

    def get_features(self):
        # 適正の見出しを取得
        features_key_elements = self.soup.select(HorsePageLocators.FEATURES_HEAD[1])
        # 見出しWeb要素を文字列に変換
        features_key = [re.sub(r"\s", "", element.get_text()) for element in features_key_elements]
        # 適正の行リストを取得
        features_table_element = self.soup.select(HorsePageLocators.FEATURES_TABLE[1])[0]
        # 行リストをフォーマット
        features_value_elements = features_table_element.select("td")
        features_value = [self.__get_left_width(element) for element in features_value_elements]
        df = pd.DataFrame(features_value, index=features_key, columns=["value"])
        df.index.name = "key"
        df = df.astype(str)
        return df
    
    def __get_left_width(self, element: bs4.element):
        """tdの中の左の青画像の幅を取得する

        Args:
            element (WebElement): imgタグを持つtd要素

        Returns:
            [type]: 青棒画像の幅
        """
        images = element.select("img")
        left_img = images[1]
        return left_img.attrs["width"]
    
    def get_horse_title(self):
        horse_title_elements = self.soup.select(HorsePageLocators.HORSE_TITLE[1])
        if not horse_title_elements:
            return None
        horse_title_element = horse_title_elements[0]
        text = horse_title_element.get_text()
        horse_title = re.sub(r"\s", "", text)
        return horse_title
    
    def get_profile(self):
        dfs = pd.read_html(self.url, match="生年月日", index_col=0)
        df = dfs[0]
        df.index.name = "key"
        df.columns = ["value"]
        trainer_element = self.soup.select(HorsePageLocators.PROFILE_TRAINER[1])[0] 
        df.loc["trainer_id", "prof_value"] = self.__get_id(trainer_element, "trainer/(.*?)/")
        owner_element = self.soup.select(HorsePageLocators.PROFILE_OWNER[1])[0]
        df.loc["owner_id", "prof_value"] = self.__get_id(owner_element, "owner/(.*?)/")
        breeder_element  = self.soup.select(HorsePageLocators.PROFILE_BREEDER[1])[0]
        df.loc["breeder_id", "prof_value"] = self.__get_id(breeder_element, "breeder/(.*?)/")
        df = df.astype(str)
        return df

class OddsPage(BasePageSelenium):
    """ページ例：https://race.netkeiba.com/odds/index.html?race_id=202105040211
    """
    def is_url_matches(self):
        cur_url = self.url
        return "odds/index.html?race_id=" in cur_url

    def update_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def change_url(self,url:str):
        self.driver.implicitly_wait(20)
        self.driver.get(url)
        time.sleep(2)
        self.update_soup()
    
    def __get_one_odds(self,type_,tan):
        """馬単，複勝で使う．馬番と対応するオッズを取得

        Args:
            type_ (str): urlのtypeに入れるパラメータ

        Returns:
            dict: 取得結果
        """
        url = self.url+f"&type={type_}"
        self.change_url(url)
        locator = OddsPageLocators.WIN[1] if tan else OddsPageLocators.PLACE[1]
        tr_elements = self.soup.select(locator + " tr")
        if tr_elements:
            header = ["馬番","オッズ"]
            data = []
            for tr in tr_elements[1::]:
                td_elements = tr.select('td')
                num = re.sub(r"\s", "", td_elements[1].get_text())
                odds = re.sub(r"\s", "", td_elements[5].get_text())
                values = [num, odds]
                data.append(dict(zip(header, values)))
            df = pd.DataFrame(data, dtype=str)
            return df
        return None

    def __get_combi_odds(self,type_):
        """馬連，馬単，ワイド，3連複，3連単の中で使う．
        2通りの組み合わせをとってくる関数．

        Args:
            type_ (str): urlのtypeに入れるパラメータ

        Returns:
            dict: 取得結果
        """
        url = self.url+f"&type={type_}&housiki=c99"
        self.change_url(url)
        ninki_select_element = self.driver.find_element_by_css_selector(OddsPageLocators.NINKI_SELECT[1])
        data = []
        select = Select(ninki_select_element)
        select_len = len(select.options)
        for index in range(1, select_len-1):
            time.sleep(1.0)
            # selectエレメント更新
            try:
                ninki_select_element = self.driver.find_element_by_css_selector(OddsPageLocators.NINKI_SELECT[1])
                select = Select(ninki_select_element)
                select.select_by_index(index)
            except selenium.common.exceptions.StaleElementReferenceException:
                time.sleep(1.0)
                ninki_select_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(OddsPageLocators.NINKI_SELECT))
                select = Select(ninki_select_element)
                ninki_select_option_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(OddsPageLocators.NINKI_SELECT))
                time.sleep(1.0)
                select.select_by_index(index)
            self.update_soup()

            tr_elements = self.soup.select(OddsPageLocators.NINKI_TABLE[1] + " tr")
            if tr_elements:
                header = ["組み合わせ","オッズ"]
                for tr in tr_elements[2::]:
                    td_elements = tr.select('td')
                    combi_li_elements = td_elements[2].select('li')
                    combi_list = []
                    for i, element in enumerate(combi_li_elements):
                        if i%2==0:
                            text = element.get_text()
                            text_space_removed = re.sub(r"\s", "", text)
                            combi_list.append(text_space_removed)
                    combi = "-".join(combi_list)
                    combi = re.sub(r"\s", "", combi)

                    # オッズが〇-〇と〇で場合分け
                    odds_elements = td_elements[3].select('span')
                    odds_elements = list(filter(lambda element :element.has_attr('id') and 'odds-' in element['id'], odds_elements))
                    if odds_elements:
                        odds_list = [re.sub(r"\s", "", element.get_text()) for element in odds_elements]
                        odds_list = list(filter(lambda x: x!="", odds_list))
                        odds = "-".join(odds_list)
                    else:
                        odds = re.sub(r"\s", "", td_elements[3].get_text())
                    values = [combi, odds]
                    data.append(dict(zip(header, values)))
        df = pd.DataFrame(data, dtype=str)
        return df

    def get_win(self):
        """単勝
        """
        df = self.__get_one_odds("b1",True)
        return df
    
    def get_place(self):
        """複勝
        """
        df = self.__get_one_odds("b1",False)
        return df

    def get_exacta(self):
        """馬単
        """
        df = self.__get_combi_odds("b6")
        return df
    
    def get_quinella(self):
        """馬連
        """
        df = self.__get_combi_odds("b4")
        return df
    
    def get_quinella_place(self):
        """ワイド
        """
        df = self.__get_combi_odds("b5")
        return df

    def get_trifecta(self):
        """3連単
        """
        df = self.__get_combi_odds("b8")
        return df
    
    def get_trio(self):
        """3連複
        """
        df = self.__get_combi_odds("b7")
        return df

class RaceListPage(BasePageSelenium):
    """ページ例：https://race.netkeiba.com/top/race_list.html?kaisai_date=20211024
    """

    def is_url_matches(self):
        cur_url = self.url
        return "race_list.html" in cur_url

    def get_race_id(self):
        race_id_elements = self.soup.select(RaceListPageLocators.RACE_ID[1])
        pattern1 = "result.html\?race_id=(\d*)"
        pattern2 = "shutuba.html\?race_id=(\d*)"
        race_id_list = []
        for element in race_id_elements:
            url = element.attrs["href"]
            match1 = re.findall(pattern1, url)
            match2 = re.findall(pattern2, url)
            if match1:
                race_id = match1[0]
                race_id_list.append(race_id)
            elif match2:
                race_id = match2[0]
                race_id_list.append(race_id)
        return race_id_list
    
class RacePage(BasePageRequest):
    """
    ページ例："https://db.netkeiba.com/race/202048112701/"
    """
    def __init__(self,url):
        super().__init__(url)
        html = str(self.soup)
        html = html.replace("</diary_snap_cut>", "")
        html = html.replace("<diary_snap_cut>", "")
        self.soup = BeautifulSoup(html, 'html.parser')

    def is_url_matches(self):
        cur_url = self.url
        return "race/" in cur_url

    def __get_id(self, element:bs4.element, pattern):
        atag_elements = element.select("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.attrs["href"]
            match = re.findall(pattern, url)
            if match:
                jockey_id = match[0]
                return jockey_id
        return None

    def get_result_list(self):
        dfs = pd.read_html(str(self.soup), match="馬名")
        df = dfs[0]
        horse_elements = self.soup.select(RacePageLocators.HORSE_NAME[1])
        jockey_elements = self.soup.select(RacePageLocators.JOCKEY_NAME[1])
        trainer_elements = self.soup.select(RacePageLocators.TRAINER_NAME[1])
        owner_elements = self.soup.select(RacePageLocators.OWNER_NAME[1])
        df["horse_id"] = [self.__get_id(element, "horse/(.*?)/") for element in horse_elements]
        df["jockey_id"] = [self.__get_id(element, "jockey/(.*?)/") for element in jockey_elements]
        df["trainer_id"] = [self.__get_id(element, "trainer/(.*?)/") for element in trainer_elements]
        df["owner_id"] = [self.__get_id(element, "owner/(.*?)/") for element in owner_elements]
        df = df.astype(str)
        return df

    def get_course_info(self):
        course_elements = self.soup.select(RacePageLocators.RACE_INFO_COURSE[1])
        if course_elements:
            course_element = course_elements[0]
            header = ["field", "turn", "in_out", "dist", "weather", "condition", "start_time"]
            text = course_element.get_text().replace("\n", "")
            pattern1 = "(芝|ダ)(.{1,2})(.*?)(\d{3,4})m / 天候 : (.*?) / .*? : (.*?) / 発走 : (\d{2}:\d{2})"
            pattern2 = "(.*?)(\d{4})m / 天候 : (.*?) / (.*?) / 発走 : (\d{2}:\d{2})"
            pattern3 = "(芝|ダ)(.{1,2})(.*?)(\d{3,4})m / 天候 : (.*?) / .*? :(.*?)/"
            if "障" in text:
                match = re.findall(pattern2, text)
                #print(match)
                if match:
                    data = list(match[0])
                    data.insert(1, "")
                    data.insert(2, "")
                    info = dict(zip(header, data))
                    return info
            elif "発走" in text:
                match = re.findall(pattern1, text)
                #print(match)
                if match:
                    data = match[0]
                    info = dict(zip(header, data))
                    return info
            else:
                match = re.findall(pattern3, text)
                # print(text)
                # print(match)
                if match:
                    data = list(match[0])
                    data[-1] = data[-1].replace(u'\xa0', '')
                    data.append("")
                    info = dict(zip(header, data))
                    return info
        return None
    # 2018年4月28日 1回新潟1日目 障害4歳以上未勝利  (混)(定量)
    def get_race_info(self):
        race_info_elements = self.soup.select(RacePageLocators.RACE_INFO[1])
        if race_info_elements:
            race_info_element = race_info_elements[0]
            text = race_info_element.get_text()
            pattern = re.compile(r'\s')
            res = pattern.split(text)
            date = res[0]
            kai_place_day = res[1]
            class_ = res[2]
            terms = res[4]
            race_info = {"date":date, "回_開催_日":kai_place_day, "階級":class_, "条件":terms}
            return race_info
        return None

    def get_title(self):
        title_elements = self.soup.select(RacePageLocators.RACE_INFO_TITLE[1])
        if title_elements:
            title_element = title_elements[0]
            title = title_element.get_text().replace("\n", "")
            return {"title": title}
        return None

    def get_return_list(self):
        return_row_elements = self.soup.select(RacePageLocators.RETURN_ROW[1])
        return_list = []
        header = ["how", "num", "return", "popularity"]
        for element in return_row_elements:
            head_element = element.select(RacePageLocators.RETURN_ROW_HEAD[1])[0]
            value_elements = element.select(RacePageLocators.RETURN_ROW_VALUE[1])
            head = head_element.get_text()
            value_list = [element.get_text("br").replace(",", "") for element in value_elements]
            value_list = [head] + value_list
            return_list.append(dict(zip(header, value_list)))
        return return_list

class ResultPage(BasePageRequest):
    """RaceResultPage action methods come here.
    """
    def is_url_matches(self):
        cur_url = self.url
        return "race_list.html" in cur_url

    def get_race_id(self):
        race_id_elements = self.soup.select(ResultPageLocators.RACE_ID[1])
        pattern = "result.html\?race_id=(\d*)"
        race_id_list = []
        for element in race_id_elements:
            url = element.attrs["href"]
            match = re.findall(pattern, url)
            if match:
                race_id = match[0]
                race_id_list.append(race_id)
        return race_id_list

class ShutubaPage(BasePageSelenium):
    """RaceResultPage action methods come here.
    """
    def is_url_matches(self):
        cur_url = self.url
        return "race/shutuba.html" in cur_url

    def __get_horse_id(self, element: bs4.element):
        """馬名が入ったtd要素からhorse_idを抽出する

        Args:
            element (WebElement): td要素
        """
        atag_elements = element.select("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.attrs["href"]
            pattern = "horse/(\d*)"
            match = re.findall(pattern, url)
            if match:
                horse_id = match[0]
                return horse_id

        return None
        
    def __get_jockey_id(self, element:bs4.element):
        atag_elements = element.select("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.attrs["href"]
            pattern = "jockey/(\d*)"
            match = re.findall(pattern, url)
            if match:
                jockey_id = match[0]
                return jockey_id
        return None

    def get_horse_list(self):
        head_elements = self.soup.select(ShutubaPageLocators.HEADS[1])
        heads = [re.sub(r"\s", "", element.get_text()) for element in head_elements]
        del heads[11]
        heads.append("horse_id")
        heads.append("jockey_id")
        horse_elements = self.soup.select(ShutubaPageLocators.HORSE[1])
        horse_list = []
        for horse_element in horse_elements:
            # .HorseList tr からtdを検索
            td_element_list = horse_element.select("td")
            values = [re.sub(r"\s", "", element.get_text()) for element in td_element_list]
            horse_id = self.__get_horse_id(td_element_list[3])
            jockey_id = self.__get_jockey_id(td_element_list[6])
            values.append(horse_id)
            values.append(jockey_id)
            horse_list.append(dict(zip(heads, values)))
        return horse_list

    def get_title(self):
        title_elements = self.soup.select(ShutubaPageLocators.TITLE[1])
        if title_elements:
            title_element = title_elements[0]
            title = re.sub(r"\s", "", title_element.get_text())
            return {"title": title}
        return None
    
    def get_date(self):
        date_elements = self.soup.select(ShutubaPageLocators.DATE[1])
        if date_elements:
            date_element = date_elements[0]
            date = re.sub(r"\s", "", date_element.get_text())
            return {"date": date}
        return None

    
