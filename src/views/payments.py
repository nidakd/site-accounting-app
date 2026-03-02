import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.connection import get_db_engine
from src.services.payment_service import kaydet_odeme
from src.utils.receipt import generate_receipt_html, generate_receipt_text

def render_payments_page():
    st.header("💰 Yeni Tahsilat Girişi")
    
    engine = get_db_engine()

    # 1. Daire listesini çekelim (Seçim kutusu için)
    daire_sorgu = f"""
        SELECT u.id, b.name || ' - Daire ' || u.unit_number || ' (' || u.owner_name || ')' as label
        FROM unit u
        JOIN building b ON u.building_id = b.id
        WHERE b.complex_id = {st.session_state.selected_site_id}
        ORDER BY b.name ASC, u.unit_number::int ASC
    """
    daireler_df = pd.read_sql(daire_sorgu, engine)
    
    # 2. Ödeme Formu
    with st.form("tahsilat_formu"):
        secilen_daire_label = st.selectbox("Ödeme Yapan Daire:", daireler_df['label'])
        daire_id = int(daireler_df[daireler_df['label'] == secilen_daire_label]['id'].values[0])

        tutar = st.number_input("Ödenen Tutar (TL):", min_value=0.0, step=100.0)
        aciklama = st.text_input("Açıklama:", placeholder="Örn: Ocak 2026 Aidatı")
        
        submit_button = st.form_submit_button("💳 Ödemeyi Sisteme İşle")
        
    if submit_button:
        if tutar > 0:
            # Tüm sayısal değerleri int() veya float() içine alarak garantiye alıyoruz
            s_id = int(st.session_state.selected_site_id)
            d_id = int(daire_id)
            t_val = float(tutar)
            
            basarili = kaydet_odeme(s_id, d_id, t_val, aciklama)
            if basarili:
                st.balloons()
                
                # --- MAKBUZ OLUŞTURMA ---
                st.success("✅ Ödeme Başarıyla Kaydedildi!")
                
                islem_tarihi = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                makbuz_metni = generate_receipt_text(st.session_state.selected_site_name, secilen_daire_label, t_val, aciklama, islem_tarihi)
                makbuz_html = generate_receipt_html(st.session_state.selected_site_name, secilen_daire_label, t_val, aciklama, islem_tarihi)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.code(makbuz_metni, language="text")
                
                with c2:
                    st.success("Belge hazırlandı! Yazdırabilir veya PDF olarak kaydedebilirsiniz.")
                    st.download_button(
                        label="️ Makbuzu Yazdır / İndir (HTML)",
                        data=makbuz_html,
                        file_name=f"tahsilat_makbuzu_{d_id}_{datetime.now().strftime('%Y%m%d%H%M')}.html",
                        mime="text/html"
                    )
