import streamlit as st

st.set_page_config(page_title="Gestión de Riesgo", layout="centered")

st.title("📊 Calculadora de Riesgo y Stop Loss")

st.sidebar.header("Parámetros generales")
importe_a_arriesgar = st.sidebar.number_input(
    "Importe a arriesgar (€)",
    min_value=1.0,
    value=100.0,
    step=1.0
)

usar_eeuu = st.sidebar.checkbox("Calcular mercado EEUU", value=True)

# ======================
# EEUU
# ======================
porcentaje_riesgo_eeuu = None

if usar_eeuu:
    st.sidebar.subheader("EEUU")
    atr_actual_eeuu = st.sidebar.number_input(
        "ATR actual EEUU",
        min_value=0.01,
        value=6.40,
        step=0.01
    )
    precio_actual_eeuu = st.sidebar.number_input(
        "Precio actual EEUU",
        min_value=0.01,
        value=244.50,
        step=0.01
    )

    num_acciones_eeuu = int(importe_a_arriesgar / (atr_actual_eeuu * 2))
    importe_total_eeuu = num_acciones_eeuu * precio_actual_eeuu
    stop_loss_eeuu = precio_actual_eeuu - (atr_actual_eeuu * 2)
    porcentaje_riesgo_eeuu = (importe_a_arriesgar / importe_total_eeuu) * 100
    perdida_total_eeuu = num_acciones_eeuu * (precio_actual_eeuu - stop_loss_eeuu)

    st.subheader("🇺🇸 Mercado EEUU")
    st.metric("Acciones a comprar", num_acciones_eeuu)
    st.metric("Importe total invertido", f"{importe_total_eeuu:.2f} €")
    st.metric("Stop Loss", f"{stop_loss_eeuu:.2f}")
    st.metric("Riesgo (%)", f"{porcentaje_riesgo_eeuu:.2f} %")
    st.metric("Pérdida total al stop", f"{perdida_total_eeuu:.2f} €")

st.divider()

# ======================
# Trade Republic
# ======================
st.sidebar.subheader("Trade Republic")
atr_actual_tr = st.sidebar.number_input(
    "ATR actual TR",
    min_value=0.01,
    value=5.8492,
    step=0.0001,
    format="%.4f"
)
precio_actual_tr = st.sidebar.number_input(
    "Precio actual TR",
    min_value=0.01,
    value=208.15,
    step=0.01
)

num_acciones_tr = int(importe_a_arriesgar / (atr_actual_tr * 2))
importe_total_tr = num_acciones_tr * precio_actual_tr
stop_loss_tr = precio_actual_tr - (atr_actual_tr * 2)
porcentaje_riesgo_tr = (importe_a_arriesgar / importe_total_tr) * 100
perdida_total_tr = num_acciones_tr * (precio_actual_tr - stop_loss_tr)

st.subheader("🇪🇺 Trade Republic")
st.metric("Acciones a comprar", num_acciones_tr)
st.metric("Importe total invertido", f"{importe_total_tr:.2f} €")
st.metric("Stop Loss (ATR)", f"{stop_loss_tr:.2f}")
st.metric("Riesgo (%)", f"{porcentaje_riesgo_tr:.2f} %")
st.metric("Pérdida total al stop", f"{perdida_total_tr:.2f} €")

# ======================
# Ajuste de stop si existe EEUU
# ======================
if porcentaje_riesgo_eeuu is not None:
    stop_loss_ajustado = precio_actual_tr - (
        precio_actual_tr * (porcentaje_riesgo_eeuu / 100)
    )
    perdida_total_ajustada = num_acciones_tr * (
        precio_actual_tr - stop_loss_ajustado
    )

    st.divider()
    st.subheader("⚖️ Ajuste de Stop (igualar riesgo EEUU)")

    st.metric(
        "Stop Loss ajustado",
        f"{stop_loss_ajustado:.2f}",
        delta=f"{stop_loss_ajustado - stop_loss_tr:.2f}"
    )

    st.metric(
        "Pérdida total (stop ajustado)",
        f"{perdida_total_ajustada:.2f} €"
    )

    if perdida_total_tr < perdida_total_ajustada:
        st.error(
            f"❌ El stop ajustado AUMENTA el riesgo.\n\n"
            f"✅ Elegir stop ATR: **{stop_loss_tr:.2f}**\n\n"
            f"Venta total al stop: **{num_acciones_tr * stop_loss_tr:.2f} €**"
        )
    else:
        st.success(
            f"✅ El stop ajustado mantiene o REDUCE el riesgo.\n\n"
            f"✅ Elegir stop ajustado: **{stop_loss_ajustado:.2f}**\n\n"
            f"Venta total al stop: **{num_acciones_tr * stop_loss_ajustado:.2f} €**"
        )

else:
    st.info(
        f"✅ Usar stop ATR estándar: **{stop_loss_tr:.2f}**\n\n"
        f"Venta total al stop: **{num_acciones_tr * stop_loss_tr:.2f} €**"
    )