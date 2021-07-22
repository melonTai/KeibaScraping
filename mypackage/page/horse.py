from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import re

class RaceResult():
    locator = "td"

    def __init__(self, element: WebElement, param_keys: list):
        param_elements = element.find_elements_by_css_selector(self.locator)
        # 抽出値
        param_values = [element.text for element in param_elements]
        # 属性に格納
        self.params = dict(zip(param_keys, param_values))


class Features():
    locator = "td"

    def __init__(self, element: WebElement, param_keys: list):
        param_elements = element.find_elements_by_css_selector(self.locator)
        param_values = [self.get_left_width(element) for element in param_elements]
        self.params = dict(zip(param_keys, param_values))

    def get_left_width(self, element: WebElement):
        """tdの中の左の青画像の幅を取得する

        Args:
            element (WebElement): imgタグを持つtd要素

        Returns:
            [type]: 青棒画像の幅
        """
        images = element.find_elements_by_css_selector("img")
        left_img = images[1]
        return left_img.get_attribute("width")

class HorsePage(BasePage):
    """RaceResultPage action methods come here.
    """
    race_history_head_locator = ".db_main_race th"
    race_history_row_locator = ".db_main_race tr"
    race_history_data_locator = "td"

    features_head_locator = ".tekisei_table th"
    features_table_locator = ".tekisei_table"

    def is_url_matches(self):
        cur_url = self.driver.current_url
        return "horse" in cur_url

    def __get_jockey_id(self, element:WebElement):
        atag_elements = element.find_elements_by_css_selector("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.get_attribute("href")
            pattern = "jockey/(\d*)"
            match = re.findall(pattern, url)
            if match:
                jockey_id = match[0]
                return jockey_id
        return None

    def __get_race_id(self, element:WebElement):
        atag_elements = element.find_elements_by_css_selector("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.get_attribute("href")
            pattern = "race/(\d*)"
            match = re.findall(pattern, url)
            if match:
                race_id = match[0]
                return race_id
        return None

    def get_race_history(self):
        # 競争成績の見出しを取得
        race_history_head_elements = self.driver.find_elements_by_css_selector(
            self.race_history_head_locator)
        # 見出しWeb要素を文字列に変換
        race_history_heads = [
            element.text.replace("\n", "") for element in race_history_head_elements]
        race_history_heads.append("race_id")
        race_history_heads.append("jockey_id")
        # 競争成績の行リストを取得
        race_history_row_elements = self.driver.find_elements_by_css_selector(
            self.race_history_row_locator)
        if race_history_row_elements:
            del race_history_row_elements[0]
        # 行リストをフォーマット
        race_history = []
        for element in race_history_row_elements:
            data_elements = element.find_elements_by_css_selector(self.race_history_data_locator)
            race_id = self.__get_race_id(data_elements[4])
            jockey_id = self.__get_jockey_id(data_elements[12])
            race_data = [element.text for element in data_elements]
            race_data.append(race_id)
            race_data.append(jockey_id)
            race_result = dict(zip(race_history_heads, race_data))
            race_history.append(race_result)
        return race_history

    def get_features(self):
        # 適正の見出しを取得
        features_head_elements = self.driver.find_elements_by_css_selector(
            self.features_head_locator)
        # 見出しWeb要素を文字列に変換
        features_heads = [element.text for element in features_head_elements]
        # 適正の行リストを取得
        features_table_element = self.driver.find_element_by_css_selector(
            self.features_table_locator)
        # 行リストをフォーマット
        features = Features(features_table_element, features_heads)
        return features