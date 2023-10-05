import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Styling

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial_scale=1.0'}])

app.layout = dbc.Container(
    [
        html.H1("Data Events Dashboard", className='text-center m-3'),
        html.Div([
            dcc.Link(f"{page['name']}", href=page["relative_path"],
                     className='btn btn-secondary m-1 mb-3',
                     style={'background-color': 'blue'})
            for page in dash.page_registry.values()
        ]),

        # Content of each page
        dash.page_container
    ],
    className='bg-primary text-white mx-auto pt-2 px-0',
    style={
        'background-color': 'blue'
    },
    fluid=True
)

if __name__ == '__main__':
    app.run(debug=True)
