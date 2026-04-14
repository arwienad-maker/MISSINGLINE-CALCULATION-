import streamlit as st
import math
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Kada-Solver Pro", page_icon="📐", layout="wide")

# Inisialisasi session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'rows' not in st.session_state:
    st.session_state.rows = 2 

def next_page(): st.session_state.page = 'calculator'
def prev_page(): st.session_state.page = 'home'
def add_row(): st.session_state.rows += 1
def rem_row(): 
    if st.session_state.rows > 1: st.session_state.rows -= 1

# ---------------------------------------------------------
# HALAMAN 1: MUKA HADAPAN
# ---------------------------------------------------------
if st.session_state.page == 'home':
    st.markdown("<h1 style='text-align: center;'>📝 MISSING LINE CALCULATION</h1>", unsafe_allow_html=True)
    st.write("---")
    
    with st.container(border=True):
        st.subheader("Sila Isi Maklumat Anda")
        nama_user = st.text_input("Nama Penuh", placeholder="Contoh: ARWIE")
        matriks_user = st.text_input("No Matriks", placeholder="Contoh: 01DGU22F1001")
        pilihan_kelas = st.selectbox("Kod Kelas", ["DGU1A", "DGU1B", "DGU2A", "DGU2B"])

    if st.button("MULA MENGIRA (NEXT) ➡️", use_container_width=True):
        if nama_user and matriks_user:
            st.session_state.nama_pelajar = nama_user
            next_page()
            st.rerun()
        else:
            st.warning("⚠️ Sila isi maklumat!")

# ---------------------------------------------------------
# HALAMAN 2: KALKULATOR (SUSUNAN KEMAS)
# ---------------------------------------------------------
elif st.session_state.page == 'calculator':
    st.title(f"🚀 Kalkulator: {st.session_state.nama_pelajar}")
    st.write("---")

    st.subheader("📋 Jadual Data Terabas")
    
    data_list = []

    # Kita jana kotak input mengikut stesen
    for i in range(st.session_state.rows):
        with st.container(border=True):
            st.markdown(f"**📍 STESEN {i+1}**")
            
            # Baris 1: Nama Stesen & Jarak
            col_a, col_b = st.columns(2)
            stn = col_a.text_input("Label Stesen", value=f"{i+1}-{i+2}", key=f"stn_{i}")
            dist = col_b.number_input("Jarak (m)", min_value=0.0, format="%.3f", key=f"dist_{i}")
            
            # Baris 2: Bering (D, M, S)
            st.markdown("*Bering (DMS)*")
            c1, c2, c3 = st.columns(3)
            d = c1.number_input("D", min_value=0, max_value=360, step=1, key=f"d_{i}")
            m = c2.number_input("M", min_value=0, max_value=60, step=1, key=f"m_{i}")
            s = c3.number_input("S", min_value=0.0, max_value=60.0, step=0.1, key=f"s_{i}")
            
            # Pengiraan Latit/Dipat Terus
            brg_dec = d + (m/60) + (s/3600)
            lat_val = dist * math.cos(math.radians(brg_dec))
            dip_val = dist * math.sin(math.radians(brg_dec))
            
            # Paparan kecil Latit & Dipat untuk setiap stesen
            st.caption(f"Hasil: Latit = {lat_val:.3f} | Dipat = {dip_val:.3f}")
            data_list.append({"Stesen": stn, "Latit": lat_val, "Dipat": dip_val})

    # Butang Kawalan
    c_btn1, c_btn2 = st.columns(2)
    c_btn1.button("➕ Tambah Baris", on_click=add_row, use_container_width=True)
    c_btn2.button("➖ Buang Baris", on_click=rem_row, use_container_width=True)

    st.write("---")

    # BAHAGIAN MISSING LINE
    st.subheader("🔍 Analisis Missing Line")
    po_dist = st.number_input("Masukkan Jarak PO (m):", value=None, format="%.3f")

    if st.button("HITUNG MISSING LINE", type="primary", use_container_width=True):
        if po_dist:
            total_lat = sum(item['Latit'] for item in data_list)
            total_dip = sum(item['Dipat'] for item in data_list)
            
            new_dist = math.sqrt(total_lat**2 + total_dip**2)
            brg_rad = math.atan2(-total_dip, -total_lat)
            brg_deg = math.degrees(brg_rad) % 360
            
            deg = int(brg_deg)
            min_ = int((brg_deg - deg) * 60)
            sec = round((((brg_deg - deg) * 60) - min_) * 60, 1)
            diff = abs(po_dist - new_dist)

            with st.expander("📝 Langkah Pengiraan", expanded=True):
                st.latex(rf"\text{{Jarak NEW}} = {new_dist:.3f}m")
                st.latex(rf"\text{{Bering NEW}} = {deg}^\circ {min_}' {sec}''")
            
            st.metric("Tikaian", f"{diff:.4f} m")
            if diff <= 0.05:
                st.success("✅ LULUS")
            else:
                st.error("❌ GAGAL")

    if st.button("⬅️ KEMBALI"):
        prev_page()
        st.rerun()