import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Judul
st.title("Model Farmakokinetik Orde Pertama (Pemberian Oral)")

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

# Parameter absorpsi
t_half_abs = st.sidebar.number_input("Waktu Paruh Absorpsi (t₁/₂,abs, jam)",
                                     min_value=0.1, max_value=100.0, value=0.5, step=0.1)
ka = np.log(2) / t_half_abs
F = st.sidebar.number_input("Bioavailabilitas (F)",
                            min_value=0.0, max_value=1.0, value=1.0, step=0.1)

# Parameter eliminasi
t_half_elim = st.sidebar.number_input("Waktu Paruh Eliminasi (t₁/₂,elim, jam)",
                                      min_value=0.1, max_value=100.0, value=6.0, step=0.1)
k = np.log(2) / t_half_elim

# Toggle dosis berulang
is_repeated = st.sidebar.checkbox("Aktifkan pemberian dosis berulang", value=True)

# Interval pemberian hanya jika berulang
if is_repeated:
    tau = st.sidebar.slider("Interval pemberian dosis (τ, jam)", 1, 24, 5)
else:
    tau = None

# Berat badan → Vd
weight_kg = st.sidebar.number_input("Berat badan (kg)", 30.0, 150.0, 70.0, step=1.0)
Vd = weight_kg * 0.8  # L

# Rentang waktu (t_end)
t_end_input = st.sidebar.text_input("Rentang waktu (jam)", value="48.0")
try:
    t_end = float(t_end_input)
except ValueError:
    t_end = 48.0

# Dosis (D)
D = st.sidebar.slider("Dosis (D)", min_value=dose_min, max_value=dose_max,
                      value=500.0, step=1.0, format="%.1f")

# Batas sumbu y
y_max_input = st.sidebar.text_input("Atur nilai maksimum sumbu y", value="25.0")
try:
    y_max = float(y_max_input)
except ValueError:
    y_max = 70.0

# Toggle garis steady-state
show_ss_lines = st.sidebar.checkbox("Tampilkan garis steady-state", value=True)

# Array waktu
t = np.linspace(0, t_end, 1000)

# Perhitungan konsentrasi
if ka == k:
    st.warning("Konstanta laju absorpsi dan eliminasi sama. Hasil mungkin tidak stabil.")

if is_repeated:
    C = np.zeros_like(t)
    for n in range(int(t_end // tau) + 1):
        dose_time = n * tau
        valid_times = t >= dose_time
        t_since_dose = t[valid_times] - dose_time
        if ka != k:
            term = (F * D * ka) / (Vd * (ka - k)) * \
                   (np.exp(-k * t_since_dose) - np.exp(-ka * t_since_dose))
        else:
            # Penanganan ketika ka = k menggunakan aturan l'Hôpital
            term = (F * D * ka * t_since_dose * np.exp(-ka * t_since_dose)) / Vd
        C[valid_times] += term

    # Hitung metrik steady-state dari interval terakhir
    if tau > 0:
        last_dose = int(t_end // tau) * tau
        mask = (t >= last_dose - tau) & (t <= last_dose)
        if any(mask):
            C_last = C[mask]
            C_ss_max = np.max(C_last)
            C_ss_min = np.min(C_last)
        else:
            C_ss_max = C_ss_min = 0
    else:
        C_ss_max = C_ss_min = 0
else:
    # Dosis tunggal
    if ka != k:
        C = (F * D * ka) / (Vd * (ka - k)) * \
            (np.exp(-k * t) - np.exp(-ka * t))
    else:
        C = (F * D * ka * t * np.exp(-ka * t)) / Vd
    C_ss_max = C_ss_min = 0

# Tampilkan metrik jika berulang
if is_repeated:
    st.subheader("📊 Metrik Steady-State")
    col1, col2 = st.columns(2)
    col1.metric("C_ss,maks (Puncak)", f"{C_ss_max:.2f}")
    col2.metric("C_ss,min (Palung)", f"{C_ss_min:.2f}")

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=C, mode='lines', name='Konsentrasi Obat'))

# Tambahkan garis steady-state jika diaktifkan
if is_repeated and show_ss_lines:
    fig.add_trace(go.Scatter(x=[0, t_end], y=[C_ss_max, C_ss_max],
                             mode='lines', name='C_ss,maks',
                             line=dict(dash='dash', color='green')))  # Tetap dalam bahasa Inggris
    fig.add_trace(go.Scatter(x=[0, t_end], y=[C_ss_min, C_ss_min],
                             mode='lines', name='C_ss,min',
                             line=dict(dash='dash', color='red')))    # Tetap dalam bahasa Inggris

# Konfigurasi layout
fig.update_layout(
    title='Farmakokinetik Pemberian Oral',
    xaxis_title='Waktu (jam)',
    yaxis_title='Konsentrasi',
    xaxis=dict(range=[0, t_end]),
    yaxis=dict(range=[0, y_max]),
    hovermode='x unified'
)

# Tampilkan plot
st.plotly_chart(fig, use_container_width=True)