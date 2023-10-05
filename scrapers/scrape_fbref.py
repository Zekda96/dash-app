# Scrape from FBRef and save it as csv
import soccerdata as sd
import os
import pandas as pd

league = "ENG-Premier League"
season = '2223'
stats_list = ['possession', 'defense']
stats = 'possession'

fbref = sd.FBref(leagues=league, seasons=season)

# Filepath for league folder
dir_fp = os.path.join('/Users/dgranja/PycharmProjects/dash-app', league, season)
# Create/Open league csv file
os.makedirs(dir_fp, exist_ok=True)
# Filepath
season_fp = f'{os.path.join(dir_fp, season)}_fbref_stats.csv'


stats_series = []
for i, stat in enumerate(stats_list):
    df_stats = fbref.read_player_season_stats(stat_type=stat)

    # Save and read csv to extend multi-index into columns
    df_stats.to_csv(season_fp)
    df = pd.read_csv(season_fp)

    if stat == 'defense':
        columns = ['League', 'Season', 'Team', 'Player', 'Nation', 'Position', 'Age', 'Born', '90s',
                   'Tackles', 'Tackles Won', 'Tackles Def 3rd', 'Tackles Mid 3rd', 'Tackles Att 3rd',
                   'Challenges Won', 'Challenges Attempted', '% of Challenge Success', 'Challenges Lost',
                   'Blocks', 'Blocks - Shot', 'Blocks - Pass',
                   'Interceptions', 'Tackles + Interceptions', 'Clearances', 'Errors'
                   ]
    elif stat == 'possession':
        columns = ['League', 'Season', 'Team', 'Player', 'Nation', 'Position', 'Age', 'Born', '90s',
                   'Touches', 'Touches Def PenAr', 'Touches Def 3rd', 'Touches Mid 3rd', 'Touches Att 3rd',
                   'Touches Att PenAr', 'Touches Live Ball', 'Take-Ons Attempted', 'Successful Take-Ons',
                   'Successful Take-On %', 'Tackled During Take-On', 'Tackled During Take-On %',
                   'Carries', 'Total Carrying Distance', 'Progressive Carrying Distance', 'Progressive Carries',
                   'Carries into Final 3rd', 'Carries Into Penalty Area', 'Miscontrols', 'Dispossessed',
                   'Passes Received', 'Progressive passes Received'
                   ]

    df.columns = columns
    df = df.loc[2:, :]
    data_df = ['League', 'Season', 'Team', 'Player',
               'Nation', 'Age', 'Born', '90s', 'Position']  # Columns to exclude from ranking

    if i == 0:
        # Save players data
        stats_series.append(df.loc[:, df.columns.isin(data_df)])

    # Save stats only
    stats_series.append(
        df.loc[:, ~df.columns.isin(data_df)]
    )


df2 = pd.concat({'Data': stats_series[0],
                 "Possession": stats_series[1],
                 'Defense': stats_series[2]
                 },
                axis=1, names=["l1", "l2"])


pickle_fp = f'{season_fp[:-4]}.pkl'
df2.to_pickle(pickle_fp)
