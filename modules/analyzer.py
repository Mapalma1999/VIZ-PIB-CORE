import pandas as pd

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