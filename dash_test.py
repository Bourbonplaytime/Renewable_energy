import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sqlite3

US_data = pd.read_csv('US_energy.csv')

app = dash.Dash(__name__)
server = app.server

ren_cats = ['hydro', 'geothermal', 'solar_electricity', 'wind_electricity', 'total_electricity']
app.layout = html.Div([html.H2('US National Renewable Energy by Source 1990-2014'),
    html.Div([dcc.Dropdown(id='category-select', options=[{'label': i.capitalize(), 'value': i} for i in ren_cats],
                           value='hydro', style={'width': '150px'})]),
    dcc.Graph('energy_visual')])

@app.callback(
    Output('energy_visual', 'figure'),
    [Input('category-select', 'value')]
)
def update_graph(grpname):
    import plotly.express as px
    db = sqlite3.connect("Energy.db")
    en_sql = US_data.to_sql("Energy", db, if_exists="replace")
    tot_query = 'SELECT * FROM Energy WHERE commodity_transaction="Electricity - net production";'
    tot_results = pd.read_sql_query(tot_query, db)
    def pd_object(name):
        query = "SELECT * FROM Energy WHERE category='" + name + "';"
        results = pd.read_sql_query(query, db)
        results[name + '_as_per'] =  results['quantity'] / tot_results['quantity'] * 100
        return results
    op = pd_object(grpname)
    def nat_bar_plotly(df, column, source):
        plot = px.bar(df, x='year', y='quantity', labels={'quantity':'Kilowatt-Hours in Millions', 'year':'Year',
              column:'Percentage of ' + source.capitalize() + ' vs Total'}, hover_data=[column], color=column,
              title=source.capitalize() + ' Energy Production')
        return plot
    graph = nat_bar_plotly(op, grpname + '_as_per', grpname)
    return graph

if __name__ == '__main__':
    app.run_server(debug=True)
