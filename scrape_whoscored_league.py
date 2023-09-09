# Get WhoScored event data for a whole season
import soccerdata as sd
import os
import pandas as pd
import json

league = 'ENG-Premier League'
season = '20-21'
match_id = 1485344

#matches = [1485477, 1485471, 1485475]
# Get matches id from cached season file

season_fp = f'/Users/dgranja/soccerdata/data/WhoScored/matches/{league}_20{season[-2:]}.csv'
season_csv = pd.read_csv(season_fp)
games_id = season_csv['game_id'].unique().tolist()


# Filepath for CSV of matches
dir_fp = os.path.join(league, season)
os.makedirs(dir_fp, exist_ok=True)

# Create/Open league csv file
season_fp = f'{os.path.join(dir_fp, season)}.csv'
open(season_fp, 'a')

# Read season
print('Reading season - ')
ws = sd.WhoScored(leagues=league, seasons=season)

events_list = []
for i, match in enumerate(games_id):
    # Scrape
    percent = i/380 * 100
    print(f'Reading match Number {i}/380 - {round(percent,2)} %')
    events = ws.read_events(match_id=match)
    print('Got match event data\nSaving to list...')
    # Save to list
    events_list.append(events)

print('Saving file...')
league = pd.concat(events_list, ignore_index=True)
league.to_csv(season_fp)
print(f'Saved to {season_fp}')
