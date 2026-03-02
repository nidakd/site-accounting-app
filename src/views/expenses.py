import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.expense_service import kaydet_gider

def render_expenses_page():
    st.header("💸 Site Gider Yönetimi")
    
    tab1, tab2 = st.tabs(["➕ Yeni Gider Ekle", "📋 Geçmiş Giderler"])
    
    with tab1:
        with st.form("gider_formu", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                miktar = st.number_input("Harcama Tutarı (TL):", min_value=0.0, step=50.0)
                kategori = st.selectbox("Gider Kategorisi:", 
                    ["Temizlik Ücreti", "Asansör Bakımı", "Elektrik Faturası", "Yakıt Ödemesi", "Su Faturası", "Huzur Hakkı", "Temizlik Malzemesi", "Diğer"])
            with col2:
                tarih = st.date_input("Harcama Tarihi:")
                aciklama = st.text_area("Harcama Detayı:", placeholder="Örn: X asansör firması aylık bakım bedeli")
            
            submit = st.form_submit_button("❌ Gideri Kasadan Düş")
            
            if submit:
                if miktar > 0:
                    if kaydet_gider(st.session_state.selected_site_id, miktar, kategori, aciklama):
                        st.success(f"Başarılı: {kategori} için ₺{miktar} gider kaydedildi.")
                        st.balloons()
                else:
                    st.warning("Lütfen harcama tutarını giriniz.")

    with tab2:
        st.subheader("📋 Son Harcamalar")
        engine = get_db_engine()
        # account_transaction tablosundaki EXPENSE (Gider) kayıtlarını çekiyoruz
        gider_query = """
                SELECT process_date as "Tarih", category as "Kategori", amount as "Tutar", description as "Açıklama"
                FROM account_transaction 
                WHERE type = 'EXPENSE'
                ORDER BY process_date DESC
        """
        giderler_df = pd.read_sql(gider_query, engine)
        
        if not giderler_df.empty:
            st.dataframe(giderler_df, use_container_width=True, hide_index=True)
        else:
            st.info("Henüz kaydedilmiş bir gider bulunmuyor.")
