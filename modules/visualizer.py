from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

def create_kpi_card(title, value_id):
    """Función auxiliar para crear una tarjeta de KPI."""
    return dbc.Card(
        dbc.CardBody([
            # CAMBIO: Se añade 'text-light' para el título, el tema se encarga del valor
            html.H4(title, className="card-title text-light"),
            html.H2(id=value_id, className="card-text") 
        ]),
        className="text-center shadow-sm h-100" # El tema DARKLY hace las tarjetas oscuras
    )

def create_layout(df):
    """
    Crea el layout de la aplicación Dash usando Dash Bootstrap Components (Modo Oscuro).
    """
    country_options = [{'label': country, 'value': country} for country in df['Country'].unique()]
    map_years = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]

    # --- Encabezado ---
    header = dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        # Columna Izquierda (Logo, Título y Selector de Métrica)
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        
                                        html.H2("VIZ-PIB CORE", className="mb-0 text-light"),
                                    ],
                                    className="d-flex align-items-center mb-2"
                                ),
                                dcc.RadioItems(
                                    id='metric-selector',
                                    options=[
                                        {'label': 'PIB Total', 'value': 'total'},
                                        {'label': 'PIB Per Cápita', 'value': 'per_capita'}
                                    ],
                                    value='total',
                                    inline=True,
                                    className="mt-2"
                                )
                            ],
                            md=5
                        ),
                        # Columna Derecha (Controles)
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Dropdown(
                                            id='country-dropdown',
                                            options=country_options,
                                            value=[],
                                            placeholder="Seleccione uno o más países...",
                                            multi=True,
                                            style={'width': '100%'} # Corrección del dropdown
                                        ),
                                        style={'flex-grow': '1', 'margin-right': '10px'}
                                    ),
                                    dbc.Button("Aplicar", id='apply-button', n_clicks=0, color="primary")
                                ],
                                style={'display': 'flex', 'width': '100%'}
                            ),
                            md=7,
                            className="d-flex align-items-center"
                        )
                    ],
                    className="w-100 align-items-center",
                    align="center",
                ),
            ],
            fluid=True,
        ),
        # CAMBIOS: color="dark" y dark=True
        color="dark",
        dark=True, 
        className="shadow-sm mb-4"
    )

    # --- Cuerpo del Dashboard ---
    body = dbc.Container(
        [
            # Fila de KPIs
            dbc.Row(
                [
                    dbc.Col(create_kpi_card("GDP Actual / Selección", "kpi-gdp-actual"), md=3),
                    dbc.Col(create_kpi_card("Máximo PIB del Período", "kpi-max-gdp"), md=3),
                    dbc.Col(create_kpi_card("Mínimo PIB del Período", "kpi-min-gdp"), md=3),
                    dbc.Col(create_kpi_card("Mayor Crecimiento Promedio", "kpi-avg-growth"), md=3),
                ],
                className="mb-4"
            ),
            
            # Fila Gráfico Principal
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Graph(id='gdp-evolution-graph', style={'height': '50vh'})),
                        className="shadow-sm"
                    ),
                    width=12
                ),
                className="mb-4"
            ),
            
            # Fila Gráficos Inferiores
            dbc.Row(
                [
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='gdp-distribution-pie')), className="shadow-sm"), md=4),
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='growth-comparison-bar')), className="shadow-sm"), md=4),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("Top Continentes por Crecimiento Anual"),
                                dcc.RadioItems(
                                    id='continent-year-selector',
                                    options=[{'label': str(year), 'value': year} for year in range(2021, 2026)],
                                    value=2025,
                                    inline=True,
                                    inputClassName="me-1",
                                    labelClassName="me-3"
                                ),
                                dcc.Graph(id='continent-growth-bar')
                            ]),
                            className="shadow-sm"
                        ),
                        md=4
                    ),
                ],
                className="mb-4"
            ),

            # Fila Mapa
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Mapa de Calor de Población Mundial (1970-2022)"),
                            dcc.Graph(id='population-heatmap'),
                            dcc.Slider(
                                id='map-year-slider',
                                min=min(map_years),
                                max=max(map_years),
                                value=max(map_years),
                                marks={year: str(year) for year in map_years},
                                step=None,
                                className="mt-3"
                            )
                        ]),
                        className="shadow-sm"
                    ),
                    width=12
                ),
                className="mb-4"
            ),

            # --- FILA DE TABLA ---
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Tabla de Datos Completos"),
                            dash_table.DataTable(
                                id='raw-data-table',
                                style_table={'height': '400px', 'overflowY': 'auto'},
                                style_as_list_view=True,
                                
                                # --- CAMBIOS: Estilos de la tabla para modo oscuro ---
                                style_cell={
                                    'padding': '10px', 
                                    'textAlign': 'left',
                                    'backgroundColor': '#343a40', # Fondo de celda oscuro
                                    'color': 'white' # Texto de celda blanco
                                },
                                style_header={
                                    'backgroundColor': '#212529', # Fondo de cabecera más oscuro
                                    'fontWeight': 'bold',
                                    'color': 'white',
                                    'borderBottom': '2px solid white'
                                },
                                # --- Fin de cambios en la tabla ---
                            )
                        ]),
                        className="shadow-sm"
                    ),
                    width=12
                ),
                className="mb-4"
            )
        ],
        fluid=True,
        # CAMBIO: Se elimina 'bg-light' y 'p-4' para que el tema se encargue del fondo
        className="p-4" 
    )

    return html.Div([header, body])