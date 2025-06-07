import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import holidays
import warnings

warnings.filterwarnings("ignore")

# 1. Cargar datos
df_2022 = pd.read_csv('2022_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df_2023 = pd.read_csv('2023_limpio.csv', sep=';', parse_dates=['fecha_de_factura'], dayfirst=True)
df = pd.concat([df_2022, df_2023], ignore_index=True)

# 2. Limpieza básica
df['cantidad_neta'] = pd.to_numeric(df['cantidad_neta'], errors='coerce')
df = df.dropna(subset=['cantidad_neta'])
df = df[df['cantidad_neta'] >= 0]  # Descartar valores negativos si no son devoluciones

# 3. Agrupar ventas diarias por cliente y ciudad
ventas_diarias = df.groupby(['fecha_de_factura', 'solicitante', 'CIUDAD'])['cantidad_neta'].sum().reset_index()
ventas_diarias.columns = ['fecha', 'solicitante', 'CIUDAD', 'cantidad_neta']

# 4. Filtrar combinaciones con al menos 180 días
clientes_unicos = ventas_diarias.groupby(['solicitante', 'CIUDAD']).size().reset_index(name='n_dias')
clientes_filtrables = clientes_unicos[clientes_unicos['n_dias'] >= 15]

# 5. Fecha de corte para train/test
fecha_corte = pd.to_datetime("2023-07-01")

# 6. Resultados finales
resultados = []

# 7. Función para crear características lagged
def create_features(data, target='cantidad_neta', lags=7):
    df = data[[target]].copy()
    for lag in range(1, lags + 1):
        df[f'lag_{lag}'] = df[target].shift(lag)
    df['rolling_mean_7'] = df[target].rolling(window=7).mean()
    df['rolling_mean_30'] = df[target].rolling(window=30).mean()
    df['trend'] = np.arange(len(df))
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['day_of_year'] = df.index.dayofyear
    df = df.dropna()
    return df

# Festivos Colombia
co_holidays = holidays.Colombia(years=[2022, 2023])

# Añadir festivos y días especiales
def add_special_days(X):
    X = X.copy()
    X['es_festivo'] = X.index.map(lambda x: int(x in co_holidays))
    X['es_ultimo_dia_mes'] = (X.index + pd.offsets.MonthEnd(0) == X.index).astype(int)
    X['es_primer_dia_mes'] = (X.index.day == 1).astype(int)
    X['es_viernes'] = (X.index.dayofweek == 4).astype(int)
    X['es_lunes'] = (X.index.dayofweek == 0).astype(int)
    X['es_fin_semana'] = ((X.index.dayofweek == 5) | (X.index.dayofweek == 6)).astype(int)
    return X

print('Iniciando...')
# 8. Bucle por cada cliente + ciudad
for _, row in clientes_filtrables.iterrows():
    cliente = row['solicitante']
    ciudad = row['CIUDAD']

    # Filtrar por cliente y ciudad
    subset = ventas_diarias[
        (ventas_diarias['solicitante'] == cliente) &
        (ventas_diarias['CIUDAD'] == ciudad)
    ].copy()

    # Asegurar frecuencia diaria
    subset = subset.set_index('fecha').asfreq('D')
    subset['cantidad_neta'] = subset['cantidad_neta'].fillna(0)

    if len(subset) < 180:
        continue

    try:
        # Crear características derivadas
        features_df = create_features(subset[['cantidad_neta']], lags=7)
        features_df = add_special_days(features_df)

        # Separar X e y
        X = features_df.drop(columns=['cantidad_neta'])
        y = features_df['cantidad_neta']

        # Dividir en train/test usando fechas
        idx_corte = y.index < fecha_corte
        X_train, X_test = X[idx_corte], X[~idx_corte]
        y_train, y_test = y[idx_corte], y[~idx_corte]

        # Validación de longitud mínima
        if len(X_train) < 180 or len(X_test) < 30:
            continue

        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Verificar consistencia
        assert len(X_train_scaled) == len(y_train), "X_train y y_train no coinciden"
        assert len(X_test_scaled) == len(y_test), "X_test y y_test no coinciden"

        # Entrenar modelos base
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)

        rf.fit(X_train_scaled, y_train)
        xgb.fit(X_train_scaled, y_train)

        # Predicciones
        rf_pred = rf.predict(X_test_scaled)
        xgb_pred = xgb.predict(X_test_scaled)

        # Stacking
        stacked_input = np.column_stack((rf_pred, xgb_pred))
        meta_model = LinearRegression()
        meta_model.fit(stacked_input, y_test)
        final_pred = meta_model.predict(stacked_input)

        # Evaluación
        mae = mean_absolute_error(y_test, final_pred)
        promedio_real = y_test.mean()
        mae_relativo = mae / promedio_real if promedio_real != 0 else None

        mask = y_test != 0
        if mask.any():
            mape = mean_absolute_percentage_error(y_test[mask], final_pred[mask]) * 100
        else:
            mape = None

        resultados.append({
            'cliente': cliente,
            'ciudad': ciudad,
            'MAE': mae,
            'Promedio_ventas_test': promedio_real,
            'MAE_relativo': mae_relativo,
            'MAPE (%)': mape,
            'observaciones': len(features_df)
        })

    except Exception as e:
        print(f"Error en {cliente} - {ciudad}: {e}")
        continue

# 9. Mostrar resultados
df_resultados = pd.DataFrame(resultados).sort_values('MAE')
print(df_resultados)

# 10. Clasificación por MAPE
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
print("\nDistribución del desempeño (porcentaje):")
print(df_resultados['desempeño'].value_counts(normalize=True) * 100)