# -*- coding: utf-8 -*-

"""データ構造系を定義する．

レース場IDやレースのデータ構造が定義される．
"""

import re
from enum import Enum

class PlaceChuo(Enum):
    """中央競馬レース場のid

    Args:
        Enum (int): Enum
    """
    Sapporo = 1#: int: 札幌レース場
    Hakodate = 2#: int: 函館レース場
    Fukushima = 3#: int: 福島レース場
    Nigata = 4#: int: 新潟レース場
    Tokyo = 5#: int: 東京レース場
    Nakayama = 6#: int: 中山レース場
    Tyukyo = 7#: int: 中京レース場
    Kyoto = 8#: int: 京都レース場
    Hanshin = 9#: int: 阪神レース場
    Ogura = 10#: int: 小倉レース場

class PlaceChiho(Enum):
    """地方競馬レース場のid

    Args:
        Enum (int): Enum
    """
    URAWA = 42#: int: 浦和レース場
    FUNABASHI = 43#: int: 船橋レース場
    OI = 44#: int: 大井レース場
    KAWASAKI = 45#: int: 川崎レース場
    MONBETSU = 46#: int: 門別レース場
    MORIOKA = 47#: int: 盛岡レース場
    MIZUZAWA = 48#: int: 水川レース場
    KANAZAWA = 49#: int: 金沢レース場
    KASAMATSU = 50#: int: 笠松レース場
    NAGOYA = 51#: int: 名古屋レース場
    SONODA = 52#: int: 園田レース場
    HIMEJI = 53#: int: 姫路レース場
    KOUCHI = 54#: int: 高知レース場
    SAGA = 55#: int: 佐賀レース場
    OBIHIROBA = 56#: int: 帯広(ば)レース場

class Race():
    """レースのデータ構造
    """
    def __init__(self, id : int or str):
        if isinstance(id, int):
            id = str(id)
        elif isinstance(id, str):
            pass
        else:
            raise Exception(f"invalid argument of type type:{type(id)},  id = {id}")
        
        self.id = id
        pattern = "(\d{4})(\w{2})(\w{2})(\w{2})(\d{2})"
        match = re.findall(pattern, id)
        if match:
            year, place, kai, day, r = match[0]
            self.year = year
            self.place = place
            self.kai = kai
            self.day = day
            self.r = r
        else:
            raise Exception(f"invalid race_id {self.id}")

if __name__ == '__main__':
    id = "202005061012"
    race = Race(id)
    print(race.year, race.place, race.kai, race.day, race.r)