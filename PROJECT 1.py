import streamlit as st
import math
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Kada-Solver Pro", page_icon="📐", layout="wide")

# Inisialisasi session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'rows' not in st.session_state:
    st.session_state.rows = 1  # Mula dengan 1 baris input

# Fungsi Navigasi
def next_page(): st.session_state.page = 'calculator'
def prev_page(): st.session_state.page = 'home'
def add_row(): st.session_state.rows += 1
def rem_row(): 
    if st.session_state.rows > 1: st.session_state.rows -= 1

# ---------------------------------------------------------
# HALAMAN 1: MUKA HADAPAN (BORANG MAKLUMAT)
# ---------------------------------------------------------
if st.session_state.page == 'home':
    st.markdown("<h1 style='text-align: center;'>📝 MISSING LINE CALCULATION</h1>", unsafe_allow_html=True)
    st.write("---")
    
    with st.container(border=True):
        st.subheader("Sila Isi Maklumat Anda")
        nama_user = st.text_input("Nama Penuh", placeholder="Contoh: ALI")
        matriks_user = st.text_input("No Matriks", placeholder="Contoh: 01DGU22F1001")
        
        senarai_kelas = [f"DGU{i}{j}" for i in range(1,6) for j in ['A','B','C']]
        pilihan_kelas = st.selectbox("Kod Kelas", senarai_kelas)

    if st.button("MULA MENGIRA (NEXT) ➡️", use_container_width=True):
        if nama_user and matriks_user:
            st.session_state.nama_pelajar = nama_user
            st.session_state.kelas_pelajar = pilihan_kelas
            next_page()
            st.rerun()
        else:
            st.warning("⚠️ Sila isi Nama dan No Matriks!")

