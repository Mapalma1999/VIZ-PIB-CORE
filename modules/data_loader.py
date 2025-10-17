import pandas as pd

def load_gdp_data(file_path):
    """
    Carga los datos del PIB desde un archivo CSV.

    Args:
        file_path (str): La ruta al archivo CSV.

    Returns:
        pandas.DataFrame: Un DataFrame con los datos del PIB,
                          o None si el archivo no se encuentra.
    """
    try:
        df = pd.read_csv(file_path)
        print(">>> Datos cargados exitosamente.")
        return df
    except FileNotFoundError:
        print(f">>> Error: El archivo no se encontró en la ruta '{file_path}'")
        return None
    except Exception as e:
        print(f">>> Error al cargar los datos: {e}")
        return None