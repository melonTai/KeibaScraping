from .base import BasePageSelenium
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import re
import pandas as pd

class OddsPage(BasePageSelenium):
    """RaceResultPage action methods come here.
    """
    ninki_select_locator = "select#ninki_select"
    ninki_select_option_locator = "select#ninki_select option"
    win_locator = "#odds_tan_block"
    place_locator = "#odds_fuku_block"
    ninki_table_locator = ".RaceOdds_HorseList_Table.Ninki"
    def is_url_matches(self):
        cur_url = self.url
        return "odds/index.html?race_id=" in cur_url

    def update_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def change_url(self,url:str):
        self.driver.get(url)
        self.update_soup()
    
    def __get_one_odds(self,type_):
        """馬単，複勝で使う．馬番と対応するオッズを取得

        Args:
            type_ (str): urlのtypeに入れるパラメータ

        Returns:
            dict: 取得結果
        """
        url = self.url+f"&type={type_}"
        self.change_url(url)
        tr_elements = self.soup.select(self.win_locator + " tr")
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
        ninki_select_element = self.driver.find_element_by_css_selector(self.ninki_select_locator)
        data = []
        select = Select(ninki_select_element)
        select_len = len(select.options)
        for index in range(1, select_len-1):
            # selectエレメント更新
            ninki_select_element = self.driver.find_element_by_css_selector(self.ninki_select_locator)
            select = Select(ninki_select_element)
            select.select_by_index(index)
            self.update_soup()

            tr_elements = self.soup.select(self.ninki_table_locator + " tr")
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
                    odds = re.sub(r"\s", "", td_elements[3].get_text())
                    values = [combi, odds]
                    data.append(dict(zip(header, values)))
        return data

    def get_win(self):
        """単勝
        """
        res = self.__get_one_odds("b1")
        return res
    
    def get_place(self):
        """複勝
        """
        res = self.__get_one_odds("b1")
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
