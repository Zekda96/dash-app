import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
#
from pitchly import Pitch
import libfutdata as lfd


def get_color(players, player):
    colors_list = ['red', 'blue', 'orange', 'purple', 'white']
    return colors_list[players.index(player)]


# ------------------------------- READ DATA --------------------------------------
season = '2223'
df = pd.read_csv(f'/Users/dgranja/PycharmProjects/dash-app/ENG-Premier League/{season}/{season}.csv')

# Clean dataframe
df = df[~df['type'].isin(['Smother', 'ShieldBallOpp', 'Card'])]  # Ignore these events
plot_df = df[df['player'].notna()]  # Eliminate non-player rows

# Add end coordinates for Goals
plot_df.loc[plot_df['type'] == 'Goal', 'end_x'] = 100.0
plot_df.loc[plot_df['type'] == 'Goal', 'end_y'] = plot_df.loc[plot_df['type'] == 'Goal', 'goal_mouth_y']

# Convert WhoScored coordinates to pitchly coordinates
plot_df.loc[:, 'x'] = lfd.convert_x(plot_df['x'], max_x=100)
plot_df.loc[:, 'y'] = lfd.convert_y(plot_df['y'], max_y=100, invert_y=False)
plot_df.loc[:, 'end_x'] = lfd.convert_x(plot_df['end_x'], max_x=100)
plot_df.loc[:, 'end_y'] = lfd.convert_y(plot_df['end_y'], max_y=100, invert_y=False)

# --------------------------------DASH APP--------------------------------------
# Plug data
df = plot_df

# Create the Dash app
dash.register_page(__name__, path='/')
# ------------------------------ COMPONENTS -----------------------------------

event_checklist = html.Div([
    html.Div('Select Events', className='text-white'),
    dcc.Dropdown(
        id='event-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.sort_values('type').type.unique()
        ],
        value=['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost'],
        multi=True,
        className='text-primary mb-2 rounded-3',
    )])

player_checklist = html.Div([
    html.Div('Select Players', className='text-white'),
    dcc.Dropdown(
        id='player-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.player.unique()
        ],
        multi=True,
        className='text-primary mb-2 rounded-3',
    )
])

team_checklist = html.Div([
    html.Div('Select Team', className='text-white'),
    dcc.Dropdown(
        id='team-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.sort_values('team').team.unique()
        ],
        value='Man Utd',
        clearable=False,
        placeholder="Select a city",
        className='text-black mb-2 rounded-3',

    )
])

plot_filter_checklist = html.Div([
    html.Div('Choose graph', className='text-white'),
    dbc.Container([
        dcc.Checklist(
            id='plot-filter-checklist',
            options=[
                {'label': 'Scatter', 'value': 'plot_dots'},
                {'label': 'Heatmap', 'value': 'plot_hm'},
            ],
            value=['plot_dots', 'plot_hm'],
            className='text-black',
            inputClassName='px-2'
        )
    ], className='bg-white mb-2 rounded-3'
    )
])

# ------------------------------ LAYOUT -----------------------------------

# Layout of the app
layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1("EPL 20/21 - Event Map", className='text-white text-center')
        ], width=12)
    ]),

    dbc.Row([

        dbc.Col([

            dbc.Container([

                dbc.Row([

                    dbc.Col([

                        html.Center(
                            dcc.Graph(id='scatter-plot',
                                      # style={'paddingLeft': '50%'}
                                      )
                        )

                    ], width=12),

                ], justify='center'),

                dbc.Row([

                    dbc.Col([
                        player_checklist,
                        event_checklist,
                    ], width=3, align='top'),

                    dbc.Col([
                        team_checklist,
                        plot_filter_checklist,
                    ], width=3, align='top')

                ])

            ], className='bg-primary rounded-3 p-5')

        ], width=12),

    ], justify='center', align='center'),

],
    className='bg-secondary',
    fluid=True,
    # style={'height': '100vh'}
)


# ---------------------------------------------------- CALLBACKS ------------------------------------------------------


