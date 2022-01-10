import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapenetkeiba.page import OddsPage
from pprint import pprint
import pandas as pd
import os

class TestOddsPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        folder = current_path + "/odds"
        if not os.path.exists(folder):
            os.makedirs(folder)
        os.chdir(folder)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('log-level=2')
        driver = webdriver.Chrome(options= options)
        driver.implicitly_wait(20)
        driver.get("https://race.netkeiba.com/odds/index.html?race_id=202105040211")
        self.page = OddsPage(driver)
    def test_get_horse_list(self):
        """test get horse info list"""
        print("win")
        df_win = self.page.get_win()
        df_win.to_csv("odds_win.csv", encoding='utf_8_sig')
        
        print("place")
        df_place = self.page.get_place()
        df_place.to_csv("odds_place.csv", encoding='utf_8_sig')
        
        print("exacta")
        df = self.page.get_exacta()
        df.to_csv("odds_exacta.csv", encoding='utf_8_sig')

        print("quinella")
        df = self.page.get_quinella()
        df.to_csv("odds_quinella.csv", encoding='utf_8_sig')

        print("quinella_place")
        df = self.page.get_quinella_place()
        df.to_csv("odds_quinella_place.csv", encoding='utf_8_sig')

        print("trifecta")
        df = self.page.get_trifecta()
        df.to_csv("odds_trifecta.csv", encoding='utf_8_sig')

        print("trio")
        df = self.page.get_trio()
        df.to_csv("odds_trio.csv", encoding='utf_8_sig')



    def tearDown(self):
        self.page.driver.close()

if __name__ == "__main__":
    unittest.main()