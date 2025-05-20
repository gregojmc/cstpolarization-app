# -*- coding: utf-8 -*-
"""
Created on Fri May 16 17:41:16 2025

@author: gregomc
streamlit run app_polarization.py
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from polarization import leer_cst, calc_AR, plot_S

st.set_page_config(page_title="Linear to Circular Polarization")

st.title("Resultados de CST")
st.subheader("Linear to Circular Polarization")

uploaded_file = st.file_uploader("Deje caer aquí un fichero o pulse Browse files", type=["cst", "txt"])

if uploaded_file is not None:
    # Leer contenido CST
    with open("temp.cst", "wb") as f:
        f.write(uploaded_file.getbuffer())

    f, S21_VV, S21_HV, S11_VV, *_ , Info = leer_cst("temp.cst")
    # Mostrar Info
    info_line1 = str(Info.get('name', ''))
    info_line2 = ' '.join(f"{k}={v}" for k, v in Info.items() if k != 'name')
    info_text = f"{info_line1}\n{info_line2}"
    st.text_area("Info", info_text, height=100)

    # Figura 1: plot_S
    st.subheader("Figura 1: Parámetros S (módulo y fase)")
    plot_S(f, S21_VV, S21_HV, S11_VV, labels=['S21_VV', 'S21_HV', 'S11_VV'])
    st.pyplot(plt)

    # Figura 2: Axial Ratio y Phase Diff
    st.subheader("Figura 2: Axial Ratio y Diferencia de Fase")
    AR, phase_diff = calc_AR(S21_VV, S21_HV)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(f, AR)
    ax1.set_title("Axial Ratio vs Frecuencia")
    ax1.set_ylabel("Axial Ratio")
    ax1.set_ylim(0, 10)
    ax1.grid()
    ax2.plot(f, np.rad2deg(phase_diff))
    ax2.set_xlabel("Frecuencia (GHz)")
    ax2.set_ylabel("Fase (grados)")
    ax2.set_yticks(np.arange(-360, 361, 90))
    ax2.grid()
    plt.tight_layout()
    st.pyplot(fig)
    