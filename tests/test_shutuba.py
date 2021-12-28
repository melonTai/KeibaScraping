import unittest
from selenium import webdriver
from package.page import ShutubaPage
from pprint import pprint
import pandas as pd
import os

class TestShutubaPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
        self.driver = webdriver.Chrome()

    def test_get_horse_list(self):
        """test get horse info list"""
        self.driver.implicitly_wait(20)
        self.driver.get("https://race.netkeiba.com/race/shutuba.html?race_id=202105030603")
        page = ShutubaPage(self.driver)
        horse_list = page.get_horse_list()
        date = page.get_date()
        print(date)
        df_shutuba = pd.DataFrame(horse_list)
        df_shutuba.to_csv("shutuba.csv")

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()