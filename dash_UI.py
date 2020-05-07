import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

#Read in 1st data set (National Stats)
US_data = pd.read_csv('US_energy.csv')
#Create database
db = sqlite3.connect("Dash_Energy.db")
#Read data into database
en_sql = US_data.to_sql("Dash_Energy", db, if_exists="replace")
#Call database to create a total US energy production to compare sources to
tot_query = 'SELECT * FROM Dash_Energy WHERE commodity_transaction="Electricity - net production";'
tot_results = pd.read_sql_query(tot_query, db)

#Creates a custom Dataframe object by using a SQL statement to filter for a particular energy source. As calculates the percentage of that source
#compared to the national whole
def pd_object(name, category):
    query = "SELECT * FROM Dash_Energy WHERE category='" + category + "';"
    results = pd.read_sql_query(query, db)
    results[name + '_as_per'] =  results['quantity'] / tot_results['quantity'] * 100
    return results
wind_results = pd_object('wind', 'wind_electricity')
sol_results = pd_object('sol', 'solar_electricity')
hyd_results = pd_object('hyd', 'hydro')
geo_results = pd_object('geo', 'geothermal')

#Read in 2nd data source(Stats by state)
by_state = pd.read_excel (r'annual_generation_state.xls', header=None)
#Rename the columns for ease of operating on and otherwise process the data
by_state = by_state.rename(columns={0:"Year", 1:"State", 2:"Type_of_producer", 3:"Energy_Source", 4:"Generation(Megawatt_Hours)"})
by_state = by_state.drop([0,1], axis=0)

#Create a custom Dataframe object for creating the heatmap
heat = ((by_state['Energy_Source'] == 'Hydroelectric Conventional') | (by_state['Energy_Source'] == 'Solar Thermal and Photovoltaic')
        | (by_state['Energy_Source'] == 'Wind') | (by_state['Energy_Source'] == 'Geothermal')) & (by_state['Type_of_producer'] ==
        "Total Electric Power Industry") & (by_state['Year'] == 2018)
heat = by_state[heat]
#drop unneeded data
drop = []
drop.append(heat.index[heat['State'] == 'US-Total'])
for thing in drop:
    heat = heat.drop(index=thing)
data = [
#Heatmap data
go.Heatmap(
    z=heat['Generation(Megawatt_Hours)'],
    x=heat['State'],
    y=heat['Energy_Source'],
    colorscale='Viridis',
    )
]
#Heatmap layout
layout = go.Layout(
    xaxis=dict(
        tickmode='linear',
        tickangle = 285
    ),
    width=1500,
    height=400
)

#Initialize the dash app
app = dash.Dash(__name__)
server = app.server

