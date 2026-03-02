import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.bulk_ops_service import add_bulk_dues, process_bulk_fuel_csv, process_past_debts_csv

def render_bulk_ops_page():
    st.header("📢 Toplu Borçlandırma Paneli")
    tab1, tab2, tab3 = st.tabs(["🏠 Sabit Aidat", "🔥 Yakıt (Excel)", "📅 Geçmiş Borç Yükle"])

    with tab1:
        st.subheader("Tüm Siteye Sabit Aidat Yansıt")
        st.info("💡 Bu işlem, muaf olarak işaretlenen yöneticileri otomatik olarak atlar.")
        
        with st.form("toplu_aidat_form"):
            col1, col2 = st.columns(2)
            with col1:
                aidat_tutar = st.number_input("Aidat Tutarı (TL):", min_value=0.0, step=50.0, value=500.0)
            with col2:
                aidat_ay = st.date_input("Aidat Dönemi:", key="aidat_date")
            
            if st.form_submit_button("🚀 Aidatları Tüm Siteye Yansıt"):
                 count = add_bulk_dues(st.session_state.selected_site_id, aidat_tutar, aidat_ay)
                 if count > 0:
                     st.success(f"Başarılı! {count} daireye ₺{aidat_tutar} aidat borcu girildi.")
                     st.balloons()
                 else:
                     st.warning("İşlem yapılamadı veya hiç daire bulunamadı.")

    with tab2:
        st.subheader("Daire Bazlı Farklı Yakıt Girişi")
        st.info("💡 Şablondaki 'Dönem' kısmını YYYY-AA-GG (Örn: 2026-01-01) formatında doldurun.")
        
        engine = get_db_engine()
        # 1. ADIM: Şablon Hazırlama (Dönem sütunu eklendi)
        # Şu anki ayın ilk gününü otomatik alalım (Her ay değişir)
        otomatik_donem = pd.Timestamp.now().replace(day=1).strftime('%Y-%m-%d')
        
        sablon_sorgu = f"""
            SELECT u.unit_number as "Daire No", u.owner_name as "Ev Sahibi", 
                   0.0 as "Tutar", '{otomatik_donem}' as "Donem" 
            FROM unit u 
            JOIN building b ON u.building_id = b.id
            WHERE b.complex_id = %s 
            ORDER BY b.name ASC, u.unit_number::int ASC
        """
        sablon_df = pd.read_sql(sablon_sorgu, engine, params=(st.session_state.selected_site_id,))
        
        csv_sablon = sablon_df.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 1. Adım: Yakıt Şablonunu İndir",
            data=csv_sablon,
            file_name='yakit_yukleme_sablonu.csv',
            mime='text/csv'
        )
        
        st.divider()
        
        # 2. ADIM: Dosya Yükleme
        yuklenen_dosya = st.file_uploader("Doldurduğunuz dosyayı yükleyin", type=['csv'], key="yakit_csv_up")
        
        if yuklenen_dosya and st.button("🚀 3. Adım: Yakıt Borçlarını İşle"):
            try:
                df_yuklenen = pd.read_csv(yuklenen_dosya)
                count = process_bulk_fuel_csv(st.session_state.selected_site_id, df_yuklenen)
                
                if count > 0:
                    st.success(f"İşlem Tamam! {count} daireye yakıt borçları tarihleriyle birlikte girildi.")
                    st.balloons()
                else:
                     st.warning("Veri işlenemedi.")
            except Exception as e:
                st.error(f"Dosya işlenirken hata oluştu: {e}")
    
    with tab3:
        st.subheader("📅 Geçmiş Dönem Detaylı Borç Aktarımı")
        st.info("💡 Blok bazlı ayrım için lütfen yeni şablonu indirin ve kullanın.")
        
        engine = get_db_engine()
        # 1. ADIM: Blok Bilgili Şablon Hazırlama
        sablon_sorgu = """
            SELECT b.name as "Blok", u.unit_number as "Daire No", u.owner_name as "Ev Sahibi", 
                   0.0 as "Gecmis_Aidat", 0.0 as "Ekim_Yakit", 
                   0.0 as "Kasim_Yakit", 0.0 as "Aralik_Yakit", 0.0 as "Diger"
            FROM unit u 
            JOIN building b ON u.building_id = b.id
            WHERE b.complex_id = %s 
            ORDER BY b.name ASC, u.unit_number::int ASC
        """
        sablon_df = pd.read_sql(sablon_sorgu, engine, params=(st.session_state.selected_site_id,))
        
        sablon_df.columns = ["Blok", "Daire No", "Ev Sahibi", "Geçmiş Aidat Borcu", "Ekim Yakıt", "Kasım Yakıt", "Aralık Yakıt", "Diğer Eksik Ödemeler"]
        
        st.download_button(
            label="📥 1. Adım: Yeni Bloklu Şablonu İndir",
            data=sablon_df.to_csv(index=False).encode('utf-8-sig'),
            file_name='bloklu_gecmis_borclar.csv',
            mime='text/csv'
        )
        
        st.divider()
        
        # 2. ADIM: Dosya Yükleme
        gecmis_dosya = st.file_uploader("Blok Bilgisi İçeren Listeyi Yükleyin", type=['csv'], key="detayli_gecmis_up")
        
        if gecmis_dosya and st.button("🚀 2. Adım: Tüm Geçmişi Sisteme Aktar"):
            try:
                bytes_data = gecmis_dosya.getvalue()
                
                # Encoding detection strategy: Try UTF-8 first, then Turkish CP1254
                encoding_used = 'utf-8-sig'
                try:
                    decoded_text = bytes_data.decode(encoding_used)
                except UnicodeDecodeError:
                    encoding_used = 'cp1254'
                    decoded_text = bytes_data.decode(encoding_used)
                
                ham_dosya = decoded_text.splitlines()
                
                baslik_satiri_index = 0
                for i, satir in enumerate(ham_dosya):
                    if "Blok" in satir or "Daire No" in satir:
                        baslik_satiri_index = i
                        break
                
                gecmis_dosya.seek(0)
                df_gecmis = pd.read_csv(gecmis_dosya, sep=None, engine='python', encoding=encoding_used, skiprows=baslik_satiri_index)
                df_gecmis.columns = [str(c).strip() for c in df_gecmis.columns]
                
                count = process_past_debts_csv(st.session_state.selected_site_id, df_gecmis)
                st.success(f"✅ Başarılı! {count} adet kayıt doğru bloklara eşlenerek yüklendi.")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Hata: {e}")
