from dash import html, dcc, dash_table

def create_layout(df):
    """
    Crea el layout estático de la aplicación Dash.
    """
    country_options = [{'label': country, 'value': country} for country in df['Country'].unique()]

    return html.Div(children=[
       
        # --- Encabezado ---
        html.Div(className='header', children=[
            html.Div(className='header-title', children=[
                html.H1('VIZ-PIB CORE - PIB por País (2020-2025)'),
                # --- NUEVO INTERRUPTOR DE MÉTRICA ---
                dcc.RadioItems(
                    id='metric-selector',
                    options=[
                        {'label': 'PIB Total', 'value': 'total'},
                        {'label': 'PIB Per Cápita', 'value': 'per_capita'}
                    ],
                    value='total', # Valor por defecto
                    labelStyle={'display': 'inline-block', 'margin-right': '15px'}
                )
            ]),
            html.Div(className='header-controls', children=[
                dcc.Dropdown(
                    id='country-dropdown',
                    options=country_options,
                    value=[],
                    placeholder="Seleccione uno o más países...",
                    clearable=False,
                    multi=True
                ),
                html.Button('Aplicar', id='apply-button', n_clicks=0)
            ])
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

            # --- Fila Intermedia ---
            html.Div(className='bottom-row', children=[
                html.Div(className='bottom-chart-container', children=[
                    dcc.Graph(id='gdp-distribution-pie')
                ]),
                html.Div(className='bottom-chart-container', children=[
                    dcc.Graph(id='growth-comparison-bar')
                ]),
                html.Div(className='bottom-chart-container', children=[
                    html.H4("Top Continentes por Crecimiento Anual"),
                    dcc.RadioItems(
                        id='continent-year-selector',
                        options=[{'label': str(year), 'value': year} for year in range(2021, 2026)],
                        value=2025,
                        inline=True
                    ),
                    dcc.Graph(id='continent-growth-bar')
                ])
            ]),

            # --- Fila de la Tabla de Datos ---
            html.Div(className='data-table-row', children=[
                html.H4("Tabla de Datos Completos"),
                dash_table.DataTable(
                    id='raw-data-table',
                    # --- ESTOS SON LOS CAMBIOS CLAVE ---
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    # ------------------------------------
                    style_cell={'textAlign': 'left'},
                    style_header={
                        'backgroundColor': 'rgb(44, 62, 80)',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_data={
                        'backgroundColor': 'rgb(248, 248, 248)',
                        'color': 'black'
                    }
                )
            ])
        ])
    ])