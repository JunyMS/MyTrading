import streamlit as st

st.set_page_config(page_title="Trader Pro TR", layout="centered")

st.title("📱 Gestión de Riesgo Pro")

# ======================
# Sidebar - Configuración de Estrategia
# ======================
with st.sidebar:
    st.header("configuración")
    capital_total = st.number_input("Capital Total Cartera (€)", value=10000.0, step=500.0)
    comision = st.number_input("Comisión TR (Compra+Venta)", value=2.0)
    atr_mult = st.slider("Multiplicador ATR (N)", 1.5, 4.0, 2.0, 0.5)

# ======================
# Entrada de Datos Principal
# ======================
col1, col2 = st.columns(2)
with col1:
    importe_a_arriesgar = st.number_input("Riesgo Máximo (€)", value=100.0, step=10.0)
with col2:
    precio_actual = st.number_input("Precio Acción (€)", value=200.0, step=0.1)

atr_actual = st.number_input("ATR Actual (N)", value=5.0, format="%.4f")

# ======================
# Cálculos Core
# ======================
distancia_stop = atr_actual * atr_mult
# Calculamos acciones restando la comisión del riesgo disponible
num_acciones = int((importe_a_arriesgar - comision) / distancia_stop) if distancia_stop > 0 else 0
total_invertido = num_acciones * precio_actual
stop_loss = precio_actual - distancia_stop

# Ratios de Beneficio
tp_1_2 = precio_actual + (distancia_stop * 2)
tp_1_3 = precio_actual + (distancia_stop * 3)

# ======================
# Visualización de Resultados
# ======================
st.divider()

if num_acciones > 0:
    c1, c2, c3 = st.columns(3)
    c1.metric("Acciones", f"{num_acciones}")
    c2.metric("Stop Loss", f"{stop_loss:.2f}€")
    c3.metric("Inversión", f"{total_invertido:.0f}€")

    # Alertas y Consejos
    pct_cartera = (total_invertido / capital_total) * 100
    
    with st.expander("📊 Detalles de la operación", expanded=True):
        st.write(f"**Riesgo real (incl. comisiones):** {((precio_actual - stop_loss) * num_acciones) + comision:.2f} €")
        st.write(f"**Peso en tu cartera:** {pct_cartera:.2f}%")
        if pct_cartera > 20:
            st.warning("⚠️ ¡Cuidado! Esta posición es muy grande para tu capital.")
    
    st.subheader("🎯 Objetivos de Ganancia (Take Profit)")
    col_tp1, col_tp2 = st.columns(2)
    col_tp1.info(f"**Ratio 1:2 (Normal)**\nVender en: **{tp_1_2:.2f}€**")
    col_tp2.success(f"**Ratio 1:3 (Pro)**\nVender en: **{tp_1_3:.2f}€**")

else:
    st.error("Aumenta el riesgo o ajusta el ATR. No puedes comprar 0 acciones.")

st.caption("Recuerda: En Trade Republic, coloca tu orden de Stop Loss manualmente después de comprar.")