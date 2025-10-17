from dash import html, dcc

def create_layout(df):
    """
    Crea el layout estático de la aplicación Dash.
    """
    country_options = [{'label': country, 'value': country} for country in df['Country'].unique()]

    return html.Div(children=[
        # --- Encabezado ---
        html.Div(className='header', children=[
            html.H1('VIZ-PIB CORE - PIB por País (2020-2025)'),
            dcc.Dropdown(
                id='country-dropdown',
                options=country_options,
                value=[df['Country'].iloc[0]], # Valor inicial como una lista
                clearable=False,
                multi=True
            ),
            html.Button('Aplicar', id='apply-button', n_clicks=0)
        ]),

        # --- Cuerpo del Dashboard ---
        html.Div(className='dashboard-body', children=[
            # --- Fila Superior ---
            html.Div(className='top-row', children=[
                html.Div(className='kpi-sidebar', children=[
                    html.Div(className='kpi-card', children=[
                        html.H3('GDP Actual / Selección'),
                        html.P(id='kpi-gdp-actual')
                    ]),
                    html.Div(className='kpi-card', children=[
                        html.H3('Máximo PIB del Período'),
                        html.P(id='kpi-max-gdp')
                    ]),
                    html.Div(className='kpi-card', children=[
                        html.H3('Mínimo PIB del Período'),
                        html.P(id='kpi-min-gdp')
                    ]),
                    html.Div(className='kpi-card', children=[
                        html.H3('Mayor Crecimiento Promedio'),
                        html.P(id='kpi-avg-growth')
                    ])
                ]),
                html.Div(className='main-chart', children=[
                    dcc.Graph(id='gdp-evolution-graph')
                ])
            ]),

            # --- Fila Inferior (para nuevos gráficos) ---
            html.Div(className='bottom-row', children=[
                html.Div(className='bottom-chart-container', children=[
                    dcc.Graph(id='gdp-distribution-pie') # <-- NUEVO GRÁFICO
                ])
            ])
        ])
    ])