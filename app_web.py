import streamlit as st
import pandas as pd
import joblib
import datetime
import random

# 1. Configurar la página web
st.set_page_config(page_title="AMR-AI Clinical Pipeline", page_icon="🧬", layout="wide")

st.title("🧬 AMR-AI: Clinical Decision Support System")
st.markdown("Sistema de apoyo a la decisión clínica basado en Inteligencia Artificial.")

# 2. Cargar el modelo
try:
    ruta_modelo = r"C:\Users\perez\modelo_amr_real.pkl" 
    modelo = joblib.load(ruta_modelo)
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}")
    st.stop()

# 3. Base de datos ampliada de antibióticos (Simulando el Cuadro Básico)
# Aquí puedes agregar todos los que quieras. Están agrupados por familia.
ANTIBIOTICOS = {
    "Meropenem": {"familia": "Carbapenémico", "tipo": "último recurso", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Amikacina"},
    "Ceftriaxona": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem"},
    "Cefotaxima": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem"},
    "Ceftazidima": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem"},
    "Ampicilina": {"familia": "Penicilina", "tipo": "primera línea", "evitar_ctex": "Sí", "usar_ctex": "Meropenem/Amikacina"},
    "Amoxicilina": {"familia": "Penicilina", "tipo": "primera línea", "evitar_ctex": "Sí", "usar_ctex": "Meropenem/Amikacina"},
    "Amikacina": {"familia": "Aminoglucósido", "tipo": "alternativa", "evitar_ctex": "No", "usar_ctex": "Es la alternativa"},
    "Gentamicina": {"familia": "Aminoglucósido", "tipo": "alternativa", "evitar_ctex": "No", "usar_ctex": "Es la alternativa"},
    "Ciprofloxacino": {"familia": "Fluoroquinolona", "tipo": "común", "evitar_ctex": "No", "usar_ctex": "Es la alternativa"},
    "Trimetoprima/Sulfametoxazol": {"familia": "Sulfonamida", "tipo": "primera línea", "evitar_ctex": "No", "usar_ctex": "Es la alternativa"}
}

# --- BARRA LATERAL: DATOS DEL PACIENTE ---
st.sidebar.header("📋 Registro del Paciente")
nombre = st.sidebar.text_input("Nombre completo del paciente:")
id_paciente = st.sidebar.text_input("ID / Expediente del hospital:")
edad = st.sidebar.number_input("Edad del paciente:", min_value=0, max_value=120, value=45)

st.sidebar.subheader("🧪 Prueba de Sensibilidad")
# El doctor elige qué antibiótico está evaluando
antibiotico_evaluado = st.sidebar.selectbox("Antibiótico a evaluar:", list(ANTIBIOTICOS.keys()))

st.sidebar.subheader("🧬 Marcadores Genéticos")
tiene_ctex = st.sidebar.checkbox("Presencia de Gen blaCTX-M (BLEE)")
tiene_kpc = st.sidebar.checkbox("Presencia de Gen blaKPC (Carbapenemasa)")

# --- ÁREA PRINCIPAL ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Análisis de Laboratorio")
    if st.button("🔬 Ejecutar Diagnóstico IA", type="primary"):
        if not nombre or not id_paciente:
            st.warning("Por favor, ingrese el nombre y el ID del paciente antes de ejecutar el diagnóstico.")
        else:
            st.session_state['analizado'] = True
            st.session_state['datos_paciente'] = {
                "nombre": nombre,
                "id": id_paciente,
                "edad": edad,
                "antibiotico": antibiotico_evaluado,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folio": f"AMR-{random.randint(1000, 9999)}"
            }

with col2:
    st.subheader("Información del Sistema")
    st.info("Sistema experto para predicción de resistencia. Evaluando farmacología clínica basada en genómica.")

# --- GENERACIÓN DEL REPORTE CLÍNICO ---
if st.session_state.get('analizado', False):
    st.markdown("---")
    datos = st.session_state['datos_paciente']
    info_ab = ANTIBIOTICOS[datos['antibiotico']]
    
    st.header("📄 Reporte Clínico Automatizado")
    
    # Recuadro con formato de receta
    with st.container(border=True):
        st.markdown(f"**Folio:** {datos['folio']} | **Fecha de Emisión:** {datos['fecha']}")
        st.markdown(f"**Paciente:** {datos['nombre']} (ID: {datos['id']}) | **Edad:** {datos['edad']} años")
        st.markdown(f"**Antibiótico Evaluado:** {datos['antibiotico']} ({info_ab['familia']})")
        st.divider()
        
        # Lógica de decisión clínica
               # Lógica de decisión clínica
        if tiene_ctex or tiene_kpc:
            st.error(f"⚠️ **RESULTADO: CEPA RESISTENTE a {datos['antibiotico']}.**")
            
            # --- LÓGICA PARA BLEE (blaCTX-M) ---
            if tiene_ctex:
                st.markdown(f"**Justificación:** Gen *blaCTX-M* (BLEE) detectado. Confiere resistencia a penicilinas y cefalosporinas de 3ra generación.")
                if "Cefalosporina" in info_ab['familia'] or "Penicilina" in info_ab['familia']:
                    st.markdown(f"❌ **Contraindicado:** {datos['antibiotico']}.")
                    st.success(f"✅ **Alternativa sugerida (Cuadro Básico):** Meropenem o Amikacina.")
                else:
                    st.markdown(f"✅ **El antibiótico {datos['antibiotico']} podría ser efectivo** a pesar de la BLEE, pero requiere validación médica.")
            
            # --- LÓGICA PARA CARBAPENEMASA (blaKPC) ---
            if tiene_kpc:
                st.markdown(f"**Justificación:** Gen *blaKPC* (Carbapenemasa) detectado. Confiere resistencia a carbapenémicos y a la mayoría de betalactámicos.")
                # Si el antibiótico evaluado es un betalactámico, le advertimos
                if info_ab['familia'] in ["Carbapenémico", "Cefalosporina 3ra Gen", "Penicilina"]:
                    st.markdown(f"❌ **Contraindicado:** {datos['antibiotico']} (Resistencia a betalactámicos).")
                
                # SIEMPRE sugerimos una alternativa para KPC
                st.warning("⚠️ **Alerta de Salud Pública:** Cepa resistente a carbapenémicos.")
                st.success("✅ **Opciones de Tratamiento (Último Recurso):**")
                st.markdown("- **Polimixina B** (si está en el cuadro básico)")
                st.markdown("- **Tigeciclina** (para infecciones complicadas)")
                st.markdown("- **Ceftazidima/Avibactam** (si el hospital cuenta con presupuesto)")
        
        else:
            # Usamos el modelo de IA
            paciente = {'Genome ID': 562, 'Laboratory Typing Method': 'Disk diffusion'}
            df_paciente = pd.DataFrame([paciente])
            df_dummies = pd.get_dummies(df_paciente)
            for col in modelo.feature_names_in_:
                if col not in df_dummies.columns:
                    df_dummies[col] = 0
            df_final = df_dummies[modelo.feature_names_in_]
            prediccion = modelo.predict(df_final)[0]
            
            if prediccion == 1:
                st.warning(f"⚠️ **RESULTADO: CEPA RESISTENTE (Predicción IA) a {datos['antibiotico']}.**")
                st.success(f"✅ **Tratamiento sugerido:** Evaluar alternativas del cuadro básico.")
            else:
                st.success(f"✅ **RESULTADO: CEPA SUSCEPTIBLE a {datos['antibiotico']}.**")
                st.info(f"💡 **El antibiótico {datos['antibiotico']} es una opción viable según la IA.**")
        
        st.divider()
        st.caption("Firma del responsable: ___________________________ (Validación médica requerida)")
        st.caption("Este es un reporte generado por IA y no sustituye el juicio clínico de un profesional de la salud.")