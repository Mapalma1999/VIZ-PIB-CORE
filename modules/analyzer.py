import pandas as pd
import pycountry_convert as pc

def analyze_country_gdp(df, country_name):
    """
    Calcula métricas clave del PIB para un país específico.
    """
    try:
        # Filtrar los datos para el país seleccionado
        country_data = df[df['Country'] == country_name]
        
        # Extraer solo las columnas de PIB
        gdp_columns = [col for col in df.columns if 'GDP_' in col]
        country_gdp = country_data[gdp_columns].iloc[0]
        
        # Calcular las métricas
        gdp_actual = country_gdp['GDP_2025']
        max_gdp_value = country_gdp.max()
        min_gdp_value = country_gdp.min()
        
        # Calcular el crecimiento promedio anual (CON LA CORRECCIÓN)
        avg_growth = country_gdp.pct_change(fill_method=None).mean() * 100
        
        # Empaquetar los resultados
        metrics = {
            'gdp_actual': gdp_actual,
            'max_gdp': {
                'value': max_gdp_value,
                'year': int(country_gdp.idxmax().split('_')[1])
            },
            'min_gdp': {
                'value': min_gdp_value,
                'year': int(country_gdp.idxmin().split('_')[1])
            },
            'avg_growth_percent': round(avg_growth, 2)
        }
        
        return metrics

    except (KeyError, IndexError):
        return None
    
    
def analyze_comparison(df, country_list):
    """
    Analiza una lista de países para encontrar los valores extremos en las
    métricas de PIB y crecimiento.
    """
    if not country_list:
        return None

    all_metrics = []
    # Primero, calculamos las métricas para cada país de la lista
    for country in country_list:
        metrics = analyze_country_gdp(df, country)
        if metrics:
            metrics['country'] = country
            all_metrics.append(metrics)

    if not all_metrics:
        return None

    # Ahora, encontramos al "ganador" de cada categoría
    country_with_max_gdp = max(all_metrics, key=lambda x: x['max_gdp']['value'])
    country_with_min_gdp = min(all_metrics, key=lambda x: x['min_gdp']['value'])
    country_with_max_growth = max(all_metrics, key=lambda x: x['avg_growth_percent'])

    # Devolvemos un diccionario con los resultados de la comparación
    return {
        'overall_max_gdp': {
            'country': country_with_max_gdp['country'],
            'value': country_with_max_gdp['max_gdp']['value'],
            'year': country_with_max_gdp['max_gdp']['year']
        },
        'overall_min_gdp': {
            'country': country_with_min_gdp['country'],
            'value': country_with_min_gdp['min_gdp']['value'],
            'year': country_with_min_gdp['min_gdp']['year']
        },
        'highest_growth': {
            'country': country_with_max_growth['country'],
            'value': country_with_max_growth['avg_growth_percent']
        }
    }
    
def analyze_world_data(df):
    """
    Calcula las métricas y datos agregados para la vista mundial.
    """
    gdp_cols = [col for col in df.columns if 'GDP_' in col]
    
    # Suma el PIB de todos los países para cada año
    world_gdp_series = df[gdp_cols].sum()
    
    # Calcula el crecimiento promedio mundial anual
    avg_growth = world_gdp_series.pct_change(fill_method=None).mean() * 100

    # Prepara los datos para el gráfico de barras de crecimiento mundial
    world_growth_df = world_gdp_series.pct_change(fill_method=None).dropna() * 100
    world_growth_df = world_growth_df.reset_index()
    world_growth_df.columns = ['Año', 'Crecimiento (%)']
    world_growth_df['Año'] = world_growth_df['Año'].str.replace('GDP_', '')

    metrics = {
        'gdp_actual': world_gdp_series['GDP_2025'],
        'max_gdp': {
            'value': world_gdp_series.max(),
            'year': int(world_gdp_series.idxmax().split('_')[1])
        },
        'min_gdp': {
            'value': world_gdp_series.min(),
            'year': int(world_gdp_series.idxmin().split('_')[1])
        },
        'avg_growth_percent': round(avg_growth, 2),
        'world_total_gdp': world_gdp_series.reset_index().rename(columns={'index': 'Año', 0: 'PIB (Billones USD)'}),
        'world_growth_data': world_growth_df
    }
    metrics['world_total_gdp']['Año'] = metrics['world_total_gdp']['Año'].str.replace('GDP_', '')
    
    return metrics

MANUAL_MAP = {
    'USA': 'North America',
    'UK': 'Europe',
    'Russia': 'Europe',
    'Korea': 'Asia',
    'Czechia': 'Europe',
    'UAE': 'Asia',
    'Macao': 'Asia',
    'Brunei': 'Asia',
    'Timor-Leste': 'Asia',
    'Sao Tome and Principe': 'Africa',
    'St. Kitts and Nevis': 'North America',
    'St. Lucia': 'North America',
    'St. Vincent and the Grenadines': 'North America',
    'Antigua and Barbuda': 'North America',
    'Trinidad and Tobago': 'North America',
    'Bosnia and Herzegovina': 'Europe',
    'North Macedonia': 'Europe',
    'Dominican Republic': 'North America',
    'Equatorial Guinea': 'Africa',
    'Cote d\'Ivoire': 'Africa',
    'Eswatini': 'Africa',
    'Cabo Verde': 'Africa',
    'Micronesia': 'Oceania',
    'Marshall Islands': 'Oceania',
    'Kosovo': 'Europe',
}


def get_continent(country_name):
    
    # 1. Revisa primero nuestro mapa manual
    if country_name in MANUAL_MAP:
        return MANUAL_MAP[country_name]
    
    # 2. Si no está en el mapa, intenta usar la librería
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return pc.convert_continent_code_to_continent_name(continent_code)
    except:
        # 3. Si todo falla, ahora sí lo asignamos a 'Otros'
        return 'Otros'

# (El resto de las funciones en el archivo no necesitan cambios)

def analyze_continent_growth(df, year):
    """
    Calcula el crecimiento promedio del PIB por continente para un año dado.
    """
    # Define el año anterior para el cálculo del crecimiento
    previous_year_col = f'GDP_{year - 1}'
    current_year_col = f'GDP_{year}'

    # Asegurarnos de que las columnas existan
    if previous_year_col not in df.columns or current_year_col not in df.columns:
        return pd.DataFrame()

    # Mapea cada país a su continente
    df['Continent'] = df['Country'].apply(get_continent)
    
    unmapped_countries = df[df['Continent'] == 'Otros']['Country'].unique()
    if len(unmapped_countries) > 0:
        print("\n>>> PAÍSES NO MAPEADOS (clasificados como 'Otros'):", unmapped_countries)
    
    # Calcula el crecimiento porcentual para cada país
    df['Growth'] = (df[current_year_col] - df[previous_year_col]) / df[previous_year_col] * 100
    
    # Agrupa por continente y calcula el crecimiento promedio, luego ordena
    continent_growth = df.groupby('Continent')['Growth'].mean().reset_index()
    continent_growth_sorted = continent_growth.sort_values(by='Growth', ascending=False)
    
    return continent_growth_sorted