import unittest
from selenium import webdriver
from mypackage.page import shutuba
from pprint import pprint
import pandas as pd
import os

class TestShutubaPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)

    def test_get_horse_list(self):
        """test get horse info list"""

        #Load the main page. In this case the home page of Python.org.
        page = shutuba.ShutubaPage("https://race.netkeiba.com/race/shutuba.html?race_id=2016104648")
        #Checks if the word "Python" is in title
        assert page.is_url_matches(), "is not race result page."
        #gets horse information list
        horse_list = page.get_horse_list()
        df_shutuba = pd.DataFrame(horse_list)
        df_shutuba.to_csv("shutuba.csv")
        #Verifies that the horse_list is not empty
        assert horse_list, "No results found."

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()