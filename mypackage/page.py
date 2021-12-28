import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import bs4
import requests

import time
import re

from .locators import CalenderPageLocators
from .locators import HorsePageLocators
from .locators import OddsPageLocators
from .locators import RaceListPageLocators
from .locators import RacePageLocators

class BasePageRequest(object):
    """Base class to initialize the base page 
    that will be called from all pages
    """                         
    def __init__(self,url:str):
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
    def __init__(self, driver):
        self.driver = driver
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def update_url(self, url:str):
        self.driver.implicitly_wait(20)
        self.driver.get(url)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def close(self):
        self.driver.close()

class CalenderPage(BasePageSelenium):
    """RaceResultPage action methods come here.
    """
    kaisai_date_locator = ".RaceCellBox a"
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
    """https://db.netkeiba.com/horse/2019105283/"""

    def is_url_matches(self):
        cur_url = self.url
        return "horse" in cur_url
    
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

    def __get_race_id(self, element:bs4.element):
        atag_elements = element.select("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.attrs["href"]
            pattern = "race/(.*?)/"
            match = re.findall(pattern, url)
            if match:
                race_id = match[0]
                return race_id
        return None

    def get_race_history(self):
        # 競争成績の見出しを取得
        race_history_head_elements = self.soup.select(HorsePageLocators.RACE_HISTORY_HEAD[1])
        # 見出しWeb要素を文字列に変換
        race_history_heads = [
            re.sub(r"\s", "", element.get_text()) for element in race_history_head_elements]
        race_history_heads.append("race_id")
        race_history_heads.append("jockey_id")
        # 競争成績の行リストを取得
        race_history_row_elements = self.soup.select(HorsePageLocators.RACE_HISTORY_ROW[1])
        if race_history_row_elements:
            del race_history_row_elements[0]
        # 行リストをフォーマット
        race_history = []
        for element in race_history_row_elements:
            data_elements = element.select(HorsePageLocators.RACE_HISTORY_DATA[1])
            race_id = self.__get_race_id(data_elements[4])
            jockey_id = self.__get_jockey_id(data_elements[12])
            race_data = [re.sub(r"\s", "", element.get_text()) for element in data_elements]
            race_data.append(race_id)
            race_data.append(jockey_id)
            race_result = dict(zip(race_history_heads, race_data))
            race_history.append(race_result)
        return race_history

    def get_features(self):
        # 適正の見出しを取得
        features_head_elements = self.soup.select(HorsePageLocators.FEATURES_HEAD[1])
        # 見出しWeb要素を文字列に変換
        features_heads = [re.sub(r"\s", "", element.get_text()) for element in features_head_elements]
        # 適正の行リストを取得
        features_table_element = self.soup.select(HorsePageLocators.FEATURES_TABLE)[0]
        # 行リストをフォーマット
        param_elements = features_table_element.select("td")
        param_values = [self.get_left_width(element) for element in param_elements]
        res = dict(zip(features_heads, param_values))
        return res
    
    def get_left_width(self, element: bs4.element):
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

class OddsPage(BasePageSelenium):
    """https://race.netkeiba.com/odds/index.html?race_id=202105040211"""
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
            return data
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
        return data

    def get_win(self):
        """単勝
        """
        res = self.__get_one_odds("b1",True)
        return res
    
    def get_place(self):
        """複勝
        """
        res = self.__get_one_odds("b1",False)
        return res

    def get_exacta(self):
        """馬単
        """
        res = self.__get_combi_odds("b6")
        return res
    
    def get_quinella(self):
        """馬連
        """
        res = self.__get_combi_odds("b4")
        return res
    
    def get_quinella_place(self):
        """ワイド
        """
        res = self.__get_combi_odds("b5")
        return res

    def get_trifecta(self):
        """3連単
        """
        res = self.__get_combi_odds("b8")
        return res
    
    def get_trio(self):
        """3連複
        """
        res = self.__get_combi_odds("b7")
        return res

class RaceListPage(BasePageSelenium):
    """RaceResultPage action methods come here.
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
    ページ例："https://race.netkeiba.com/top/race_list.html?kaisai_date=20211024"
    """
    
    header_locator = ".race_table_01 th"
    result_row_locator = ".race_table_01 tr"
    result_data_locator = "td"

    return_row_locator = ".pay_table_01 tr"
    return_row_head_locator = "th"
    return_row_value_locator = "td"

    race_info_title_locator = ".racedata dd h1"
    race_info_course_locator = ".racedata dd diary_snap_cut span"
    race_info_locator = ".data_intro > p"

    def is_url_matches(self):
        cur_url = self.url
        return "race/" in cur_url

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

    def get_result_list(self):
        result_row_elements = self.soup.select(RacePageLocators.RESULT_ROW[1])
        header_elements = self.soup.select(RacePageLocators.HEADER[1])

        header = [element.get_text().replace("\n", "") for element in header_elements]
        header.append("horse_id")
        header.append("jockey_id")

        result_list = []
        for element in result_row_elements[1::]:
            data_elements = element.select(RacePageLocators.RESULT_DATA[1])
            if data_elements:
                datas = [element.get_text().replace("\n", "") for element in data_elements]
                horse_id = self.__get_horse_id(data_elements[3])
                jockey_id = self.__get_jockey_id(data_elements[6])
                datas.append(horse_id)
                datas.append(jockey_id)
                row = dict(zip(header, datas))
                result_list.append(row)
        return result_list

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
    race_id_locator = ".RaceList_DataItem a"

    def is_url_matches(self):
        cur_url = self.url
        return "race_list.html" in cur_url

    def get_race_id(self):
        race_id_elements = self.soup.select(self.race_id_locator)
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
    heads_locator = ".Header th"
    horse_locator = ".HorseList"
    title_locator = ".RaceName"
    date_locator = "#RaceList_DateList .Active a"
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
        head_elements = self.soup.select(self.heads_locator)
        heads = [re.sub(r"\s", "", element.get_text()) for element in head_elements]
        del heads[11]
        heads.append("horse_id")
        heads.append("jockey_id")
        horse_elements = self.soup.select(self.horse_locator)
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
        title_elements = self.soup.select(self.title_locator)
        if title_elements:
            title_element = title_elements[0]
            title = re.sub(r"\s", "", title_element.get_text())
            return {"title": title}
        return None
    
    def get_date(self):
        date_elements = self.soup.select(self.date_locator)
        if date_elements:
            date_element = date_elements[0]
            date = re.sub(r"\s", "", date_element.get_text())
            return {"date": date}
        return None

    
