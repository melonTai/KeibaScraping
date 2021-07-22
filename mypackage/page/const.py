import re

class Place():
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

class Race():
    def __init__(self, id : int or str):
        if isinstance(id, int):
            id = str(id)
        elif isinstance(id, str):
            pass
        else:
            raise Exception(f"invalid argument of type type:{type(id)}")
        if len(id) != 12 or not id.isdecimal():
            raise Exception(f"invalid race_id: {id}")
        self.id = id
        pattern = "(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})"
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