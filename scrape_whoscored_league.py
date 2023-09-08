# Get WhoScored event data for a whole season
import soccerdata as sd
import os
import pandas as pd
import json

league = 'ENG-Premier League'
season = '20-21'
match_id = 1485344

matches = [1485477, 1485471, 1485475]

# Filepath for CSV of matches
dir_fp = os.path.join(league, season)
os.makedirs(dir_fp, exist_ok=True)

# Create/Open league csv file
season_fp = f'{os.path.join(dir_fp, season)}.csv'
open(season_fp, 'a')

events_list = []
for match in matches:
    # Scrape
    print('Reading season')
    ws = sd.WhoScored(leagues=league, seasons=season)
    print('Reading match')
    events = ws.read_events(match_id=match)
    print('Got match event data\nSaving file...')
    # Save to list
    events_list.append(events)

league = pd.concat(events_list, ignore_index=True)
league.to_csv(season_fp)
