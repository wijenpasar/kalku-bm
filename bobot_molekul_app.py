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
# Periodic table (full grid) - dataset posisi
# -------------------------
# Grup memakai penomoran IUPAC 1..18.
# Blok: s / p / d / f
PERIODIC_META = {
    # Period 1
    "H": (1, 1, "s"),
    "He": (1, 18, "s"),

    # Period 2
    "Li": (2, 1, "s"),
    "Be": (2, 2, "s"),
    "B": (2, 13, "p"),
    "C": (2, 14, "p"),
    "N": (2, 15, "p"),
    "O": (2, 16, "p"),
    "F": (2, 17, "p"),
    "Ne": (2, 18, "p"),

    # Period 3
    "Na": (3, 1, "s"),
    "Mg": (3, 2, "s"),
    "Al": (3, 13, "p"),
    "Si": (3, 14, "p"),
    "P": (3, 15, "p"),
    "S": (3, 16, "p"),
    "Cl": (3, 17, "p"),
    "Ar": (3, 18, "p"),

    # Period 4
    "K": (4, 1, "s"),
    "Ca": (4, 2, "s"),
    "Sc": (4, 3, "d"),
    "Ti": (4, 4, "d"),
    "V": (4, 5, "d"),
    "Cr": (4, 6, "d"),
    "Mn": (4, 7, "d"),
    "Fe": (4, 8, "d"),
    "Co": (4, 9, "d"),
    "Ni": (4, 10, "d"),
    "Cu": (4, 11, "d"),
    "Zn": (4, 12, "d"),
    "Ga": (4, 13, "p"),
    "Ge": (4, 14, "p"),
    "As": (4, 15, "p"),
    "Se": (4, 16, "p"),
    "Br": (4, 17, "p"),
    "Kr": (4, 18, "p"),

    # Period 5
    "Rb": (5, 1, "s"),
    "Sr": (5, 2, "s"),
    "Y": (5, 3, "d"),
    "Zr": (5, 4, "d"),
    "Nb": (5, 5, "d"),
    "Mo": (5, 6, "d"),
    "Tc": (5, 7, "d"),
    "Ru": (5, 8, "d"),
    "Rh": (5, 9, "d"),
    "Pd": (5, 10, "d"),
    "Ag": (5, 11, "d"),
    "Cd": (5, 12, "d"),
    "In": (5, 13, "p"),
    "Sn": (5, 14, "p"),
    "Sb": (5, 15, "p"),
    "Te": (5, 16, "p"),
    "I": (5, 17, "p"),
    "Xe": (5, 18, "p"),

    # Period 6
    "Cs": (6, 1, "s"),
    "Ba": (6, 2, "s"),
    "La": (6, 3, "d"),
    # Lanthanides (deret)
    "Ce": (6, 4, "f"),
    "Pr": (6, 5, "f"),
    "Nd": (6, 6, "f"),
    "Pm": (6, 7, "f"),
    "Sm": (6, 8, "f"),
    "Eu": (6, 9, "f"),
    "Gd": (6, 10, "f"),
    "Tb": (6, 11, "f"),
    "Dy": (6, 12, "f"),
    "Ho": (6, 13, "f"),
    "Er": (6, 14, "f"),
    "Tm": (6, 15, "f"),
    "Yb": (6, 16, "f"),
    "Lu": (6, 17, "f"),

    "Hf": (6, 4, "d"),
    "Ta": (6, 5, "d"),
    "W": (6, 6, "d"),
    "Re": (6, 7, "d"),
    "Os": (6, 8, "d"),
    "Ir": (6, 9, "d"),
    "Pt": (6, 10, "d"),
    "Au": (6, 11, "d"),
    "Hg": (6, 12, "d"),
    "Tl": (6, 13, "p"),
    "Pb": (6, 14, "p"),
    "Bi": (6, 15, "p"),
    "Po": (6, 16, "p"),
    "At": (6, 17, "p"),
    "Rn": (6, 18, "p"),

    # Period 7
    "Fr": (7, 1, "s"),
    "Ra": (7, 2, "s"),
    "Ac": (7, 3, "d"),
    # Actinides (deret)
    "Th": (7, 4, "f"),
    "Pa": (7, 5, "f"),
    "U": (7, 6, "f"),
    "Np": (7, 7, "f"),
    "Pu": (7, 8, "f"),
    "Am": (7, 9, "f"),
    "Cm": (7, 10, "f"),
    "Bk": (7, 11, "f"),
    "Cf": (7, 12, "f"),
    "Es": (7, 13, "f"),
    "Fm": (7, 14, "f"),
    "Md": (7, 15, "f"),
    "No": (7, 16, "f"),
    "Lr": (7, 17, "f"),
}