# ---------------------------------------------------------
# HALAMAN 2: KALKULATOR DENGAN JADUAL LATIT/DIPAT
# ---------------------------------------------------------
elif st.session_state.page == 'calculator':
    st.title(f"🚀 Kalkulator Terabas: {st.session_state.nama_pelajar}")
    st.write("---")

    # BAHAGIAN 1: JADUAL INPUT DINAMIK
    st.subheader("📋 Jadual Data Terabas")
    st.info("💡 Petua: Nilai Latit & Dipat akan muncul secara automatik sebaik sahaja data lengkap diisi.")

    data_list = []
    
    # Header Jadual
    head1, head2, head3, head4, head5, head6, head7 = st.columns([1, 1, 1, 1, 1.5, 1.2, 1.2])
    head1.write("**Stesen**")
    head2.write("**Bering (D)**")
    head3.write("**M(M)**")
    head4.write("**S(S)**")
    head5.write("**Jarak (m)**")
    head6.write("**Latit**")
    head7.write("**Dipat**")

    # Jana Baris Input
    for i in range(st.session_state.rows):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1, 1.5, 1.2, 1.2])
        stn = c1.text_input(f"Stn {i+1}", value=f"{i+1}-{i+2}", key=f"stn_{i}", label_visibility="collapsed")
        
        # Input tanpa default value 0
        d = c2.number_input(f"D_{i}", min_value=0, max_value=360, step=1, value=None, key=f"d_{i}", label_visibility="collapsed")
        m = c3.number_input(f"M_{i}", min_value=0, max_value=60, step=1, value=None, key=f"m_{i}", label_visibility="collapsed")
        s = c4.number_input(f"S_{i}", min_value=0.0, max_value=60.0, step=0.1, value=None, key=f"s_{i}", label_visibility="collapsed")
        dist = c5.number_input(f"Dist_{i}", min_value=0.0, format="%.3f", value=None, key=f"dist_{i}", label_visibility="collapsed")
        
        lat_val = 0.0
        dip_val = 0.0
        
        if d is not None and m is not None and s is not None and dist is not None:
            brg_dec = d + (m/60) + (s/3600)
            lat_val = dist * math.cos(math.radians(brg_dec))
            dip_val = dist * math.sin(math.radians(brg_dec))
            
            c6.code(f"{lat_val:.3f}")
            c7.code(f"{dip_val:.3f}")
            data_list.append({"Stesen": stn, "Latit": lat_val, "Dipat": dip_val})
        else:
            c6.code("0.000")
            c7.code("0.000")
            data_list.append({"Stesen": stn, "Latit": 0.0, "Dipat": 0.0})

    # Butang Kawalan Jadual
    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    col_btn1.button("➕ Tambah Baris", on_click=add_row)
    col_btn2.button("➖ Buang Baris", on_click=rem_row)

    st.write("---")

    # BAHAGIAN 2: PENGIRAAN MISSING LINE
    st.subheader("🔍 Analisis Missing Line")
    po_dist = st.number_input("Masukkan Jarak PO (m) untuk perbandingan:", value=None, format="%.3f")

    if st.button("HITUNG MISSING LINE", type="primary", use_container_width=True):
        if po_dist is None:
            st.warning("⚠️ Masukkan Jarak PO terlebih dahulu.")
        else:
            total_lat = sum(item['Latit'] for item in data_list)
            total_dip = sum(item['Dipat'] for item in data_list)
            
            # Pengiraan NEW Distance & Bearing
            new_dist = math.sqrt(total_lat**2 + total_dip**2)
            brg_rad = math.atan2(-total_dip, -total_lat) # Arah penutup
            brg_deg = math.degrees(brg_rad) % 360
            
            # DMS Conversion
            deg = int(brg_deg)
            min_ = int((brg_deg - deg) * 60)
            sec = round((((brg_deg - deg) * 60) - min_) * 60, 1)
            diff = abs(po_dist - new_dist)

            # 1. Paparan Langkah Pengiraan
            st.subheader("📝 Langkah-Langkah Pengiraan")
            with st.expander("Klik untuk lihat jalan kerja Matematik", expanded=True):
                st.latex(r"\sum \text{Latit} = " + f"{total_lat:.3f}")
                st.latex(r"\sum \text{Dipat} = " + f"{total_dip:.3f}")
                
                st.markdown("**1. Mencari Jarak Baru (New Distance):**")
                st.latex(r"\text{Jarak} = \sqrt{(\sum L)^2 + (\sum D)^2}")
                # Penggunaan double curly braces {{ }} untuk mengelakkan ralat syntax f-string
                formula_jarak = rf"\text{{Jarak}} = \sqrt{{({total_lat:.3f})^2 + ({total_dip:.3f})^2}} = {new_dist:.3f}\text{{ m}}"
                st.latex(formula_jarak)
                
                st.markdown("**2. Mencari Bering Baru (New Bearing):**")
                st.latex(r"\theta = \tan^{-1}\left(\frac{-\sum D}{-\sum L}\right)")
                formula_bering = rf"\theta = \tan^{{-1}}\left(\frac{{{-total_dip:.3f}}}{{{-total_lat:.3f}}}\right) = {brg_deg:.3f}^\circ"
                st.latex(formula_bering)
                st.info(f"Tukaran DMS: {deg}° {min_}' {sec}\"")

            # 2. Ringkasan Akhir
            st.write("---")
            st.subheader("📊 Keputusan Akhir")
            res1, res2, res3 = st.columns(3)
            res1.metric("Bering NEW", f"{deg}° {min_}' {sec}\"")
            res2.metric("Jarak NEW", f"{new_dist:.3f} m")
            res3.metric("Beza (Tikaian)", f"{diff:.4f} m")

            if diff <= 0.05:
                st.balloons()
                st.success(f"✅ STATUS: LULUS (Tikaian: {diff:.4f}m)")
            else:
                st.error(f"❌ STATUS: GAGAL (Tikaian melebihi 0.05m)")

    if st.button("⬅️ KEMBALI KE BORANG"):
        prev_page()
        st.rerun()