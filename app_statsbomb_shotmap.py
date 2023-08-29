import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from statsbombpy import sb
#
from pitchly import Pitch
import statsbomb_invert as sbi

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


# --------------------------------DASH APP--------------------------------------

# Sample data for demonstration
df = shots_df

# Create the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Checklist(
        id='scatter-checklist',
        options=[
            {'label': 'Goal', 'value': 'Goal'},
            {'label': 'Post', 'value': 'Post'},
            {'label': 'Off Target', 'value': 'Off T'}
        ],
        value=['Goal'],
        inline=True
    ),
    dcc.Graph(id='scatter-plot')
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

    for val in vals:
        dff = df[df['shot_outcome'] == val]
        for i, shot in enumerate(dff.iterrows()):
            shot = shot[1]
            if i == 0:
                fig = fig.add_scatter(x=[shot['x'], shot['end_x']],
                                      y=[shot['y'], shot['end_y']],
                                      name=f'{val}',
                                      mode="lines+markers",
                                      legendgroup=f'{val}',
                                      marker=dict(
                                          size=[14, 0],
                                          color='rgba(135, 206, 250, 1)',
                                          line_width=3,
                                          line_color='black'
                                      )
                                      )
            else:
                fig = fig.add_scatter(x=[shot['x'], shot['end_x']],
                                      y=[shot['y'], shot['end_y']],
                                      name=f'{val}',
                                      mode="lines+markers",
                                      legendgroup=f'{val}',
                                      showlegend=False,
                                      marker=dict(
                                          size=[14, 0],
                                          color='rgba(135, 206, 250, 1)',
                                          line_width=3,
                                          line_color='black'
                                      )
                                      )

    # Style Goals
    fig.update_traces(selector=dict(type="scatter", name='Goal'),
                      marker=dict(color='red',
                                  ),
                      )

    # Style Off Target
    fig.update_traces(selector=dict(type="scatter", name='Off T'),
                      marker=dict(color='red',
                                  symbol='x-thin'
                                  ),
                      )

    return fig

    # Set y-axis range
    # fig.update_yaxes()


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

