import pandas as pd
from modules.data_loader import load_gdp_data # Reutilizamos nuestro cargador

def prepare_merged_data(gdp_path, pop_path):
    """
    Carga los datos de PIB y población, los une y calcula el PIB per cápita.
    """
    # 1. Cargar y limpiar datos de PIB
    df_gdp = load_gdp_data(gdp_path)
    if df_gdp is None:
        return None
    
    # Renombrar columnas de año a 'GDP_YYYY'
    cols_to_rename = {col: f'GDP_{col}' for col in df_gdp.columns if col.isdigit()}
    df_gdp.rename(columns=cols_to_rename, inplace=True)

    # 2. Cargar y preparar datos de población
    try:
        df_pop = pd.read_csv(pop_path)
        # Seleccionamos y renombramos las columnas que nos interesan
        df_pop = df_pop[['Country/Territory', '2022 Population']]
        df_pop.rename(columns={
            'Country/Territory': 'Country',
            '2022 Population': 'Population'
        }, inplace=True)
    except FileNotFoundError:
        print(f">>> Error: El archivo de población no se encontró en '{pop_path}'")
        return None
    
    # 3. Unir (merge) los dos datasets
    # Usamos un 'left' merge para mantener todos los países del dataset de PIB
    df_merged = pd.merge(df_gdp, df_pop, on='Country', how='left')

    # 4. Calcular las métricas de PIB per cápita
    gdp_cols = [col for col in df_merged.columns if 'GDP_' in col]
    for col in gdp_cols:
        year = col.split('_')[1]
        # El PIB está en Billones (10^9), así que lo multiplicamos para la división
        df_merged[f'GDP_per_capita_{year}'] = (df_merged[col] * 1_000_000_000) / df_merged['Population']
    
    print(">>> Datos de PIB y población unidos y procesados exitosamente.")
    return df_merged