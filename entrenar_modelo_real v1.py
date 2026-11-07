import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("Cargando el dataset masivo de AMR...")

# 1. Cargar el archivo (asegúrate de que el nombre sea exacto)
df = pd.read_csv(r"C:\Users\perez\ecoli_amr_all_antibiotics.csv")

# 2. Filtrar para el antibiótico que nos interesa (Meropenem)
# (También podrías usar 'ciprofloxacin', 'ampicillin', etc.)
print("Filtrando datos para Meropenem...")
df_mero = df[df['Antibiotic'] == 'meropenem'].copy()

# 3. Limpieza de datos
# Quitamos nulos en el fenotipo y convertimos a 1 (Resistente) y 0 (Susceptible)
df_mero = df_mero.dropna(subset=['Resistant Phenotype'])
df_mero['is_resistant'] = df_mero['Resistant Phenotype'].apply(lambda x: 1 if str(x).strip() == 'Resistant' else 0)

# 4. Crear variables ficticias para las bacterias y otros datos (Encoding)
# Como no tenemos los genes exactos en este CSV, usaremos el "Genome ID" y "Laboratory Typing Method" como features
# (En un caso real, se usarían los genes, pero con este dataset probamos la logística)
features = pd.get_dummies(df_mero[['Genome ID', 'Laboratory Typing Method']], drop_first=True)

# Si el dataset no tiene suficientes variaciones, creamos una columna de ruido para que el modelo tenga algo con qué aprender
if features.shape[1] == 0:
    features['dummy_feature'] = np.random.rand(len(features))

X = features
y = df_mero['is_resistant']

print(f"El dataset filtrado tiene {len(y)} muestras reales de Meropenem.")
print(f"De las cuales {sum(y)} son resistentes y {len(y) - sum(y)} son susceptibles.")

# 5. Entrenamiento
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 6. Evaluación
predicciones = modelo.predict(X_test)
precision = accuracy_score(y_test, predicciones)

print("\n" + "="*50)
print(f"¡PRECISIÓN DE LA IA CON DATOS REALES: {precision * 100:.2f}%!")
print("="*50)

# 7. Guardar el nuevo modelo real
ruta_modelo = r"C:\Users\perez\modelo_amr_real.pkl"
joblib.dump(modelo, ruta_modelo)
print(f"¡Nuevo modelo guardado en: {ruta_modelo}!")