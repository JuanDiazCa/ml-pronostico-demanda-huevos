import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error

# 1. Cargar datos
df_2022 = pd.read_csv('2022_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df_2023 = pd.read_csv('2023_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df = pd.concat([df_2022, df_2023])

# 2. Limpieza
df['cantidad_neta'] = pd.to_numeric(df['cantidad_neta'], errors='coerce')
#df = df[df['cl_factura'] == 'VENTA']
df = df.dropna(subset=['cantidad_neta'])

# 3. Agrupar ventas diarias por cliente y ciudad
ventas_diarias = df.groupby(['fecha_de_factura', 'solicitante', 'CIUDAD'])['cantidad_neta'].sum().reset_index()
ventas_diarias.columns = ['ds', 'solicitante', 'CIUDAD', 'y']

# 4. Generar lista de combinaciones cliente + ciudad con al menos 180 días
clientes_unicos = ventas_diarias.groupby(['solicitante', 'CIUDAD']).size().reset_index(name='n_dias')
clientes_filtrables = clientes_unicos[clientes_unicos['n_dias'] >= 180]

# 5. Fecha de corte: 18 meses entrenamiento, 6 prueba
fecha_corte = pd.to_datetime("2023-07-01")

# 6. Evaluar cada combinación con Prophet
resultados = []

for _, row in clientes_filtrables.iterrows():
    cliente = row['solicitante']
    ciudad = row['CIUDAD']

    subset = ventas_diarias[
        (ventas_diarias['solicitante'] == cliente) &
        (ventas_diarias['CIUDAD'] == ciudad)
    ].sort_values('ds')

    train = subset[subset['ds'] < fecha_corte]
    test = subset[subset['ds'] >= fecha_corte]

    # Saltar si no hay suficiente información para prueba
    if len(train) < 100 or len(test) < 30:
        continue

    # Entrenar modelo
    modelo = Prophet(daily_seasonality=True)
    modelo.fit(train)

    # Generar pronóstico
    future = modelo.make_future_dataframe(periods=len(test), freq='D')
    forecast = modelo.predict(future)

    # Comparar con test real
    comparacion = forecast[['ds', 'yhat']].merge(test[['ds', 'y']], on='ds', how='inner')
    if len(comparacion) == 0:
        continue

    # Calcular métricas
    mae = mean_absolute_error(comparacion['y'], comparacion['yhat'])
    promedio_real = comparacion['y'].mean()
    mae_relativo = mae / promedio_real if promedio_real != 0 else None

    comparacion_filtrada = comparacion[comparacion['y'] != 0]
    if len(comparacion_filtrada) == 0:
        mape = None
    else:
        mape = (abs((comparacion_filtrada['y'] - comparacion_filtrada['yhat']) / comparacion_filtrada['y'])).mean() * 100

    resultados.append({
        'cliente': cliente,
        'ciudad': ciudad,
        'MAE': mae,
        'Promedio_ventas_test': promedio_real,
        'MAE_relativo': mae_relativo,
        'MAPE (%)': mape,
        'observaciones': len(subset)
    })

# 7. Mostrar y guardar resultados
df_resultados = pd.DataFrame(resultados).sort_values('MAE')
print(df_resultados)


