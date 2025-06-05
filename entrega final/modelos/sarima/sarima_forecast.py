import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# 1. Cargar datos
df_2022 = pd.read_csv('2022_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df_2023 = pd.read_csv('2023_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df = pd.concat([df_2022, df_2023])

# 2. Limpieza
df['cantidad_neta'] = pd.to_numeric(df['cantidad_neta'], errors='coerce')
df = df.dropna(subset=['cantidad_neta'])

# 3. Agrupar ventas diarias por cliente y ciudad
ventas_diarias = df.groupby(['fecha_de_factura', 'solicitante', 'CIUDAD'])['cantidad_neta'].sum().reset_index()
ventas_diarias.columns = ['fecha', 'solicitante', 'CIUDAD', 'cantidad_neta']

# 4. Generar lista de combinaciones cliente + ciudad con al menos 180 días
clientes_unicos = ventas_diarias.groupby(['solicitante', 'CIUDAD']).size().reset_index(name='n_dias')
clientes_filtrables = clientes_unicos[clientes_unicos['n_dias'] >= 180]

# 5. Fecha de corte
fecha_corte = pd.to_datetime("2023-07-01")

# 6. Evaluar cada combinación con SARIMA
resultados = []

for _, row in clientes_filtrables.iterrows():
    cliente = row['solicitante']
    ciudad = row['CIUDAD']

    subset = ventas_diarias[
        (ventas_diarias['solicitante'] == cliente) &
        (ventas_diarias['CIUDAD'] == ciudad)
    ].sort_values('fecha')

    subset = subset.set_index('fecha').asfreq('D')
    subset['cantidad_neta'] = subset['cantidad_neta'].fillna(0)

    train = subset[subset.index < fecha_corte]
    test = subset[subset.index >= fecha_corte]

    if len(train) < 180 or len(test) < 30:
        continue

    try:
        # Entrenar SARIMA
        model = SARIMAX(train['cantidad_neta'],
                        order=(1, 1, 1),
                        seasonal_order=(1, 1, 1, 7),  # semanal
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        results = model.fit(disp=False)

        # Pronóstico
        pred = results.predict(start=test.index[0], end=test.index[-1])

        # Evaluación
        mae = mean_absolute_error(test['cantidad_neta'], pred)
        promedio_real = test['cantidad_neta'].mean()
        mae_relativo = mae / promedio_real if promedio_real != 0 else None

        comparacion_filtrada = test[test['cantidad_neta'] != 0]
        pred_filtrada = pred[test['cantidad_neta'] != 0]
        if len(comparacion_filtrada) == 0:
            mape = None
        else:
            mape = (abs((comparacion_filtrada['cantidad_neta'] - pred_filtrada) / comparacion_filtrada['cantidad_neta'])).mean() * 100

        resultados.append({
            'cliente': cliente,
            'ciudad': ciudad,
            'MAE': mae,
            'Promedio_ventas_test': promedio_real,
            'MAE_relativo': mae_relativo,
            'MAPE (%)': mape,
            'observaciones': len(subset)
        })

    except Exception as e:
        print(f"Error en {cliente} - {ciudad}: {e}")
        continue

# 7. Mostrar resultados
df_resultados = pd.DataFrame(resultados).sort_values('MAE')
print(df_resultados)

# 8. Clasificación del desempeño por MAPE
def clasificar_mape(mape):
    if pd.isna(mape):
        return 'Sin datos'
    elif mape < 10:
        return 'Excelente'
    elif mape < 20:
        return 'Buena'
    elif mape < 50:
        return 'Aceptable'
    else:
        return 'Mala'

df_resultados['desempeño'] = df_resultados['MAPE (%)'].apply(clasificar_mape)

# Mostrar resumen de desempeño
print("\nDistribución del desempeño (porcentaje):")
print(df_resultados['desempeño'].value_counts(normalize=True) * 100)

# Guardar resultados en Excel
df_resultados.to_excel('resultados_modelo_sarima.xlsx', index=False)
