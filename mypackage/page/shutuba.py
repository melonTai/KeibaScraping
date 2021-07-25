from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import bs4

class HorseShutuba():
    def __init__(self, element : bs4.element, param_keys : list):
        # .HorseList tr からtdを検索
        param_element_list = element.select("td")
        # 印欄は不必要につき削除
        del param_element_list[2]
        del param_keys[2]
        # 抽出値
        param_values = [element.text for element in param_element_list]
        # 属性に格納
        self.params = dict(zip(param_keys, param_values))


class ShutubaPage(BasePage):
    """RaceResultPage action methods come here.
    """
    heads_locator = ".Header th"
    horse_locator = ".HorseList"
    def is_url_matches(self):
        cur_url = self.driver.current_url
        return "race/shutuba.html" in cur_url

    def get_horse_list(self):
        head_elements = self.soup.select(self.heads_locator)
        heads = [element.get_text().replace("\n", "") for element in head_elements]
        horse_elements = self.soup.select(self.horse_locator)
        horse_list = []
        for horse_element in horse_elements:
            horse = HorseShutuba(horse_element, heads.copy())
            horse_list.append(horse)
        return horse_list
    
