import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.personnel_service import kaydet_personel_odeme

def render_personnel_page():
    st.header("👷 Personel Yönetimi ve Maaş Takibi")
    
    tab1, tab2 = st.tabs(["👥 Personel Listesi", "💸 Maaş/Ödeme Yap"])
    
    engine = get_db_engine()

    with tab1:
        st.subheader("Aktif Personeller")
        # Veritabanındaki personelleri çekiyoruz
        personel_df = pd.read_sql(f"SELECT name as \"İsim\", role as \"Görev\", salary as \"Maaş\" FROM employee WHERE complex_id = {st.session_state.selected_site_id}", engine)
        
        if not personel_df.empty:
            st.table(personel_df)
        else:
            st.info("Henüz sisteme kayıtlı personel bulunmuyor.")

    with tab2:
        st.subheader("Ödeme Formu")
        with st.form("personel_odeme_formu", clear_on_submit=True):
            # Personel seçimi için listeyi tekrar çekelim
            p_list = pd.read_sql(f"SELECT id, name FROM employee WHERE complex_id = {st.session_state.selected_site_id}", engine)
            
            if not p_list.empty:
                secilen_p = st.selectbox("Personel Seçin:", p_list['name'])
                p_id = p_list[p_list['name'] == secilen_p]['id'].values[0]
                
                tutar = st.number_input("Ödeme Tutarı (TL):", min_value=0.0, step=100.0)
                aciklama = st.text_input("Açıklama:", value=f"{secilen_p} - Ocak 2026 Maaş Ödemesi")
                
                if st.form_submit_button("Ödemeyi Onayla"):
                    if tutar > 0:
                        if kaydet_personel_odeme(st.session_state.selected_site_id, int(p_id), tutar, aciklama):
                            st.success(f"{secilen_p} personeline ₺{tutar} ödeme yapıldı ve kasadan düşüldü.")
                    else:
                        st.warning("Lütfen tutar giriniz.")
            else:
                st.error("Ödeme yapabilmek için önce personel eklemelisiniz.")
