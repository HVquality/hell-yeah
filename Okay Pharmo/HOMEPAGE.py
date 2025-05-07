import streamlit as st

st.set_page_config(
    page_title="Farmakokinetika Apps",  # Browser tab title
    page_icon="💊",  # Browser tab icon (emoji or image)
)

st.title("Aplikasi Farmakokinetika 💊")  # Main title
st.markdown("""
Selamat datang di simulasi farmakokinetika!

**Navigasi halaman:** Gunakan sidebar di sebelah kiri untuk berpindah antara:
1. **Farmakokinetika IV Bolus**  
2. **Farmakokinetika Pemberian Oral**  
3. **Farmakokinetika Michaelis-Menten**
""")