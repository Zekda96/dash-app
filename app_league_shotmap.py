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


# Read Data

new_df = pd.read_csv('ENG-Premier League/20-21/20-21.csv')

pass_df = new_df[new_df['type'] == 'Pass']
ar_passes_df = pass_df[(pass_df['player'] == 'Andy Robertson') & (pass_df['game_id'] == 1485208)]
plot_df = ar_passes_df[ar_passes_df['minute'] == 11]

# Convert WhoScored coordinates to pitchly coordinates
# Convert from statsbomb yards to meters
plot_df['x'] = lfd.convert_x(plot_df['x'], max_x=100)
plot_df['y'] = lfd.convert_y(plot_df['y'], max_y=100, invert_y=False)

plot_df['end_x'] = lfd.convert_x(plot_df['end_x'], max_x=100)
plot_df['end_y'] = lfd.convert_y(plot_df['end_y'], max_y=100, invert_y=False)

# --------------------------------DASH APP--------------------------------------


# Sample data for demonstration
df = plot_df

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

# Layout of the app
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1("Event Map", className='text-secondary text-center')

        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Checklist(
                id='scatter-checklist',
                options=[
                    {'label': 'Goal', 'value': 'Goal'},
                    {'label': 'Post', 'value': 'Post'},
                    {'label': 'Off Target', 'value': 'Off T'}
                ],
                value=['Goal'],
                inline=True
            )
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Checklist(
                id='team1-checklist',
                options=[
                    {'label': 'Jugador1', 'value': 'Jugador1'},
                    {'label': 'Jugador2', 'value': 'Jugador2'},
                ],
                value=['Jugador2'],
                inline=False
            )
        ], width=1),
        dbc.Col([
            dcc.Graph(id='scatter-plot')
            ], width=11)
        ])
])


# Callback to update the scatter plot based on checklist selection
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('scatter-checklist', 'value')]
)
def update_scatter(vals):
    pitch = Pitch()
    fig = pitch.plot_pitch(show=False)
    fig.update_layout(title_text='Pass map')
    #fig.update_traces(showlegend=False)

    # Iterate over list of shot types
    for val in vals:
        for i, shot in enumerate(plot_df.iterrows()):
            shot = shot[1]
            fig = fig.add_scatter(x=[shot['x'], shot['end_x']],
                                  y=[shot['y'], shot['end_y']],
                                  name=val,
                                  mode="lines+markers",
                                  legendgroup=val,
                                  marker_color=list(map(SetColor, [shot['team']])),
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

