import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
#
from pitchly import Pitch
import libfutdata as lfd


def SetColor(x):
    if x == 'Marcus Rashford':
        return 'red'
    else:
        return 'blue'


def get_color(players, player):
    colors_list = ['red', 'blue', 'orange', 'purple', 'white']
    return colors_list[players.index(player)]


# ------------------------------- READ DATA --------------------------------------

df = pd.read_csv('ENG-Premier League/20-21/20-21.csv')

# pass_df = new_df[new_df['type'] == 'Pass']
# plot_df = pass_df[(pass_df['player'] == 'Andy Robertson') & (pass_df['game_id'] == 1485208)]
# plot_df = df[df['team'] == 'Man Utd']
plot_df = df[df['player'].notna()]

plot_df.loc[plot_df['type'] == 'Goal', 'end_x'] = 100.0
plot_df.loc[plot_df['type'] == 'Goal', 'end_y'] = plot_df.loc[plot_df['type'] == 'Goal', 'goal_mouth_y']

# Convert WhoScored coordinates to pitchly coordinates
plot_df.loc[:, 'x'] = lfd.convert_x(plot_df['x'], max_x=100)
plot_df.loc[:, 'y'] = lfd.convert_y(plot_df['y'], max_y=100, invert_y=False)

plot_df.loc[:, 'end_x'] = lfd.convert_x(plot_df['end_x'], max_x=100)
plot_df.loc[:, 'end_y'] = lfd.convert_y(plot_df['end_y'], max_y=100, invert_y=False)

# --------------------------------DASH APP--------------------------------------
# Plug data for demonstration
df = plot_df

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
# ------------------------------ COMPONENTS -----------------------------------

event_checklist = html.Div([
    html.Div('Select Events', className='text-white'),
    dcc.Dropdown(
        id='event-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.type.unique()
        ],
        value=['Goal', 'MissedShot', 'SavedShot'],
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

team_radioitems = html.Div([
    html.Div('Select Team', className='text-white'),
    dcc.RadioItems(
        id='team-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.team.unique()
        ],
        value='Man Utd',
        className='text-black mb-2 rounded-3',
    )
])

# ------------------------------ LAYOUT -----------------------------------

# Layout of the app
app.layout = dbc.Container([

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

                ], justify='center', className='bg-red'),

                dbc.Row([

                    dbc.Col([
                        player_checklist,
                        event_checklist
                    ], width=3, align='top'),

                    dbc.Col([
                        team_checklist
                    ], width=3, align='top')

                ])

            ], className='bg-primary rounded-3 p-5')

        ], width=12),

    ], justify='center', align='center', className='bg-blue'),

],
    className='bg-secondary',
    fluid=True,
    # style={'height': '100vh'}
)


# ------------------------------ CALLBACKS -----------------------------------

# Callback to update the scatter plot based on checklist selection
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('event-checklist', 'value'),
     Input('player-checklist', 'value'),
     Input('team-checklist', 'value'), ]
)
def update_scatter(events, players, team):
    pitch = Pitch()
    fig = pitch.plot_pitch(show=False)
    wh_ratio = 1000 / 700
    w = 1000
    fig.update_layout(title_text='Event map',
                      # title_automargin=True,
                      width=w, height=w / wh_ratio,
                      )
    # fig.update_traces(showlegend=False)

    # Filter by team and events
    df_f = df[df['team'] == team]
    df_f = df_f[df_f['type'].isin(events)]

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

    # Style - Goals
    # fig.update_traces(selector=dict(type="scatter"),
    #                   patch=dict(
    #                       marker=dict(symbol='x',
    #                                   ),
    #                       # line=dict(color='red'
    #                       #           )
    #                   )
    #                   )

    return fig


# Update player dropdown options based on team chosen
@app.callback(
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
@app.callback(
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


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
