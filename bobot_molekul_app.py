import re
import math
from collections import defaultdict

import pandas as pd
import streamlit as st

# -------------------------
# Data massa atom (g/mol)
# -------------------------
# Nilai relatif (standar IUPAC); cukup untuk kebutuhan kalkulator edukasi.
ATOMIC_MASS = {
    # 1
    "H": 1.008,
    "He": 4.0026,
    # 2
    "Li": 6.94,
    "Be": 9.0122,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Ne": 20.1797,
    # 3
    "Na": 22.9897,
    "Mg": 24.305,
    "Al": 26.9815,
    "Si": 28.085,
    "P": 30.9738,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.948,
    # 4
    "K": 39.0983,
    "Ca": 40.078,
    "Sc": 44.9559,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938,
    "Fe": 55.845,
    "Co": 58.9332,
    "Ni": 58.6934,
    "Cu": 63.546,
    "Zn": 65.38,
    # 5
    "Ga": 69.723,
    "Ge": 72.64,
    "As": 74.9216,
    "Se": 78.96,
    "Br": 79.904,
    "Kr": 83.798,
    # 6
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.9059,
    "Zr": 91.224,
    "Nb": 92.9064,
    "Mo": 95.96,
    "Tc": 98.0,
    "Ru": 101.07,
    "Rh": 102.9055,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.411,
    # 7
    "In": 114.818,
    "Sn": 118.71,
    "Sb": 121.76,
    "Te": 127.6,
    "I": 126.90447,
    "Xe": 131.293,
    # 8
    "Cs": 132.90545,
    "Ba": 137.327,
    "La": 138.90547,
    "Ce": 140.116,
    "Pr": 140.90765,
    "Nd": 144.242,
    "Pm": 145.0,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.92535,
    "Dy": 162.5,
    "Ho": 164.93033,
    "Er": 167.259,
    "Tm": 168.93422,
    "Yb": 173.054,
    "Lu": 174.9668,
    # 9
    "Hf": 178.49,
    "Ta": 180.94788,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.084,
    "Au": 196.96657,
    "Hg": 200.59,
    # 10
    "Tl": 204.38,
    "Pb": 207.2,
    "Bi": 208.9804,
    "Po": 209.0,
    "At": 210.0,
    "Rn": 222.0,
    # 11
    "Fr": 223.0,
    "Ra": 226.0,
    "Ac": 227.0,
    "Th": 232.03806,
    "Pa": 231.03588,
    "U": 238.02891,
    # 12 (opsional beberapa lagi agar input sering terpakai)
    "Np": 237.0,
    "Pu": 244.0,
    "Am": 243.0,
    "Cm": 247.0,
    "Bk": 247.0,
    "Cf": 251.0,
    "Es": 252.0,
    "Fm": 257.0,
    "Md": 258.0,
    "No": 259.0,
    "Lr": 262.0,
}

# -------------------------
# Parser rumus kimia
# -------------------------
# Mendukung:
# - elemen: H, He, Na, Cl, ...
# - angka multiplikator: H2, O3
# - tanda kurung: Ca(OH)2 (ditangani sederhana untuk ()
# - tidak mendukung dot hydration: CuSO4·5H2O (bisa ditambah jika perlu)

TOKEN_RE = re.compile(r"([A-Z][a-z]?|\(|\)|\d+|\.|·)")


def _normalize_formula(formula: str) -> str:
    # Tangani format hidrasi: Na2B4O7.10H2O atau CuSO4·5H2O
    # Parser utama belum mendukung 'tambah' (+), jadi kita ubah jadi "Na2B4O7" dan "10H2O"
    # dengan membuat tanda '.' sebagai pemisah komponen.
    formula = formula.strip().replace(" ", "")
    # Samakan dot hydration
    formula = formula.replace("·", ".")
    return formula




def _parse_tokens(formula: str):
    tokens = TOKEN_RE.findall(formula)
    if not tokens:
        raise ValueError("Rumus tidak dapat diparse. Pastikan format benar, mis. H2O atau Ca(OH)2")
    return tokens


