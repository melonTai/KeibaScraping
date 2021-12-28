import unittest
from selenium import webdriver
from package.page import CalenderPage
from pprint import pprint
import pandas as pd
import os

class TestCalenderPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)

    def test_get_kaisai_date_list(self):
        """test get horse info list"""
        year = 2020
        month = 7
        driver = webdriver.Chrome()
        driver.implicitly_wait(20)
        url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
        driver.get(url)
        #Load the main page. In this case the home page of Python.org.
        page = CalenderPage(driver)
        self.page = page
        kaisai_date_list = page.get_kaisai_date_list()
        df_race = pd.DataFrame(kaisai_date_list)
        df_race.to_csv("kaisai_date.csv")
        driver.close()

if __name__ == "__main__":
    unittest.main()