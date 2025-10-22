import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd

from modules.data_preparer import prepare_merged_data
from modules.analyzer import analyze_country_gdp, analyze_comparison, analyze_world_data, analyze_continent_growth
from modules.visualizer import create_layout

# --- 1. Cargar y Preparar Datos ---
GDP_DATA_PATH = 'data/2020-2025.csv'
POP_DATA_PATH = 'data/world_population.csv'
df = prepare_merged_data(GDP_DATA_PATH, POP_DATA_PATH)

# --- 2. Inicializar la Aplicación Dash ---
app = dash.Dash(__name__)
app.layout = create_layout(df)

# --- 3. Lógica de Interacción (Callbacks) ---

# Callback para el contenido dinámico (KPIs y Gráfico Principal)
# Callback para el contenido dinámico (KPIs y Gráfico Principal)
@app.callback(
    Output('gdp-evolution-graph', 'figure'),
    Output('kpi-gdp-actual', 'children'),
    Output('kpi-max-gdp', 'children'),
    Output('kpi-min-gdp', 'children'),
    Output('kpi-avg-growth', 'children'),
    Input('apply-button', 'n_clicks'),
    State('country-dropdown', 'value'),
    Input('metric-selector', 'value')
)
def update_dynamic_content(n_clicks, selected_countries, metric_type):
    # --- Lógica de estado inicial (VISTA MUNDIAL) ---
    if n_clicks == 0:
        world_metrics = analyze_world_data(df)
        fig_line = px.line(
            world_metrics['world_total_gdp'], x='Año', y='PIB (Billones USD)',
            title='Evolución del PIB Mundial Total', markers=True
        )
        kpi_actual = f"Mundial: {world_metrics['gdp_actual']:,.0f} B"
        kpi_max = f"Mundial: {world_metrics['max_gdp']['value']:,.0f} B"
        kpi_min = f"Mundial: {world_metrics['min_gdp']['value']:,.0f} B"
        kpi_growth = f"Mundial: {world_metrics['avg_growth_percent']}%"
        return fig_line, kpi_actual, kpi_max, kpi_min, kpi_growth

    # --- Lógica de Interacción del Usuario ---
    prefix = 'GDP_' if metric_type == 'total' else 'GDP_per_capita_'
    y_axis_label = 'PIB (Billones USD)' if metric_type == 'total' else 'PIB Per Cápita (USD)'
    title_suffix = 'PIB Total' if metric_type == 'total' else 'PIB Per Cápita'
    value_format = '{:,.2f} B' if metric_type == 'total' else '${:,.0f}'

    if not selected_countries:
        empty_fig = px.line(title='Seleccione países y presione "Aplicar"')
        return empty_fig, "N/A", "N/A", "N/A", "N/A"

    comparison_df = df[df['Country'].isin(selected_countries)]
    
    # --- CORRECCIÓN CLAVE AQUÍ ---
    if metric_type == 'total':
        # Selecciona solo las columnas de PIB Total, excluyendo per cápita
        gdp_cols = [col for col in df.columns if col.startswith(prefix) and 'per_capita' not in col]
    else:
        # Para per cápita, la lógica original era correcta
        gdp_cols = [col for col in df.columns if col.startswith(prefix)]
    # -----------------------------
    
    melted_df = comparison_df.melt(id_vars=['Country'], value_vars=gdp_cols, var_name='Año', value_name=y_axis_label)
    melted_df['Año'] = melted_df['Año'].str.replace(prefix, '').str.replace('_', ' ')
    fig_line = px.line(melted_df, x='Año', y=y_axis_label, color='Country', title=f'Evolución del {title_suffix}', markers=True)
    fig_line.update_layout(margin=dict(l=20, r=20, t=40, b=20), legend_title_text='Países')
    
    if len(selected_countries) == 1:
        metrics = analyze_country_gdp(df, selected_countries[0], metric_type)
        kpi_actual = value_format.format(metrics['gdp_actual'])
        kpi_max = f"{value_format.format(metrics['max_gdp']['value'])} ({metrics['max_gdp']['year']})"
        kpi_min = f"{value_format.format(metrics['min_gdp']['value'])} ({metrics['min_gdp']['year']})"
        kpi_growth = f"{metrics['avg_growth_percent']}% anual"
    else:
        comp_metrics = analyze_comparison(df, selected_countries, metric_type)
        max_gdp_data = comp_metrics['overall_max_gdp']
        min_gdp_data = comp_metrics['overall_min_gdp']
        growth_data = comp_metrics['highest_growth']
        kpi_actual = "Comparación"
        kpi_max = f"{max_gdp_data['country']}: {value_format.format(max_gdp_data['max_gdp']['value'])}"
        kpi_min = f"{min_gdp_data['country']}: {value_format.format(min_gdp_data['min_gdp']['value'])}"
        kpi_growth = f"{growth_data['country']}: {growth_data['avg_growth_percent']}%"

    return fig_line, kpi_actual, kpi_max, kpi_min, kpi_growth

