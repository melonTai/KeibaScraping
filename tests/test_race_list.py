import unittest
from selenium import webdriver
from scrapenetkeiba.page import RaceListPage
from pprint import pprint
import pandas as pd
import os
class TestRaceListPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(20)
        self.driver.get("https://race.netkeiba.com/top/race_list.html?kaisai_date=20211024")
    def test_get_race_id_list(self):
        page = RaceListPage(self.driver)
        race_id_list = page.get_race_id()
        df_result = pd.DataFrame(race_id_list)
        df_result.to_csv("race_id_list.csv")

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()