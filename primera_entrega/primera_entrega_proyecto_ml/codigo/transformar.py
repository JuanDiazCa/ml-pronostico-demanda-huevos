import pandas as pd

# Ruta del archivo
ruta_archivo = "../datos/originales/FLASH BI.xlsx"

# Cargar el archivo Excel
df = pd.read_excel(ruta_archivo)

# Mostrar información inicial
print("Filas y columnas originales:", df.shape)

# Verificar nombres de columnas
print("Nombres de columnas originales:")
print(df.columns)

# Renombrar columnas
df.rename(columns=lambda col: col.strip().replace(" ", "_").lower(), inplace=True)

# Eliminar columnas que no se necesitan
df.drop(columns=['posicion','fact_anulada','destinatario','nomb_destinatario','stcd1'], inplace=True)

# Eliminar filas vacías
df.dropna(how='all', inplace=True)

# Eliminar filas duplicadas
df.drop_duplicates(inplace=True)

# Convertir la columna de fecha a tipo datetime
if 'Fecha de factura' in df.columns:
    df['Fecha de factura'] = pd.to_datetime(df['Fecha de factura'], errors='coerce')

# Anonimizar nombres de clientes
if 'nomb_solicitante' in df.columns:
    nombres_clientes = df['nomb_solicitante'].dropna().unique()
    mapa_clientes = {nombre: f"Cliente_{i+1}" for i, nombre in enumerate(nombres_clientes)}
    df['nomb_solicitante'] = df['nomb_solicitante'].map(mapa_clientes)

# Anonimizar zonas de ventas
if 'zona_de_ventas' in df.columns:
    zonas = df['zona_de_ventas'].dropna().unique()
    mapa_zonas = {zona: f"Zona_{i+1}" for i, zona in enumerate(zonas)}
    df['zona_de_ventas'] = df['zona_de_ventas'].map(mapa_zonas)

# Anonimizar canales de distribución
if 'canal_dist' in df.columns:
    canales = df['canal_dist'].dropna().unique()
    mapa_canales = {canal: f"Canal_{i+1}" for i, canal in enumerate(canales)}
    df['canal_dist'] = df['canal_dist'].map(mapa_canales)

# Verificar cambios
print("Datos después de limpieza:")
print(df.head())

# Guardar los datosen un nuevo archivo CSV
df.to_csv("../datos/transformados/flash_bi_limpio.csv", index=False, encoding="utf-8-sig")

print("Transformación completa. Archivo guardado en 'datos/transformados/flash_bi_limpio.csv'")