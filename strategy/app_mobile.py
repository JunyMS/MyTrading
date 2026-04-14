import streamlit as st

st.set_page_config(
    page_title="Gestión de Riesgo",
    layout="centered"
)

st.title("📱 Gestión de Riesgo")

# st.markdown("Configuración sencilla pensada para móvil")

# ======================
# Parámetros generales
# ======================
st.subheader("⚙️ Parámetros generales")

st.number_input(
    "Capital Total Cartera (€)", 
    value=10000.0, 
    step=1000.0
)

col1, col2 = st.columns(2)

with col1:
    importe_a_arriesgar = st.number_input(
        "Importe a arriesgar (€)",
        min_value=1.0,
        value=100.0,
        step=1.0
    )

with col2:
    distancia_atr = st.number_input(
        "Distancia ATR (número de ATR para el stop)",
        min_value=0.1,
        value=2.0,
        step=1.0
    )



usar_eeuu = st.toggle("Usar mercado EEUU", value=False)

# ======================
# Tabs (mejor UX móvil)
# ======================
tab_eeuu, tab_tr, tab_resultado = st.tabs(
    ["🇺🇸 EEUU", "🇪🇺 TR", "✅ Resultado"]
)

# ======================
# EEUU
# ======================
porcentaje_riesgo_eeuu = None

with tab_eeuu:
    if not usar_eeuu:
        st.info("Mercado EEUU desactivado")
    else:
        atr_actual_eeuu = st.number_input(
            "ATR actual EEUU",
            min_value=0.01,
            value=6.40,
            step=1.00
        )

        precio_actual_eeuu = st.number_input(
            "Precio actual EEUU",
            min_value=0.01,
            value=244.50,
            step=1.00
        )

        num_acciones_eeuu = int(importe_a_arriesgar / (atr_actual_eeuu * distancia_atr))
        stop_loss_eeuu = precio_actual_eeuu - (atr_actual_eeuu * distancia_atr)
        importe_total_eeuu = num_acciones_eeuu * precio_actual_eeuu
        porcentaje_riesgo_eeuu = (importe_a_arriesgar / importe_total_eeuu) * 100
        perdida_total_eeuu = num_acciones_eeuu * (precio_actual_eeuu - stop_loss_eeuu)
        importe_venta_eeuu = num_acciones_eeuu * stop_loss_eeuu

        st.metric("Acciones", num_acciones_eeuu)
        st.metric("Stop Loss", f"{stop_loss_eeuu:.2f}")
        st.metric("Riesgo (%)", f"{porcentaje_riesgo_eeuu:.2f} %")
        st.metric("Pérdida máxima", f"{perdida_total_eeuu:.2f} €")
        st.metric("Venta total al stop", f"{importe_venta_eeuu:.2f} €")


# ======================
# Trade Republic
# ======================
with tab_tr:
    atr_actual_tr = st.number_input(
        "ATR actual TR",
        min_value=0.01,
        value=5.8492,
        step=0.0001,
        format="%.4f"
    )

    precio_actual_tr = st.number_input(
        "Precio actual TR",
        min_value=0.01,
        value=208.15,
        step=1.00
    )

    num_acciones_tr = int(importe_a_arriesgar / (atr_actual_tr * distancia_atr))
    stop_loss_tr = precio_actual_tr - (atr_actual_tr * distancia_atr)
    importe_total_tr = num_acciones_tr * precio_actual_tr
    porcentaje_riesgo_tr = (importe_a_arriesgar / importe_total_tr) * 100
    perdida_total_tr = num_acciones_tr * (precio_actual_tr - stop_loss_tr)
    importe_venta_tr = num_acciones_tr * stop_loss_tr

    st.metric("Acciones a comprar", num_acciones_tr)
    st.metric("**Stop ATR**", f"{stop_loss_tr:.2f} €")
    st.metric("Riesgo (%)", f"{porcentaje_riesgo_tr:.2f} %")
    st.metric("Pérdida máxima", f"{perdida_total_tr:.2f} €")
    st.metric("Venta total al stop", f"{importe_venta_tr:.2f} €")

# ======================
# Resultado final
# ======================
with tab_resultado:
    st.subheader("🎯 Decisión de Stop Loss")

    if porcentaje_riesgo_eeuu is not None:
        stop_loss_ajustado = precio_actual_tr - (
            precio_actual_tr * (porcentaje_riesgo_eeuu / 100)
        )

        perdida_ajustada = num_acciones_tr * (
            precio_actual_tr - stop_loss_ajustado
        )

        st.metric("Stop ATR", f"{stop_loss_tr:.2f}")
        st.metric("Stop ajustado", f"{stop_loss_ajustado:.2f}")

        if perdida_ajustada > perdida_total_tr:
            st.warning(
                f"❌ Stop ajustado aumenta el riesgo\n\n"
                f"✅ Usar stop ATR: **{stop_loss_tr:.2f}**\n\n"
                f"💰 Venta total al stop: **{num_acciones_tr * stop_loss_tr:.2f} €**"
            )
        else:
            st.success(
                f"✅ Stop ajustado mantiene/reduce riesgo\n\n"
                f"➡️ Usar stop ajustado: **{stop_loss_ajustado:.2f}**\n\n"
                f"💰 Venta total al stop: **{num_acciones_tr * stop_loss_ajustado:.2f} €**"

            )
    else:
        st.success(
            f"✅ Mercado EEUU no usado\n\n"
            f"➡️ Usar stop ATR: **{stop_loss_tr:.2f}**\n\n"
            f"💰 Venta total al stop: **{num_acciones_tr * stop_loss_tr:.2f} €**"
        )
