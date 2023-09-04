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
import statsbomb_invert as sbi


def SetColor(x):
    if x == 'Barcelona':
        return 'red'
    else:
        return 'blue'


# Read Data

events = pd.read_csv('match_69302.csv')


new_df = events[['team', 'player', 'type', 'timestamp', 'period', 'location', 'shot_statsbomb_xg',
                 'shot_body_part', 'shot_technique', 'shot_outcome', 'shot_end_location']]

shots_df = new_df[(new_df['type'] == 'Shot')]

# Separate coordinates
lis = shots_df.location.str.split(',', expand=True)
shots_df['x'] = pd.to_numeric(lis[0].str.strip('['))
shots_df['y'] = pd.to_numeric(lis[1].str.strip(']'))

lis = shots_df.shot_end_location.str.split(',', expand=True)
shots_df['end_x'] = pd.to_numeric(lis[0].str.strip('['))
shots_df['end_y'] = pd.to_numeric(lis[1].str.strip(']'))
shots_df['end_z'] = pd.to_numeric(lis[2].str.strip(']'))

# shots_df[['x', 'y']] = shots_df['location'].apply(pd.Series)
# shots_df[['end_x', 'end_y', 'end_z']] = shots_df['shot_end_location'].apply(pd.Series)

# Convert from statsbomb yards to meters
shots_df['x'] = sbi.convert_x(shots_df['x'])
shots_df['y'] = sbi.convert_y(shots_df['y'])

shots_df['end_x'] = sbi.convert_x(shots_df['end_x'])
shots_df['end_y'] = sbi.convert_y(shots_df['end_y'])

# Edit timestamp
t = shots_df['timestamp'].str.split(':', expand=True)[[1, 2]]
m = t[1]
s = t[2].str.split('.', expand=True)[0]
shots_df['timestamp'] = pd.DataFrame(m + ':' + s)


# --------------------------------DASH APP--------------------------------------

# Sample data for demonstration
df = shots_df

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
            dcc.Graph(id='scatter-plot')
            ], width=12)
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
        dff = df[df['shot_outcome'] == val]
        for i, shot in enumerate(dff.iterrows()):
            shot = shot[1]
            fig = fig.add_scatter(x=[shot['x'], shot['end_x']],
                                  y=[shot['y'], shot['end_y']],
                                  name=val,
                                  mode="lines+markers",
                                  legendgroup=val,
                                  customdata=np.stack([shot[['shot_statsbomb_xg', 'shot_body_part',
                                                             'timestamp', 'period',
                                                             'player', 'team']]]),
                                  hovertemplate='<b>Team</b>: %{customdata[5]}<br>' +
                                                '<b>Player</b>: %{customdata[4]}<br>' +
                                                '<b>xG</b>: %{customdata[0]:.2f}<br>' +
                                                '<b>Body Part</b>: %{customdata[1]}<br>' +
                                                '<b>Min</b>: %{customdata[2]} (%{customdata[3]}° Half)<br>' +
                                                '<extra></extra>',
                                  marker_color=list(map(SetColor, [shot['team']])),
                                  showlegend=False
                                  )
            # Only add label to first marker of each shot type
            if i == 0:
                fig.update_traces(showlegend=True, selector=dict(name=val))

    # General Scatter properties
    fig.update_traces(selector=dict(type="scatter"),
                      patch=dict(
                          marker=dict(size=[18, 0],
                                      #color='rgba(135, 206, 250, 1)',
                                      line_color='black'
                                      ),
                          line=dict(dash="dot",
                                    color='black',
                                    width=4
                                    )
                      )
                      )
    # Scatter properties by team
    # fig.update_traces(selector=dict(name="scatter"),
    #                   patch=dict(
    #                       marker=dict(size=[18, 0],
    #                                   color='rgba(135, 206, 250, 1)',
    #                                   line_color='black'
    #                                   ),
    #                       line=dict(dash="dot",
    #                                 color='black',
    #                                 width=4
    #                                 )
    #                   )
    #                   )

    # Style - Goals
    # fig.update_traces(selector=dict(type="scatter", name='Goal'),
    #                   patch=dict(
    #                       marker=dict(color='red',
    #                                   ),
    #                       line=dict(color='red'
    #                                 )
    #                   )
    #                   )

    # Style - Off Target
    fig.update_traces(selector=dict(type="scatter", name='Off T'),
                      marker=dict(symbol='x'
                                  ),
                      )

    return fig

    # Set y-axis range
    # fig.update_yaxes()


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

