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
    Lee un fichero CST en texto plano y devuelve siempre:
      - f: array de frecuencias (GHz)
      - S21_VV, S21_HV, S11_VV, S11_HV,
        S21_VH, S21_HH, S11_VH, S11_HH: arrays complejos
      - Info: dict con 'Parameters' = {...}
    """
    Info = {}
    bloques = []
    f = None

    with open(filename, 'r') as fid:
        lines = fid.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detectar inicio de bloque
        if 'Parameters' in line:
            # Extraer parámetros solo una vez
            if 'Parameters' not in Info:
                params_str = line.split('{',1)[1].rsplit('}',1)[0]
                Info['Parameters'] = {
                    k: float(v) if ('.' in v or 'e' in v.lower()) else int(v)
                    for item in params_str.split(';')
                    for k, v in [item.strip().split('=')]
                }
            # Saltar 3 líneas de cabecera
            i += 3
            data = []
            while i < len(lines):
                line = lines[i].strip()
                if not line or 'Parameters' in line:
                    break  # fin de bloque
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        nums = [float(parts[0]), float(parts[1]), float(parts[2])]
                        data.append(nums)
                    except ValueError:
                        pass
                i += 1
            if data:
                arr = np.array(data)
                if f is None:
                    f = arr[:, 0]
                mag = arr[:, 1]
                pha = arr[:, 2]
                bloques.append(mag * np.exp(1j * np.deg2rad(pha)))
            continue
        i += 1

    # Rellenar hasta 8 bloques
    salida = []
    for idx in range(8):
        if idx < len(bloques):
            salida.append(bloques[idx])
        else:
            salida.append(np.full_like(f, np.nan) + 1j * np.full_like(f, np.nan))

    return f, salida, Info

def plot_S(freq, *signals, labels, linestyle='solid', ax1=None, ax2=None, suptitle=None):
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
    suptitle : str, optional
        Título general del gráfico.
        
    Returns
    -------
    ax1, ax2 : ejes de matplotlib
    """
    if ax1 is None or ax2 is None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        nuevo_plot = True
    else:
        fig = ax1.figure
        nuevo_plot = False

    for sig, label in zip(signals, labels):
        ax1.plot(freq, np.abs(sig), label=label, linestyle=linestyle)
    ax1.set_ylabel('Magnitud (dB)')
    ax1.set_title('Parámetros S (módulo)')
    ax1.grid(True)
    ax1.set_ylim(0, 1)
    ax1.legend()

    for sig, label in zip(signals, labels):
        ax2.plot(freq, np.unwrap(np.angle(sig, deg=True)), label=label, linestyle=linestyle)
    ax2.set_xlabel('Frecuencia (GHz)')
    ax2.set_ylabel('Fase (°)')
    ax2.set_title('Parámetros S (fase)')
    ax2.grid(True)
    ax2.set_xlim(min(freq), max(freq))
    ax2.legend()

    if suptitle:
        fig.suptitle(suptitle, fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
    elif nuevo_plot:
        plt.tight_layout()
        plt.show()

    return ax1, ax2
