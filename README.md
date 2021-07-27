# KeibaScraping
スクレイピングによりレースや馬データを収集する

# 使用方法
## scrape_results.py
過去のレース結果を取得し、年ごとにcsvで取得

同スクリプトで取得済みcsvのアップデートも可能

'''
python scrape_results.py [レース場id] [開始年] [終了年]
'''

[レース場id](#race_id)

## scrape_horse.py
scrape_results.pyで取得したレース結果csvを読み取り、出場している馬の戦績を取得する

'''
python scrape_horse.py
'''

# レース場id
<a id=race_id><a>
|レース場|id|
|:---|:---|
|札幌|1|
|函館|2|
|福島|3|
|新潟|4|
|東京|5|
|中山|6|
|中京|7|
|京都|8|
|阪神|9|
|小倉|10|
