# ============================================================
# BookCycle - Platform Jual Beli Buku Bekas Mahasiswa
# Sistem Rekomendasi Multi-Parameter dengan Pembobotan Adaptif
# ============================================================
# Cara menjalankan:
#   pip install streamlit pandas plotly
#   streamlit run bookcycle_app.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
import copy

# ─────────────────────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BookCycle – Rekomendasi Buku Bekas Mahasiswa",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS KUSTOM (Tema BookCycle)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');

  /* Root & Background */
  html, body, [data-testid="stAppViewContainer"] {
      background: #0f1117;
      color: #e8e0d4;
      font-family: 'DM Sans', sans-serif;
  }
  [data-testid="stSidebar"] {
      background: #16191f !important;
      border-right: 1px solid #2a2d35;
  }

  /* Header */
  .bookcycle-header {
      text-align: center;
      padding: 1.5rem 0 0.5rem;
  }
  .bookcycle-header h1 {
      font-family: 'Playfair Display', serif;
      font-size: 2.8rem;
      color: #f0c060;
      letter-spacing: -1px;
      margin: 0;
  }
  .bookcycle-header p {
      color: #8a8fa8;
      font-size: 0.95rem;
      margin-top: 4px;
  }

  /* Section Title */
  .section-title {
      font-family: 'Playfair Display', serif;
      font-size: 1.3rem;
      color: #f0c060;
      border-bottom: 2px solid #f0c06040;
      padding-bottom: 6px;
      margin-bottom: 1rem;
  }

  /* Book Card */
  .book-card {
      background: #1c1f2a;
      border: 1px solid #2e3141;
      border-radius: 12px;
      padding: 1rem 1.2rem;
      margin-bottom: 0.8rem;
      position: relative;
      transition: border 0.2s;
  }
  .book-card:hover { border-color: #f0c06070; }
  .book-card .rank-badge {
      position: absolute;
      top: -10px; left: 14px;
      background: #f0c060;
      color: #0f1117;
      font-weight: 700;
      font-size: 0.75rem;
      padding: 2px 10px;
      border-radius: 20px;
  }
  .book-card .book-title {
      font-family: 'Playfair Display', serif;
      font-size: 1.05rem;
      color: #f0ebe0;
      margin: 4px 0 6px;
  }
  .book-card .meta {
      font-size: 0.8rem;
      color: #8a8fa8;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 8px;
  }
  .book-card .meta span { display: flex; align-items: center; gap: 4px; }
  .book-card .score-bar-bg {
      height: 6px;
      background: #2e3141;
      border-radius: 4px;
      overflow: hidden;
  }
  .book-card .score-bar-fill {
      height: 100%;
      border-radius: 4px;
      background: linear-gradient(90deg, #f0c060, #e07030);
  }
  .book-card .score-label {
      font-size: 0.78rem;
      color: #f0c060;
      font-weight: 600;
      margin-top: 4px;
  }

  /* Weight chip */
  .weight-chip {
      display: inline-block;
      background: #252837;
      color: #c8c4d8;
      border-radius: 20px;
      padding: 2px 10px;
      font-size: 0.76rem;
      margin: 2px;
      border: 1px solid #3a3d50;
  }

  /* Condition badge */
  .cond-sangat-baik { color: #4caf88; font-weight: 600; }
  .cond-baik        { color: #60a0f0; font-weight: 600; }
  .cond-cukup       { color: #f0a040; font-weight: 600; }

  /* Sidebar labels */
  .sidebar-label {
      font-size: 0.78rem;
      color: #8a8fa8;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 4px;
  }

  /* Feedback log */
  .feedback-item {
      background: #1c1f2a;
      border-left: 3px solid #f0c060;
      padding: 6px 10px;
      border-radius: 0 6px 6px 0;
      font-size: 0.8rem;
      color: #c0bcd0;
      margin-bottom: 4px;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer { visibility: hidden; }
  .stButton > button {
      background: #f0c060 !important;
      color: #0f1117 !important;
      font-weight: 600 !important;
      border-radius: 8px !important;
      border: none !important;
  }
  .stButton > button:hover { background: #e0b050 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MODUL 1 – DATASET UTAMA (Mock Data BookCycle)
# Struktur terinspirasi dari books.toscrape.com, diperkaya
# dengan kolom khusus platform BookCycle
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_dataset() -> pd.DataFrame:
    """
    Membuat dataset simulasi buku bekas mahasiswa.
    Kolom dasar: Judul, Kategori, Harga (£), Rating (bintang 1-5).
    Kolom tambahan BookCycle: Program Studi, Mata Kuliah,
    Kondisi, Skor Kondisi, Nama Penjual, Rating Penjual.
    """
    random.seed(42)

    data = [
        # ── TEKNIK & INFORMATIKA ────────────────────────────────────
        {"title": "Calculus: Early Transcendentals",      "category": "Science",      "price": 45000, "rating": 5,
         "prodi": "Teknik Elektro",    "matkul": "Kalkulus",            "kondisi": "Sangat Baik", "penjual": "Budi S.",    "rating_penjual": 4.8},
        {"title": "Introduction to Algorithms",            "category": "Computers",    "price": 85000, "rating": 4,
         "prodi": "Informatika",       "matkul": "Algoritma & Struktur Data", "kondisi": "Baik",       "penjual": "Rina A.",    "rating_penjual": 4.5},
        {"title": "Computer Networks: A Top-Down Approach","category": "Computers",    "price": 72000, "rating": 4,
         "prodi": "Informatika",       "matkul": "Jaringan Komputer",   "kondisi": "Baik",       "penjual": "Dian P.",    "rating_penjual": 4.2},
        {"title": "Clean Code",                            "category": "Computers",    "price": 55000, "rating": 5,
         "prodi": "Informatika",       "matkul": "Pemrograman Lanjut",  "kondisi": "Sangat Baik", "penjual": "Andi K.",    "rating_penjual": 5.0},
        {"title": "Python Crash Course",                   "category": "Computers",    "price": 42000, "rating": 5,
         "prodi": "Informatika",       "matkul": "Pemrograman Dasar",   "kondisi": "Baik",       "penjual": "Sari M.",    "rating_penjual": 4.7},
        {"title": "Discrete Mathematics and Its Applications","category": "Science",   "price": 68000, "rating": 4,
         "prodi": "Informatika",       "matkul": "Matematika Diskrit",  "kondisi": "Cukup",      "penjual": "Yogi L.",    "rating_penjual": 3.8},
        {"title": "Database System Concepts",              "category": "Computers",    "price": 60000, "rating": 4,
         "prodi": "Informatika",       "matkul": "Basis Data",          "kondisi": "Sangat Baik", "penjual": "Nita R.",    "rating_penjual": 4.6},
        {"title": "Operating System Concepts",             "category": "Computers",    "price": 58000, "rating": 3,
         "prodi": "Informatika",       "matkul": "Sistem Operasi",      "kondisi": "Cukup",      "penjual": "Hendra W.",  "rating_penjual": 3.5},
        {"title": "Artificial Intelligence: A Modern Approach","category": "Computers","price": 95000, "rating": 5,
         "prodi": "Informatika",       "matkul": "Kecerdasan Buatan",   "kondisi": "Baik",       "penjual": "Lina F.",    "rating_penjual": 4.9},
        {"title": "Deep Learning",                         "category": "Computers",    "price": 88000, "rating": 5,
         "prodi": "Informatika",       "matkul": "Machine Learning",    "kondisi": "Sangat Baik", "penjual": "Reza T.",    "rating_penjual": 4.8},
        # ── FISIKA & MATEMATIKA ─────────────────────────────────────
        {"title": "University Physics",                    "category": "Science",      "price": 50000, "rating": 4,
         "prodi": "Fisika",            "matkul": "Fisika Dasar",        "kondisi": "Baik",       "penjual": "Wati N.",    "rating_penjual": 4.3},
        {"title": "Fundamentals of Physics",               "category": "Science",      "price": 48000, "rating": 4,
         "prodi": "Fisika",            "matkul": "Fisika Dasar",        "kondisi": "Cukup",      "penjual": "Joko S.",    "rating_penjual": 3.9},
        {"title": "Mathematical Methods for Physicists",   "category": "Science",      "price": 62000, "rating": 5,
         "prodi": "Fisika",            "matkul": "Fisika Matematika",   "kondisi": "Baik",       "penjual": "Dewi P.",    "rating_penjual": 4.4},
        {"title": "Quantum Mechanics",                     "category": "Science",      "price": 75000, "rating": 5,
         "prodi": "Fisika",            "matkul": "Mekanika Kuantum",    "kondisi": "Sangat Baik", "penjual": "Arif M.",    "rating_penjual": 4.7},
        {"title": "Classical Mechanics",                   "category": "Science",      "price": 55000, "rating": 4,
         "prodi": "Fisika",            "matkul": "Mekanika Klasik",     "kondisi": "Baik",       "penjual": "Sinta H.",   "rating_penjual": 4.1},
        {"title": "Linear Algebra and Its Applications",   "category": "Science",      "price": 40000, "rating": 4,
         "prodi": "Matematika",        "matkul": "Aljabar Linear",      "kondisi": "Cukup",      "penjual": "Bimo K.",    "rating_penjual": 3.6},
        {"title": "Probability and Statistics for Engineers","category": "Science",    "price": 35000, "rating": 3,
         "prodi": "Teknik Elektro",    "matkul": "Statistika",          "kondisi": "Cukup",      "penjual": "Clara V.",   "rating_penjual": 3.2},
        # ── EKONOMI & BISNIS ────────────────────────────────────────
        {"title": "Principles of Economics",               "category": "Business",     "price": 30000, "rating": 4,
         "prodi": "Ekonomi",           "matkul": "Pengantar Ekonomi",   "kondisi": "Baik",       "penjual": "Dito R.",    "rating_penjual": 4.0},
        {"title": "Microeconomics",                        "category": "Business",     "price": 38000, "rating": 4,
         "prodi": "Ekonomi",           "matkul": "Ekonomi Mikro",       "kondisi": "Sangat Baik", "penjual": "Eka S.",     "rating_penjual": 4.5},
        {"title": "Corporate Finance",                     "category": "Business",     "price": 55000, "rating": 3,
         "prodi": "Manajemen",         "matkul": "Keuangan Perusahaan", "kondisi": "Baik",       "penjual": "Fira L.",    "rating_penjual": 4.2},
        {"title": "Marketing Management",                  "category": "Business",     "price": 42000, "rating": 4,
         "prodi": "Manajemen",         "matkul": "Manajemen Pemasaran", "kondisi": "Sangat Baik", "penjual": "Galih P.",   "rating_penjual": 4.6},
        {"title": "Accounting Principles",                 "category": "Business",     "price": 28000, "rating": 3,
         "prodi": "Akuntansi",         "matkul": "Akuntansi Dasar",     "kondisi": "Cukup",      "penjual": "Hana W.",    "rating_penjual": 3.4},
        # ── KEDOKTERAN & BIOLOGI ────────────────────────────────────
        {"title": "Campbell Biology",                      "category": "Science",      "price": 90000, "rating": 5,
         "prodi": "Biologi",           "matkul": "Biologi Umum",        "kondisi": "Sangat Baik", "penjual": "Ivan D.",    "rating_penjual": 4.9},
        {"title": "Anatomy & Physiology",                  "category": "Medical",      "price": 78000, "rating": 4,
         "prodi": "Kedokteran",        "matkul": "Anatomi",             "kondisi": "Baik",       "penjual": "Julia F.",   "rating_penjual": 4.5},
        {"title": "Pharmacology for Nurses",               "category": "Medical",      "price": 65000, "rating": 4,
         "prodi": "Keperawatan",       "matkul": "Farmakologi",         "kondisi": "Baik",       "penjual": "Kevin A.",   "rating_penjual": 4.3},
        {"title": "Biochemistry",                          "category": "Medical",      "price": 70000, "rating": 5,
         "prodi": "Kedokteran",        "matkul": "Biokimia",            "kondisi": "Sangat Baik", "penjual": "Lisa M.",    "rating_penjual": 4.7},
        # ── HUKUM & SOSIAL ──────────────────────────────────────────
        {"title": "Introduction to Law",                   "category": "Law",          "price": 32000, "rating": 3,
         "prodi": "Hukum",             "matkul": "Pengantar Hukum",     "kondisi": "Cukup",      "penjual": "Miko T.",    "rating_penjual": 3.7},
        {"title": "Constitutional Law",                    "category": "Law",          "price": 45000, "rating": 4,
         "prodi": "Hukum",             "matkul": "Hukum Tata Negara",   "kondisi": "Baik",       "penjual": "Nana B.",    "rating_penjual": 4.1},
        {"title": "Sociology: Core Concepts",              "category": "Social",       "price": 25000, "rating": 3,
         "prodi": "Sosiologi",         "matkul": "Sosiologi Dasar",     "kondisi": "Cukup",      "penjual": "Omar G.",    "rating_penjual": 3.0},
        {"title": "Psychology: Principles and Applications","category": "Social",      "price": 38000, "rating": 4,
         "prodi": "Psikologi",         "matkul": "Psikologi Umum",      "kondisi": "Baik",       "penjual": "Putri S.",   "rating_penjual": 4.4},
        # ── TEKNIK SIPIL & ARSITEKTUR ───────────────────────────────
        {"title": "Structural Analysis",                   "category": "Engineering",  "price": 58000, "rating": 4,
         "prodi": "Teknik Sipil",      "matkul": "Analisis Struktur",   "kondisi": "Baik",       "penjual": "Qori N.",    "rating_penjual": 4.2},
        {"title": "Fluid Mechanics",                       "category": "Engineering",  "price": 52000, "rating": 4,
         "prodi": "Teknik Sipil",      "matkul": "Mekanika Fluida",     "kondisi": "Sangat Baik", "penjual": "Rafi A.",    "rating_penjual": 4.6},
        {"title": "Principles of Foundation Engineering",  "category": "Engineering",  "price": 62000, "rating": 3,
         "prodi": "Teknik Sipil",      "matkul": "Geoteknik",           "kondisi": "Cukup",      "penjual": "Siska L.",   "rating_penjual": 3.5},
        {"title": "Electric Circuits",                     "category": "Engineering",  "price": 48000, "rating": 4,
         "prodi": "Teknik Elektro",    "matkul": "Rangkaian Listrik",   "kondisi": "Baik",       "penjual": "Tio W.",     "rating_penjual": 4.0},
        {"title": "Signals and Systems",                   "category": "Engineering",  "price": 55000, "rating": 4,
         "prodi": "Teknik Elektro",    "matkul": "Sinyal & Sistem",     "kondisi": "Sangat Baik", "penjual": "Uma K.",     "rating_penjual": 4.8},
        {"title": "Control Systems Engineering",           "category": "Engineering",  "price": 60000, "rating": 5,
         "prodi": "Teknik Elektro",    "matkul": "Sistem Kontrol",      "kondisi": "Baik",       "penjual": "Vino P.",    "rating_penjual": 4.5},
    ]

    df = pd.DataFrame(data)

    # Mapping kondisi → skor numerik
    kondisi_skor = {"Sangat Baik": 1.0, "Baik": 0.8, "Cukup": 0.6}
    df["skor_kondisi"] = df["kondisi"].map(kondisi_skor)

    # Normalisasi harga: 0 (termahal) → 1 (termurah)
    min_p, max_p = df["price"].min(), df["price"].max()
    df["skor_harga_norm"] = 1 - (df["price"] - min_p) / (max_p - min_p)

    # Normalisasi rating penjual: rating_penjual / 5
    df["skor_penjual_norm"] = df["rating_penjual"] / 5.0

    return df


# ─────────────────────────────────────────────────────────────
# STATE MANAGEMENT – Session State Initialization
# ─────────────────────────────────────────────────────────────
def init_state():
    """Inisialisasi semua nilai di st.session_state."""
    # Bobot awal seimbang: masing-masing 20%
    if "weights" not in st.session_state:
        st.session_state.weights = {
            "W_akad":    0.20,  # Skor Akademik
            "W_harga":   0.20,  # Skor Harga
            "W_kondisi": 0.20,  # Skor Kondisi
            "W_penjual": 0.20,  # Skor Rating Penjual
            "W_riwayat": 0.20,  # Skor Riwayat Kategori
        }
    # Riwayat interaksi pengguna
    if "history_categories" not in st.session_state:
        st.session_state.history_categories = []
    # Log feedback (ditampilkan di sidebar)
    if "feedback_log" not in st.session_state:
        st.session_state.feedback_log = []
    # Riwayat bobot (untuk animasi chart)
    if "weights_history" not in st.session_state:
        st.session_state.weights_history = [copy.deepcopy(st.session_state.weights)]


init_state()


# ─────────────────────────────────────────────────────────────
# MODUL 2 – MESIN PEMBOBOTAN MULTI-PARAMETER
# ─────────────────────────────────────────────────────────────
def compute_scores(df: pd.DataFrame,
                   user_prodi: str,
                   user_matkul: list[str],
                   user_price_min: int,
                   user_price_max: int,
                   history_categories: list[str],
                   weights: dict) -> pd.DataFrame:
    """
    Menghitung skor relevansi tiap buku berdasarkan profil pengguna
    dan bobot adaptif saat ini.

    Parameter
    ---------
    df               : DataFrame buku
    user_prodi       : Program studi pengguna
    user_matkul      : Daftar mata kuliah yang sedang ditempuh
    user_price_min/max: Rentang harga preferensi (Rp)
    history_categories: Riwayat kategori yang pernah diinteraksi
    weights          : Bobot adaptif saat ini (dict)

    Return
    ------
    df dengan kolom skor per parameter dan total_score.
    """
    result = df.copy()

    # ── a) Skor Akademik (W_akad) ─────────────────────────────
    # Nilai tertinggi jika prodi & matkul sama dengan profil user
    def akad_score(row):
        prodi_match  = 1.0 if row["prodi"] == user_prodi else 0.0
        matkul_match = 1.0 if row["matkul"] in user_matkul else 0.0
        # Gabungan: 60% prodi + 40% matkul
        return round(0.6 * prodi_match + 0.4 * matkul_match, 4)

    result["skor_akad"] = result.apply(akad_score, axis=1)

    # ── b) Skor Harga (W_harga) ───────────────────────────────
    # Tinggi jika harga masuk rentang preferensi user DAN di bawah rata-rata pasar
    avg_price = df["price"].mean()

    def harga_score(row):
        in_range   = 1.0 if user_price_min <= row["price"] <= user_price_max else 0.0
        below_avg  = 1.0 if row["price"] < avg_price else 0.5
        return round(0.5 * in_range + 0.5 * below_avg, 4)

    result["skor_harga"] = result.apply(harga_score, axis=1)

    # ── c) Skor Kondisi (W_kondisi) ───────────────────────────
    # Langsung dari kolom skor_kondisi (Sangat Baik=1.0, Baik=0.8, Cukup=0.6)
    result["skor_kondisi_param"] = result["skor_kondisi"]

    # ── d) Skor Rating Penjual (W_penjual) ────────────────────
    # Normalisasi: rating_penjual / 5
    result["skor_penjual"] = result["skor_penjual_norm"]

    # ── e) Skor Riwayat (W_riwayat) ──────────────────────────
    # Tinggi jika kategori buku pernah diinteraksi user sebelumnya
    result["skor_riwayat"] = result["category"].apply(
        lambda cat: 1.0 if cat in history_categories else 0.0
    )

    # ── f) Total Score (Weighted Sum) ─────────────────────────
    result["total_score"] = (
        weights["W_akad"]    * result["skor_akad"] +
        weights["W_harga"]   * result["skor_harga"] +
        weights["W_kondisi"] * result["skor_kondisi_param"] +
        weights["W_penjual"] * result["skor_penjual"] +
        weights["W_riwayat"] * result["skor_riwayat"]
    ).round(4)

    return result.sort_values("total_score", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
# MODUL 3 – PEMBOBOTAN ADAPTIF (Feedback Loop)
# ─────────────────────────────────────────────────────────────
def identify_dominant_param(book_row: pd.Series) -> str:
    """
    Identifikasi parameter dominan dari sebuah buku —
    parameter mana yang memberi kontribusi skor terbesar.
    """
    w = st.session_state.weights
    contributions = {
        "W_akad":    w["W_akad"]    * book_row["skor_akad"],
        "W_harga":   w["W_harga"]   * book_row["skor_harga"],
        "W_kondisi": w["W_kondisi"] * book_row["skor_kondisi_param"],
        "W_penjual": w["W_penjual"] * book_row["skor_penjual"],
        "W_riwayat": w["W_riwayat"] * book_row["skor_riwayat"],
    }
    return max(contributions, key=contributions.get)


def adjust_weights(dominant_param: str, delta: float):
    """
    Sesuaikan bobot secara adaptif:
    - Naikkan bobot parameter dominan sebesar delta.
    - Kurangi bobot lainnya secara proporsional agar total = 1.0.

    Parameter
    ---------
    dominant_param : kunci bobot yang akan dinaikkan (misal 'W_harga')
    delta          : besaran kenaikan (+0.05 untuk klik, +0.1 untuk beli)
    """
    weights = st.session_state.weights
    current  = weights[dominant_param]
    # Batas atas bobot tunggal: 0.60 (agar tidak mendominasi terlalu ekstrem)
    new_dominant = min(current + delta, 0.60)
    actual_delta = new_dominant - current  # delta nyata setelah klamping

    other_keys = [k for k in weights if k != dominant_param]
    other_total = sum(weights[k] for k in other_keys)

    # Kurangi bobot lain secara proporsional
    if other_total > 0:
        for k in other_keys:
            proportion = weights[k] / other_total
            weights[k] = max(weights[k] - proportion * actual_delta, 0.05)

    weights[dominant_param] = new_dominant

    # Normalisasi ulang agar benar-benar = 1.0 (mengatasi floating-point drift)
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 4)

    st.session_state.weights = weights
    # Simpan snapshot bobot untuk chart riwayat
    st.session_state.weights_history.append(copy.deepcopy(weights))


def handle_interaction(book_row: pd.Series, action: str):
    """
    Proses interaksi pengguna (klik/simpan atau beli).
    Perbarui riwayat kategori & jalankan feedback loop.
    """
    dominant = identify_dominant_param(book_row)
    delta = 0.05 if action == "klik" else 0.10

    # Tambahkan kategori ke riwayat
    cat = book_row["category"]
    if cat not in st.session_state.history_categories:
        st.session_state.history_categories.append(cat)

    adjust_weights(dominant, delta)

    param_labels = {
        "W_akad": "Akademik", "W_harga": "Harga",
        "W_kondisi": "Kondisi", "W_penjual": "Penjual", "W_riwayat": "Riwayat"
    }
    emoji = "🔖" if action == "klik" else "🛒"
    log_entry = (
        f"{emoji} <b>{book_row['title'][:30]}…</b> — "
        f"Param dominan: <b>{param_labels[dominant]}</b> "
        f"(+{'5' if action == 'klik' else '10'}%)"
    )
    st.session_state.feedback_log.insert(0, log_entry)


# ─────────────────────────────────────────────────────────────
# MODUL 1 – UI SIDEBAR (Profil Pengguna)
# ─────────────────────────────────────────────────────────────
def render_sidebar():
    """
    Render sidebar berisi:
    - Logo & identitas platform
    - Form profil pengguna (Program Studi, Mata Kuliah, Preferensi Harga)
    - Visualisasi bobot adaptif real-time
    - Log feedback interaksi
    """
    with st.sidebar:
        st.markdown("## 📚 BookCycle")
        st.markdown("<div style='color:#8a8fa8;font-size:0.82rem;margin-top:-10px;margin-bottom:16px;'>Platform Buku Bekas Mahasiswa</div>", unsafe_allow_html=True)
        st.divider()

        # ── Profil Pengguna ──────────────────────────────────
        st.markdown("### 👤 Profil Saya")

        all_prodi = [
            "Informatika", "Teknik Elektro", "Teknik Sipil",
            "Fisika", "Matematika", "Ekonomi", "Manajemen",
            "Akuntansi", "Biologi", "Kedokteran", "Keperawatan",
            "Hukum", "Sosiologi", "Psikologi"
        ]
        user_prodi = st.selectbox("🎓 Program Studi", all_prodi, index=0)

        all_matkul = [
            "Kalkulus", "Algoritma & Struktur Data", "Jaringan Komputer",
            "Pemrograman Lanjut", "Pemrograman Dasar", "Matematika Diskrit",
            "Basis Data", "Sistem Operasi", "Kecerdasan Buatan", "Machine Learning",
            "Fisika Dasar", "Fisika Matematika", "Mekanika Kuantum",
            "Mekanika Klasik", "Aljabar Linear", "Statistika",
            "Pengantar Ekonomi", "Ekonomi Mikro", "Keuangan Perusahaan",
            "Manajemen Pemasaran", "Akuntansi Dasar", "Biologi Umum",
            "Anatomi", "Farmakologi", "Biokimia", "Pengantar Hukum",
            "Hukum Tata Negara", "Sosiologi Dasar", "Psikologi Umum",
            "Analisis Struktur", "Mekanika Fluida", "Geoteknik",
            "Rangkaian Listrik", "Sinyal & Sistem", "Sistem Kontrol"
        ]
        user_matkul = st.multiselect(
            "📖 Mata Kuliah Saat Ini",
            all_matkul,
            default=["Algoritma & Struktur Data", "Pemrograman Lanjut"]
        )

        st.markdown("**💰 Rentang Harga (Rp)**")
        price_min, price_max = st.slider(
            "Harga", 0, 100000, (20000, 70000), step=5000,
            format="Rp %d", label_visibility="collapsed"
        )

        # Riwayat kategori yang sudah diinteraksi
        st.markdown("**📂 Riwayat Kategori:**")
        if st.session_state.history_categories:
            st.caption(", ".join(st.session_state.history_categories))
        else:
            st.caption("_Belum ada interaksi_")

        st.divider()

        # ── Visualisasi Bobot Adaptif ────────────────────────
        st.markdown("### ⚖️ Bobot Adaptif Saat Ini")
        weights = st.session_state.weights
        param_labels = {
            "W_akad": "Akademik", "W_harga": "Harga",
            "W_kondisi": "Kondisi", "W_penjual": "Penjual", "W_riwayat": "Riwayat"
        }
        colors = ["#f0c060", "#60a8f0", "#60d0a0", "#f07060", "#c080f0"]

        fig_weights = go.Figure(go.Bar(
            x=[param_labels[k] for k in weights],
            y=[v * 100 for v in weights.values()],
            marker_color=colors,
            text=[f"{v*100:.1f}%" for v in weights.values()],
            textposition="outside",
            textfont=dict(color="#e8e0d4", size=11),
        ))
        fig_weights.update_layout(
            plot_bgcolor="#16191f", paper_bgcolor="#16191f",
            font=dict(color="#c8c4d8", family="DM Sans"),
            yaxis=dict(range=[0, 70], showgrid=True,
                       gridcolor="#2a2d35", ticksuffix="%"),
            xaxis=dict(showgrid=False),
            margin=dict(l=0, r=0, t=10, b=0),
            height=200,
            showlegend=False,
        )
        st.plotly_chart(fig_weights, use_container_width=True)

        # ── Chart Riwayat Pergeseran Bobot ──────────────────
        if len(st.session_state.weights_history) > 1:
            st.markdown("**📈 Tren Pergeseran Bobot**")
            hist = st.session_state.weights_history
            fig_trend = go.Figure()
            for i, (key, label) in enumerate(param_labels.items()):
                fig_trend.add_trace(go.Scatter(
                    x=list(range(len(hist))),
                    y=[h[key] * 100 for h in hist],
                    name=label,
                    line=dict(color=colors[i], width=2),
                    mode="lines+markers",
                    marker=dict(size=5),
                ))
            fig_trend.update_layout(
                plot_bgcolor="#16191f", paper_bgcolor="#16191f",
                font=dict(color="#c8c4d8", family="DM Sans"),
                yaxis=dict(showgrid=True, gridcolor="#2a2d35", ticksuffix="%"),
                xaxis=dict(title="Interaksi ke-", showgrid=False),
                margin=dict(l=0, r=0, t=10, b=0),
                height=220,
                legend=dict(
                    orientation="h", y=-0.3,
                    font=dict(size=10)
                ),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # ── Reset Bobot ──────────────────────────────────────
        if st.button("🔄 Reset Bobot ke Default"):
            st.session_state.weights = {k: 0.20 for k in st.session_state.weights}
            st.session_state.history_categories = []
            st.session_state.feedback_log = []
            st.session_state.weights_history = [copy.deepcopy(st.session_state.weights)]
            st.rerun()

        st.divider()

        # ── Log Feedback ─────────────────────────────────────
        st.markdown("### 🗒️ Log Interaksi")
        if st.session_state.feedback_log:
            for entry in st.session_state.feedback_log[:8]:
                st.markdown(f"<div class='feedback-item'>{entry}</div>", unsafe_allow_html=True)
        else:
            st.caption("_Klik/Simpan atau Beli buku untuk melihat feedback loop bekerja_")

    return user_prodi, user_matkul, price_min, price_max


# ─────────────────────────────────────────────────────────────
# MODUL 4 – UI UTAMA (Hasil Rekomendasi)
# ─────────────────────────────────────────────────────────────
def render_book_card(idx: int, row: pd.Series, tab_prefix: str = ""):
    """
    Render satu kartu buku dengan info lengkap dan tombol interaksi.
    """
    kondisi_cls = {
        "Sangat Baik": "cond-sangat-baik",
        "Baik":        "cond-baik",
        "Cukup":       "cond-cukup",
    }.get(row["kondisi"], "")

    kondisi_icon = {"Sangat Baik": "✨", "Baik": "👍", "Cukup": "🔸"}.get(row["kondisi"], "")
    star_str = "⭐" * int(row["rating"]) + "☆" * (5 - int(row["rating"]))
    score_pct = int(row["total_score"] * 100)
    score_width = score_pct

    st.markdown(f"""
    <div class="book-card">
        <div class="rank-badge">#{idx+1}</div>
        <div class="book-title">{row['title']}</div>
        <div class="meta">
            <span>🎓 {row['prodi']}</span>
            <span>📖 {row['matkul']}</span>
            <span>🏷️ Rp {row['price']:,}</span>
            <span class="{kondisi_cls}">{kondisi_icon} {row['kondisi']}</span>
            <span>👤 {row['penjual']} ({row['rating_penjual']:.1f}/5)</span>
            <span>{star_str}</span>
            <span>📂 {row['category']}</span>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{score_width}%"></div>
        </div>
        <div class="score-label">Skor Relevansi: {row['total_score']:.4f}
            &nbsp;|&nbsp;
            Akademik: {row['skor_akad']:.2f} &nbsp;
            Harga: {row['skor_harga']:.2f} &nbsp;
            Kondisi: {row['skor_kondisi_param']:.2f} &nbsp;
            Penjual: {row['skor_penjual']:.2f} &nbsp;
            Riwayat: {row['skor_riwayat']:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tombol interaksi — menggunakan kolom agar rapi
    col_a, col_b, col_c = st.columns([1, 1, 4])
    with col_a:
        if st.button("🔖 Simpan", key=f"{tab_prefix}klik_{idx}_{row['title'][:10]}"):
            handle_interaction(row, "klik")
            st.toast(f"Buku disimpan! Bobot diperbarui 📊", icon="🔖")
            st.rerun()
    with col_b:
       if st.button("🛒 Beli", key=f"{tab_prefix}beli_{idx}_{row['title'][:10]}"):
            handle_interaction(row, "beli")
            st.toast(f"Pembelian tercatat! Bobot diperbarui 📊", icon="🛒")
            st.rerun()


def render_analytics(scored_df: pd.DataFrame):
    """
    Tampilkan analitik sederhana: distribusi kategori & harga buku yang direkomendasikan.
    """
    st.markdown('<div class="section-title">📊 Analitik Dataset</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        cat_counts = scored_df["category"].value_counts().reset_index()
        cat_counts.columns = ["Kategori", "Jumlah"]
        fig_cat = px.bar(
            cat_counts, x="Jumlah", y="Kategori", orientation="h",
            color="Jumlah", color_continuous_scale=["#2e3141", "#f0c060"],
            title="Distribusi Kategori Buku"
        )
        fig_cat.update_layout(
            plot_bgcolor="#1c1f2a", paper_bgcolor="#1c1f2a",
            font=dict(color="#c8c4d8"), title_font=dict(color="#f0c060"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0), height=280,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        fig_price = px.histogram(
            scored_df, x="price", nbins=12,
            color_discrete_sequence=["#60a8f0"],
            title="Distribusi Harga Buku (Rp)"
        )
        fig_price.update_layout(
            plot_bgcolor="#1c1f2a", paper_bgcolor="#1c1f2a",
            font=dict(color="#c8c4d8"), title_font=dict(color="#f0c060"),
            xaxis_title="Harga (Rp)", yaxis_title="Jumlah",
            margin=dict(l=0, r=0, t=40, b=0), height=280,
        )
        st.plotly_chart(fig_price, use_container_width=True)

    # Scatter: Skor Relevansi vs Harga
    fig_scatter = px.scatter(
        scored_df.head(20), x="price", y="total_score",
        color="kondisi", size="skor_penjual_norm",
        hover_data=["title", "prodi", "matkul"],
        color_discrete_map={
            "Sangat Baik": "#4caf88", "Baik": "#60a0f0", "Cukup": "#f0a040"
        },
        title="Skor Relevansi vs Harga (Top 20 Buku)",
        labels={"price": "Harga (Rp)", "total_score": "Skor Relevansi"}
    )
    fig_scatter.update_layout(
        plot_bgcolor="#1c1f2a", paper_bgcolor="#1c1f2a",
        font=dict(color="#c8c4d8"), title_font=dict(color="#f0c060"),
        margin=dict(l=0, r=0, t=40, b=0), height=300,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# MAIN APPLICATION FLOW
# ─────────────────────────────────────────────────────────────
def main():
    # ── Header ──────────────────────────────────────────────
    st.markdown("""
    <div class="bookcycle-header">
        <h1>📚 BookCycle</h1>
        <p>Sistem Rekomendasi Buku Bekas Berbasis Multi-Parameter dengan Pembobotan Adaptif</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar (Profil Pengguna) ────────────────────────────
    user_prodi, user_matkul, price_min, price_max = render_sidebar()

    # ── Load & Score Dataset ─────────────────────────────────
    df = load_dataset()
    scored_df = compute_scores(
        df,
        user_prodi=user_prodi,
        user_matkul=user_matkul,
        user_price_min=price_min,
        user_price_max=price_max,
        history_categories=st.session_state.history_categories,
        weights=st.session_state.weights
    )

    # ── Metrics Row ──────────────────────────────────────────
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("📚 Total Buku", len(df))
    col_m2.metric("🎯 Relevan (Skor ≥ 0.5)", len(scored_df[scored_df["total_score"] >= 0.5]))
    col_m3.metric("🏆 Skor Tertinggi", f"{scored_df['total_score'].max():.4f}")
    col_m4.metric("💰 Harga Termurah", f"Rp {df['price'].min():,}")

    st.divider()

    # ── Filter & Tampilkan Buku ──────────────────────────────
    tab_all, tab_top, tab_analytics = st.tabs(
        ["📋 Semua Rekomendasi", "🏆 Top 10", "📊 Analitik"]
    )

    with tab_all:
        st.markdown('<div class="section-title">Rekomendasi Berdasarkan Profil Anda</div>',
                    unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_query = st.text_input("🔍 Cari judul / mata kuliah", placeholder="contoh: Kalkulus")
        with col_f2:
            filter_kondisi = st.multiselect(
                "Kondisi", ["Sangat Baik", "Baik", "Cukup"],
                default=["Sangat Baik", "Baik", "Cukup"]
            )

        display_df = scored_df.copy()
        if search_query:
            q = search_query.lower()
            display_df = display_df[
                display_df["title"].str.lower().str.contains(q) |
                display_df["matkul"].str.lower().str.contains(q)
            ]
        if filter_kondisi:
            display_df = display_df[display_df["kondisi"].isin(filter_kondisi)]

        st.caption(f"Menampilkan {len(display_df)} buku")

        for i, (_, row) in enumerate(display_df.iterrows()):
            render_book_card(i, row, tab_prefix="all_")

    with tab_top:
        st.markdown('<div class="section-title">🏆 Top 10 Buku Terpersonalisasi</div>',
                    unsafe_allow_html=True)
        top10 = scored_df.head(10)
        for i, (_, row) in enumerate(top10.iterrows()):
            render_book_card(i, row, tab_prefix="top_")
    with tab_analytics:
        render_analytics(scored_df)

    # ── Footer ───────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#3a3d50;font-size:0.78rem;'>"
        "BookCycle © 2025 — Sistem Rekomendasi Multi-Parameter dengan Pembobotan Adaptif"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
