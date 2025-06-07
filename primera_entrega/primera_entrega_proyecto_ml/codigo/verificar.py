import pandas as pd

# Ruta del archivo transformado
archivo_limpio = "../datos/transformados/flash_bi_limpio.csv"

# Cargar los datos limpios
df_limpio = pd.read_csv(archivo_limpio)

# Mostrar resumen
print("Filas y columnas del archivo limpio:", df_limpio.shape)
print("Primeras filas del archivo limpio:")
print(df_limpio.head())
