from .base import BasePage
from selenium.webdriver.remote.webelement import WebElement
import re

class CalenderPage(BasePage):
    """RaceResultPage action methods come here.
    """
    kaisai_date_locator = ".RaceCellBox a"
    def is_url_matches(self):
        cur_url = self.driver.current_url
        return "calendar.html" in cur_url

    def get_kaisai_date_list(self):
        kaisai_date_elements = self.soup.select(self.kaisai_date_locator)
        pattern = "race_list.html\?kaisai_date=(\d*)"
        kaisai_dates = []
        for element in kaisai_date_elements:
            url = element.attrs["href"]
            matches = re.findall(pattern, url)
            if matches:
                kaisai_date = matches[0]
                kaisai_dates.append(kaisai_date)
        return kaisai_dates
        