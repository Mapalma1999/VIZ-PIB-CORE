import pandas as pd
from modules.data_loader import load_gdp_data
from modules.analyzer import get_continent # <-- NUEVA IMPORTACIÓN

def prepare_merged_data(gdp_path, pop_path):
    
    # 1. Cargar y limpiar datos de PIB (sin cambios)
    df_gdp = load_gdp_data(gdp_path)
    if df_gdp is None:
        return None
    
    cols_to_rename = {col: f'GDP_{col}' for col in df_gdp.columns if col.isdigit()}
    df_gdp.rename(columns=cols_to_rename, inplace=True)

    # 2. Cargar y preparar datos de población
    try:
        df_pop = pd.read_csv(pop_path)
        
        # --- CÓDIGO DE DEPURACIÓN PARA ENCONTRAR PAÍSES NO MAPEADOS ---
        df_pop['Continent_Check'] = df_pop['Country/Territory'].apply(get_continent)
        unmapped_countries = df_pop[df_pop['Continent_Check'] == 'Otros']['Country/Territory'].unique()
        if len(unmapped_countries) > 0:
            print("\n>>> PAÍSES NO MAPEADOS DESDE world_population.csv:", unmapped_countries)
        # ----------------------------------------------------------------

        df_pop = df_pop[['Country/Territory', '2022 Population']]
        df_pop.rename(columns={
            'Country/Territory': 'Country',
            '2022 Population': 'Population'
        }, inplace=True)
    except FileNotFoundError:
        print(f">>> Error: El archivo de población no se encontró en '{pop_path}'")
        return None
    
    # 3. Unir (merge) los dos datasets (sin cambios)
    df_merged = pd.merge(df_gdp, df_pop, on='Country', how='left')

    # 4. Calcular las métricas de PIB per cápita (sin cambios)
    gdp_cols = [col for col in df_merged.columns if 'GDP_' in col]
    for col in gdp_cols:
        year = col.split('_')[1]
        df_merged[f'GDP_per_capita_{year}'] = (df_merged[col] * 1_000_000_000) / df_merged['Population']
    
    print(">>> Datos de PIB y población unidos y procesados exitosamente.")
    return df_merged