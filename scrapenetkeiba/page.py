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

import numpy as np

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
        """ある年のある月において，レースが開催されている日にちを取得する．

        Returns:
            list of str: 取得した開催年月日のリスト
                例えば，2020年7月12日に開催レースがあれば，
                リスト中に'20200712'が含まれる
        Examples:
            >>> year = 2020
            >>> month = 7
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
            >>> driver.get(url)
            >>> page = CalenderPage(driver)
            >>> page.get_kaisai_date_list()
            ['20200704', '20200705', '20200711', '20200712', '20200718', '20200719', '20200725', '20200726']
            >>> driver.close()
        """
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
                id = match[0]
                return id
        return None


    def get_race_history(self):
        """馬の過去戦績を取得する．

        Returns:
            pd.DataFrame: 馬の過去戦績のデータフレーム
        
        Examples:
            >>> url="https://db.netkeiba.com/horse/2019105283/"
            >>> HorsePage(url).get_race_history()
                       日付    開催 天気   R            レース名   映像  頭数 枠番  馬番  オッズ 人気 着順  騎手  斤量     距離 馬場 馬場指数     タイム    着差 ﾀｲﾑ指数       通過        ペース    上り       馬体重 厩舎ｺﾒﾝﾄ   備考   勝ち馬(2着馬)      賞金       race_id jockey_id
            0  2021/12/19  6阪神6  晴  11  朝日フューチュリティ(G1)  nan  15  5   9  7.8  3  1  武豊  55  芝1600  良   **  1:33.5  -0.1    **      8-7  34.3-35.2  34.5  496(-10)    nan  nan    (セリフォス)  7110.6  202109060611     00666
            1  2021/10/23  4東京5  晴   9        アイビーS(L)  nan   8  4   4  3.8  2  1  武豊  55  芝1800  良   **  1:49.3   0.0    **    2-4-3  35.9-34.5  34.0  506(+12)    nan  nan   (グランシエロ)  1716.8  202105040509     00666
            2  2021/09/05  4小倉8  曇   5            2歳新馬  nan  13  8  13  1.7  1  1  武豊  54  芝1800  良   **  1:50.2  -0.1    **  6-4-3-2  38.7-34.3  34.1    494(0)    nan  nan  (ガイアフォース)   700.0  202110040805     00666
        """
        try:
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
                return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_features(self):
        """馬の適正レビューの左側のバーの長さを取得する．

        馬の適正レビューのコース適正，距離適性，脚質，成長，重馬場について，
        左側のバーの長さを取得する．バーが短ければ右側の適性があり，長ければ，左側の適性がある．
        例えば，コース適正の場合，バーが短ければ，ダート適正，長ければ芝適正となる．
        **バーの長さは最大116，最小26**

        Returns:
            pandas.DataFrame: 各適正レビューのデータフレーム
        
        Examples:
            >>> url="https://db.netkeiba.com/horse/2019105283/"
            >>> HorsePage(url).get_features()
                  value
            key
            コース適性   106
            距離適性     58
            脚質       58
            成長       11
            重馬場     104

        """
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
        """馬名を取得する．

        Returns:
            str: 馬名
        
        Examples:
            >>> url="https://db.netkeiba.com/horse/2019105283/"
            >>> HorsePage(url).get_horse_title()
            'ドウデュース'
        """
        horse_title_elements = self.soup.select(HorsePageLocators.HORSE_TITLE[1])
        if not horse_title_elements:
            return None
        horse_title_element = horse_title_elements[0]
        text = horse_title_element.get_text()
        horse_title = re.sub(r"\s", "", text)
        return horse_title
    
    def get_profile(self):
        """馬のプロフィールを取得する．

        Returns:
            pandas.DataFrame: プロフィールのデータフレーム
        
        Examples:
            >>> url="https://db.netkeiba.com/horse/2019105283/"
            >>> HorsePage(url).get_profile()
                                    value
            key
            生年月日                  2019年5月7日
            調教師                   友道康夫 (栗東)
            馬主                       キーファーズ
            生産者                    ノーザンファーム
            産地                          安平町
            セリ取引価格                        -
            獲得賞金               9,527万円 (中央)
            通算成績             3戦3勝 [3-0-0-0]
            主な勝鞍        21'朝日杯フューチュリティS(G1)
            近親馬              フラーレン、ロンズデーライト
            trainer_id                01061
            owner_id                 002803
            breeder_id               373126
        """
        dfs = pd.read_html(self.url, match="生年月日", index_col=0)
        df = dfs[0]
        df.index.name = "key"
        df.columns = ["value"]
        trainer_element = self.soup.select(HorsePageLocators.PROFILE_TRAINER[1])[0] 
        df.loc["trainer_id", "value"] = self.__get_id(trainer_element, "trainer/(.*?)/")
        owner_element = self.soup.select(HorsePageLocators.PROFILE_OWNER[1])[0]
        df.loc["owner_id", "value"] = self.__get_id(owner_element, "owner/(.*?)/")
        breeder_element  = self.soup.select(HorsePageLocators.PROFILE_BREEDER[1])[0]
        df.loc["breeder_id", "value"] = self.__get_id(breeder_element, "breeder/(.*?)/")
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
        """単勝オッズを取得する．

        Returns:
            pandas.DataFrame: 単勝オッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_win()
                馬番   オッズ
            0    1   2.6
            1    2  35.9
            2    3  40.0
            3    4  61.5
            4    5   8.7
            5    6  39.4
            6    7   2.7
            7    8  33.7
            8    9  32.6
            9   10  16.6
            10  11  45.0
            11  12   7.8
            12  13  27.7
            >>> driver.close()
        """
        df = self.__get_one_odds("b1",True)
        return df
    
    def get_place(self):
        """複勝オッズを取得する．

        Returns:
            pandas.DataFrame: 複勝オッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_place()
                馬番       オッズ
            0    1   1.2-1.5
            1    2   4.2-7.4
            2    3   5.1-9.1
            3    4  9.3-16.7
            4    5   1.8-2.9
            5    6   3.7-6.5
            6    7   1.2-1.5
            7    8   4.3-7.6
            8    9   4.2-7.4
            9   10   2.7-4.6
            10  11  6.1-10.9
            11  12   1.9-3.0
            12  13  5.9-10.6
            >>> driver.close()
        """
        df = self.__get_one_odds("b1",False)
        return df

    def get_exacta(self):
        """馬単オッズを取得する．

        Returns:
            pandas.DataFrame: 馬単オッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_exacta()
                組み合わせ    オッズ
            0      1-7    6.7
            1      7-1    6.7
            2      1-5   13.9
            3     1-12   14.6
            4     7-12   17.7
            ..     ...    ...
            195    4-5  727.7
            196  11-10  738.2
            197   13-2  754.4
            198   8-13  814.8
            199   4-12  828.5
            <BLANKLINE>
            [200 rows x 2 columns]
            >>> driver.close()
        """
        df = self.__get_combi_odds("b6")
        return df
    
    def get_quinella(self):
        """馬連オッズを取得する．

        Returns:
            pandas.DataFrame: 馬連オッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_quinella()
            組み合わせ    オッズ
            0    1-7    3.5
            1   1-12    9.9
            2    1-5    9.9
            3   7-12   12.7
            4    5-7   13.0
            ..   ...    ...
            73  3-11  811.1
            74  4-13  890.4
            75   4-9  900.8
            76   3-4  932.5
            77   4-6  976.6
            <BLANKLINE>
            [78 rows x 2 columns]
            >>> driver.close()
        """
        df = self.__get_combi_odds("b4")
        return df
    
    def get_quinella_place(self):
        """ワイドオッズを取得する．

        Returns:
            pandas.DataFrame: ワイドオッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_quinella_place()
            組み合わせ          オッズ
            0    1-7      1.8-2.0
            1    1-5      3.4-4.2
            2   1-12      3.9-4.8
            3    5-7      4.0-5.1
            4   7-12      4.5-5.7
            ..   ...          ...
            73   4-8  146.8-150.4
            74  4-13  171.4-175.5
            75   4-6  172.3-177.1
            76   3-4  179.3-183.1
            77   4-9  188.0-192.1
            <BLANKLINE>
            [78 rows x 2 columns]
            >>> driver.close()
        """
        df = self.__get_combi_odds("b5")
        return df

    def get_trifecta(self):
        """三連単オッズを取得する．

        Returns:
            pandas.DataFrame: 三連単オズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_trifecta()
                組み合わせ      オッズ
            0     1-7-12     27.7
            1      1-7-5     28.2
            2      7-1-5     29.9
            3     7-1-12     30.3
            4      1-5-7     44.7
            ...      ...      ...
            1795  3-13-4  54068.5
            1796  11-3-4  55066.7
            1797   4-6-9  55579.7
            1798   4-9-6  56278.8
            1799   6-9-4  56278.8
            <BLANKLINE>
            [1800 rows x 2 columns]
            >>> driver.close()
        """
        df = self.__get_combi_odds("b8")
        return df
    
    def get_trio(self):
        """三連複オッズを取得する．

        Returns:
            pandas.DataFrame: 三連単オッズのデータフレーム
        
        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
            >>> page = OddsPage(driver)
            >>> page.get_trio()
                組み合わせ     オッズ
            0      1-5-7     9.1
            1     1-7-12     9.2
            2     1-7-10    15.8
            3     1-5-12    22.1
            4      1-2-7    26.6
            ..       ...     ...
            295  3-11-12  1544.2
            296    4-5-8  1581.7
            297   2-4-12  1636.0
            298    3-4-5  1639.7
            299   2-8-13  1710.0
            <BLANKLINE>
            [300 rows x 2 columns]
            >>> driver.close()
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
        """ある年月日に開催されている全レースのレースidを取得する．

        Returns:
            list of str: レースidリスト

        Examples:
            >>> options = Options()
            >>> options.add_argument('--headless')
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options= options)
            >>> driver.implicitly_wait(20)
            >>> year=2021
            >>> month=10
            >>> day=3
            >>> kaisai_date=f"{year:04}{month:02}{day:02}"
            >>> url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
            >>> driver.get(url)
            >>> page=RaceListPage(driver)
            >>> page.get_race_id()
            ['202106040901', '202106040902', '202106040903', '202106040904', '202106040905', '202106040906', '202106040907', '202106040908', '202106040909', '202106040910', '202106040911', '202106040912', '202107050901', '202107050902', '202107050903', '202107050904', '202107050905', '202107050906', '202107050907', '202107050908', '202107050909', '202107050910', '202107050911', '202107050912']
            >>> driver.close()
        """
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
        """過去のレース結果を取得する．

        Returns:
            pandas.DataFrame: [description]
        
        Examples:
            >>> page = RacePage("https://db.netkeiba.com/race/202048112701/")
            >>> page.get_result_list()
        """
        try:
            dfs = pd.read_html(str(self.soup), match="馬名")
        except Exception:
            return pd.DataFrame()
        df = dfs[0]
        if len(df) > 0:
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
        else:
            return pd.DataFrame()

    def get_course_info(self):
        """レースのコース情報を取得する．

        Returns:
            dict of str: レースのコース情報
        
        Examples:
            >>> page = RacePage("https://db.netkeiba.com/race/202048112701/")
            >>> page.get_course_info()
        """
        course_elements = self.soup.select(RacePageLocators.RACE_INFO_COURSE[1])
        if course_elements:
            course_element = course_elements[0]
            header = ["field", "turn", "in_out", "dist", "weather", "condition", "start_time"]
            text = course_element.get_text().replace("\n", "")
            # print(text)
            pattern1 = "(芝|ダ)(.{1,2})(.*?)(\d{3,4})m / 天候 : (.*?) / .*? : (.*?) / 発走 : (\d{2}:\d{2})"
            pattern2 = "(.*?)(\d{4})m / 天候 : (.*?) / (.*?) / 発走 : (\d{2}:\d{2})"
            pattern3 = "(芝|ダ)(.{1,2})(.*?)(\d{3,4})m / 天候 : (.*?) / .*? :(.*?)/"
            pattern4 = "(芝|ダ)(.{1,2})(.*?)(\d{3,4})m / 天候 : (.*?) / .*?"
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
                
        return dict(zip(header, [np.nan]*len(header)))
    # 2018年4月28日 1回新潟1日目 障害4歳以上未勝利  (混)(定量)
    def get_race_info(self):
        """レース情報を取得する．

        Returns:
            dict of str: レース情報の辞書
        
        Examples:
            >>> page = RacePage("https://db.netkeiba.com/race/202048112701/")
            >>> page.get_race_info()
        """
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
        """レース名を取得する．

        Returns:
            dict of str: レース名
        
        Examples:
            >>> page = RacePage("https://db.netkeiba.com/race/202048112701/")
            >>> page.get_title()
        """
        title_elements = self.soup.select(RacePageLocators.RACE_INFO_TITLE[1])
        if title_elements:
            title_element = title_elements[0]
            title = title_element.get_text().replace("\n", "")
            return {"title": title}
        return None

    def get_return_list(self):
        """払い戻しを取得する．

        Returns:
            list of dict: 払い戻しの辞書リスト
        
        Examples:
            >>> page = RacePage("https://db.netkeiba.com/race/202048112701/")
            >>> page.get_return_list()
        """
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

class ShutubaPage(BasePageSelenium):
    """ページ例：https://race.netkeiba.com/race/shutuba.html?race_id=202106050911
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
        """出馬情報を取得する．

        Returns:
            pandas.DataFrame: 出馬表のデータフレーム
        
        Examples:
            >>> page = ShutubaPage("https://race.netkeiba.com/race/shutuba.html?race_id=202106050911")
            >>> page.get_horse_list()
        """
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
        df = pd.DataFrame(horse_list, dtype=str)
        return df

    def get_title(self):
        """レース名を取得する．

        Returns:
            dict of str: レース名
        
        Examples:
            >>> page = ShutubaPage("https://race.netkeiba.com/race/shutuba.html?race_id=202106050911")
            >>> page.get_title()
        """
        title_elements = self.soup.select(ShutubaPageLocators.TITLE[1])
        if title_elements:
            title_element = title_elements[0]
            title = re.sub(r"\s", "", title_element.get_text())
            return {"title": title}
        return None
    
    def get_date(self):
        """開催日を取得する．

        Returns:
            dict of str: 開催日
        
        Examples:
            >>> page = ShutubaPage("https://race.netkeiba.com/race/shutuba.html?race_id=202106050911")
            >>> page.get_date()
        """
        date_elements = self.soup.select(ShutubaPageLocators.DATE[1])
        if date_elements:
            date_element = date_elements[0]
            date = re.sub(r"\s", "", date_element.get_text())
            return {"date": date}
        return None
    
    def get_race_info(self):
        """レース情報を取得する．

        Returns:
            pandas.Series: レース情報のpandas.Series
        
        Examples:
            >>> from selenium.webdriver.chrome.options import Options
            >>> from selenium import webdriver
            >>> options = Options()
            >>> options.add_argument('log-level=2')
            >>> driver = webdriver.Chrome(options=options)
            >>> driver.implicitly_wait(20)
            >>> driver.get("https://race.netkeiba.com/race/shutuba.html?race_id=202106050911")
            >>> page = ShutubaPage(driver)
            >>> page.get_race_info()
            フィールド_距離                           芝2000m
            レースR                                  11R
            レース名                               ホープフルS
            第何回                                    5回
            開催場所                                   中山
            何日目                                   9日目
            出場馬種類_馬齢                            サラ系２歳
            クラス2                                 オープン
            レースタイプ1                        (国際)牡・牝(指)
            レースタイプ2                                馬齢
            レースタイプ3                               15頭
            賞金          本賞金:7000,2800,1800,1100,700万円
            クラス1                      Icon_GradeType1
            発走時間                                15:25
            dtype: object
        """
        race_field_dist_elements = self.soup.select(ShutubaPageLocators.RACE_FIELD_DIST[1])
        race_num_elements = self.soup.select(ShutubaPageLocators.RACE_NUM[1])
        race_name_elements = self.soup.select(ShutubaPageLocators.RACE_NAME[1])
        race_class1_elements = self.soup.select(ShutubaPageLocators.RACE_CLASS1[1])
        race_kai_elements = self.soup.select(ShutubaPageLocators.RACE_KAI[1])
        race_place_elements = self.soup.select(ShutubaPageLocators.RACE_PLACE[1])
        race_day_elements = self.soup.select(ShutubaPageLocators.RACE_DAY[1])
        horse_type_age_elements = self.soup.select(ShutubaPageLocators.HORSE_TYPE_AGE[1])
        race_class2_elements = self.soup.select(ShutubaPageLocators.RACE_CLASS2[1])
        race_type1_elements = self.soup.select(ShutubaPageLocators.RACE_TYPE1[1])
        race_type2_elements = self.soup.select(ShutubaPageLocators.RACE_TYPE2[1])
        race_type3_elements = self.soup.select(ShutubaPageLocators.RACE_TYPE3[1])
        race_prize_elements = self.soup.select(ShutubaPageLocators.RACE_PRIZE[1])
        race_data_01 = self.soup.select(ShutubaPageLocators.RACE_DATA01[1])
        race_data_01_text = re.sub(r"\s", "", race_data_01[0].get_text()).split("/")
        start_time = race_data_01_text[0].replace("発走", "")
        element_list = [
                        race_field_dist_elements, race_num_elements, race_name_elements,race_kai_elements,
                        race_place_elements, race_day_elements, horse_type_age_elements, race_class2_elements,
                        race_type1_elements, race_type2_elements, race_type3_elements, race_prize_elements
                        ]
        value_list = [re.sub(r"\s", "", element[0].get_text()) if element else None for element in element_list]
        key_list = ["フィールド_距離", "レースR", "レース名", "第何回", "開催場所", "何日目", "出場馬種類_馬齢", "クラス2", "レースタイプ1", "レースタイプ2", "レースタイプ3", "賞金"]
        class1_values = (race_class1_elements[0]["class"]) if race_class1_elements else []
        class1_values = [v for v in class1_values if v!="Icon_GradeType"]
        class1_value = "-".join(class1_values)
        key_list.append("クラス1")
        value_list.append(class1_value)
        key_list.append("発走時間")
        value_list.append(start_time)
        df_race_info = pd.Series(value_list, index=key_list)

        return df_race_info

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    
