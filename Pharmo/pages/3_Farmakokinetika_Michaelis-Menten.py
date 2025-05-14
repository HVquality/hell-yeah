import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Judul
st.title("Model Farmakokinetika Michaelis-Menten")

# Sidebar
st.sidebar.header("Parameter Model")

# Parameter Input
weight_kg = st.sidebar.number_input("Berat Badan (kg)", 30.0, 150.0, 70.0, step=1.0)
Vd = weight_kg * 0.8  # L

# Michaelis-Menten parameter
V_max_per_kg = st.sidebar.number_input(
    "Vₘₐₓ (mg/h/kg)",
    min_value=0.1,
    max_value=50.0,
    value=1.16,
    step=0.05
)
V_max = V_max_per_kg * weight_kg  # mg/h

K_m = st.sidebar.number_input(
    "Kₘ (mg/L)",
    min_value=0.1,
    max_value=1000.0,
    value=24.1,
    step=1.0
)

# Parameter dosis
is_repeated = st.sidebar.checkbox("Aktifkan dosis berulang", value=True)
tau = st.sidebar.slider("Interval dosis (τ, jam)", 1, 48, 24) if is_repeated else None
D = st.sidebar.number_input("Dosis (mg)", min_value=0.0, max_value=5000.0, value=530.0, step=10.0)
t_end = st.sidebar.number_input("Jangka waktu (hours)", min_value=1.0, max_value=1000.0, value=400.0)

# MEC dan MTC
st.sidebar.header("Parameter Terapetik")
mec = st.sidebar.number_input("MEC (Minimum Effective Concentration) [mg/L]",
                              min_value=0.0,
                              max_value=1000.0,
                              value=5.0)
mtc = st.sidebar.number_input("MTC (Maximum Tolerated Concentration) [mg/L]",
                              min_value=0.0,
                              max_value=1000.0,
                              value=15.0)

# Parameter simulasi
dt = 0.05  # Time step
t = np.arange(0, t_end + dt, dt)
C = np.zeros_like(t)


dose_times = []
if is_repeated:
    dose_times = np.arange(0, t_end, tau)
else:
    dose_times = [0.0]


for i in range(len(t) - 1):
    # pengambilan dosis
    if any(np.isclose(t[i], dose_times, atol=dt / 2)):
        C[i] += D / Vd

    # Michaelis-Menten eliminasi
    if C[i] > 0:
        elimination_rate = (V_max / Vd) * C[i] / (K_m + C[i])
        C[i + 1] = C[i] - elimination_rate * dt
        C[i + 1] = max(C[i + 1], 0)  # Non-negative constraint
    else:
        C[i + 1] = 0

# Steady-state, perhitungan
if is_repeated and (len(dose_times) > 3):
    last_dose = dose_times[-3]  # Ambil 3 interval terakhir
    mask = (t >= last_dose) & (t <= last_dose + 3 * tau)
    C_ss = C[mask]
    if len(C_ss) > 0:
        C_ss_max = np.max(C_ss)
        C_ss_min = np.min(C_ss)
    else:
        C_ss_max = C_ss_min = 0
else:
    C_ss_max = C_ss_min = np.max(C) if not is_repeated else 0

# Visualisasi
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=t,
    y=C,
    mode='lines',
    line=dict(color='#1f77b4', width=2),
    name='Konsentrasi Plasma',
    hovertemplate="Waktu: %{x:.1f} jam<br>Konsentrasi: %{y:.2f} mg/L<extra></extra>"
))

# TAMBAHAN GARIS MEC dan MTC
if mec > 0:
    fig.add_hline(y=mec, line_dash="dot", line_color="green",
                  annotation_text=f"MEC: {mec} mg/L",
                  annotation_position="bottom right")

if mtc > 0:
    fig.add_hline(y=mtc, line_dash="dot", line_color="red",
                  annotation_text=f"MTC: {mtc} mg/L",
                  annotation_position="top right")
# (akhir tambahan MEC MTC)

# Tanda pengambilan dosis
if is_repeated:
    for dose_time in dose_times:
        fig.add_vline(
            x=dose_time,
            line_dash="dot",
            line_color="gray",
            annotation_text=f"",
            annotation_position="top right"
        )

fig.update_layout(
    title='Profil Konsentrasi-Waktu',
    xaxis_title='Waktu (jam)',
    yaxis_title='Konsentrasi (mg/L)',
    hovermode='x unified',
    template='plotly_white'
)
st.plotly_chart(fig, use_container_width=True)

# Stat
st.subheader("📊 Parameter Farmakokinetik")
col1, col2, col3 = st.columns(3)
col1.metric("Volume Distribusi (Vd)", f"{Vd:.1f} L")
col2.metric("Vₘₐₓ Sistemik", f"{V_max:.1f} mg/h")
col3.metric("Kₘ", f"{K_m:.1f} mg/L")

if is_repeated:
    st.subheader("📈 Parameter Steady-State")
    col1, col2 = st.columns(2)
    col1.metric("Cₛₛ,ₘₐₓ (Maksimal)", f"{C_ss_max:.2f} mg/L")
    col2.metric("Cₛₛ,ₘᵢₙ (Minimum)", f"{C_ss_min:.2f} mg/L")
