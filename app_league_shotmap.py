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
plot_df = df[df['team'] == 'Man Utd']
plot_df = plot_df[plot_df['player'].notna()]

plot_df.loc[plot_df['type'] == 'Goal', 'end_x'] = 100.0
plot_df.loc[plot_df['type'] == 'Goal', 'end_y'] = plot_df.loc[plot_df['type'] == 'Goal', 'goal_mouth_y']

# Convert WhoScored coordinates to pitchly coordinates
plot_df['x'] = lfd.convert_x(plot_df['x'], max_x=100)
plot_df['y'] = lfd.convert_y(plot_df['y'], max_y=100, invert_y=False)

plot_df['end_x'] = lfd.convert_x(plot_df['end_x'], max_x=100)
plot_df['end_y'] = lfd.convert_y(plot_df['end_y'], max_y=100, invert_y=False)

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
        className='text-primary my-2'
        # className='btn btn-primary text-white mx-2 my-1 rounded-3',
    )])

player_checklist = dcc.Dropdown(
    id='player-checklist',
    options=[
        {'label': x, 'value': x}
        for x in df.player.unique()
    ],
    value=['Marcus Rashford'],
    multi=True,
    className='text-primary mx-2 my-1 py-1 rounded-3',
)

# ------------------------------ LAYOUT -----------------------------------

# Layout of the app
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1("Event Map", className='text-white text-center')
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            # event_checklist
        ], width=2)

    ], justify='center'),

    dbc.Row([

        dbc.Col([
            dbc.Container([

                dbc.Row([

                    dbc.Col([
                        dcc.Graph(id='scatter-plot')
                    ], width=8),

                    dbc.Col([
                        html.Div('Choose Team'),

                        html.Div('Choose Player'),
                        player_checklist,
                        html.Div('Choose Event'),
                        event_checklist
                    ], width=4, align='center')

                ], justify='start')

            ], className='bg-primary rounded-3 p-5')
        ], width=12),

        dbc.Col([
            dbc.Container([
                # player_checklist,
                # event_checklist
            ], className='bg-white rounded-3')
        ], width=3)

    ], justify='center', align='center', className='blue'),

], className='bg-secondary',
    fluid=True
)


# Callback to update the scatter plot based on checklist selection
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('event-checklist', 'value'),
     Input('player-checklist', 'value')]
)
def update_scatter(vals, players):
    pitch = Pitch()
    fig = pitch.plot_pitch(show=False)
    wh_ratio = 1000 / 700
    w = 400
    fig.update_layout(title_text='Pass map',
                      autosize=True,
                      title_automargin=True,
                      # width=w, height=w/wh_ratio,
                      )
    # fig.update_traces(showlegend=False)

    # Iterate over list of shot types
    df_f = df[df['player'].isin(players)]
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

    return fig

    # Set y-axis range
    # fig.update_yaxes()


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
