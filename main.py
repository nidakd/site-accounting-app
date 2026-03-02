import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Import connections
from src.database.connection import get_db_engine

# Import Auth
from src.auth.auth import check_password

# Import Views
from src.views.overview import render_overview_page
from src.views.buildings import render_buildings_page
from src.views.payments import render_payments_page
from src.views.expenses import render_expenses_page
from src.views.personnel import render_personnel_page
from src.views.bulk_ops import render_bulk_ops_page

load_dotenv()

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Site Yönetim Paneli", layout="wide")

# --- SİTE SEÇİM MANTIĞI ---
if 'selected_site_id' not in st.session_state:
    # Karşılama Ekranı
    st.title("🏙️ Site Yönetim Sistemine Hoş Geldiniz")
    st.info("Devam etmek için lütfen yönetmek istediğiniz siteyi seçin.")
    
    engine = get_db_engine()
    if engine:
        query = "SELECT id, name FROM complex_properties"
        sites_df = pd.read_sql(query, engine)

        if not sites_df.empty:
            secilen_ad = st.selectbox("Site Seçiniz:", sites_df['name'])
            site_id = int(sites_df[sites_df['name'] == secilen_ad]['id'].values[0])
            
            if st.button("Sisteme Giriş Yap"):
                st.session_state.selected_site_id = site_id
                st.session_state.selected_site_name = secilen_ad
                st.rerun()
else:

    if not check_password():
        st.stop()


    # --- ANA PANEL (SİTE SEÇİLDİKTEN SONRA) ---
    st.sidebar.title(f"📍 {st.session_state.selected_site_name}")
    st.sidebar.success(f"🔓 Giriş: nidakd")
    
    # Sol Menü Modülleri
    menu = st.sidebar.radio(
    "Menü",
    ["📊 Genel Bakış", "💰 Kasa (Tahsilat)", "🏢 Bloklar ve Daireler", "📜 Giderler", "👷 Personeller", "📢 Toplu İşlemler"]
    )

    if st.sidebar.button("🔄 Site Değiştir"):
        del st.session_state.selected_site_id
        st.session_state["password_correct"] = False
        st.rerun()

    # View Routing
    if menu == "📊 Genel Bakış":
        render_overview_page()
        
    elif menu == "🏢 Bloklar ve Daireler":
        render_buildings_page()

    elif menu == "💰 Kasa (Tahsilat)":
        render_payments_page()

    elif menu == "👷 Personeller":
        render_personnel_page()

    elif menu == "📜 Giderler":
        render_expenses_page()

    elif menu == "📢 Toplu İşlemler":
        render_bulk_ops_page()
