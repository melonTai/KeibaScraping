import unittest
from selenium import webdriver
from package.page import HorsePage
from pprint import pprint
import pandas as pd
import os
class TestShutubaPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)

    def test_get_horse_info_list(self):
        """test get horse info list"""

        #Load the main page. In this case the home page of Python.org.
        page = HorsePage("https://db.netkeiba.com/horse/2014104386")
        race_list = page.get_race_history()
        df_race = pd.DataFrame(race_list)
        df_race.to_csv("race.csv")
        features = page.get_features()
        df_features = pd.DataFrame([features])
        df_features.to_csv("features.csv")
        horse_title = page.get_horse_title()
        print(horse_title)

if __name__ == "__main__":
    unittest.main()