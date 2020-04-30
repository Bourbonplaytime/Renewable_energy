import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

US_data = pd.read_csv('US_energy.csv')

db = sqlite3.connect("Dash_Energy.db")
en_sql = US_data.to_sql("Dash_Energy", db, if_exists="replace")
tot_query = 'SELECT * FROM Dash_Energy WHERE commodity_transaction="Electricity - net production";'
tot_results = pd.read_sql_query(tot_query, db)
def pd_object(name, category):
    query = "SELECT * FROM Dash_Energy WHERE category='" + category + "';"
    results = pd.read_sql_query(query, db)
    results[name + '_as_per'] =  results['quantity'] / tot_results['quantity'] * 100
    return results
wind_results = pd_object('wind', 'wind_electricity')
sol_results = pd_object('sol', 'solar_electricity')
hyd_results = pd_object('hyd', 'hydro')
geo_results = pd_object('geo', 'geothermal')

app = dash.Dash(__name__)
server = app.server

ren_cats = ['hydro', 'geothermal', 'solar_electricity', 'wind_electricity', 'total_electricity']
app.layout = html.Div([html.H2('US National Renewable Energy by Source 1990-2014'),
    html.Div([dcc.Dropdown(id='category-select', options=[{'label': i.capitalize(), 'value': i} for i in ren_cats],
                           value='hydro', style={'width': '150px'})]),
    dcc.Graph('energy_visual'),
    html.Div([html.H2('US National Renewable Energy by Year Side by Side in Kilowatt-Hours:Millions 1990-2014'),
    dcc.Graph(figure = go.Figure(data=[
    go.Bar(name='Wind', x=wind_results['year'], y=wind_results['quantity']),
    go.Bar(name='Solar', x=sol_results['year'], y=sol_results['quantity']),
    go.Bar(name='Hydro', x=hyd_results['year'], y=hyd_results['quantity']),
    go.Bar(name='Geothermal', x=geo_results['year'], y=geo_results['quantity'])
        ]))
    ])
])

@app.callback(
    Output('energy_visual', 'figure'),
    [Input('category-select', 'value')]
)
def update_graph(grpname):
    db = sqlite3.connect("Dash_Energy.db")
    en_sql = US_data.to_sql("Dash_Energy", db, if_exists="replace")
    tot_query = 'SELECT * FROM Dash_Energy WHERE commodity_transaction="Electricity - net production";'
    tot_results = pd.read_sql_query(tot_query, db)
    def pd_object(name):
        query = "SELECT * FROM Dash_Energy WHERE category='" + name + "';"
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
