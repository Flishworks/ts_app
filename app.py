import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dash import Dash, html, dcc
from plotly_resampler import FigureResampler
from dash import State, no_update, html, Output, Input
import numpy as np
import parsers as prs
from styles import *

SESSION_DATA = []
app = Dash(__name__)
_fig = make_subplots(rows=1, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[""],
            row_heights=[1]
)
fig = FigureResampler(
    _fig,
    default_n_shown_samples=1000,
    verbose=False,
)
app.layout = html.Div([
    html.Div(
        children = [
            dcc.Upload(id='data_upload', children=html.Div(['Select file to upload']),
                style = uploader_style),
            # refresh button
            html.Button('Clear', id='clear_plots', n_clicks=0, style = clear_button_style),
        ], style={}),
    dcc.Graph(id='plot', figure = fig, config = {'scrollZoom': True, 'displaylogo' : False},
                style = {'height': '100vh'}),
])
fig.register_update_graph_callback (    # Register the plot update callbacks for the resampler
    app=app, graph_id="plot"
)

#### Uploader Callback ####
@app.callback(  Output(component_id='plot', component_property='figure', allow_duplicate=True),
                Input('data_upload', 'contents'),
                State('data_upload', 'filename'),
                prevent_initial_call=True)
def update_plot(content, fname):
    try:
        parsed = prs.parse_router(fname, content)
        global SESSION_DATA
        SESSION_DATA.extend(parsed) #list of dicts, each dict has a df and a height
        num_plots = len(SESSION_DATA)
        row_heights = [parsed['height'] for parsed in SESSION_DATA]
        _fig = make_subplots(rows=num_plots, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02,
                    subplot_titles=[""],
                    row_heights=row_heights
        )

        fig.replace(_fig)
        row = 0
        for parsed in SESSION_DATA:
            row += 1
            df = parsed['df']
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                fig.add_trace(go.Scattergl(name=col, showlegend=True, ), hf_x=df.index, hf_y=df[col], row=row, col=1)
                
        return fig
    
    except Exception as e:
        print(f"Error loading file {fname}")
        print(e)
        return no_update

#### Clear Button Callback ####
@app.callback(  Output(component_id='plot', component_property='figure', allow_duplicate=True),
                Input('clear_plots', 'n_clicks'),
                prevent_initial_call=True)
def clear_plot(n_clicks):
    if n_clicks is None:
        return no_update
    global SESSION_DATA
    SESSION_DATA = []
    _fig = make_subplots(rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=[""],
    )
    fig.replace(_fig)
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8051)

