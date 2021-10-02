from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import re
import bs4
import sys
import io

class RacePage(BasePage):
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
        result_row_elements = self.soup.select(
            self.result_row_locator)
        header_elements = self.soup.select(
            self.header_locator)

        header = [element.get_text().replace("\n", "")
                      for element in header_elements]
        header.append("horse_id")
        header.append("jockey_id")

        result_list = []
        for element in result_row_elements[1::]:
            data_elements = element.select(
                self.result_data_locator)
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
        course_elements = self.soup.select(self.race_info_course_locator)
        if course_elements:
            course_element = course_elements[0]
            header = ["field", "turn", "in_out", "dist", "weather", "condition", "start_time"]
            text = course_element.get_text().replace("\n", "")
            pattern1 = "(芝|ダ)(.{1,2})(.*?)(\d{4})m / 天候 : (.*?) / .*? : (.*?) / 発走 : (\d{2}:\d{2})"
            pattern2 = "(.*?)(\d{4})m / 天候 : (.*?) / (.*?) / 発走 : (\d{2}:\d{2})"
            pattern3 = "(芝|ダ)(.{1,2})(.*?)(\d{4})m / 天候 : (.*?) / .*? :(.*?)/"
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
        race_info_elements = self.soup.select(self.race_info_locator)
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
        title_elements = self.soup.select(self.race_info_title_locator)
        if title_elements:
            title_element = title_elements[0]
            title = title_element.get_text().replace("\n", "")
            return {"title": title}
        return None

    def get_return_list(self):
        return_row_elements = self.soup.select(
            self.return_row_locator)
        return_list = []
        header = ["how", "num", "return", "popularity"]
        for element in return_row_elements:
            head_element = element.select(
                self.return_row_head_locator)[0]
            value_elements = element.select(
                self.return_row_value_locator)
            head = head_element.get_text()
            value_list = [element.get_text("br").replace(",", "") for element in value_elements]
            value_list = [head] + value_list
            return_list.append(dict(zip(header, value_list)))
        return return_list