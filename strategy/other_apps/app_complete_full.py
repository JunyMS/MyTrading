import streamlit as st

st.set_page_config(
    page_title="Gestión de Riesgo Pro",
    layout="centered"
)

st.title("📱 Gestión de Riesgo")

# ======================
# Parámetros Base
# ======================
with st.container():
    col_risk, col_mult = st.columns(2)
    with col_risk:
        importe_a_arriesgar = st.number_input("Riesgo (€)", min_value=1.0, value=100.0, step=5.0)
    with col_mult:
        # Añadimos el multiplicador aquí porque es clave para ajustar la estrategia
        atr_mult = st.number_input("Mult. ATR (N)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

    usar_eeuu = st.toggle("🇺🇸 Usar referencia EEUU", value=True)

# ======================
# Tabs para móvil (UX limpia)
# ======================
tab_eeuu, tab_tr, tab_resultado = st.tabs(["🇺🇸 EEUU", "🇪🇺 Trade Rep.", "✅ Resultado"])

# --- VARIABLES GLOBALES PARA CÁLCULO ---
porcentaje_riesgo_eeuu = None
num_acciones_tr = 0
stop_loss_tr = 0.0
precio_actual_tr = 0.0

# ======================
# TAB EEUU
# ======================
with tab_eeuu:
    if not usar_eeuu:
        st.info("Referencia de EEUU desactivada")
    else:
        atr_eeuu = st.number_input("ATR EEUU (Dólares)", value=6.40, format="%.2f")
        precio_eeuu = st.number_input("Precio EEUU (Dólares)", value=244.50, format="%.2f")
        
        # Lógica original
        num_acciones_eeuu = int(importe_a_arriesgar / (atr_eeuu * atr_mult))
        stop_eeuu = precio_eeuu - (atr_eeuu * atr_mult)
        total_eeuu = num_acciones_eeuu * precio_eeuu
        porcentaje_riesgo_eeuu = (importe_a_arriesgar / total_eeuu) * 100
        
        st.metric("Riesgo Posición", f"{porcentaje_riesgo_eeuu:.2f} %")
        st.caption(f"Si compras en USA, tu Stop está a un {porcentaje_riesgo_eeuu:.2f}% de distancia.")

# ======================
# TAB TRADE REPUBLIC
# ======================
with tab_tr:
    atr_tr = st.number_input("ATR en TR (Euros)", value=5.8492, format="%.4f")
    precio_actual_tr = st.number_input("Precio en TR (Euros)", value=208.15, format="%.2f")
    
    # Cálculos TR
    num_acciones_tr = int(importe_a_arriesgar / (atr_tr * atr_mult))
    stop_loss_tr = precio_actual_tr - (atr_tr * atr_mult)
    importe_total_tr = num_acciones_tr * precio_actual_tr
    
    st.metric("Nº Acciones", num_acciones_tr)
    st.metric("Inversión Total", f"{importe_total_tr:.2f} €")
    st.metric("Stop ATR Puro", f"{stop_loss_tr:.2f} €")

# ======================
# TAB RESULTADO (EL COMPARADOR)
# ======================
with tab_resultado:
    st.subheader("🎯 Estrategia Final")
    
    if porcentaje_riesgo_eeuu is not None:
        # Aplicamos el % de riesgo de EEUU al precio de TR
        stop_ajustado = precio_actual_tr * (1 - (porcentaje_riesgo_eeuu / 100))
        
        # ¿Cuál es más seguro?
        if stop_ajustado < stop_loss_tr:
            st.warning("⚠️ El stop de EEUU es más amplio que el ATR de TR")
            st.write(f"Stop ATR (Más ajustado): **{stop_loss_tr:.2f} €**")
            st.write(f"Stop Ajustado (Más holgado): **{stop_ajustado:.2f} €**")
        else:
            st.success("✅ El stop ajustado es más seguro")
        
        # Decisión final visual
        st.divider()
        st.markdown(f"### 📍 Poner Stop en: `{stop_loss_tr:.2f} €`")
        st.markdown(f"### 📦 Comprar: `{num_acciones_tr}` acciones")
        
    else:
        st.info("Usa la pestaña de EEUU para comparar el riesgo.")
        st.write(f"Basado solo en ATR de TR:")
        st.success(f"Stop Loss: **{stop_loss_tr:.2f} €**")