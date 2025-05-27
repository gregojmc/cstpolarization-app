#
# streamlit run app_cst_linear_to_circular2.py
# Versión 2: acepta mayor número de ficheros de entrada y exporta

import io
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from polarization import leer_cst, calc_AR, plot_S

st.set_page_config(page_title="Linear to Circular Polarization")

st.title("Resultados de CST")
st.subheader("Linear to Circular Polarization")
st.markdown("""
**Instrucciones:**
1. Suba un `.txt`  de CST Studio mediante S-parameters, Export/Plot Data (ASCII):
    - La excitación por un único puerto 
    - Dos modos, con un total de 4 u 8 datos. En este orden: 
    - Zmax(1), Zmin(1)       
    - Zmax(2), Zmin(1)       
    - Zmin(1), Zmin(1)       
    - El resto me da igual, no los usa. 
2. La aplicación plotea:
   - El módulo y fase de S21 y S11
   - El Axial Ratio y la diferencia de fase
3. Al final podrá exportar los resultados 
""")
uploaded_file = st.file_uploader("Deje caer aquí un fichero o pulse Browse files", type=["cst", "txt"])

if uploaded_file is not None:
    try:
        with open("temp.cst", "wb") as f_out:
            f_out.write(uploaded_file.getbuffer())

        f, salida, Info = leer_cst("temp.cst")  # <- ahora retorna f, salida, Info
        S21_VV, S21_HV, S11_VV, S11_HV, S21_VH, S21_HH, S11_VH, S11_HH = salida

        info_line1 = str(Info.get('Parameters', {}).get('name', ''))
        info_line2 = ' '.join(f"{k}={v}" for k, v in Info.get('Parameters', {}).items() if k != 'name')
        info_text = f"{info_line1}\n{info_line2}"
        st.text_area("Info", info_text, height=200)

        st.subheader("Figura 1: Parámetros S (módulo y fase)")
        plot_S(f, S21_VV, S21_HV, S11_VV, labels=['S21_VV', 'S21_HV', 'S11_VV'], suptitle="Parámetros S")
        st.pyplot(plt)

        st.subheader("Figura 2: Axial Ratio y Diferencia de Fase")
        AR, phase_diff = calc_AR(S21_VV, S21_HV)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        ax1.plot(f, 20*log10(AR))
        ax1.set_title("Axial Ratio vs Frecuencia")
        ax1.set_ylabel("Axial Ratio [dBm]")
        ax1.set_ylim(0, 10)
        ax1.grid()
        ax2.plot(f, np.rad2deg(phase_diff))
        ax2.set_xlabel("Frecuencia (GHz)")
        ax2.set_ylabel("Fase (grados)")
        ax2.set_yticks(np.arange(-360, 361, 90))
        ax2.grid()
        plt.tight_layout()
        st.pyplot(fig)
        
        # Exportar datos
        st.subheader("Exportar resultados")
        nombre_usuario = st.text_input("Nombre de fichero", value="export_cst_result")
        # Formatear nombre final con extensión
        nombre_final = f"{nombre_usuario.strip() or 'export_cst_result'}.txt"

        mag_phase = lambda x: (np.abs(x), np.angle(x, deg=True))
        mag_S21_VV, pha_S21_VV = mag_phase(S21_VV)
        mag_S21_HV, pha_S21_HV = mag_phase(S21_HV)
        mag_S11_VV, pha_S11_VV = mag_phase(S11_VV)
        mag_S11_HV, pha_S11_HV = mag_phase(S11_HV)
        deg_phase_diff = np.rad2deg(phase_diff)

        output = io.StringIO()
        output.write(f"%Producido por app_cst_linear_to_circular.py\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"%Fichero de entrada: {uploaded_file.name}\n")
        params_line = ' '.join(f"{k}={v}" for k, v in Info.get('Parameters', {}).items())
        output.write(f"%Parameters: {params_line}\n")
        output.write("%frequency\tS21_VV_mag\tS21_VV_phase\tS21_HV_mag\tS21_HV_phase\tS11_VV_mag\tS11_VV_phase\tS11_HV_mag\tS11_HV_phase\tAR\tphase_diff\n")
        output.write("%-------------------------------------------------------------------------------------------\n")

        for i in range(len(f)):
            fila = [
                f[i],
                mag_S21_VV[i], pha_S21_VV[i],
                mag_S21_HV[i], pha_S21_HV[i],
                mag_S11_VV[i], pha_S11_VV[i],
                mag_S11_HV[i], pha_S11_HV[i],
                AR[i], deg_phase_diff[i]
            ]
            output.write('\t'.join(f"{val:.6g}" for val in fila) + '\n')

        st.download_button(
            label="Exportar",
            data=output.getvalue(),
            file_name=nombre_final, 
            mime="text/plain"
        )
        

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
