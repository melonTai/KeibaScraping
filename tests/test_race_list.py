import unittest
from selenium import webdriver
from mypackage.page import race_list
from pprint import pprint
import pandas as pd
import os
class TestRaceListPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
    def test_get_race_id_list(self):
        """test get race list"""

        #Load the main page. In this case the home page of Python.org.
        page = race_list.RaceListPage("https://race.netkeiba.com/top/race_list.html?kaisai_date=20200105")
        #Checks if the word "Python" is in title
        assert page.is_url_matches(), "is not race id page."
        #gets horse information list
        race_id_list = page.get_race_id()
        df_result = pd.DataFrame(race_id_list)
        df_result.to_csv("race_id_list.csv")
        #Verifies that the horse_list is not empty
        assert race_id_list, "No race_id_list found."

    def tearDown(self):
        pass
        #self.driver.close()

if __name__ == "__main__":
    unittest.main()