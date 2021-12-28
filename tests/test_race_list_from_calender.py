import unittest
from selenium import webdriver
from mypackage.page import race_list, calender
from pprint import pprint
import pandas as pd
import os
import time
class TestRaceListPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
    def test_get_race_id_list(self):
        """test get race list"""

        #Load the main page. In this case the home page of Python.org.
        calender_page = calender.CalenderPage("https://race.netkeiba.com/top/calendar.html?year=2021&month=10")
        kaisai_dates = calender_page.get_kaisai_date_list()
        calender_page.close()
        page = race_list.RaceListPage(f"https://race.netkeiba.com/top/race_list.html")
        for kaisai_date in kaisai_dates:
            page.update_url(f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}")
            print(f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}")
            #Checks if the word "Python" is in title
            assert page.is_url_matches(), "is not race id page."
            #gets horse information list
            race_id_list = page.get_race_id()
            print(race_id_list)
            if os.path.exists("race_id_list.csv"):
                df_result = pd.read_csv("race_id_list.csv", index_col=0)
                df = pd.DataFrame(race_id_list, columns=["race_id"])
                df_result = df_result.append(df)
                df_result.to_csv("race_id_list.csv")
            else:
                df_result = pd.DataFrame(race_id_list, columns=["race_id"])
                df_result.to_csv("race_id_list.csv")
            time.sleep(1)

    def tearDown(self):
        pass
        #self.driver.close()

if __name__ == "__main__":
    unittest.main()