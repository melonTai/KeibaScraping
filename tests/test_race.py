from typing import Counter
import unittest
from selenium import webdriver
from package.page import RacePage
from package import utils
from pprint import pprint
import pandas as pd
import os
class TestResultPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)

    def test_get_result_list(self):
        """test get horse info list"""
        page = RacePage("https://db.netkeiba.com/race/202048112701/")
        result_list = page.get_result_list()
        corse_info = page.get_course_info()
        race_info = page.get_race_info()
        title = page.get_title()
        print(corse_info, race_info, title)
        df_race = pd.DataFrame(result_list)
        for key, value in corse_info.items():
            df_race[key] = value
        for key, value in race_info.items():
            df_race[key] = value
        for key, value in title.items():
            df_race[key] = value
        df_race["ref_time"] = utils.get_ref_time(202101010101)
        df_race.to_csv("race.csv", encoding="utf_8_sig")
        
        return_list = page.get_return_list()
        df_return = pd.DataFrame(return_list)
        df_return.to_csv("return.csv", encoding="utf_8_sig")
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()