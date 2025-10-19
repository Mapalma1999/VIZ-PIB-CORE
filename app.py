import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

# Importaciones de nuestros módulos
from modules.data_loader import load_gdp_data
from modules.data_cleaner import clean_gdp_data
from modules.analyzer import analyze_country_gdp, analyze_comparison, analyze_world_data, analyze_continent_growth
from modules.visualizer import create_layout

# --- 1. Cargar y Preparar Datos ---
DATA_PATH = 'data/2020-2025.csv'
df_raw = load_gdp_data(DATA_PATH)
df = clean_gdp_data(df_raw)

# --- 2. Inicializar la Aplicación Dash ---
app = dash.Dash(__name__)
app.layout = create_layout(df)

# --- 3. Lógica de Interacción (Callbacks) ---

@app.callback(
    Output('gdp-evolution-graph', 'figure'),
    Output('gdp-distribution-pie', 'figure'),
    Output('growth-comparison-bar', 'figure'),
    Output('kpi-max-gdp', 'children'),
    Output('kpi-min-gdp', 'children'),
    Output('kpi-avg-growth', 'children'),
    Input('apply-button', 'n_clicks'),
    State('country-dropdown', 'value')
)
def update_main_dashboard(n_clicks, selected_countries):
    # --- ESTADO INICIAL (VISTA MUNDIAL POR DEFECTO) ---
    if n_clicks is None or n_clicks == 0:
        world_metrics = analyze_world_data(df)
        fig_line = px.line(
            world_metrics['world_total_gdp'], x='Año', y='PIB (Billones USD)',
            title='Evolución del PIB Mundial Total', markers=True
        )
        fig_bar = px.bar(
            world_metrics['world_growth_data'], x='Año', y='Crecimiento (%)',
            title='Crecimiento Anual del PIB Mundial (%)'
        )
        kpi_max = f"Mundial: {world_metrics['max_gdp']['value']:,.0f} B"
        kpi_min = f"Mundial: {world_metrics['min_gdp']['value']:,.0f} B"
        kpi_growth = f"Mundial: {world_metrics['avg_growth_percent']}%"

    # --- LÓGICA DE USUARIO (CUANDO SE PRESIONA "APLICAR") ---
    else:
        if not selected_countries:
            empty_fig = px.line(title='Seleccione países y presione "Aplicar"')
            return empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A"

        comparison_df = df[df['Country'].isin(selected_countries)]
        gdp_cols = [col for col in df.columns if 'GDP_' in col]
        melted_df = comparison_df.melt(id_vars=['Country'], value_vars=gdp_cols, var_name='Año', value_name='PIB (Billones USD)')
        melted_df['Año'] = melted_df['Año'].str.replace('GDP_', '')
        fig_line = px.line(melted_df, x='Año', y='PIB (Billones USD)', color='Country', title='Comparación de Evolución del PIB', markers=True, custom_data=['Country'])
        fig_line.update_layout(margin=dict(l=20, r=20, t=40, b=20), legend_title_text='Países')
        fig_line.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>PIB: %{y:,.2f} B<br>Año: %{x}')

        if len(selected_countries) == 1:
            metrics = analyze_country_gdp(df, selected_countries[0])
            kpi_max = f"{metrics['max_gdp']['value']:,.2f} B ({metrics['max_gdp']['year']})"
            kpi_min = f"{metrics['min_gdp']['value']:,.2f} B ({metrics['min_gdp']['year']})"
            kpi_growth = f"{metrics['avg_growth_percent']}% anual"
        else:
            comp_metrics = analyze_comparison(df, selected_countries)
            kpi_max = f"{comp_metrics['overall_max_gdp']['country']}: {comp_metrics['overall_max_gdp']['value']:,.2f} B"
            kpi_min = f"{comp_metrics['overall_min_gdp']['country']}: {comp_metrics['overall_min_gdp']['value']:,.2f} B"
            kpi_growth = f"{comp_metrics['highest_growth']['country']}: {comp_metrics['highest_growth']['value']}%"
        
        growth_df = comparison_df[gdp_cols].pct_change(axis='columns', fill_method=None) * 100
        growth_df['Country'] = comparison_df['Country']
        melted_growth_df = growth_df.melt(id_vars=['Country'], value_vars=[col for col in gdp_cols if col != 'GDP_2020'], var_name='Año', value_name='Crecimiento (%)')
        melted_growth_df['Año'] = melted_growth_df['Año'].str.replace('GDP_', '')
        fig_bar = px.bar(melted_growth_df, x='Año', y='Crecimiento (%)', color='Country', barmode='group', title='Comparación de Crecimiento Anual (%)')
        fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20), legend_title_text='Países')

    # --- GRÁFICO DE DONA (siempre muestra datos mundiales) ---
    df_2025 = df.sort_values(by='GDP_2025', ascending=False)
    top_5 = df_2025.head(5)
    others_gdp = df_2025.iloc[5:]['GDP_2025'].sum()
    others_row_df = pd.DataFrame([{'Country': 'Otros', 'GDP_2025': others_gdp}])
    plot_df_pie = pd.concat([top_5, others_row_df], ignore_index=True)
    fig_pie = px.pie(plot_df_pie, names='Country', values='GDP_2025', title='Distribución del GDP Mundial 2025', hole=0.4)
    fig_pie.update_traces(textinfo='percent+label', textposition='inside')

    return fig_line, fig_pie, fig_bar, kpi_max, kpi_min, kpi_growth


@app.callback(
    Output('kpi-gdp-actual', 'children'),
    Input('apply-button', 'n_clicks'),
    Input('gdp-evolution-graph', 'clickData'),
    State('country-dropdown', 'value')
)
def update_actual_gdp(n_clicks, clickData, selected_countries):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if n_clicks is None or n_clicks == 0:
        world_metrics = analyze_world_data(df)
        return f"Mundial: {world_metrics['gdp_actual']:,.0f} B"

    if triggered_id == 'gdp-evolution-graph' and clickData:
        country_name = clickData['points'][0]['customdata'][0]
        gdp_value = clickData['points'][0]['y']
        return f"{country_name}: {gdp_value:,.2f} B USD"
    
    if selected_countries and len(selected_countries) == 1:
        metrics = analyze_country_gdp(df, selected_countries[0])
        return f"{metrics['gdp_actual']:,.2f} B USD"

    return "Haz clic en el gráfico"


@app.callback(
    Output('continent-growth-bar', 'figure'),
    Input('continent-year-selector', 'value')
)
def update_continent_growth(selected_year):
    continent_growth_df = analyze_continent_growth(df, selected_year)
    fig_continent = px.bar(
        continent_growth_df,
        x='Growth',
        y='Continent',
        orientation='h',
        title=f"Crecimiento Promedio por Continente ({selected_year})"
    )
    fig_continent.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis={'categoryorder':'total ascending'}
    )
    fig_continent.update_traces(text=continent_growth_df['Growth'].apply(lambda x: f'{x:.2f}%'), textposition='outside')
    
    return fig_continent


# --- 4. Ejecutar el Servidor ---
if __name__ == '__main__':
    app.run(debug=True)