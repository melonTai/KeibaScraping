import re
from enum import Enum

class PlaceChuo(Enum):
    Sapporo = 1
    Hakodate = 2
    Fukushima = 3
    Nigata = 4
    Tokyo = 5
    Nakayama = 6
    Tyukyo = 7
    Kyoto = 8
    Hanshin = 9
    Ogura = 10

class PlaceChiho(Enum):
    URAWA = 42
    FUNABASHI = 43
    OI = 44
    KAWASAKI = 45
    MONBETSU = 46
    MORIOKA = 47
    MIZUZAWA = 48
    KANAZAWA = 49
    KASAMATSU = 50
    NAGOYA = 51
    SONODA = 52
    HIMEJI = 53
    KOUCHI = 54
    SAGA = 55
    OBIHIROBA = 56

class Race():
    def __init__(self, id : int or str):
        if isinstance(id, int):
            id = str(id)
        elif isinstance(id, str):
            pass
        else:
            raise Exception(f"invalid argument of type type:{type(id)},  id = {id}")
        
        self.id = id
        pattern = "(\d{4})(\w{2})(\w{2})(\d{2})(\d{2})"
        match = re.findall(pattern, id)
        if match:
            year, place, kai, day, r = match[0]
            self.year = year
            self.place = place
            self.kai = kai
            self.day = day
            self.r = r
        else:
            raise Exception("invalid race_id")

if __name__ == '__main__':
    id = "202005061012"
    race = Race(id)
    print(race.year, race.place, race.kai, race.day, race.r)