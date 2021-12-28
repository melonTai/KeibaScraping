from selenium.webdriver.common.by import By

class CalenderPageLocators(object):
    KAISAI_DATE = (By.CSS_SELECTOR, ".RaceCellBox a")

class HorsePageLocators(object):
    RACE_HISTORY_HEAD = (By.CSS_SELECTOR, ".db_main_race th")
    RACE_HISTORY_ROW = (By.CSS_SELECTOR, ".db_main_race tr")
    RACE_HISTORY_DATA = (By.CSS_SELECTOR, "td")

    FEATURES_HEAD = (By.CSS_SELECTOR, ".tekisei_table th")
    FEATURES_TABLE = (By.CSS_SELECTOR, ".tekisei_table")

    HORSE_TITLE = (By.CSS_SELECTOR, ".horse_title h1")

class OddsPageLocators(object):
    NINKI_SELECT = (By.CSS_SELECTOR, "select#ninki_select")
    NINKI_SELECT_OPTION = (By.CSS_SELECTOR, "select#ninki_select option")
    WIN = (By.CSS_SELECTOR, "#odds_tan_block")
    PLACE = (By.CSS_SELECTOR, "#odds_fuku_block")
    NINKI_TABLE = (By.CSS_SELECTOR, ".RaceOdds_HorseList_Table.Ninki")

class RaceListPageLocators(object):
    RACE_ID = (By.CSS_SELECTOR, ".RaceList_DataItem a")

class RacePageLocators(object):
    HEADER = (By.CSS_SELECTOR, ".race_table_01 th")
    RESULT_ROW = (By.CSS_SELECTOR, ".race_table_01 tr")
    RESULT_DATA = (By.CSS_SELECTOR,"td")
    RETURN_ROW = (By.CSS_SELECTOR,".pay_table_01 tr")
    RETURN_ROW_HEAD = (By.CSS_SELECTOR,"th")
    RETURN_ROW_VALUE = (By.CSS_SELECTOR,"td")
    RACE_INFO_TITLE = (By.CSS_SELECTOR,".racedata dd h1")
    RACE_INFO_COURSE = (By.CSS_SELECTOR,".racedata dd diary_snap_cut span")
    RACE_INFO = (By.CSS_SELECTOR,".data_intro > p")

class ResultPageLocators(object):
    RACE_ID = (By.CSS_SELECTOR,".RaceList_DataItem a")