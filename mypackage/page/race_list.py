from .base import BasePageSelenium
from selenium.webdriver.remote.webelement import WebElement
import re

class RaceListPage(BasePageSelenium):
    """RaceResultPage action methods come here.
    """
    race_id_locator = ".RaceList_DataItem a"

    def is_url_matches(self):
        cur_url = self.url
        return "race_list.html" in cur_url

    def get_race_id(self):
        race_id_elements = self.soup.select(self.race_id_locator)
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