# Scrape from FBRef and save it as csv
import soccerdata as sd
import os
import pandas as pd

league = "ENG-Premier League"
season = '2223'
stats = 'possession'

fbref = sd.FBref(leagues=league, seasons=season)

df_stats = fbref.read_player_season_stats(stat_type=stats)

df_stats.head()

# Filepath for CSV of stats
dir_fp = os.path.join('/Users/dgranja/PycharmProjects/dash-app', league, season)
# Create/Open league csv file
os.makedirs(dir_fp, exist_ok=True)

# Save to csv
season_fp = f'{os.path.join(dir_fp, season)}_fbref_{stats}.csv'
df_stats.to_csv(season_fp)

# Read to edit
df = pd.read_csv(season_fp)
if stats == 'defense':
    columns = ['League', 'Season', 'Team', 'Player', 'Nation', 'Position', 'Age', 'Born', '90s',
               'Tackles', 'Tackles Won', 'Tackles Def 3rd', 'Tackles Mid 3rd', 'Tackles Att 3rd',
               'Challenges Won','Challenges Attempted','% of Challenge Success', 'Challenges Lost',
               'Blocks','Blocks - Shot', 'Blocks - Pass',
               'Interceptions', 'Tackles + Interceptions', 'Clearances', 'Errors'
               ]
elif stats == 'possession':
    columns = ['League', 'Season', 'Team', 'Player', 'Nation', 'Position', 'Age', 'Born', '90s',
               'Touches', 'Touches Def PenAr', 'Touches Def 3rd', 'Touches Mid 3rd', 'Touches Att 3rd',
               'Touches Att PenAr', 'Touches Live Ball', 'Take-Ons Attempted', 'Successful Take-Ons',
               'Successful Take-On %', 'Tackled During Take-On', 'Tackled During Take-On %',
               'Carries', 'Total Carrying Distance', 'Progressive Carrying Distance', 'Progressive Carries',
               'Carries into Final 3rd', 'Carries Into Penalty Area', 'Miscontrols', 'Dispossessed',
               'Passes Received', 'Progressive passes Received'
               ]


df.columns = columns
df = df.iloc[2:]

df.to_csv(f'{season_fp}', index=False)



