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
    if x == 'Barcelona':
        return 'red'
    else:
        return 'blue'


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
    dcc.Dropdown(
        id='event-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.type.unique()
        ],
        value=['Goal'],
        multi=True,
        className='text-primary mb-2 rounded-3',
    )])

player_checklist = html.Div([
    dcc.Dropdown(
        id='player-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.player.unique()
        ],
        value=['Marcus Rashford'],
        multi=True,
        className='text-primary mb-2 rounded-3',
    )
])

team_checklist = html.Div([
    dcc.Dropdown(
        id='team-checklist',
        options=[
            {'label': x, 'value': x}
            for x in df.team.unique()
        ],
        value='Man Utd',
        clearable=False,
        placeholder="Select a city",
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
                        dcc.Graph(id='scatter-plot')
                    ], width=9),

                    dbc.Col([
                        html.Div('Select Team'),
                        team_checklist,
                        html.Div('Select Players'),
                        player_checklist,
                        html.Div('Select Events'),
                        event_checklist

                    ], width=3, align='center')

                ], justify='center')

            ], className='bg-primary rounded-3 p-5')
        ], width=12),

    ], justify='center', align='center', className='bg-blue'),

], className='bg-secondary',
    fluid=True,
    style={'height': '100vh'}
)


# ------------------------------ CALLBACKS -----------------------------------

# Callback to update the scatter plot based on checklist selection
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('event-checklist', 'value'),
     Input('player-checklist', 'value'),
     Input('team-checklist', 'value'), ]
)
def update_scatter(vals, players, team):
    pitch = Pitch()
    fig = pitch.plot_pitch(show=False)
    wh_ratio = 1000 / 700
    w = 400
    fig.update_layout(title_text='Event map',
                      autosize=True,
                      title_automargin=True,
                      # width=w, height=w/wh_ratio,
                      )
    # fig.update_traces(showlegend=False)

    # Iterate over list of shot types
    df_f = df[df['team'] == team]
    df_f = df_f[df_f['player'].isin(players)]
    for val in vals:
        dff = df_f[df_f['type'] == val]
        for i, event in enumerate(dff.iterrows()):
            event = event[1]
            x = event['x']
            y = event['y']
            end_x = event['end_x']
            end_y = event['end_y']
            fig = fig.add_scatter(x=[x, end_x],
                                  y=[y, end_y],
                                  name=val,
                                  mode="lines+markers",
                                  legendgroup=val,
                                  marker_color=list(map(SetColor, [event['team']])),
                                  showlegend=False
                                  )
            # Only add label to first marker of each shot type
            if i == 0:
                fig.update_traces(showlegend=True, selector=dict(name=val))
    # Set y-axis range
    # fig.update_yaxes()
    return fig


# Update dropdown options
@app.callback(
    Output("player-checklist", "options"),
    Input("team-checklist", "value")
)
def update_options(team):
    options = [
        {'label': x, 'value': x}
        for x in df.loc[df['team'] == team, 'player'].unique()
    ],
    return options[0]


@app.callback(
    Output("player-checklist", "value"),
    Input("team-checklist", "value")
)
def update_value(team):
    players_list = df.loc[df["team"] == team, "player"].unique()
    max_goalscorer = ''
    max_goals = 0
    for player in players_list:
        goals = len(df[(df['type'] == 'Goal') & (df['player'] == player)])
        if goals > max_goals:
            max_goals = goals
            max_goalscorer = player
    default_player = max_goalscorer
    return [default_player]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
