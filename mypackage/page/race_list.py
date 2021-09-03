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
        pattern = "result.html\?race_id=(\d*)"
        race_id_list = []
        for element in race_id_elements:
            url = element.attrs["href"]
            match = re.findall(pattern, url)
            if match:
                race_id = match[0]
                race_id_list.append(race_id)
        return race_id_list