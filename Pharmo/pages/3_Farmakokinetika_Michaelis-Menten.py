import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Title
st.title("Model Farmakokinetika Michaelis-Menten")

# Sidebar header
st.sidebar.header("Parameter Model")

# Compact layout for dose limits
col1, col2 = st.sidebar.columns(2)
with col1:
    dose_min = st.text_input("Atur dosis minimum (mg)", value="0.0")
with col2:
    dose_max = st.text_input("Atur dosis maksimum (mg)", value="1000.0")

try:
    dose_min = float(dose_min)
    dose_max = float(dose_max)
except ValueError:
    dose_min, dose_max = 0.0, 1000.0

# Weight parameters
weight_kg = st.sidebar.number_input("Berat Badan (kg)", 30.0, 150.0, 50.0, step=1.0)
Vd = weight_kg * 0.8  # L

# Michaelis-Menten parameters (weight-adjusted)
V_max_per_kg = st.sidebar.number_input("Vₘₐₓ (mg/h/kg)",
                                       min_value=0.1, max_value=50.0,
                                       value=0.3, step=0.05,
                                       help="Eliminasi maksimum per kilogram")
V_max = V_max_per_kg * weight_kg  # Convert to absolute V_max

K_m = st.sidebar.number_input("Kₘ (mg/L)",
                              min_value=0.1, max_value=1000.0,
                              value=20.0, step=1.0,
                              help="konstanta Michaelis (konsentrasi pada saat ½Vₘₐₓ)")

# Repeated dosing toggle
is_repeated = st.sidebar.checkbox("Aktifkan dosis berulang", value=True)
tau = st.sidebar.slider("Interval dosis (τ, jam)", 1, 24, 2) if is_repeated else None

# Time span
t_end = float(st.sidebar.text_input("Jangka waktu (hours)", value="24.0")) or 100.0

# Dose (D)
D = st.sidebar.slider("Dosis (mg)", min_value=dose_min, max_value=dose_max, value=1000.0, step=1.0)

# Y-axis limit
y_max = float(st.sidebar.text_input("Atur nilai sumbu-y tertinggi", value="100.0")) or 100.0

# Time array
dt = 0.1  # Smaller time step for stability
t = np.arange(0, t_end + dt, dt)

# Initialize concentration array
C = np.zeros_like(t)

# Dosing schedule
dose_times = np.arange(0, t_end, tau) if is_repeated else [0]

# Numerical integration (Euler method)
for dose_time in dose_times:
    idx = int(dose_time / dt)
    C[idx] += D / Vd  # Instantaneous absorption

    # Simulate elimination for this dose
    for i in range(idx, len(t) - 1):
        if C[i] > 0:
            dCdt = -V_max * C[i] / (K_m + C[i])
            C[i + 1] = C[i] + dCdt * dt
            C[i + 1] = max(C[i + 1], 0)  # Prevent negative concentrations

# Steady-state metrics (last dosing interval)
if is_repeated and len(dose_times) > 1:
    last_dose = dose_times[-1]
    mask = (t >= last_dose - tau) & (t <= last_dose)
    C_last = C[mask] if any(mask) else [0]
    C_ss_max, C_ss_min = np.max(C_last), np.min(C_last)
else:
    C_ss_max = C_ss_min = 0

# Display metrics
if is_repeated:
    st.subheader("📊 Kondisi Steady-State")
    col1, col2 = st.columns(2)
    col1.metric("C_ss,max (Peak)", f"{C_ss_max:.2f} mg/L")
    col2.metric("C_ss,min (Trough)", f"{C_ss_min:.2f} mg/L")

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=C, mode='lines', name='Concentration'))
fig.update_layout(
    title='Farmakokinetika Michaelis-Menten',
    xaxis_title='Waktu (jam)',
    yaxis_title='Konsentrasi (mg/L)',
    xaxis=dict(range=[0, t_end]),
    yaxis=dict(range=[0, y_max]),
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)