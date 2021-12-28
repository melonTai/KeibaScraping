import unittest
from selenium import webdriver
from package.page import RaceListPage, CalenderPage
from pprint import pprint
import pandas as pd
import os
import time
class TestRaceListPage(unittest.TestCase):
    """A sample test class to show how page object works"""

    def setUp(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path)
        self.driver = webdriver.Chrome()
    def test_get_race_id_list(self):
        """test get race list"""
        self.driver.implicitly_wait(20)
        self.driver.get("https://race.netkeiba.com/top/calendar.html?year=2021&month=10")
        calender_page = CalenderPage(self.driver)
        kaisai_dates = calender_page.get_kaisai_date_list()

        self.driver.get(f"https://race.netkeiba.com/top/race_list.html")
        page = RaceListPage(self.driver)
        for kaisai_date in kaisai_dates:
            page.update_url(f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}")
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
        self.driver.close()

if __name__ == "__main__":
    unittest.main()