# Callback para el contenido "estático"
@app.callback(
    Output('gdp-distribution-pie', 'figure'),
    Output('growth-comparison-bar', 'figure'),
    Output('raw-data-table', 'data'),
    Output('raw-data-table', 'columns'),
    Input('apply-button', 'n_clicks'),
    State('country-dropdown', 'value')
)
def update_static_content(n_clicks, selected_countries):
    table_data = df.to_dict('records')
    table_columns = [{"name": i, "id": i} for i in df.columns]
    
    df_2025 = df.sort_values(by='GDP_2025', ascending=False)
    top_5 = df_2025.head(5)
    others_gdp = df_2025.iloc[5:]['GDP_2025'].sum()
    others_row_df = pd.DataFrame([{'Country': 'Otros', 'GDP_2025': others_gdp}])
    plot_df_pie = pd.concat([top_5, others_row_df], ignore_index=True)
    fig_pie = px.pie(plot_df_pie, names='Country', values='GDP_2025', title='Distribución GDP Mundial 2025 (Total)', hole=0.4)

    if n_clicks == 0:
        world_metrics = analyze_world_data(df)
        fig_bar = px.bar(
            world_metrics['world_growth_data'], x='Año', y='Crecimiento (%)',
            title='Crecimiento Anual del PIB Mundial (%)'
        )
    elif not selected_countries:
        fig_bar = px.bar(title='Comparación de Crecimiento Anual (%)')
    else:
        comparison_df = df[df['Country'].isin(selected_countries)]
        gdp_cols = [col for col in df.columns if col.startswith('GDP_') and 'per_capita' not in col]
        growth_df = comparison_df[gdp_cols].pct_change(axis='columns', fill_method=None) * 100
        growth_df['Country'] = comparison_df['Country']
        melted_growth_df = growth_df.melt(id_vars=['Country'], value_vars=[col for col in gdp_cols if col != 'GDP_2020'], var_name='Año', value_name='Crecimiento (%)')
        melted_growth_df['Año'] = melted_growth_df['Año'].str.replace('GDP_', '')
        fig_bar = px.bar(melted_growth_df, x='Año', y='Crecimiento (%)', color='Country', barmode='group', title='Comparación de Crecimiento Anual (%)')
    
    return fig_pie, fig_bar, table_data, table_columns

# Callback para continentes
@app.callback(
    Output('continent-growth-bar', 'figure'),
    Input('continent-year-selector', 'value')
)
def update_continent_growth(selected_year):
    continent_growth_df = analyze_continent_growth(df, selected_year)
    fig_continent = px.bar(continent_growth_df, x='Growth', y='Continent', orientation='h', title=f"Crecimiento Promedio por Continente ({selected_year})")
    fig_continent.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis={'categoryorder':'total ascending'})
    fig_continent.update_traces(text=continent_growth_df['Growth'].apply(lambda x: f'{x:.2f}%'), textposition='outside')
    return fig_continent

if __name__ == '__main__':
    app.run(debug=True)