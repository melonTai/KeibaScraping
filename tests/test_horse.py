import unittest
from selenium import webdriver
from mypackage.page import horse
from pprint import pprint
import pandas as pd
import os
class TestShutubaPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://db.netkeiba.com/horse/2014104386")
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)

    def test_get_horse_info_list(self):
        """test get horse info list"""

        #Load the main page. In this case the home page of Python.org.
        page = horse.HorsePage(self.driver)
        #Checks if the word "Python" is in title
        assert page.is_url_matches(), "is not race result page."
        #gets horse information list
        race_list = page.get_race_history()
        df_race = pd.DataFrame(race_list)
        df_race.to_csv("race.csv")
        #Verifies that the horse_list is not empty
        assert race_list, "No race found."
        features = page.get_features()
        features_params = features.params
        df_features = pd.DataFrame([features_params])
        df_features.to_csv("features.csv")
        #Verifies that the horse_list is not empty
        assert features_params, "No features found."

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()