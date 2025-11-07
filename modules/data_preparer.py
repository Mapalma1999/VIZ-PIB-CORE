import pandas as pd
from modules.data_loader import load_gdp_data

def prepare_merged_data(gdp_path, pop_path):
    """
    Carga, une y prepara los datos de PIB y población (histórica).
    VERSIÓN CON CORRECCIÓN DE SettingWithCopyWarning.
    """
    # 1. Cargar datos de PIB
    df_gdp = load_gdp_data(gdp_path)
    if df_gdp is None:
        return None
    cols_to_rename_gdp = {col: f'GDP_{col}' for col in df_gdp.columns if col.isdigit()}
    df_gdp.rename(columns=cols_to_rename_gdp, inplace=True)

    # 2. Cargar y preparar datos de población
    try:
        df_pop_raw = pd.read_csv(pop_path)
        
        columns_to_map = {
            'Country/Territory': 'Country',
            'CCA3': 'CCA3',
            '2022 Population': 'Population_2022',
            '2020 Population': 'Population_2020',
            '2015 Population': 'Population_2015',
            '2010 Population': 'Population_2010',
            '2000 Population': 'Population_2000',
            '1990 Population': 'Population_1990',
            '1980 Population': 'Population_1980',
            '1970 Population': 'Population_1970'
        }

        existing_cols = [col for col in columns_to_map.keys() if col in df_pop_raw.columns]
        
        # --- CORRECCIÓN DEFINITIVA ---
        # Forzamos a Pandas a crear una COPIA explícita
        df_pop = df_pop_raw[existing_cols].copy()
        # -----------------------------
        
        df_pop.rename(columns=columns_to_map, inplace=True)

        if 'Population_2022' in df_pop.columns:
            # Ahora esta asignación SÍ es segura
            df_pop['Population'] = df_pop['Population_2022']

    except FileNotFoundError:
        print(f">>> Error: El archivo de población no se encontró en '{pop_path}'")
        return None
    
    # 3. Unir los dos datasets
    df_merged = pd.merge(df_gdp, df_pop, on='Country', how='left')

    # 4. Calcular el PIB per cápita
    if 'Population' in df_merged.columns:
        gdp_cols = [col for col in df_merged.columns if 'GDP_' in col]
        for col in gdp_cols:
            year = col.split('_')[1]
            try:
                df_merged[f'GDP_per_capita_{year}'] = (df_merged[col].astype(float) * 1_000_000_000) / df_merged['Population'].astype(float)
            except (TypeError, ValueError):
                df_merged[f'GDP_per_capita_{year}'] = pd.NA
    
    print(">>> Datos de PIB y población (histórica) unidos y procesados.")
    return df_merged