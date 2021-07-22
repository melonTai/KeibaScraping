from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import re


class ResultPage(BasePage):
    """RaceResultPage action methods come here.
    """
    header_locator = ".race_table_01 th"
    result_row_locator = ".race_table_01 tr"
    result_data_locator = "td"

    return_row_locator = ".pay_table_01 tr"
    return_row_head_locator = "th"
    return_row_value_locator = "td"

    race_info_title_locator = ".racedata dd h1"
    race_info_course_locator = ".racedata dd diary_snap_cut span"
    race_info_date_locator = ".data_intro > p"

    def is_url_matches(self):
        cur_url = self.driver.current_url
        return "race/" in cur_url

    def __get_horse_id(self, element: WebElement):
        """馬名が入ったtd要素からhorse_idを抽出する

        Args:
            element (WebElement): td要素
        """
        atag_elements = element.find_elements_by_css_selector("a")
        if atag_elements:
            atag_element = atag_elements[0]
            url = atag_element.get_attribute("href")
            pattern = "horse/(\d*)"
            match = re.findall(pattern, url)
            if match:
                horse_id = match[0]
                return horse_id

        return None
        
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

    def get_result_list(self):
        result_row_elements = self.driver.find_elements_by_css_selector(
            self.result_row_locator)
        header_elements = self.driver.find_elements_by_css_selector(
            self.header_locator)

        header = [element.text.replace("\n", "")
                      for element in header_elements]
        header.append("horse_id")
        header.append("jockey_id")

        result_list = []
        for element in result_row_elements[1::]:
            data_elements = element.find_elements_by_css_selector(
                self.result_data_locator)
            if data_elements:
                datas = [element.text.replace("\n", "") for element in data_elements]
                horse_id = self.__get_horse_id(data_elements[3])
                jockey_id = self.__get_jockey_id(data_elements[6])
                datas.append(horse_id)
                datas.append(jockey_id)
                row = dict(zip(header, datas))
                result_list.append(row)
        return result_list

    def get_course_info(self):
        course_elements = self.driver.find_elements_by_css_selector(self.race_info_course_locator)
        if course_elements:
            course_element = course_elements[0]
            header = ["corse", "turn", "dist", "weather", "condition", "start_time"]
            text = course_element.text
            pattern = "(.*?)(\d{4})m / 天候 : (.*?) / .*? : (.*?) / 発走 : (\d{2}:\d{2})"
            match = re.findall(pattern, text)
            if match:
                _data = list(match[0])
                if "障" in _data[0]:
                    course_turn = [_data[0], ""]
                else:
                    course_turn = [_data[0][0], _data[0][1]]
                data = course_turn + _data[1::]
                info = dict(zip(header, data))
                return info
        return None

    def get_date(self):
        date_elements = self.driver.find_elements_by_css_selector(self.race_info_date_locator)
        if date_elements:
            date_element = date_elements[0]
            text = date_element.text
            pattern = "\d{4}年\d{1,2}月\d{1,2}日"
            match = re.findall(pattern, text)
            if match:
                data = match[0]
                date = {"date" : data}
                #print(date)
                return date
        return None

    def get_title(self):
        title_elements = self.driver.find_elements_by_css_selector(self.race_info_title_locator)
        if title_elements:
            title_element = title_elements[0]
            title = title_element.text
            return {"title": title}
        return None

    def get_return_list(self):
        return_row_elements = self.driver.find_elements_by_css_selector(
            self.return_row_locator)
        return_list = []
        for element in return_row_elements:
            head_element = element.find_element_by_css_selector(
                self.return_row_head_locator)
            value_elements = element.find_elements_by_css_selector(
                self.return_row_value_locator)
            head = head_element.text
            value_list = [element.text.replace(
                "\n", "") for element in value_elements]
            return_list.append([head] + value_list)
        return return_list
