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
                value=[],
                placeholder="Seleccione uno o más países...",
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

            # --- Fila Inferior (con los 3 gráficos) ---
            html.Div(className='bottom-row', children=[
                # Gráfico de dona
                html.Div(className='bottom-chart-container', children=[
                    dcc.Graph(id='gdp-distribution-pie')
                ]),
                # Gráfico de barras de crecimiento por país
                html.Div(className='bottom-chart-container', children=[
                    dcc.Graph(id='growth-comparison-bar')
                ]),
                # Gráfico de barras de crecimiento por continente
                html.Div(className='bottom-chart-container', children=[
                    html.H4("Top Continentes por Crecimiento Anual"),
                    dcc.RadioItems(
                        id='continent-year-selector',
                        options=[{'label': str(year), 'value': year} for year in range(2021, 2026)],
                        value=2025, # Año por defecto
                        inline=True
                    ),
                    dcc.Graph(id='continent-growth-bar')
                ])
            ])
        ])
    ])