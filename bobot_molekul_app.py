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
    # --- Custom CSS (hanya untuk tampilan Beranda) ---
    st.markdown(
        """
        <style>
        .hero-wrap{
            position:relative;
            padding: 22px 20px;
            border-radius: 18px;
            overflow:hidden;
            background: linear-gradient(120deg, rgba(59,130,246,0.18), rgba(217,70,239,0.14), rgba(34,197,94,0.10));
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        }
        .hero-title{font-size: 34px; font-weight: 800; letter-spacing: .2px;}
        .hero-sub{opacity: .88; font-size: 14px;}
        .badge{
            display:inline-flex; align-items:center; gap:8px;
            padding: 8px 12px; border-radius: 999px;
            background: rgba(0,0,0,0.04);
            border: 1px solid rgba(0,0,0,0.06);
            font-weight: 650;
        }
        .kartu{
            padding: 14px 14px;
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.06);
            background: rgba(255,255,255,0.65);
            backdrop-filter: blur(6px);
            box-shadow: 0 8px 22px rgba(0,0,0,0.04);
            min-height: 120px;
        }
        .kartu h4{margin:0 0 6px 0; font-size: 16px;}
        .kartu p{margin:0; opacity:.85; font-size: 13px; line-height:1.35;}
        .cta-row{margin-top: 14px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;}
        .btn-big{font-weight: 800;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- “Gambar unsur kimia” (SVG inline, tidak perlu file eksternal) ---
    unsur_svg = r"""
    <svg viewBox="0 0 620 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#60a5fa" stop-opacity="0.55"/>
          <stop offset="0.5" stop-color="#d946ef" stop-opacity="0.40"/>
          <stop offset="1" stop-color="#22c55e" stop-opacity="0.35"/>
        </linearGradient>
        <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity="0.15"/>
        </filter>
      </defs>

      <rect x="0" y="0" width="620" height="220" rx="18" fill="url(#g1)" opacity="0.95"/>

      <!-- Background sparkles -->
      <g opacity="0.35" fill="#fff">
        <circle cx="50" cy="45" r="3"/><circle cx="110" cy="30" r="2"/>
        <circle cx="560" cy="40" r="3"/><circle cx="500" cy="70" r="2"/>
        <circle cx="590" cy="140" r="3"/><circle cx="40" cy="170" r="2"/>
      </g>

      <!-- Orbital atom (H-like) -->
      <g transform="translate(80,35)" filter="url(#shadow)">
        <circle cx="110" cy="80" r="46" fill="rgba(255,255,255,0.35)" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
        <circle cx="110" cy="80" r="17" fill="#60a5fa" fill-opacity="0.9"/>
        <circle cx="110" cy="80" r="6" fill="#ffffff"/>
        <ellipse cx="110" cy="80" rx="82" ry="26" fill="none" stroke="#d946ef" stroke-width="3" opacity="0.35"/>
        <ellipse cx="110" cy="80" rx="64" ry="20" fill="none" stroke="#22c55e" stroke-width="3" opacity="0.30"/>
        <circle cx="170" cy="70" r="10" fill="#d946ef" fill-opacity="0.75"/>
        <circle cx="60" cy="95" r="9" fill="#22c55e" fill-opacity="0.65"/>
        <text x="110" y="140" text-anchor="middle" font-size="22" font-weight="800" fill="rgba(0,0,0,0.75)">H</text>
        <text x="110" y="160" text-anchor="middle" font-size="12" font-weight="700" fill="rgba(0,0,0,0.55)">unsur simbolik</text>
      </g>

      <!-- Molecule connections -->
      <g transform="translate(290,20)" filter="url(#shadow)">
        <circle cx="60" cy="90" r="22" fill="rgba(96,165,250,0.55)" stroke="rgba(255,255,255,0.65)" stroke-width="2"/>
        <circle cx="170" cy="55" r="18" fill="rgba(217,70,239,0.50)" stroke="rgba(255,255,255,0.65)" stroke-width="2"/>
        <circle cx="230" cy="130" r="20" fill="rgba(34,197,94,0.45)" stroke="rgba(255,255,255,0.65)" stroke-width="2"/>
        <circle cx="110" cy="165" r="16" fill="rgba(96,165,250,0.50)" stroke="rgba(255,255,255,0.65)" stroke-width="2"/>

        <path d="M60 90 L170 55" stroke="#d946ef" stroke-width="4" stroke-linecap="round" opacity="0.45"/>
        <path d="M170 55 L230 130" stroke="#22c55e" stroke-width="4" stroke-linecap="round" opacity="0.42"/>
        <path d="M60 90 L110 165" stroke="#60a5fa" stroke-width="4" stroke-linecap="round" opacity="0.42"/>
        <path d="M110 165 L230 130" stroke="#d946ef" stroke-width="4" stroke-linecap="round" opacity="0.35"/>

        <text x="60" y="96" text-anchor="middle" font-size="16" font-weight="900" fill="rgba(0,0,0,0.7)">Na</text>
        <text x="170" y="62" text-anchor="middle" font-size="14" font-weight="900" fill="rgba(0,0,0,0.7)">Cl</text>
        <text x="230" y="136" text-anchor="middle" font-size="14" font-weight="900" fill="rgba(0,0,0,0.7)">O</text>
        <text x="110" y="172" text-anchor="middle" font-size="14" font-weight="900" fill="rgba(0,0,0,0.7)">C</text>
      </g>

      <!-- Caption -->
      <text x="315" y="205" text-anchor="middle" font-size="14" font-weight="800" fill="rgba(0,0,0,0.60)">
        Simbol unsur + koneksi molekul — vibes kimia!
      </text>
    </svg>
    """

    # --- Layout Beranda ---
    st.markdown(
        f"""<div class='hero-wrap'>
            <div class='badge'>⚛️ Visual Kimia • Mr Calculator</div>
            <div style='height:10px'></div>
            <div class='hero-title'>Jelajahi rumus, rasakan kimia ✨</div>
            <div class='hero-sub'>Hitung <b>Mr (bobot molekul)</b> dan <b>berat ekuivalen (Be)</b> hanya dari rumus — plus ilustrasi unsur yang bikin makin seru.</div>
            <div class='cta-row'>
              <a href='#' onclick='window.parent.postMessage({type: "streamlit:setComponentValue", value: 1}, "*")' style='text-decoration:none'>
                <span class='btn-big'>
              </a>
            </div>
          </div>""",
        unsafe_allow_html=True,
    )

    # Render SVG
    st.markdown(unsur_svg, unsafe_allow_html=True)

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """<div class='kartu'>
                <h4>🧾 Input rumus</h4>
                <p>Ketik cepat seperti <b>H2O</b>, <b>CO2</b>, <b>NaCl</b>, atau <b>Ca(OH)2</b>.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """<div class='kartu'>
                <h4>🧠 Parsing pintar</h4>
                <p>Mendukung tanda kurung <b>()</b> dan notasi <b>dot hydrate</b> (contoh <b>CuSO4·5H2O</b>).</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """<div class='kartu'>
                <h4>⚖️ Mr + detail unsur</h4>
                <p>Lihat kontribusi tiap unsur: jumlah atom dan kontribusi massa.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """<div class='kartu'>
                <h4>📌 Be = Mr / n</h4>
                <p>Hitung berat ekuivalen dengan <b>Be</b> berdasarkan nilai <b>n</b>.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # CTA sederhana: gunakan tombol untuk menyetel session_state dan refresh pilihan menu.
    # Karena radio menu tidak bisa dipaksa lewat HTML, kita gunakan session_state untuk menyetel ulang dan memunculkan hint.
    if st.button("🚀 Mulai hitung sekarang (ke Kalkulator)", type="primary"):
        st.session_state["_jump_to_kalkulator"] = True
        st.rerun()

    st.info("Gunakan sidebar untuk pindah menu. Tombol di atas hanya memberi hint cepat untuk memulai di tab Kalkulator.")

    # Jika ada flag jump, tampilkan tombol otomatis untuk user.
    if st.session_state.get("_jump_to_kalkulator"):
        st.session_state["_jump_to_kalkulator"] = False
        st.toast("Langkah berikutnya: pilih menu 'Kalkulator' di sidebar.")

    st.caption("Tip: gunakan menu di sidebar untuk berpindah halaman.")

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
