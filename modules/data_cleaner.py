import pandas as pd

def clean_gdp_data(df):
    """
    Limpia y estandariza el DataFrame del PIB.
    """
    if df is None:
        return None

    cleaned_df = df.copy()

    # Única Tarea: Renombrar columnas de año a 'GDP_YYYY'
    cols_to_rename = {}
    for col in cleaned_df.columns:
        if col.isdigit():
            cols_to_rename[col] = f'GDP_{col}'

    cleaned_df.rename(columns=cols_to_rename, inplace=True)
    print(">>> Columnas de año estandarizadas a formato 'GDP_YYYY'.")
    
    return cleaned_df