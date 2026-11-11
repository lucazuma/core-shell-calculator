import streamlit as st
import numpy as np

st.set_page_config(page_title="Core-Shell Calculator", layout="centered")

st.title("🔬 Analizzatore Tetraedro Troncato Core-Shell")
st.write("Modello geometrico basato su $V = 0.618 \\cdot h^3$ e $S = 2.45 \\cdot h^2$ (Modello di Jordi).")

# Database materiali
materials_data = {
    'InAs': {'cell_vol_nm3': 0.22123, 'anion': 'As'},
    'ZnSe': {'cell_vol_nm3': 0.18300, 'ml_thickness_nm': 0.401, 'anion': 'Se'},
    'ZnTe': {'cell_vol_nm3': 0.22765, 'ml_thickness_nm': 0.432, 'anion': 'Te'},
    'ZnS': {'cell_vol_nm3': 0.16046, 'ml_thickness_nm': 0.384, 'anion': 'S'},
    'InP': {'cell_vol_nm3': 0.20216, 'ml_thickness_nm': 0.415, 'anion': 'P'}
}

# Definizione dei sistemi
systems = {
    "InAs@ZnSe": {"type": "single", "shell": 'ZnSe'},
    "InAs@ZnS": {"type": "single", "shell": 'ZnS'},
    "InAs@ZnTe": {"type": "single", "shell": 'ZnTe'},
    "InAs@InP": {"type": "single", "shell": 'InP'},
    "InAs@ZnTe@ZnSe": {"type": "multi", "shell1": 'ZnTe', "shell2": 'ZnSe'},
    "InAs@ZnSe@ZnS": {"type": "multi", "shell1": 'ZnSe', "shell2": 'ZnS'},
    "InAs@InP@ZnSe": {"type": "multi", "shell1": 'InP', "shell2": 'ZnSe'}
}

system_choice = st.selectbox("Seleziona il tipo di cristallo:", list(systems.keys()))
core_h = st.number_input("Altezza del core di InAs (nm):", min_value=0.5, max_value=20.0, value=3.0, step=0.1)

# Calcoli geometrici del Core
vol_core = 0.618 * (core_h ** 3)
as_atoms = (vol_core / materials_data['InAs']['cell_vol_nm3']) * 4.0
surface_area_core = 2.45 * (core_h ** 2)

st.markdown("---")
st.subheader("📊 Dati Core InAs")
col1, col2, col3 = st.columns(3)
col1.metric("Volume Core", f"{vol_core:.3f} nm³")
col2.metric("Area Superficiale Core", f"{surface_area_core:.3f} nm²")
col3.metric("Atomi di As (e In)", f"{as_atoms:.1f}")
st.markdown("---")

sys_info = systems[system_choice]

# CASO 1: Single Shell (es. InAs@ZnSe)
if sys_info["type"] == "single":
    shell_mat = sys_info["shell"]
    info = materials_data[shell_mat]
    ml_thick = info['ml_thickness_nm']
    cell_vol = info['cell_vol_nm3']
    anion = info['anion']
    
    st.subheader(f"Analisi Monolayer Shell ({shell_mat}, fino a 10 ML)")
    
    table_data = []
    for ml in range(1, 11):
        total_h_ml = core_h + (2 * ml * ml_thick)
        total_vol_ml = 0.618 * (total_h_ml ** 3)
        exact_shell_vol = total_vol_ml - vol_core
        total_surface_ml = 2.45 * (total_h_ml ** 2)
        anion_atoms = (exact_shell_vol / cell_vol) * 4.0
        ratio = anion_atoms / as_atoms
        
        table_data.append({
            "ML": ml,
            "Altezza NC (nm)": round(total_h_ml, 3),
            "Vol. Shell (nm³)": round(exact_shell_vol, 3),
            "Area Totale (nm²)": round(total_surface_ml, 3),
            f"Atomi {anion}": round(anion_atoms, 1),
            f"Rapporto {anion}/As": round(ratio, 3)
        })
    
    st.table(table_data)

# CASO 2: Multi Shell (es. InAs@ZnSe@ZnS o InAs@ZnTe@ZnSe)
elif sys_info["type"] == "multi":
    shell1_mat = sys_info["shell1"]
    shell2_mat = sys_info["shell2"]
    
    info1 = materials_data[shell1_mat]
    info2 = materials_data[shell2_mat]
    
    st.subheader(f"1° Strato Shell: {shell1_mat} (fino a 10 ML)")
    
    table_data_1 = []
    for ml1 in range(1, 11):
        h1 = core_h + (2 * ml1 * info1['ml_thickness_nm'])
        v1 = 0.618 * (h1 ** 3) - vol_core
        s1 = 2.45 * (h1 ** 2)
        atoms1 = (v1 / info1['cell_vol_nm3']) * 4.0
        ratio1 = atoms1 / as_atoms
        
        table_data_1.append({
            "ML 1° Shell": ml1,
            "Altezza NC (nm)": round(h1, 3),
            "Vol. 1° Shell (nm³)": round(v1, 3),
            "Area Totale (nm²)": round(s1, 3),
            f"Atomi {info1['anion']}": round(atoms1, 1),
            f"Rapporto {info1['anion']}/As": round(ratio1, 3)
        })
    st.table(table_data_1)
    
    st.markdown("---")
    ml1_fixed = st.slider(f"Seleziona i ML fissi del 1° strato ({shell1_mat}) per calcolare il 2° strato:", min_value=1, max_value=10, value=2)
    
    # Altezza e volume dopo il 1° strato fissato
    h_after_1 = core_h + (2 * ml1_fixed * info1['ml_thickness_nm'])
    vol_after_1 = 0.618 * (h_after_1 ** 3)
    
    st.subheader(f"2° Strato Shell: {shell2_mat} (con {ml1_fixed} ML di {shell1_mat}, fino a 5 ML)")
    
    table_data_2 = []
    for ml2 in range(1, 6):
        h2 = h_after_1 + (2 * ml2 * info2['ml_thickness_nm'])
        v_total = 0.618 * (h2 ** 3)
        v_shell2 = v_total - vol_after_1
        s2 = 2.45 * (h2 ** 2)
        atoms2 = (v_shell2 / info2['cell_vol_nm3']) * 4.0
        ratio2 = atoms2 / as_atoms
        
        table_data_2.append({
            "ML 2° Shell": ml2,
            "Altezza Tot (nm)": round(h2, 3),
            "Vol. 2° Shell (nm³)": round(v_shell2, 3),
            "Area Totale (nm²)": round(s2, 3),
            f"Atomi {info2['anion']} (2° Shell)": round(atoms2, 1),
            f"Rapporto {info2['anion']}/As": round(ratio2, 3)
        })
    st.table(table_data_2)
