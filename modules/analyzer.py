import pandas as pd
import pycountry_convert as pc

# --- 1. EL MAPA MANUAL VIVE AQUÍ ---
MANUAL_MAP = {
    'USA': 'North America', 'UK': 'Europe', 'Russia': 'Europe', 'Korea': 'Asia',
    'Czechia': 'Europe', 'UAE': 'Asia', 'Macao': 'Asia', 'Brunei': 'Asia',
    'Timor-Leste': 'Asia', 'Sao Tome and Principe': 'Africa', 'St. Kitts and Nevis': 'North America',
    'St. Lucia': 'North America', 'St. Vincent and the Grenadines': 'North America',
    'Antigua and Barbuda': 'North America', 'Trinidad and Tobago': 'North America',
    'Bosnia and Herzegovina': 'Europe', 'North Macedonia': 'Europe',
    'Dominican Republic': 'North America', 'Equatorial Guinea': 'Africa',
    'Cote d\'Ivoire': 'Africa', 'Eswatini': 'Africa', 'Cabo Verde': 'Africa',
    'Micronesia': 'Oceania', 'Marshall Islands': 'Oceania',
    'Curacao': 'North America', 'DR Congo': 'Africa', 'Reunion': 'Africa',
    'Saint Barthelemy': 'North America', 'Sint Maarten': 'North America',
    'Vatican City': 'Europe', 'Western Sahara': 'Africa','Kosovo': 'Europe' 
}

# --- 2. LA FUNCIÓN QUE USA EL MAPA VIVE AQUÍ ---
def get_continent(country_name):
    """
    Convierte un nombre de país a su continente, usando un mapa manual primero.
    """
    if country_name in MANUAL_MAP:
        return MANUAL_MAP[country_name]
    
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return pc.convert_continent_code_to_continent_name(continent_code)
    except:
        return 'Otros'

# --- 3. EL RESTO DE FUNCIONES DE ANÁLISIS ---
def analyze_country_gdp(df, country_name, metric_type='total'):
    """Calcula métricas clave para un país, adaptándose al tipo de métrica."""
    prefix = 'GDP_' if metric_type == 'total' else 'GDP_per_capita_'
    try:
        country_data = df[df['Country'] == country_name]
        gdp_columns = [col for col in df.columns if col.startswith(prefix)]
        country_gdp = country_data[gdp_columns].iloc[0]
        
        metrics = {
            'gdp_actual': country_gdp[f'{prefix}2025'],
            'max_gdp': {
                'value': country_gdp.max(),
                'year': int(country_gdp.idxmax().split('_')[-1])
            },
            'min_gdp': {
                'value': country_gdp.min(),
                'year': int(country_gdp.idxmin().split('_')[-1])
            },
            'avg_growth_percent': round(country_gdp.pct_change(fill_method=None).mean() * 100, 2)
        }
        return metrics
    except (KeyError, IndexError, AttributeError):
        return None

def analyze_comparison(df, country_list, metric_type='total'):
    """Analiza una lista de países, adaptándose al tipo de métrica."""
    if not country_list: return None
    all_metrics = []
    for country in country_list:
        metrics = analyze_country_gdp(df, country, metric_type)
        if metrics:
            metrics['country'] = country
            all_metrics.append(metrics)

    if not all_metrics: return None

    try:
        country_with_max_gdp = max(all_metrics, key=lambda x: x['max_gdp']['value'])
        country_with_min_gdp = min(all_metrics, key=lambda x: x['min_gdp']['value'])
        country_with_max_growth = max(all_metrics, key=lambda x: x.get('avg_growth_percent', -float('inf')))
    except (TypeError, ValueError):
        return None

    return {
        'overall_max_gdp': country_with_max_gdp,
        'overall_min_gdp': country_with_min_gdp,
        'highest_growth': country_with_max_growth
    }

def analyze_world_data(df):
    """Calcula las métricas y datos agregados para la vista mundial."""
    gdp_cols = [col for col in df.columns if col.startswith('GDP_') and 'per_capita' not in col]
    gdp_cols_exist = [col for col in gdp_cols if col in df.columns]
    if not gdp_cols_exist:
        return None 

    world_gdp_series = df[gdp_cols_exist].sum()
    avg_growth = world_gdp_series.pct_change(fill_method=None).mean() * 100
    
    world_growth_df = (world_gdp_series.pct_change(fill_method=None).dropna() * 100).reset_index()
    world_growth_df.columns = ['Año', 'Crecimiento (%)']
    world_growth_df['Año'] = world_growth_df['Año'].str.replace('GDP_', '')
    
    metrics = {
        'gdp_actual': world_gdp_series.get('GDP_2025', 0),
        'max_gdp': {'value': world_gdp_series.max(), 'year': int(world_gdp_series.idxmax().split('_')[-1])},
        'min_gdp': {'value': world_gdp_series.min(), 'year': int(world_gdp_series.idxmin().split('_')[-1])},
        'avg_growth_percent': round(avg_growth, 2),
        'world_total_gdp': world_gdp_series.reset_index().rename(columns={'index': 'Año', 0: 'PIB (Billones USD)'}),
        'world_growth_data': world_growth_df
    }
    metrics['world_total_gdp']['Año'] = metrics['world_total_gdp']['Año'].str.replace('GDP_', '')
    return metrics

def analyze_continent_growth(df, year):
    """
    Calcula el crecimiento promedio, trabajando sobre una copia 
    y siguiendo las mejores prácticas de Pandas.
    """
    df_copy = df.copy() 
    previous_year_col = f'GDP_{year - 1}'
    current_year_col = f'GDP_{year}'
    
    if previous_year_col not in df_copy.columns or current_year_col not in df_copy.columns:
        return pd.DataFrame() 
        
    df_copy['Continent'] = df_copy['Country'].apply(get_continent)
    
    df_copy[previous_year_col] = pd.to_numeric(df_copy[previous_year_col], errors='coerce')
    df_copy[current_year_col] = pd.to_numeric(df_copy[current_year_col], errors='coerce')
    
    df_copy_safe = df_copy[df_copy[previous_year_col].notna() & (df_copy[previous_year_col] != 0)].copy()
    
    if not df_copy_safe.empty:
        # --- CORRECCIÓN PARA EL SettingWithCopyWarning ---
        # Usamos .loc para asignar la nueva columna de forma segura
        df_copy_safe.loc[:, 'Growth'] = (df_copy_safe[current_year_col] - df_copy_safe[previous_year_col]) / df_copy_safe[previous_year_col] * 100
        continent_growth = df_copy_safe.groupby('Continent')['Growth'].mean().reset_index()
        return continent_growth.sort_values(by='Growth', ascending=False)
    else:
        return pd.DataFrame(columns=['Continent', 'Growth'])