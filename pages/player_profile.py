import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plot_pizza as piz
import matplotlib.pyplot as plt

#
from pitchly import Pitch
import libfutdata as lfd

import plotly.graph_objects as go


# --------------------------------DASH APP--------------------------------------
# Plug data


# Create the Dash app
dash.register_page(__name__)

# ------------------------------ COMPONENTS -----------------------------------

# ---------------------------------- PIZZA CHART -------------------------------

fig = piz.get_pizza()
plt.title('Hello', fontdict={'color': 'red'})
src = piz.mpl_to_plotly(fig)
radar1 = html.Img(src=src)


# ------------------------------ LAYOUT -----------------------------------

layout = dbc.Container([

    dbc.Row([

        dbc.Col([

            dbc.Container([


                html.Center(radar1),

            ],
                className='bg-primary rounded-3 p-5'
            )

        ], width=6, align='center'),

    ], justify='center')

],
    className='bg-secondary',
    fluid=True,
)
