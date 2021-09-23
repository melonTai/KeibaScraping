import unittest
from selenium import webdriver
from mypackage.page import odds
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
        self.page = odds.OddsPage("https://race.netkeiba.com/odds/index.html?race_id=202106040511")
    def test_get_horse_list(self):
        """test get horse info list"""
        #Checks if the word "Python" is in title
        assert self.page.is_url_matches(), "is not race result page."
        # get odds
        win_list = self.page.get_win()
        assert win_list, "No results found."
        df_win = pd.DataFrame(win_list)
        df_win.to_csv("odds_win.csv", encoding='utf_8_sig')
        
        place_list = self.page.get_place()
        assert place_list, "No results found."
        df_place = pd.DataFrame(place_list)
        df_place.to_csv("odds_place.csv", encoding='utf_8_sig')
        
        data_list = self.page.get_exacta()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_exacta.csv", encoding='utf_8_sig')

        data_list = self.page.get_quinella()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_quinella.csv", encoding='utf_8_sig')

        data_list = self.page.get_exacta()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_exacta.csv", encoding='utf_8_sig')

        data_list = self.page.get_quinella_place()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_quinella_place.csv", encoding='utf_8_sig')

        data_list = self.page.get_trifecta()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_trifecta.csv", encoding='utf_8_sig')

        data_list = self.page.get_trio()
        assert data_list, "Noresults found."
        df = pd.DataFrame(data_list)
        df.to_csv("odds_trio.csv", encoding='utf_8_sig')



    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()