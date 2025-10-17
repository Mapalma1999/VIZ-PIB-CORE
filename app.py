import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd # <-- Importante añadir pandas

# Importaciones de nuestros módulos
from modules.data_loader import load_gdp_data
from modules.data_cleaner import clean_gdp_data
from modules.analyzer import analyze_country_gdp, analyze_comparison
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
    Output('kpi-max-gdp', 'children'),
    Output('kpi-min-gdp', 'children'),
    Output('kpi-avg-growth', 'children'),
    Input('apply-button', 'n_clicks'),
    State('country-dropdown', 'value')
)
def update_main_dashboard(n_clicks, selected_countries):
    if not selected_countries:
        empty_fig = px.line(title='Seleccione uno o más países')
        return empty_fig, empty_fig, "-", "-", "-"

    # --- Gráfico de Evolución ---
    comparison_df = df[df['Country'].isin(selected_countries)]
    gdp_cols = [col for col in df.columns if 'GDP_' in col]
    melted_df = comparison_df.melt(
        id_vars=['Country'], value_vars=gdp_cols,
        var_name='Año', value_name='PIB (Billones USD)'
    )
    melted_df['Año'] = melted_df['Año'].str.replace('GDP_', '')
    fig_line = px.line(
        melted_df, x='Año', y='PIB (Billones USD)', color='Country',
        title='Comparación de Evolución del PIB', markers=True,
        custom_data=['Country']
    )
    fig_line.update_layout(margin=dict(l=20, r=20, t=40, b=20), legend_title_text='Países')
    fig_line.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>PIB: %{y:,.2f} B<br>Año: %{x}')

    # --- Lógica dinámica de KPIs ---
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

    # --- Gráfico de Dona (con la corrección) ---
    df_2025 = df.sort_values(by='GDP_2025', ascending=False)
    top_5 = df_2025.head(5)
    others_gdp = df_2025.iloc[5:]['GDP_2025'].sum()
    
    # Creamos un DataFrame para la fila "Otros"
    others_row_df = pd.DataFrame([{'Country': 'Otros', 'GDP_2025': others_gdp}])
    
    # Usamos pd.concat en lugar del .append obsoleto
    plot_df = pd.concat([top_5, others_row_df], ignore_index=True)
    
    fig_pie = px.pie(
        plot_df,
        names='Country',
        values='GDP_2025',
        title='Distribución del GDP Mundial 2025',
        hole=0.4
    )
    fig_pie.update_traces(textinfo='percent+label', textposition='inside')

    return fig_line, fig_pie, kpi_max, kpi_min, kpi_growth


# Callback para el KPI "GDP Actual" (sin cambios)
@app.callback(
    Output('kpi-gdp-actual', 'children'),
    Input('apply-button', 'n_clicks'),
    Input('gdp-evolution-graph', 'clickData'),
    State('country-dropdown', 'value')
)
def update_actual_gdp(n_clicks, clickData, selected_countries):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'gdp-evolution-graph' and clickData:
        country_name = clickData['points'][0]['customdata'][0]
        gdp_value = clickData['points'][0]['y']
        return f"{country_name}: {gdp_value:,.2f} B USD"
    
    if len(selected_countries) == 1:
        metrics = analyze_country_gdp(df, selected_countries[0])
        return f"{metrics['gdp_actual']:,.2f} B USD"

    return "Haz clic en el gráfico"


# --- 4. Ejecutar el Servidor ---
if __name__ == '__main__':
    app.run(debug=True)