#Categories for renewable dropdown
ren_cats = ['hydro', 'geothermal', 'solar_electricity', 'wind_electricity']
#Categories for by state dropdown
st_cats = ['Hydroelectric Conventional', 'Solar Thermal and Photovoltaic', 'Wind', 'Geothermal']
#HTML
app.layout = html.Div(
    className='wrapper',
    children = [
    html.Div([
    html.H2('US National Renewable Energy by Source 1990-2014'),
    html.H3('Visualizations for the different major sources of US renewables can be selected via the dropdown'),
    dcc.Dropdown(id='category-select', options=[{'label': i.capitalize(), 'value': i} for i in ren_cats],
                           value='hydro', style={'width': '150px'}),
    dcc.Graph('energy_visual'),
    html.H5('''Hydro Energy is the major player in US renewables contributing more than all other sources combined. Hydro energy is produced by
    flowing water causing a turbine to spin. The total Hydro generation varies greatly by year in response to water availability. This is largely a
    function of rainfall but can include other factors such as melting ice. Though Hydro energy as a percentage of the overall American yield peaked in
    1996 the yields in total have not fallen outside of normal yearly fluctuation and in 2011 almost topped the total generation of 1996 though more
    total US generation caused it to be a significantly smaller percentage of the whole.'''),
    html.H5('''Geothermal power is produced by drilling a well into a geothermal pool of water. The trapped steam generated within the wells spins a
    turbine producing energy. Though geothermal energy has been a player in the US infrastructure for some time it's growth is slow due to high risks
    in production and exploration, high costs in developing new technology, and long build times for production facilities.'''),
    html.H5('''Solar energy is produced though a panel which collects natural energies emitted from the sun. Solar is a fast growing part of the
    American energy infrastructure up about 600% from 2010. It is still a fairly small part of the total peaking at about 0.6% in 2014 but continues
    to be a larger and larger part every year. Solar has a unique place in that it can be affordable to residential households and has been employed
    for individuals to not only power their homes but pump power into the energy grid.'''),
    html.H5('''Wind power is typically collected via a mill which spins in the wind turning a turbine. Wind like Solar has experienced steady growth
    in recent years and can be credited for up to 4+% of the American total. If this growth can continue over time Wind has the potential to overtake
    the less reliable hydro sources which now contribute more than twice as much energy in total to America. Wind and solar appear to be the upcoming
    players in a 21st century American energy economy which will have to take growing advantage of renewable opportunities.''')
    ]),
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
    html.H2('US Renewable Energy by State in Megawatt Hours Heat Map'),
    dcc.Graph(
    figure = go.Figure(data=data, layout=layout)),
    html.H5('''Looking at the by state statistics a few things stand out to me. Most of the states employ 2-3 of the 4 tracked sources with Mississippi
    being an outlier in only tapping one, and California, Hawaii, Idaho, New Mexico, Nevada, Oregon and Utah using all 4 tracked sources of generation.'''),
    html.H5('''Hydro is by far most popular on the west coast with Washington leading the way then Oregon and California. New York is the only state on
    the East Coast with anything comparable to those states on the far west. I was kind of surprised to see there isn't more of a focus on tapping Hydro
    which generates more power than all other sources combined. I expected to see bigger hotbeds in New England and around the Great Lakes.'''),
    html.H5('''The leader in solar is California by a wide margin with other major players in Nevada, Arizona and North Carolina. It's unsurprising
    to see a dedication to this source in desert areas where the availability of sunlight doesn't vary as much. Solar however could be tapped to some
    extent everywhere so I was surprised to see North Dakota, West Virginia, New Hampshire and Alaska not producing any. Three of the four of those states
    are on the extreme North part of the country where less sunlight can be expected so I would think this explains part of this phenomena.'''),
    html.H5('''Wind seems to  be overwhelmingly popular in the great plains with Texas, Oklahoma, Kansas, and Iowa being some of the major players.
    There is a noted absence of wind utilization in the South with no state East of Louisiana and south of Tennessee-North Carolina producing any
    at all. Kentucky and Virginia also produce no wind power according to the data. It seems wind does not do as well in New England as it does in other
    parts of the country.'''),
    html.H5('''Geothermal is only tapped by 7 total states none being east of New Mexico. Once again California takes the top spot in geothermal with
    Nevada getting the second largest contribution. Geothermal produces the least of the four sources by a considerable margin and with solar trending up
    very quickly that margin will likely continue to grow. Geothermal also seems to be the least cost efficient so those two points probably factor
    heavily in its being the least popular. It is also worth noting some very specific geographic requirements must be met to get the most out of it.''')
    ]),
    html.Div([
    html.H2('US Renewable Energy by State 2018'),
    dcc.Dropdown(id='source-select', options=[{'label': i.capitalize(), 'value': i} for i in st_cats],
                           value='Hydroelectric Conventional', style={'width': '150px'}),
    dcc.Graph('by_state')
    ]),
])

#Callback for US Renewables by source
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
#Callback for by state generation choropleths
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

#Run app
if __name__ == '__main__':
    app.run_server(debug=True)
