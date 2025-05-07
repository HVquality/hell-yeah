import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Judul
st.title("Model Farmakokinetik Orde Pertama (IV Bolus)")

# Header sidebar
st.sidebar.header("Parameter Model")

# Layout kompak untuk batas dosis
col1, col2 = st.sidebar.columns(2)
with col1:
    dose_min = st.text_input("Atur dosis minimum (D)", value="0.0")
with col2:
    dose_max = st.text_input("Atur dosis maksimum (D)", value="500.0")

try:
    dose_min = float(dose_min)
    dose_max = float(dose_max)
except ValueError:
    dose_min, dose_max = 0.0, 500.0

# Input waktu paruh → k
t_half = st.sidebar.number_input("Waktu Paruh (t₁/₂, jam)", min_value=0.1, max_value=100.0, value=6.0, step=0.1)
k = np.log(2) / t_half

# Toggle dosis berulang
is_repeated = st.sidebar.checkbox("Aktifkan pemberian dosis berulang", value=True)

# Interval pemberian hanya jika berulang
if is_repeated:
    tau = st.sidebar.slider("Interval pemberian dosis (τ, jam)", 1, 24, 6)
else:
    tau = None  # Tidak digunakan dalam mode dosis tunggal

# Berat badan → Vd
weight_kg = st.sidebar.number_input("Berat badan (kg)", 30.0, 150.0, 70.0, step=1.0)
Vd = weight_kg * 0.8  # L

# Rentang waktu (t_end) sebagai input
t_end_input = st.sidebar.text_input("Rentang waktu (jam)", value="100.0")
try:
    t_end = float(t_end_input)
except ValueError:
    t_end = 24.0

# Dosis (D)
D = st.sidebar.slider("Dosis (D)", min_value=dose_min, max_value=dose_max, value=500.0, step=1.0, format="%.1f")

# Maksimum sumbu y independen
y_max_input = st.sidebar.text_input("Atur nilai maksimum sumbu y", value="40.0")
try:
    y_max = float(y_max_input)
except ValueError:
    y_max = 70.0

# Toggle untuk menampilkan garis steady-state
show_ss_lines = st.sidebar.checkbox("Tampilkan garis C_ss,maks dan C_ss,min", value=True)

# Array waktu
t = np.linspace(0, t_end, 1000)

# Perhitungan konsentrasi
if is_repeated:
    C = np.zeros_like(t)
    for n in range(int(t_end // tau) + 1):
        dose_time = n * tau
        C += np.where(t >= dose_time, D / Vd * np.exp(-k * (t - dose_time)), 0)
    # Nilai steady-state
    try:
        C_ss_max = D / (Vd * (1 - np.exp(-k * tau)))
        C_ss_min = C_ss_max * np.exp(-k * tau)
    except ZeroDivisionError:
        C_ss_max = C_ss_min = 0
else:
    # Model dosis tunggal
    C = D / Vd * np.exp(-k * t)
    C_ss_max = C_ss_min = 0

# Tampilkan metrik steady-state jika berulang
if is_repeated:
    st.subheader("📊 Metrik Steady-State")
    col5, col6 = st.columns(2)
    col5.metric("C_ss,maks (Maksimum)", f"{C_ss_max:.2f}")
    col6.metric("C_ss,min (Minimum)", f"{C_ss_min:.2f}")

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=C, mode='lines', name='Konsentrasi Obat'))

# Tambahkan garis steady-state opsional
if is_repeated and show_ss_lines:
    fig.add_trace(go.Scatter(x=[0, t_end], y=[C_ss_max, C_ss_max],
                             mode='lines', name='C_ss,maks',
                             line=dict(dash='dash', color='green')))
    fig.add_trace(go.Scatter(x=[0, t_end], y=[C_ss_min, C_ss_min],
                             mode='lines', name='C_ss,min',
                             line=dict(dash='dash', color='red')))

# Konfigurasi layout
fig.update_layout(
    title='Farmakokinetik: Dosis Tunggal vs Berulang',
    xaxis_title='Waktu (jam)',
    yaxis_title='Konsentrasi',
    xaxis=dict(range=[0, t_end]),
    yaxis=dict(range=[0, y_max]),
    hovermode='x unified'
)

# Tampilkan plot
st.plotly_chart(fig, use_container_width=True)