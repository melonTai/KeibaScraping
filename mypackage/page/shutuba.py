from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import bs4
import re

class ShutubaPage(BasePage):
    """RaceResultPage action methods come here.
    """
    heads_locator = ".Header th"
    horse_locator = ".HorseList"
    title_locator = ".RaceName"
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
    
