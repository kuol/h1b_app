import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html


def get_df_hq(df):
    df_hq = pd.DataFrame()
    for year in df['year'].unique():
        df_year = df[df['year'] == year]
        df_year = df_year.groupby('head_quarter')['num_applications'].sum().reset_index(name="num_applications")
        df_year['year'] = year
        df_hq = df_hq.append(df_year)
    return df_hq


def get_df_hq_ratio(df):
    df['us_hq'] = df['head_quarter'] == 'US'
    
    d = {'year':[], 'ratio': []}
    for year in df['year'].unique():
        df_year= df[df['year']==year]
        df_year = df_year.groupby('us_hq', as_index=False)['num_applications'].sum()
        num_us = df_year[df_year['us_hq'] == True]['num_applications'].tolist()[0]
        num_non_us = df_year[df_year['us_hq'] == False]['num_applications'].tolist()[0]
        ratio = num_us / num_non_us
        d['year'].append(year)
        d['ratio'].append(ratio)

    return pd.DataFrame(d)
                                

def generate_table(df, max_rows=15):
    cols = list(df.columns)
    cols.remove('year')
    n = min(len(df), max_rows)

    return html.Table(
        [html.Tr([html.Th(col) for col in cols])] + 
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in cols
            ]) for i in range(n)]
    )


def generate_pie(labels, values, title):
    trace = go.Pie(labels = labels, values = values)
    layout = go.Layout(title = title)
    return {'data': [trace], 'layout': layout}


def generate_scatter_line(df):
    trace = go.Scatter(x=df['year'], y=df['ratio'], mode='lines+markers')
    layout = go.Layout(
            title = "Ratio for Number of Applications from US Based or Non-US Based Companies",
            xaxis = dict(title = "Year"),
            yaxis = dict(title = "Ratio: US / Non-US")
            )
    return dcc.Graph(
            id = 'hq_ratio_chart', 
            figure = {'data': [trace], 'layout': layout}
            )


title = html.H4(children="Headquarter of Top 15 H-1B Sponsors")
    
drop_down = html.Div([
    dcc.Dropdown(
        id = 'year_dropdown',
        options = [
            {'label': '2013', 'value': 2013},
            {'label': '2014', 'value': 2014},
            {'label': '2015', 'value': 2015},
            {'label': '2016', 'value': 2016},
            {'label': '2017', 'value': 2017},
        ],
        value = 2017,
        )], 
    style={'width': '48%', 'display': 'inline-block'})


df = pd.read_csv("./data/topN.csv")
df_hq = get_df_hq(df)
df_hq_ratio = get_df_hq_ratio(df_hq)

# ====================================
# Create a Dash object (called "app") with certain css style sheet
# ====================================
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)


# ====================================
# Define app layout
# ====================================
app.layout = html.Div(children=[
    title,
    drop_down,
    html.Div(id='my_table', className="six columns"),
    html.Div([dcc.Graph(id='hq_pie')], style = {'width': '48%', 'display': 'inline-block'}),
    html.Div([generate_scatter_line(df_hq_ratio)], style = {'width': '48%', 'display': 'inline-block'})
    ])


# ====================================
# Define app callback
# ====================================
# Top 15 H-1B sponsor table
@app.callback(
    dash.dependencies.Output('my_table', 'children'),
    [dash.dependencies.Input('year_dropdown', 'value')]
    )
def update_table(year):
    df_year = df[df['year'] == year]
    return generate_table(df_year)

# Pie 
@app.callback(
    dash.dependencies.Output('hq_pie', 'figure'),
    [dash.dependencies.Input('year_dropdown', 'value')]
    )
def update_hq_pie(year):
    df_year = df_hq[df_hq['year'] == year]
    labels = df_year['head_quarter']
    values = df_year['num_applications']
    title = "Headquarter Location of Top 15 H-1B Sponsors"
    return generate_pie(labels, values, title)



if __name__ == '__main__':
    app.run_server(debug=True)
