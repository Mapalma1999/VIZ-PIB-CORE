import pandas as pd

def load_gdp_data(file_path):

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