# Update player dropdown options based on team chosen
@callback(
    Output("player-checklist", "options"),
    Input("team-checklist", "value")
)
def update_options(team):
    s_df = df.sort_values('player')
    options = [
        {'label': x, 'value': x}
        for x in s_df.loc[s_df['team'] == team, 'player'].unique()
    ],
    return options[0]


# Update player dropdown default value from chosen team top 3 goalscorers (Depending on team chosen)
@callback(
    Output("player-checklist", "value"),
    Input("team-checklist", "value")
)
def update_value(team):
    players_list = df.loc[df["team"] == team, "player"].unique()
    max_goalscorer = []
    sec_gs = []
    third_gs = []
    max_goals, sec_goals, thi_goals = [0, 0, 0]
    for player in players_list:
        goals = len(df[(df['type'] == 'Goal') & (df['player'] == player)])
        if goals > max_goals:
            max_goals = goals
            max_goalscorer = player
        elif goals > sec_goals:
            sec_goals = goals
            sec_gs = player
        elif goals > thi_goals:
            thi_goals = goals
            third_gs = player
    return [max_goalscorer, sec_gs, third_gs]


# ------------------------------------- CALLBACK: MAIN SCATTER PLOT --------------------------------------------------
@callback(
    Output('scatter-plot', 'figure'),
    [Input('event-checklist', 'value'),
     Input('player-checklist', 'value'),
     Input('team-checklist', 'value'),
     Input('plot-filter-checklist', 'value'), ]
)
def update_scatter(events, players, team, filter_list):
    pitch = Pitch()
    fig = pitch.plot_pitch(show=False)
    wh_ratio = 1000 / 700
    w = 1000
    fig.update_layout(
        title_text='Event map',
        # title_automargin=True,
        width=w, height=w / wh_ratio,
        )
    # fig.update_traces(showlegend=False)

    # Filter by team and events
    df_f = df[df['team'] == team]
    df_f = df_f[df_f['type'].isin(events)]

    if 'plot_dots' in filter_list:
        # Plot markers by player
        for p in players:
            c = get_color(players, p)
            dff = df_f[df_f['player'] == p]
            # Iter over all events for selected player
            for i, event in enumerate(dff.iterrows()):
                event = event[1]
                x = event['x']
                y = event['y']
                end_x = event['end_x']
                end_y = event['end_y']
                if event['type'] == 'Goal':
                    fig = fig.add_scatter(x=[x, end_x],
                                          y=[y, end_y],
                                          name=p,
                                          mode="lines+markers",
                                          legendgroup=p,
                                          customdata=np.stack([event['type']]),
                                          # Styling
                                          marker_size=8, marker_color=c,
                                          # marker_symbol='x',
                                          # marker_opacity=0.5,
                                          # opacity=0.5,
                                          line_color='white', line_dash='dot',
                                          showlegend=False
                                          )

                else:
                    fig = fig.add_scatter(x=[x, end_x],
                                          y=[y, end_y],
                                          name=p,
                                          mode="lines+markers",
                                          legendgroup=p,
                                          customdata=np.stack([event['type']]),
                                          # Styling
                                          marker_size=8, marker_color=c,
                                          marker_symbol='x',
                                          # marker_opacity=0.5,
                                          # opacity=0.5,
                                          line_color='white', line_dash='dot',
                                          showlegend=False
                                          )
                # Only add label to first marker of each shot type
                if i == 0:
                    fig.update_traces(showlegend=True, selector=dict(legendgroup=p))

    if 'plot_hm' in filter_list:
        yl = 68
        xl = 106

        y_num = 6
        x_num = 12

        hist_df = df_f[df_f['player'].isin(players)]
        fig.add_trace(go.Histogram2d(x=hist_df['x'],
                                     y=hist_df['y'],
                                     # colorscale='YlGn',
                                     colorscale='Greens',
                                     opacity=0.8,
                                     # zmax=10,
                                     # nbinsx=9,
                                     # nbinsy=9,
                                     ybins=dict(start=-34, end=34, size=yl / y_num),
                                     xbins=dict(start=-53, end=53, size=xl / x_num),
                                     zauto=False,
                                     ))

    return fig