# -------------------------
# Parser rumus kimia
# -------------------------
TOKEN_RE = re.compile(r"([A-Z][a-z]?|\(|\)|\d+|\.|·)")


def _normalize_formula(formula: str) -> str:
    formula = formula.strip().replace(" ", "")
    return formula.replace("·", ".")


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

    # Dot-hydrate: mis. Na2B4O7.10H2O atau CuSO4·5H2O (diubah jadi dot '.')
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
                raise ValueError("Kurung ')' tidak memiliki pasangan '('")
            group_counts = stack.pop()

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

st.title("🧪 Kalkulator Bobot Molekul dan Bobot Ekuivalen (Mr) dari Rumus Kimia")
st.caption("Masukkan rumus kimia seperti: H2O, CO2, NaCl, Ca(OH)2. Mendukung tanda kurung ().")

# Sidebar menu (Beranda / Kalkulator / Tabel Periodik)
menu = st.sidebar.radio(
    "Menu",
    options=["Beranda", "Kalkulator", "Tabel Periodik"],
    index=0,
)

if menu == "Beranda":
    # --- Hero dekoratif + unsur kimia ---
    st.markdown(
        """
        <style>
        .beranda-wrap{position:relative; padding: 18px 16px; border-radius: 18px; overflow:hidden;}
        .beranda-wrap:before{
            content:'';
            position:absolute; inset:-2px;
            background: radial-gradient(circle at 20% 20%, rgba(99, 102, 241, .25), transparent 45%),
                        radial-gradient(circle at 70% 10%, rgba(34, 197, 94, .18), transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(59, 130, 246, .18), transparent 45%),
                        linear-gradient(135deg, rgba(16,185,129,.14), rgba(99,102,241,.10), rgba(59,130,246,.08));
            filter: blur(0px);
            z-index:0;
        }
        .beranda-content{position:relative; z-index:1;}
        .chip{display:inline-flex; gap:10px; align-items:center; padding:10px 14px; border-radius:999px;
              background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);}
        .chip b{font-size:14px;}
        .kartu{border-radius:16px; padding:14px 14px; border: 1px solid rgba(0,0,0,0.08);
               background: rgba(255,255,255,0.65); box-shadow: 0 8px 24px rgba(0,0,0,0.06);} 
        .kartu h4{margin:0 0 6px 0; font-size:16px;}
        .kartu p{margin:0; opacity:.85; font-size:13.5px; line-height:1.35;}
        .svg-orn{width:220px; height:auto; opacity:.95; filter: drop-shadow(0 10px 18px rgba(0,0,0,.10)); position:relative; z-index:2;}
        .cta-btn{display:inline-flex; align-items:center; justify-content:center; padding:12px 18px; border-radius:14px;
                 background: linear-gradient(135deg,#22c55e,#3b82f6); color:white; font-weight:700; text-decoration:none;}
        .cta-btn:hover{filter:brightness(1.03)}

        /* Responsive + anti-overlap */
        @media (max-width: 860px){
          .svg-orn{width: 160px;}
          .periodic-grid{grid-template-columns: repeat(9, 1fr);}
        }
        @media (max-width: 720px){
          .beranda-hero-flex{flex-direction: column !important; align-items: stretch !important;}
          .beranda-hero-right{justify-content: flex-start !important;}
          .svg-orn{width: 100% !important; max-width: 320px; margin-top: 10px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='beranda-wrap'>
          <div class='beranda-content'>
            <div style='display:flex; gap:16px; align-items:flex-start; justify-content:space-between; flex-wrap:wrap;'>
              <div style='min-width: 320px; flex: 1;'>
                <div class='chip'>
                  <span style='font-size:22px;'>🧪</span>
                  <b>Kalkulator Bobot Molekul</b>
                </div>
                <div style='height:10px'></div>
                <h2 style='margin:0; font-size:28px;'>Hitung <span style='color:#3b82f6;'>Mr</span> & <span style='color:#22c55e;'>Berat Ekuivalen (Be)</span></h2>
                <p style='margin:10px 0 0 0; opacity:.85; font-size:14.5px; max-width: 640px;'>
                  Masukkan rumus kimia (contoh: <b>H2O</b>, <b>CO2</b>, <b>NaCl</b>, <b>Ca(OH)2</b>). Aplikasi mendukung kurung <b>()</b>
                  dan notasi dot hydrate (contoh: <b>CuSO4·5H2O</b>).
                </p>

                <div style='height:14px'></div>
                <div>
                  <a class='cta-btn' href='?menu=Kalkulator'>➡️ Ke Tab Kalkulator</a>
                  <div style='height:8px'></div>
                  <span style='font-size:12.5px; opacity:.75;'>Klik tombol untuk lanjut hitung.</span>
                </div>
              </div>

              <!-- SVG unsur kimia dekoratif -->
              <div style='display:flex; align-items:center; justify-content:flex-end; flex:0.4;'>
                <svg class='svg-orn' viewBox='0 0 420 260' xmlns='http://www.w3.org/2000/svg'>
                  <defs>
                    <linearGradient id='g1' x1='0' y1='0' x2='1' y2='1'>
                      <stop offset='0' stop-color='#3b82f6' stop-opacity='0.95'/>
                      <stop offset='1' stop-color='#22c55e' stop-opacity='0.85'/>
                    </linearGradient>
                    <radialGradient id='glow' cx='30%' cy='20%' r='70%'>
                      <stop offset='0' stop-color='#a78bfa' stop-opacity='0.35'/>
                      <stop offset='1' stop-color='#000' stop-opacity='0'/>
                    </radialGradient>
                    <pattern id='grid' width='18' height='18' patternUnits='userSpaceOnUse'>
                      <path d='M18 0H0V18' fill='none' stroke='rgba(255,255,255,.35)' stroke-width='1'/>
                    </pattern>
                  </defs>

                  <rect x='0' y='0' width='420' height='260' fill='url(#glow)'/>
                  <rect x='0' y='0' width='420' height='260' fill='url(#grid)' opacity='0.28'/>

                  <!-- atom -->
                  <g transform='translate(210 120)'>
                    <circle r='62' fill='none' stroke='rgba(59,130,246,0.25)' stroke-width='2'/>
                    <circle r='88' fill='none' stroke='rgba(34,197,94,0.18)' stroke-width='2'/>
                    <ellipse cx='0' cy='0' rx='110' ry='44' fill='none' stroke='rgba(167,139,250,0.18)' stroke-width='2'/>

                    <g opacity='0.95'>
                      <circle cx='0' cy='0' r='26' fill='url(#g1)'/>
                      <text x='0' y='10' text-anchor='middle' font-family='system-ui, -apple-system, Segoe UI, Roboto' font-size='16' fill='white' font-weight='800'>C</text>
                    </g>

                    <g>
                      <circle cx='86' cy='0' r='10' fill='rgba(34,197,94,0.95)'/>
                      <circle cx='-64' cy='52' r='8' fill='rgba(59,130,246,0.95)'/>
                      <circle cx='-38' cy='-58' r='6' fill='rgba(167,139,250,0.95)'/>
                      <circle cx='38' cy='58' r='7' fill='rgba(34,197,94,0.85)'/>
                    </g>
                  </g>

                  <!-- rumus molekul dekoratif -->
                  <g font-family='ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto' fill='rgba(255,255,255,0.85)' font-weight='800'>
                    <text x='44' y='70' font-size='24' fill='rgba(255,255,255,0.78)'>H₂O</text>
                    <text x='330' y='60' font-size='18' fill='rgba(255,255,255,0.72)'>CO₂</text>
                    <text x='62' y='208' font-size='20' fill='rgba(255,255,255,0.70)'>NaCl</text>
                    <text x='255' y='208' font-size='18' fill='rgba(255,255,255,0.68)'>Ca(OH)₂</text>
                  </g>

                  <!-- garis orbit -->
                  <path d='M64 132 C120 96, 178 90, 216 108' fill='none' stroke='rgba(255,255,255,.22)' stroke-width='2' stroke-linecap='round'/>
                  <path d='M120 168 C160 210, 240 224, 314 186' fill='none' stroke='rgba(255,255,255,.18)' stroke-width='2' stroke-linecap='round'/>

                </svg>
              </div>
            </div>

            <div style='height:18px'></div>
            <div style='display:flex; gap:14px; align-items:flex-start; justify-content:space-between; flex-wrap:wrap;'>
              <div style='flex: 1; min-width: 260px; position:relative; z-index:3;'>
                <div style='padding:12px 14px; border-radius:14px; border: 1px solid rgba(255,255,255,0.35); background: rgba(255,255,255,0.12);'>
                  <b style='font-size:14.5px;'>😂 Kutipan random tentang kimia</b>
                  <div style='margin-top:6px; opacity:.9; font-size:13.5px; line-height:1.35;'>
                    “Kimia itu seperti masak: kalau takaran salah, reaksinya bisa bikin ‘meledak’… tapi setidaknya jadi pelajaran!”
                  </div>
                </div>
              </div>

              <div style='flex: 0.9; min-width: 260px; display:flex; justify-content:flex-end;'>
                <!-- Struktur kimia (SVG inline sederhana) -->
                <svg viewBox='0 0 520 180' style='width:100%; max-width:520px; height:auto; filter: drop-shadow(0 12px 20px rgba(0,0,0,.10));'>
                  <defs>
                    <linearGradient id='bond' x1='0' y1='0' x2='1' y2='1'>
                      <stop offset='0' stop-color='#3b82f6' stop-opacity='0.95'/>
                      <stop offset='1' stop-color='#22c55e' stop-opacity='0.9'/>
                    </linearGradient>
                  </defs>

                  <!-- bonds -->
                  <path d='M70 90 L160 90' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M160 90 L245 52' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M160 90 L245 128' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M245 52 L330 52' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M245 128 L330 128' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M330 52 L415 90' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>
                  <path d='M330 128 L415 90' stroke='url(#bond)' stroke-width='6' stroke-linecap='round'/>

                  <!-- atoms (lingkaran) -->
                  <g font-family='ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto' font-weight='800'>
                    <g transform='translate(70,90)'>
                      <circle r='18' fill='rgba(59,130,246,0.18)' stroke='rgba(59,130,246,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eaf2ff'>C</text>
                    </g>
                    <g transform='translate(160,90)'>
                      <circle r='18' fill='rgba(34,197,94,0.16)' stroke='rgba(34,197,94,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eafff4'>C</text>
                    </g>
                    <g transform='translate(245,52)'>
                      <circle r='18' fill='rgba(59,130,246,0.18)' stroke='rgba(59,130,246,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eaf2ff'>O</text>
                    </g>
                    <g transform='translate(245,128)'>
                      <circle r='18' fill='rgba(34,197,94,0.16)' stroke='rgba(34,197,94,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eafff4'>H</text>
                    </g>
                    <g transform='translate(330,52)'>
                      <circle r='18' fill='rgba(167,139,250,0.16)' stroke='rgba(167,139,250,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#f1eaff'>N</text>
                    </g>
                    <g transform='translate(330,128)'>
                      <circle r='18' fill='rgba(59,130,246,0.18)' stroke='rgba(59,130,246,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eaf2ff'>S</text>
                    </g>
                    <g transform='translate(415,90)'>
                      <circle r='18' fill='rgba(34,197,94,0.16)' stroke='rgba(34,197,94,0.55)' stroke-width='3'/>
                      <text text-anchor='middle' y='6' font-size='16' fill='#eafff4'>Cl</text>
                    </g>
                  </g>
                </svg>
              </div>
            </div>

            <div style='display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:12px;'>
              <div class='kartu'>
                <h4>⚛️ Parsing Rumus</h4>
                <p>Gampang masukin format seperti <b>Ca(OH)₂</b> dan mendukung <b>dot hydrate</b>.</p>
              </div>
              <div class='kartu'>
                <h4>📌 Komposisi Unsur</h4>
                <p>Lihat jumlah atom tiap unsur beserta kontribusi ke <b>Mr</b>.</p>
              </div>
              <div class='kartu'>
                <h4>🧮 Mr (Bobot Molekul)</h4>
                <p>Hitung total massa molar berbasis dataset massa atom.</p>
              </div>
              <div class='kartu'>
                <h4>🧰 Berat Ekuivalen (Be)</h4>
                <p>Gunakan rumus <b>Be = Mr / n</b> (input <b>n</b>).</p>
              </div>
            </div>

            <div style='height:12px'></div>
            <p style='margin:0; font-size:12.5px; opacity:.7;'>Tip: Gunakan sidebar untuk pindah menu. Tombol di hero membuka tab Kalkulator.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tetap sediakan informasi ringkas (non-polish) tanpa mengulang banyak teks
    st.markdown("---")
    st.write("**Ringkasnya:** aplikasi ini menghitung <b>Mr</b> dari rumus kimia dan membantu menghitung <b>Be</b> berdasarkan <b>Mr / n</b>.")
    st.caption("Jika ada simbol seperti '·' (dot), coba input mis. CuSO4·5H2O.")

elif menu == "Kalkulator":
    formula = st.text_input(
        "Rumus kimia",
        value="Ca(OH)2",
        help="Gunakan format huruf besar-kecil (mis. Na, Cl) dan angka untuk jumlah atom.",
    )


    col1, col2 = st.columns(2)
    with col1:
        enable_table = st.checkbox("Tampilkan tabel komposisi", value=True)
    with col2:
        decimals = st.slider("Jumlah desimal", min_value=2, max_value=6, value=4)

    # Integrasi sederhana: kalau dipilih dari tab periodik, tampilkan hint
    if "prefill_symbol" in st.session_state and st.session_state.get("prefill_symbol"):
        st.info(f"Unsur dipilih dari tabel: {st.session_state['prefill_symbol']}.")

    if st.button("Hitung", type="primary"):
        try:
            counts = parse_formula(formula)
            total_mr = calculate_molar_mass(counts)

            st.subheader(f"Hasil: Mr({formula}) = {total_mr:.{decimals}f} g/mol")

            # Simpan agar output tidak hilang saat input n berubah (Streamlit rerun).
            st.session_state["last_formula"] = formula
            st.session_state["last_counts"] = counts
            st.session_state["last_total_mr"] = total_mr

        except Exception as e:
            st.error(str(e))

    # Input n (valensi ekuivalen / jumlah elektron) dijaga agar selalu bilangan bulat > 0.
    n_eq_raw = st.text_input(
        "Berat ekuivalen (Be): masukkan nilai n (valensi ekuivalen / jumlah elektron)",
        value=str(st.session_state.get("n_eq_raw", "1")),
        help="Contoh: 1, 2, 3. Bilangan bulat > 0. Jika pakai desimal atau koma, akan ditolak.",
    )
    st.session_state["n_eq_raw"] = n_eq_raw

    def _parse_int_positive(value: str):
        v = str(value).strip()
        if not v:
            return None
        # dukung format Indonesia: 2,0 -> tolak (karena diminta bulat)
        v = v.replace(",", ".")
        try:
            # validasi ketat: harus int murni (tidak boleh 2.0)
            if "." in v:
                return None
            n = int(v)
        except Exception:
            return None
        if n <= 0:
            return None
        return n

    n_eq = _parse_int_positive(n_eq_raw)

    if "last_total_mr" in st.session_state and "last_counts" in st.session_state:
        if n_eq is None:
            st.warning("Input n tidak valid. Masukkan bilangan bulat > 0 (mis. 1 atau 2).")
        else:
            total_mr = float(st.session_state["last_total_mr"])
            counts = st.session_state["last_counts"]

            be = total_mr / float(n_eq)
            st.info(
                f"Berat ekuivalen (Be) = Mr / n = {total_mr:.{decimals}f} / {n_eq} = {be:.{decimals}f} g/ekuiv"
            )

            details = []
            for el in sorted(counts.keys(), key=lambda x: (x != "", x)):
                cnt = counts[el]
                mr_el = ATOMIC_MASS[el] * cnt
                details.append(
                    {
                        "Unsur": el,
                        "Jumlah atom": cnt,
                        "Mr atom (g/mol)": ATOMIC_MASS[el],
                        "Kontribusi (g/mol)": mr_el,
                    }
                )

            df = pd.DataFrame(details)
            if enable_table:
                st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.caption(
                "Catatan: Mr dihitung dari massa atom relatif (g/mol) standar. Nilai di dataset dapat berbeda sedikit tergantung sumber."
            )

    st.markdown("---")
    st.markdown(
        "**Contoh input**: `H2O`, `CO2`, `CH3COOH`, `NaCl`, `Ca(OH)2`\n"
        "Jika rumus mengandung simbol `·` (dot) seperti `CuSO4·5H2O`, perlu fitur parsing tambahan."
    )

elif menu == "Tabel Periodik":
    st.subheader("Tabel Periodik dari dataset massa atom")


    available = sorted(set(ATOMIC_MASS.keys()) & set(PERIODIC_META.keys()))

    selected = st.selectbox("Pilih unsur", options=["(tidak ada)"] + available, index=0)

    # Grid 7x18 (periode x grup)
    grid = []
    for period in range(1, 8):
        row = []
        for group in range(1, 19):
            found = None
            for el in available:
                p, g, _b = PERIODIC_META[el]
                if p == period and g == group:
                    found = el
                    break
            row.append(found)
        grid.append(row)

    # Header labels (row/column)
    column_labels = list(range(1, 19))
    row_labels = list(range(1, 8))


    # Map blok (s/p/d/f) menjadi label yang lebih mudah dimengerti user
    block_label = {
        "s": "Blok s (alkali/alkali tanah & H/He)",
        "p": "Blok p (unsur golongan utama)",
        "d": "Blok d (logam transisi)",
        "f": "Blok f (lantanida & aktinida)",
    }

    block_color = {
        "s": "#E3F2FD",
        "p": "#E8F5E9",
        "d": "#FFF3E0",
        "f": "#F3E5F5",
    }


    import html as _html

    st.markdown(
        """
        <style>
        .periodic-grid{display:grid; grid-template-columns: repeat(18, 1fr); gap: 6px;}
        .cell{height: 62px; border-radius: 10px; border: 1px solid rgba(0,0,0,0.08); display:flex; flex-direction:column; align-items:center; justify-content:center;}
        .cell.empty{background:transparent; border: 1px dashed rgba(0,0,0,0.12);}
        .small{font-size: 11px; opacity: 0.85; margin-top: 2px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    def render_cell(el):
        if el is None:
            return "<div class='cell empty'></div>"
        p, g, block = PERIODIC_META[el]
        color = block_color.get(block, "#FFFFFF")
        return (
            "<div class='cell' style='background:%s' title='%s | Period %s, Group %s | Block %s'>"
            "<b>%s</b>"
            "<div class='small'>%.3f</div>"
            "</div>"
            % (
                _html.escape(color),
                _html.escape(el),
                p,
                g,
                _html.escape(block),
                _html.escape(el),
                ATOMIC_MASS[el],
            )
        )

    for row in grid:
        cols = "".join(render_cell(el) for el in row)
        st.markdown(f"<div class='periodic-grid'>{cols}</div>", unsafe_allow_html=True)

    st.divider()

    if selected != "(tidak ada)":
        p, g, block = PERIODIC_META[selected]
        st.markdown(f"### Detail unsur: **{selected}**")
        st.write(
            {
                "Periode": p,
                "Golongan": g,
                "Blok": block,
                "Kategori blok (jelas)": block_label.get(block, block),
                "Massa atom (g/mol)": ATOMIC_MASS[selected],
            }
        )


        if st.button("Masukkan simbol ke kalkulator (hint)"):
            st.session_state["prefill_symbol"] = selected
            st.toast(f"{selected} disimpan untuk hint di tab Kalkulator.")

