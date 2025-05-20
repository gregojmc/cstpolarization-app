# -*- coding: utf-8 -*-
"""
Created on Fri May 16 11:51:12 2025

@author: gregomc
"""
import matplotlib.pyplot as plt
import numpy as np

def calc_tpp_tmm_y(Tyy, Txy):
    """

    """
    tpp_y = (np.sqrt(2) / 2) * (Txy + 1j * Tyy)
    tmm_y = (np.sqrt(2) / 2) * (Txy - 1j * Tyy)
    return tpp_y, tmm_y

def calc_AR(Tyy, Txy):
    """
    """
    phase_diff = np.unwrap(np.angle(Tyy)) - np.unwrap(np.angle(Txy))
    a = np.abs(Tyy)**4 + np.abs(Txy)**4 + 2 * np.abs(Tyy)**2 * np.abs(Txy)**2 * np.cos(2 * phase_diff)
    num = np.abs(Tyy)**2 + np.abs(Txy)**2 + np.sqrt(a)
    den = np.abs(Tyy)**2 + np.abs(Txy)**2 - np.sqrt(a)
    AR = np.sqrt(num / den)
    return AR, phase_diff

def leer_cst(filename):
    """
    Lee un archivo de salida de CST con datos S-parameters complejos y extrae 
    la información en formato usable.
    
    filename: Ruta al archivo .txt exportado desde CST.
    
    Retorna:

    f: Vector de frecuencias (GHz).
    S21_VV, S21_HV, S11_VV, S11_HV, S21_VH, S21_HH, S11_VH, S11_HH: 
        Arreglos complejos con parámetros S.
    Info: Diccionario con los metadatos extraídos del archivo 
        (como dimensiones físicas o etiquetas)
    
    """

    Info = {}
    S = {
        'S21_VV': [], 'S21_HV': [], 'S11_VV': [], 'S11_HV': [],
        'S21_VH': [], 'S21_HH': [], 'S11_VH': [], 'S11_HH': []
    }

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Leer Info
    Info['name'] = lines[0].replace('%', '').split('->')[0].strip()
    param_line = lines[1]
    params_str = param_line.split('{')[1].split('}')[0]
    params = params_str.split(';')
    for p in params:
        key, value = p.strip().split('=')
        try:
            Info[key] = float(value) if '.' in value else int(value)
        except ValueError:
            Info[key] = value

    # Saltar líneas con % y procesar bloques
    block_names = list(S.keys())
    block_index = 0
    current_data = []

    for line in lines[2:]:
        line = line.strip()
        if not line or line.startswith('%'):
            if current_data and block_index < 8:
                arr = np.array(current_data)
                if block_index == 0:
                    f = arr[:, 0]
                magnitude = arr[:, 1]
                phase_deg = arr[:, 2]
                S[block_names[block_index]] = magnitude * np.exp(1j * np.deg2rad(phase_deg))
                current_data = []
                block_index += 1
            continue

        try:
            values = [float(val) for val in line.replace('\t', ' ').split()]
            if len(values) >= 3:
                current_data.append(values)
        except ValueError:
            continue

    # Procesar último bloque si no terminó en %
    if current_data and block_index < 8:
        arr = np.array(current_data)
        if block_index == 0:
            f = arr[:, 0]
        magnitude = arr[:, 1]
        phase_deg = arr[:, 2]
        S[block_names[block_index]] = magnitude * np.exp(1j * np.deg2rad(phase_deg))

    return f, S['S21_VV'], S['S21_HV'], S['S11_VV'], S['S11_HV'], S['S21_VH'], S['S21_HH'], S['S11_VH'], S['S11_HH'], Info

def plot_S(freq, *signals, labels, linestyle='solid', ax1=None, ax2=None):
    """
    Grafica la magnitud y la fase de varios parámetros S sobre la frecuencia.
    Puede reutilizar ejes existentes para añadir más curvas al mismo gráfico.

    Parameters
    ----------
    freq : ndarray
        Vector de frecuencias (en GHz).
    *signals : ndarray
        Cada uno de los parámetros S a graficar (arrays complejos).
    labels : list of str
        Etiquetas correspondientes a cada parámetro.
    linestyle : str, optional
        Estilo de línea para todas las curvas. Por defecto 'solid'.
    ax1, ax2 : matplotlib.axes.Axes, optional
        Ejes existentes para añadir curvas. Si no se dan, se crean nuevos.
        
    ejemplo: 
    # Primer grupo de curvas
    ax1, ax2 = plot_S(f, S21_VV, S21_HV, labels=['S21_VV', 'S21_HV'], linestyle='solid')

    # Segundo grupo de curvas en el mismo gráfico
    plot_S(f, S11_VV, S11_HV, labels=['S11_VV', 'S11_HV'], linestyle='dashed', ax1=ax1, ax2=ax2)    
    """
    if ax1 is None or ax2 is None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        nuevo_plot = True
    else:
        nuevo_plot = False

    for sig, label in zip(signals, labels):
        ax1.plot(freq, np.abs(sig), label=label, linestyle=linestyle)
    ax1.set_ylabel('Magnitud (dB)')
    ax1.set_title('Parámetros S (módulo)')
    ax1.grid(True)
    ax1.set_ylim(0,1)
    ax2.set_xlim(min(freq), max(freq))
    ax1.legend()

    for sig, label in zip(signals, labels):
        ax2.plot(freq, np.unwrap(np.angle(sig, deg=True)), label=label, linestyle=linestyle)
    ax2.set_xlabel('Frecuencia (GHz)')
    ax2.set_ylabel('Fase (°)')
    ax2.set_title('Parámetros S (fase)')
    ax2.grid(True)
    ax2.set_xlim(min(freq), max(freq))
    ax2.legend()

    if nuevo_plot:
        plt.tight_layout()
        plt.show()

    return ax1, ax2

