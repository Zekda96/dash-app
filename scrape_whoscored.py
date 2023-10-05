# Scrape a single match from WhoScored and save it as csv
import soccerdata as sd
import os
import pandas as pd
import json

league = 'ENG-Premier League'
season = '2021'
match_id = 1485344

#matches = [1485477, 1485471, 1485475]
dir_fp = os.path.join(league, season)
os.makedirs(dir_fp, exist_ok=True)

print('Reading season')
ws = sd.WhoScored(leagues=league, seasons=season)
print('Reading match')
events = ws.read_events(match_id=match_id)
print('Got match event data\nSaving file...')
events.to_csv(f'{os.path.join(dir_fp, str(match_id))}.csv')
