# Scrape from FBRef and save it as csv
import soccerdata as sd
import os
import pandas as pd
from gspread_dataframe import set_with_dataframe


def get_data(stat_name: str):
    print(f'Saving [{stat_name}]')
    #
    df_stats = fbref.read_player_season_stats(stat_type=stat_name)
    # Save and read csv to extend multi-index into columns
    df_stats.to_csv('fbref_stats.csv')
    df1 = pd.read_csv('fbref_stats.csv')
    os.remove('fbref_stats.csv')

    # Multi-index splits into several rows. Grab all column names and put them
    # together
    #
    # Some are in row 1
    player_data = df1.iloc[1, :4].reset_index(drop=True).tolist()
    # Some stayed as a column name
    matches = df1.columns[4:8].tolist()
    # And other are on row 0
    stats = df1.iloc[0, 8:].reset_index(drop=True).tolist()
    # Ignore first 2 rows
    df1 = df1.loc[2:, :]
    df1.columns = player_data + matches + stats
    df1 = df1.reset_index(drop=True)
    return df1


def get_data_passing():
    print(f'Saving [passing]]')
    #
    df_stats = fbref.read_player_season_stats(stat_type='passing')
    # Save and read csv to extend multi-index into columns
    df_stats.to_csv('fbref_stats.csv')
    df1 = pd.read_csv('fbref_stats.csv')
    os.remove('fbref_stats.csv')

    # Multi-index splits into several rows. Grab all column names and put them
    # together
    #
    # Some are in row 1
    player_data = df1.iloc[1, :4].reset_index(drop=True).tolist()
    # Some stayed as a column name
    matches = df1.columns[4:9].tolist()
    stats2 = df1.columns[23:].tolist()
    # And other are on row 0
    stats1 = df1.iloc[0, 9:23].reset_index(drop=True).tolist()
    # Ignore first 2 rows
    df1 = df1.loc[2:, :]
    df1.columns = player_data + matches + stats1 + stats2
    df1 = df1.reset_index(drop=True)
    return df1


def get_data_passing_types():
    print(f'Saving [passing_types]')
    df_stats = fbref.read_player_season_stats(stat_type='passing_types')
    # Save and read csv to extend multi-index into columns
    df_stats.to_csv('fbref_stats.csv')
    df1 = pd.read_csv('fbref_stats.csv')
    os.remove('fbref_stats.csv')

    # Multi-index splits into several rows. Grab all column names and put them
    # together
    #
    # Some are in row 1
    player_data = df1.iloc[1, :4].reset_index(drop=True).tolist()
    # Some stayed as a column name
    matches = df1.columns[4:10].tolist()
    # And other are on row 0
    stats = df1.iloc[0, 10:24].reset_index(drop=True).tolist()
    # Ignore first 2 rows since they don't contain data
    df1 = df1.loc[2:, :]
    df1.columns = player_data + matches + stats
    df1 = df1.reset_index(drop=True)
    return df1


league = "ENG-Premier League"
season = '22-23'
stats_list = ["standard", 'shooting', "passing", "passing_types",
              "goal_shot_creation", 'defense', 'possession', "misc",
              "keeper", "keeper_adv"]
# stats_list = ["standard", "shooting"]

fbref = sd.FBref(leagues=league, seasons=season)

# Filepath for league folder
dir_fp = os.path.join('/Users/dgranja/PycharmProjects/dash-app',
                      league,
                      season
                      )
# Create/Open league csv file
os.makedirs(dir_fp, exist_ok=True)
# Filepath
season_fp = f'{os.path.join(dir_fp, season)}_fbref_stats.csv'

# Get all data
df_standard = get_data('standard')
df_shooting = get_data('shooting')
df_passing = get_data_passing()
df_passing_types = get_data_passing_types()
df_gsca = get_data('goal_shot_creation')
df_defense = get_data('defense')
df_possession = get_data('possession')
df_misc = get_data('misc')


# ---------------------------- Merging data -----------------------------------
# ----------------------------- Standard --------------------------------------
df = df_standard.iloc[:, 0:12]  # Get players data
df = df.join(df_standard.iloc[:, 15])  # Get npG

# Rename column names where desired
df = df.rename(columns={'G-PK': 'npGoals'})

