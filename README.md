# ml-pronostico-demanda-huevos

<h1 style="text-align: center;">
<strong>Proyecto de Machine Learning</strong>
</h1>
<h2 style="text-align: center;">
Universidad Autónoma de Occidente
</h2>
<h3 style="text-align: center;">
Maestría en Inteligencia Artificial y Ciencia de Datos
</h3>
<h3 style="text-align: center;">
Asignatura: Aprendizaje Automático
</h3>
<h3 style="text-align: center;">
Profesor: Francisco Jose Mercado Rivera, PhD
</h3>
<h3 style="text-align: center;">
5 junio 2025
</h3>

---

## Autores:

<div align="center">

| Juan David Díaz Calero |  Luis Carlos Correa Zuluaga   |      Carlos Becerra       |
| :--------------------: | :---------------------------: | :-----------------------: |
|     Cód. 22502473      |         Cód. 22501541         |       Cód. 22500215       |
| juan.diaz_c@uao.edu.co | luis_carlos.correa@uao.edu.co | carlos.becerra@uao.edu.co |

</div>

---

## Descripción del Proyecto

Este repositorio contiene el desarrollo completo del proyecto de pronóstico de la demanda de huevos utilizando técnicas de Machine Learning. El trabajo se divide en dos entregas principales:

- **Primera Entrega:** Se enfoca en el proceso ETL (Extracción, Transformación y Carga) de datos, validación, anonimización y la preparación de la información para su análisis en Power BI.
- **Entrega Final:** Incluye la implementación de modelos predictivos (como Prophet, SARIMA y modelos stacked con Random Forest y XGBoost) y los informes/resultados obtenidos, presentados tanto en notebooks como en documentos PDF.

---

## Estructura del Repositorio

```
.
├── .gitignore                    # Ignora carpetas y archivos no deseados
├── README.md                     # Documentación general del repositorio
├── entrega_final/                # Contiene todo lo relacionado con la entrega final
│   ├── Entrega_final_machine_learning.pdf   # Informe final del proyecto
│   ├── Presentación_Proyecto_ML_Huevos.pdf    # Presentación del proyecto
│   ├── modelos/                  # Modelos predictivos
│   │   ├── prophet/
|   |   |   ├──plots
|   |   |   └── prophet_forecast.ipynb
│   │   ├── sarima/
|   |   |   ├──plots
|   |   |   └── sarima_forecast.ipynb
│   │   └── stacked/
|   |   |   ├──plots
|   |   |   └── random_forest_xgboost_stacked.ipynb
│   └── notebbooks_pdf/           # Notebooks convertidos a PDF
│       ├── prophet-forecast.pdf
│       ├── random-forest-xgboost-stacked.pdf
│       └── sarima-forecast.pdf
└── primera_entrega/              # Material y código de la primera entrega
    ├── Presentacion_primera_entrega_proyecto_ML.pdf   # Presentación de la primera entrega
    └── primera_entrega_proyecto_ml/
        ├── codigo/               # Scripts para transformación y validación ETL
        │   ├── transformar.py
        │   └── verificar.py
        ├── datos/                # Datos originales y transformados
        │   ├── originales/       # Datos extraídos (e.g., de SAP, Excel)
        │   └── transformados/    # Datos limpios (e.g., flash_bi_limpio.csv)
        ├── Visualizacion/        # Dashboard en Power BI
        │   └── dashboard ventas.pbix
        ├── principal.py          # Script principal para la ejecución del ETL
        ├── README.md             # Documentación específica de la primera entrega
        └── requisitos.txt        # Dependencias del entorno Python para ETL
```

---

## Requisitos

Para ejecutar el código de la primera entrega, asegúrate de contar con:

- Python 3.10 o superior
- pandas
- openpyxl

Puedes instalar las dependencias utilizando:

```bash
pip install -r "primera entrega/primera_entrega_proyecto_ml/requisitos.txt"
```

---

## Ejecución

---

### Primera Entrega (ETL)

Ejecuta el proceso ETL navegando a la carpeta de la primera entrega y corriendo el script principal:

```bash
python "primera entrega/primera_entrega_proyecto_ml/principal.py"
```

Las diapositivas correspondientes a la presentación de la primera entrega es el siguiente:
[Presentación de primera entrega](primera_entrega/Presentacion_primera_entrega_proyecto_ML.pdf)

---

### Entrega Final (Modelos Predictivos)

Dentro de la carpeta `entrega_final/modelos` encontrarás los distintos modelos implementados:

- Modelo SARIMA: [sarima_forecast.ipynb](entrega_final/modelos/sarima/sarima_forecast.ipynb)
- Modelo Prophet: [sarima_forecast.ipynb](entrega_final/modelos/prophet/prophet_forecast.ipynb)
- Modelo Stacked: [random_forest_xgboost_stacked.ipynb](entrega_final/modelos/stacked/random_forest_xgboost_stacked.ipynb)

También están disponibles los notebooks convertidos a PDF en `entrega final/notebbooks_pdf`.

Las diapositivas correspondientes a la presentación de la entrega final es el siguiente:

- [Presentación de entrega final](entrega_final/Presentación_Proyecto_ML_Huevos.pdf)

El documento de la entrega final es el siguiente:

- [Documento de entrega final](entrega_final/Entrega_final_machine_learning.pdf)

---