def parse_formula(formula: str) -> dict[str, int]:
    formula = _normalize_formula(formula)
    formula = formula.strip().replace(" ", "")
    if not formula:
        raise ValueError("Rumus kosong")

    # Dot-hydrate: mis. Na2B4O7.10H2O atau CuSO4·5H2O
    # Interpretasi: (bagian sebelum dot) + (angka setelah dot) * (bagian setelah dot)
    # Contoh: Na2B4O7.10H2O -> parse(Na2B4O7) + 10*parse(H2O)
    if "." in formula:
        parts = formula.split(".")
        if len(parts) == 2 and parts[1]:
            m = re.match(r"^(\d+)(.*)$", parts[1])
            if m:
                mult = int(m.group(1))
                rest = m.group(2)
                base_counts = parse_formula(parts[0])
                hydrate_counts = parse_formula(rest)
                merged: defaultdict[str, int] = defaultdict(int)
                for el, cnt in base_counts.items():
                    merged[el] += cnt
                for el, cnt in hydrate_counts.items():
                    merged[el] += cnt * mult
                return dict(merged)

    tokens = _parse_tokens(formula)
    stack: list[defaultdict[str, int]] = [defaultdict(int)]


    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append(defaultdict(int))
            i += 1
        elif tok == ")":
            if len(stack) == 1:
                raise ValueError("Kurung ')" "'" " tidak memiliki pasangan '('")
            group_counts = stack.pop()

            # cek angka setelah ')'
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1

            for el, cnt in group_counts.items():
                stack[-1][el] += cnt * mult
            i += 1
        elif tok.isdigit():
            raise ValueError("Angka tanpa elemen/kurung sebelumya")
        else:
            # token elemen
            el = tok
            if el not in ATOMIC_MASS:
                raise ValueError(f"Unsur tidak dikenal: {el}")

            cnt = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                cnt = int(tokens[i + 1])
                i += 1

            stack[-1][el] += cnt
            i += 1

    if len(stack) != 1:
        raise ValueError("Kurung '(' tidak ditutup")

    return dict(stack[0])


def calculate_molar_mass(counts: dict[str, int]) -> float:
    total = 0.0
    for el, cnt in counts.items():
        total += ATOMIC_MASS[el] * cnt
    return total


# -------------------------
# UI Streamlit
# -------------------------
st.set_page_config(page_title="Kalkulator Bobot Molekul", layout="wide")

st.title("🧪 Kalkulator Bobot Molekul (Mr) dari Rumus Kimia")
st.caption("Masukkan rumus kimia seperti: H2O, CO2, NaCl, Ca(OH)2. Mendukung tanda kurung ().")

formula = st.text_input("Rumus kimia", value="Ca(OH)2", help="Gunakan format huruf besar-kecil (mis. Na, Cl) dan angka untuk jumlah atom.")

col1, col2 = st.columns(2)
with col1:
    enable_table = st.checkbox("Tampilkan tabel komposisi", value=True)
with col2:
    decimals = st.slider("Jumlah desimal", min_value=2, max_value=6, value=4)

if st.button("Hitung", type="primary"):
    try:
        counts = parse_formula(formula)
        total_mr = calculate_molar_mass(counts)

        # Tampilkan hasil
        st.subheader(f"Hasil: Mr({formula}) = {total_mr:.{decimals}f} g/mol")

        details = []
        for el in sorted(counts.keys(), key=lambda x: (x != "", x)):
            cnt = counts[el]
            mr_el = ATOMIC_MASS[el] * cnt
            details.append({
                "Unsur": el,
                "Jumlah atom": cnt,
                "Mr atom (g/mol)": ATOMIC_MASS[el],
                "Kontribusi (g/mol)": mr_el,
            })

        df = pd.DataFrame(details)

        if enable_table:
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.caption("Catatan: Mr dihitung dari massa atom relatif (g/mol) standar. Nilai di dataset dapat berbeda sedikit tergantung sumber.")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.markdown(
    "**Contoh input**: `H2O`, `CO2`, `CH3COOH`, `NaCl`, `Ca(OH)2`\n"
    "Jika rumus mengandung simbol `·` (dot) seperti `CuSO4·5H2O`, perlu fitur parsing tambahan." 
)