# ------------------------------- Shooting ------------------------------------
df = df.join(df_shooting.iloc[:, 9:26])  # Get shooting stats
df = df.rename(
    columns={
        'Gls': 'Goals',
        'Sh': 'Shots',
        'SoT': 'SoT',
        'SoT%': 'SoT%',
        'Sh/90': 'Sh/90',
        'SoT/90': 'SoT/90',
        'G/Sh': 'G/Sh',
        'G/SoT': 'G/SoT',
        'Dist': 'AvgShotDistance',
        'FK': 'FKShots',
        'PK': 'PK',
        'PKatt': 'PKsAtt',
        'xG': 'xG',
        'npxG': 'npxG',
        'npxG/Sh': 'npxG/Sh',
        'G-xG': 'G-xG',
        'np:G-xG': 'npG-xG',
    }
)
# -------------------------------- Passing ------------------------------------
df = df.join(df_passing.iloc[:, 9:14])  # Get passing stats
df = df.rename(
    columns={
        'Cmp': 'PassesCompleted',
        'Att': 'PassesAttempted',
        'Cmp%': 'TotCmp%',
        'TotDist': 'TotalPassDist',
        'PrgDist': 'ProgPassDist',
    }
)
df = df.join(df_passing.iloc[:, 14:17])  # Get passing stats
df = df.rename(
    columns={
        'Cmp': 'ShortPassCmp',
        'Att': 'ShortPassAtt',
        'Cmp%': 'ShortPassCmp%',
    }
)
df = df.join(df_passing.iloc[:, 17:20])  # Get passing stats
df = df.rename(
    columns={
        'Cmp': 'MedPassCmp',
        'Att': 'MedPassAtt',
        'Cmp%': 'MedPassCmp%',

    }
)
df = df.join(df_passing.iloc[:, 20:32])  # Get passing stats
df = df.rename(
    columns={
        'Cmp': 'LongPassCmp',
        'Att': 'LongPassAtt',
        'Cmp%': 'LongPassCmp%',
        'Ast': 'Assists',
        'xAG': 'xAG',
        'xA': 'xA',
        'A-xAG': 'A-xAG',
        'KP': 'KeyPasses',
        '1/3': 'Final1/3Cmp',
        'PPA': 'PenAreaCmp',
        'CrsPA': 'CrsPenAreaCmp',
        'PrgP': 'ProgPasses'
    }
)
# -------------------------- Passing Types ------------------------------------
df = df.join(df_passing_types.iloc[:, 10:21])  # Get stats
df = df.rename(
    columns={
        'Live': 'LivePass',
        'Dead': 'DeadPass',
        'FK': 'FKPasses',
        'TB': 'ThruBalls',
        'Sw': 'Switches',
        'Crs': 'Crs',
        'TI': 'ThrowIn',
        'CK': 'CornerKicks',
        'In': 'InSwingCK',
        'Out': 'OutSwingCK',
        'Str': 'StraightCK',
    }
)
df = df.join(df_passing_types.iloc[:, 22:24])  # Get stats
df = df.rename(
    columns={
        'Off': 'PassesOffside',
        'Blocks': 'PassesBlocked',
    }
)
# --------------------- Goal & Shot Creation Actions --------------------------
df = df.join(df_gsca.iloc[:, 9:17])  # Get SCA stats
df = df.rename(
    columns={
        'SCA': 'SCA',
        'SCA90': 'SCA90',
        'PassLive': 'SCAPassLive',
        'PassDead': 'SCAPassDead',
        'TO': 'SCADrib',
        'Sh': 'SCASh',
        'Fld': 'SCAFld',
        'Def': 'SCADef',
    }
)
df = df.join(df_gsca.iloc[:, 17:25])  # Get GCA stats
df = df.rename(
    columns={
        'GCA': 'GCA',
        'GCA90': 'GCA90',
        'PassLive': 'GCAPassLive',
        'PassDead': 'GCAPassDead',
        'TO': 'GCADrib',
        'Sh': 'GCASh',
        'Fld': 'GCAFld',
        'Def': 'GCADef'
    }
)
#
#     elif stat == 'defense':
#         df = df.rename(
#             columns={'Tkl': 'Tkl',
#                      'TklW': 'TklWinPoss',
#                      'Def 3rd': 'Def3rdTkl',
#                      'Mid 3rd': 'Mid3rdTkl',
#                      'Att 3rd': 'Att3rdTkl',
#                      'Tkl': 'DrbTkl',
#                      'Att': 'DrbPastAtt',
#                      'Tkl%': 'DrbTkl%',
#                      'Lost': 'DrbPast',
#                      'Blocks': 'Blocks',
#                      'Sh': 'ShBlocks',
#                      'Pass': 'PassBlocks',
#                      'Int': 'Int',
#                      'Tkl+Int': 'Tkl+Int',
#                      'Clr': 'Clr',
#                      'Err': 'Err'
#                      }
#         )
#
#     elif stat == 'possession':
#         df = df.rename(
#             columns={'Touches': 'Touches',
#                      'Def Pen': 'DefPenTouch',
#                      'Def 3rd': 'Def3rdTouch',
#                      'Mid 3rd': 'Mid3rdTouch',
#                      'Att 3rd': 'Att3rdTouch',
#                      'Att Pen': 'AttPenTouch',
#                      'Live': 'LiveTouch',
#                      'Succ': 'SuccDrb',
#                      'Att': 'AttDrb',
#                      'Succ%': 'DrbSucc%',
#                      'Tkld': 'TimesTackled',
#                      'Tkld%': 'TimesTackled%',
#                      'Carries': 'Carries',
#                      'TotDist': 'TotalCarryDistance',
#                      'PrgDist': 'ProgCarryDistance',
#                      'PrgC': 'ProgCarries',
#                      '1/3': 'CarriesToFinalThird',
#                      'CPA': 'CarriesToPenArea',
#                      'Mis': 'CarryMistakes',
#                      'Dis': 'Disposesed',
#                      'Rec': 'ReceivedPass',
#                      'PrgR': 'ProgPassesRec'})
#
#     elif stat == 'misc':
#         df = df.rename(
#             columns={'CrdY': 'Yellows',
#                      'CrdR': 'Reds',
#                      '2CrdY': 'Yellow2',
#                      'Fls': 'Fls',
#                      'Fld': 'Fld',
#                      'Off': 'Off',
#                      'PKwon': 'PKwon',
#                      'PKcon': 'PKcon',
#                      'OG': 'OG',
#                      'Recov': 'Recov',
#                      'Won': 'AerialWins',
#                      'Lost': 'AerialLoss',
#                      'Won%': 'AerialWin%',
#                      }
#         )
#
#     elif stat == 'keeper':
#         df.rename(
#             columns={'GA': 'GA',
#                      'GA90': 'GA90',
#                      'SoTA': 'SoTA',
#                      'Saves': 'Saves',
#                      'Save%.1': 'Save%',
#                      'W': 'W',
#                      'D': 'D',
#                      'L': 'L',
#                      'CS': 'CS',
#                      'CS%': 'CS%',
#                      'PKsFaced': 'PKsFaced',
#                      'PKA': 'PKA',
#                      'PKsv': 'PKsv',
#                      'PKm': 'PKm',
#                      'Save%.2': 'PKSave%'
#                      }
#         )
#
#     elif stat == "keeper_adv":
#         df.rename(
#             columns={'PKA': 'PKGA',
#                      'FK': 'FKGA',
#                      'CK': 'CKGA',
#                      'OG': 'OGA',
#                      'PSxG': 'PSxG',
#                      'PSxG/SoT': 'PSxG/SoT',
#                      'PSxG+/-': 'PSxG+/-',
#                      '/90': 'PSxG+/- /90',
#                      'Cmp': 'LaunchCmp',
#                      'Att': 'LaunchAtt',
#                      'Cmp%': 'LaunchPassCmp%',
#                      'Att': 'PassAtt',
#                      'Thr': 'PassThr',
#                      'Launch%': 'PassesLaunch%',
#                      'AvgLen': 'AvgLenLaunch',
#                      'Att': 'GoalKicksAtt',
#                      'Launch%': 'GoalKicksLaunch%',
#                      'AvgLen': 'AvgLen',
#                      'Opp': 'OppCrs',
#                      'Stp': 'StpCrs',
#                      'Stp%': 'CrsStp%',
#                      '#OPA': '#OPA',
#                      '#OPA/90': '#OPA/90',
#                      'AvgDist': 'AvgDistOPA'
#                      }
#
#         )
#
#     data_df = ['league', 'season', 'team', 'player',
#                'nation',  'pos', 'age', 'born', '90s',]  # Columns to exclude from ranking
#     if i == 0:
#         # Save players data
#         stats_series.append(
#             df.loc[:, df.columns.isin(data_df)]
#         )
#
#     # Save stats only
#     stats_series.append(
#         df.loc[:, ~df.columns.isin(data_df)]
#     )
#
#
# df2 = pd.concat(stats_series, axis=1).reset_index(drop=True)
#

df2.to_csv(f'{season_fp}', index=False)
print(f'Saved to {season_fp}')
# pickle_fp = f'{season_fp[:-4]}.pkl'
# df2.to_pickle(pickle_fp)
