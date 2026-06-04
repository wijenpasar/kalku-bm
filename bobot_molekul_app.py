import streamlit as st


def main():
    st.set_page_config(page_title="Kalku BM", page_icon="🧪", layout="centered")

    # --- Navigation ---
    menu = st.sidebar.radio(
        "Menu",
        ["Beranda", "Kalkulator", "Tabel Periodik"],
        index=0,
    )

    if menu == "Beranda":
        # --- Funny & cute beranda ---
        st.markdown(
            """
            <style>
            .hero {
                padding: 18px 18px;
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(236,72,153,0.14), rgba(34,197,94,0.12));
                border: 1px solid rgba(255,255,255,0.18);
                position: relative;
                overflow: hidden;
            }
            .hero h1 { margin-bottom: 4px; }
            .tag {
                display: inline-block;
                padding: 6px 10px;
                border-radius: 999px;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
                font-weight: 700;
                letter-spacing: 0.2px;
            }
            .card {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 16px;
                padding: 14px 14px;
                min-height: 124px;
            }
            .card .emoji { font-size: 30px; }
            .sparkle {
                position:absolute;
                right:-40px;
                top:-40px;
                opacity: 0.28;
                transform: rotate(18deg);
                pointer-events:none;
            }
            .bottom-row {
                margin-top: 14px;
            }
            .cta-wrap {
                margin-top: 10px;
                display:flex;
                gap:10px;
                flex-wrap:wrap;
            }
            .btn {
                border: 0;
                background: linear-gradient(135deg, #6366f1, #ec4899);
                color: white;
                font-weight: 800;
                padding: 10px 14px;
                border-radius: 12px;
                cursor: pointer;
                box-shadow: 0 10px 22px rgba(99,102,241,0.25);
            }
            .btn:active { transform: translateY(1px); }
            .btn-secondary {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.18);
                color: #f8fafc;
                font-weight: 800;
                padding: 10px 14px;
                border-radius: 12px;
            }
            @media (max-width: 640px) {
                .sparkle { display:none; }
                .hero { padding: 14px; }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="hero">
              <div class="sparkle">
                <svg width="220" height="220" viewBox="0 0 220 220" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M110 10L126 66L182 82L126 98L110 154L94 98L38 82L94 66L110 10Z" fill="#FFFFFF"/>
                  <path d="M168 130L174 152L196 158L174 164L168 186L162 164L140 158L162 152L168 130Z" fill="#FFFFFF" opacity="0.8"/>
                  <path d="M50 130L56 152L78 158L56 164L50 186L44 164L22 158L44 152L50 130Z" fill="#FFFFFF" opacity="0.7"/>
                </svg>
              </div>
              <span class="tag">🧪 Kalku BM — lucu tapi serius!</span>
              <h1 style="margin-top:10px; font-size: 40px; line-height: 1.1;">Selamat datang di Beranda 👋</h1>
              <p style="font-size: 16px; opacity: 0.92;">
                Di sini kita bantu hitung dan eksplorasi kimia. Kalau molekul bisa bicara, mereka bakal bilang: “makasih ya!”
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(
                """
                <div class="bottom-row card">
                  <div class="emoji">🧮</div>
                  <h3 style="margin:6px 0 6px;">Kalkulator</h3>
                  <p style="margin:0; opacity:0.9;">Hitung cepat: bobot molekul dan yang sejenisnya.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div class="bottom-row card">
                  <div class="emoji">📚</div>
                  <h3 style="margin:6px 0 6px;">Tabel Periodik</h3>
                  <p style="margin:0; opacity:0.9;">Cari info unsur—biar gak bingung pas belajar.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.markdown(
                """
                <div class="card">
                  <div class="emoji">✨</div>
                  <h3 style="margin:6px 0 6px;">Auto-friendly</h3>
                  <p style="margin:0; opacity:0.9;">UI dirancang biar nyaman dipakai.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
                <div class="card">
                  <div class="emoji">😄</div>
                  <h3 style="margin:6px 0 6px;">Gampang dipahami</h3>
                  <p style="margin:0; opacity:0.9;">Langkahnya dibuat simpel dan jelas.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                """
                <div class="card">
                  <div class="emoji">🧠</div>
                  <h3 style="margin:6px 0 6px;">Belajar makin ngebut</h3>
                  <p style="margin:0; opacity:0.9;">Cocok buat tugas & latihan.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="cta-wrap">
              <form action="/Kalkulator" method="get">
                <button class="btn" type="submit">➡️ Yuk ke Kalkulator!</button>
              </form>
              <div class="btn-secondary" style="padding:10px 14px; border-radius:12px;">
                Tip: pilih menu di sidebar juga bisa 😎
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif menu == "Kalkulator":
        st.title("Kalkulator")
        st.info("Bagian ini sementara—fokus tugas sekarang: tampilan Beranda yang lucu.")

    else:  # Tabel Periodik
        st.title("Tabel Periodik")
        st.info("Bagian ini sementara—fokus tugas sekarang: tampilan Beranda yang lucu.")


if __name__ == "__main__":
    main()

