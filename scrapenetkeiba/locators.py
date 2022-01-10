# -*- coding: utf-8 -*-

"""netkeiba.comの抽出したい要素のロケータ

各ロケータには，抽出したい要素を特定するcssセレクタやXPATHを定義する．
ロケータは各ページごとにクラスで分類する．
例えば，CalenderPageLocatorsはpageモジュールのCalenderPageで使用される．
"""


from selenium.webdriver.common.by import By

class CalenderPageLocators(object):
    KAISAI_DATE = (By.CSS_SELECTOR, ".RaceCellBox a")

class HorsePageLocators(object):
    RACE_HISTORY_HEAD = (By.CSS_SELECTOR, ".db_main_race th")
    RACE_HISTORY_ROW = (By.CSS_SELECTOR, ".db_main_race tr")
    RACE_HISTORY_DATA = (By.CSS_SELECTOR, "td")
    RACE_HISTORY_RACENAME = (By.CSS_SELECTOR, ".db_main_race tr td:nth-child(5)")
    RACE_HISTORY_JOCKEYNAME = (By.CSS_SELECTOR, ".db_main_race tr td:nth-child(13)")

    FEATURES_HEAD = (By.CSS_SELECTOR, ".tekisei_table th")
    FEATURES_TABLE = (By.CSS_SELECTOR, ".tekisei_table")

    HORSE_TITLE = (By.CSS_SELECTOR, ".horse_title h1")

    PROFILE_TRAINER = (By.CSS_SELECTOR, ".db_prof_table tr:nth-child(2) td")
    PROFILE_OWNER = (By.CSS_SELECTOR, ".db_prof_table tr:nth-child(3) td")
    PROFILE_BREEDER = (By.CSS_SELECTOR, ".db_prof_table tr:nth-child(4) td")

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
    RACE_INFO_COURSE = (By.CSS_SELECTOR,".racedata dd p span")
    RACE_INFO = (By.CSS_SELECTOR,".data_intro > p")

    HORSE_NAME = (By.CSS_SELECTOR, ".race_table_01 tr td:nth-of-type(4)")
    JOCKEY_NAME = (By.CSS_SELECTOR, ".race_table_01 tr td:nth-of-type(7)")
    TRAINER_NAME = (By.CSS_SELECTOR, ".race_table_01 tr td:nth-of-type(19)")
    OWNER_NAME = (By.CSS_SELECTOR, ".race_table_01 tr td:nth-of-type(20)")
    PRIZE_NAME = (By.CSS_SELECTOR, ".race_table_01 tr td:nth-of-type(21)")


class ResultPageLocators(object):
    RACE_ID = (By.CSS_SELECTOR,".RaceList_DataItem a")

class ShutubaPageLocators(object):
    HEADS = (By.CSS_SELECTOR, ".Header th")
    HORSE = (By.CSS_SELECTOR, ".HorseList")
    TITLE = (By.CSS_SELECTOR, ".RaceName")
    DATE = (By.CSS_SELECTOR, "#RaceList_DateList .Active a")

    RACE_FIELD_DIST = (By.CSS_SELECTOR, ".RaceData01 span:nth-of-type(1)")
    RACE_NUM = (By.CSS_SELECTOR, ".RaceList_Item01 .RaceNum")
    RACE_NAME = (By.CSS_SELECTOR, ".RaceList_Item02 .RaceName")
    RACE_CLASS1 = (By.CSS_SELECTOR, ".RaceList_Item02 .RaceName .Icon_GradeType:nth-of-type(1)")
    RACE_KAI = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(1)")
    RACE_PLACE = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(2)")
    RACE_DAY = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(3)")
    HORSE_TYPE_AGE = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(4)")
    RACE_CLASS2 = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(5)")
    RACE_TYPE1 = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(6)")
    RACE_TYPE2 = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(7)")
    RACE_TYPE3 = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(8)")
    RACE_PRIZE = (By.CSS_SELECTOR, ".RaceData02 span:nth-of-type(9)")
    