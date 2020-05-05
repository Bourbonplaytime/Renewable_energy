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

by_state = pd.read_excel (r'annual_generation_state.xls', header=None)
by_state = by_state.rename(columns={0:"Year", 1:"State", 2:"Type_of_producer", 3:"Energy_Source", 4:"Generation(Megawatt_Hours)"})
by_state = by_state.drop([0,1], axis=0)

app = dash.Dash(__name__)
server = app.server

ren_cats = ['hydro', 'geothermal', 'solar_electricity', 'wind_electricity']
st_cats = ['Hydroelectric Conventional', 'Solar Thermal and Photovoltaic', 'Wind', 'Geothermal']
app.layout = html.Div([html.H2('US National Renewable Energy by Source 1990-2014'),
    html.Div([dcc.Dropdown(id='category-select', options=[{'label': i.capitalize(), 'value': i} for i in ren_cats],
                           value='hydro', style={'width': '150px'})]),
    dcc.Graph('energy_visual'),
    html.Div([
    html.H2('US National Renewable Energy Side by Side by Year in Kilowatt-Hours:Millions 1990-2014'),
    dcc.Graph(figure = go.Figure(data=[
    go.Bar(name='Wind', x=wind_results['year'], y=wind_results['quantity']),
    go.Bar(name='Solar', x=sol_results['year'], y=sol_results['quantity']),
    go.Bar(name='Hydro', x=hyd_results['year'], y=hyd_results['quantity']),
    go.Bar(name='Geothermal', x=geo_results['year'], y=geo_results['quantity'])
        ]))
    ]),
    html.Div([
    html.H2('US Renewable Energy by State 2018'),
    dcc.Dropdown(id='source-select', options=[{'label': i.capitalize(), 'value': i} for i in st_cats],
                           value='Hydroelectric Conventional', style={'width': '150px'}),
    dcc.Graph('by_state')
    ]),
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

@app.callback(
    Output('by_state', 'figure'),
    [Input('source-select', 'value')]
)
def make_choropleth(source):
    def st_df_object(source, year):
        results = (by_state['Energy_Source'] == source) & (by_state['Type_of_producer'] ==
                "Total Electric Power Industry") & (by_state['Year'] == year)
        results = by_state[results]
        drop = results.index[results['State'] == 'US-Total']
        results = results.drop(index=drop)
        return results
    df = st_df_object(source, 2018)
    def plotly_choropleth(df, source):
        fig = go.Figure(data=go.Choropleth(
        locations=df['State'],
        z = df['Generation(Megawatt_Hours)'],
        locationmode = 'USA-states',
        colorscale = 'Reds',
        colorbar_title = "Megawatt Hours",
        ))

        fig.update_layout(
        title_text = '2018 ' + source + ' Generation by State',
        geo_scope='usa'
        )

        return fig
    st_graph = plotly_choropleth(df, source)
    return st_graph


if __name__ == '__main__':
    app.run_server(debug=True)
