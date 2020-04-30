import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sqlite3

US_data = pd.read_csv('US_energy.csv')

db = sqlite3.connect("Energy.db")

en_sql = US_data.to_sql("Energy", db, if_exists="replace")

tot_query = 'SELECT * FROM Energy WHERE commodity_transaction="Electricity - net production";'

tot_results = pd.read_sql_query(tot_query, db)

app = dash.Dash(__name__)
server = app.server

ren_cats = ['hydro', 'geothermal', 'solar_electricity', 'wind_electricity', 'total_electricity']
app.layout = html.Div([
    html.Div([dcc.Dropdown(id='category-select', options=[{'label': i.capitalize(), 'value': i} for i in ren_cats],
                           value='hydro', style={'width': '140px'})]),
    dcc.Graph('energy_visual', config={'displayModeBar': False})])

@app.callback(
    Output('energy_visual', 'figure'),
    [Input('category-select', 'value')]
)
def update_graph(grpname):
    import plotly.express as px
    return px.bar(US_data[US_data.category == grpname], x='year', y='quantity', labels={'quantity':'Kilowatt-Hours in Millions', 'year':'Year'},
    title=grpname.capitalize() + ' Energy Production')

if __name__ == '__main__':
    app.run_server(debug=False)
