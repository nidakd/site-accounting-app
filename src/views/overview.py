import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.overview_service import get_genel_istatistikler, get_aylik_tahsilat_verisi, get_blok_borc_verisi

def render_overview_page():
    st.header(f"📊 {st.session_state.selected_site_name} Genel Durum")
    
    # Fonksiyonu çağırıp istatistikleri alıyoruz
    stats = get_genel_istatistikler(st.session_state.selected_site_id)
    
    # Üst Metrik Kartları
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("💰 Toplam Tahsilat (Kasa)", f"₺{stats['toplam_tahsilat']:,.2f}")
    with m2:
        st.metric("🚨 Bekleyen Toplam Alacak", f"₺{stats['toplam_alacak']:,.2f}")
    with m3:
        st.metric("🏦 Kasa Bakiyesi", f"₺{stats['kasa_mevcut']:,.2f}")

    st.divider()
    
    # --- RAPORLAMA VE EXCEL ÇIKTISI ---
    st.subheader("📥 Veri Dışarı Aktar (Excel/CSV)")
    
    if st.button("📊 Güncel Borç Listesini Hazırla"):
        engine = get_db_engine()
        sorgu = """
            SELECT b.name as "Blok", 
                   u.unit_number as "Daire No", 
                   u.owner_name as "Ev Sahibi", 
                   d.type as "Tur", 
                   d.expected_amount as "Tutar", 
                   d.period_month as "Donem", 
                   d.status as "Durum"
            FROM debt_item d
            JOIN unit u ON d.unit_id = u.id
            JOIN building b ON u.building_id = b.id
            ORDER BY b.name ASC, u.unit_number::int ASC, d.period_month DESC
        """
        df_indir = pd.read_sql(sorgu, engine)
        
        if not df_indir.empty:
            df_indir['Tur'] = df_indir['Tur'].replace({
                'DUES': 'Aidat', 
                'FUEL': 'Yakıt',
                'OTHER': 'Diğer'
            })
            df_indir['Durum'] = df_indir['Durum'].replace({'UNPAID': 'Ödenmedi', 'PAID': 'Ödendi'})
            df_indir['Donem'] = pd.to_datetime(df_indir['Donem']).dt.strftime('%m/%Y')
            df_indir.columns = ["Blok", "Daire No", "Ev Sahibi", "Borç Türü", "Tutar (TL)", "Dönem", "Ödeme Durumu"]
            csv = df_indir.to_csv(index=False).encode('utf-8-sig')
            
            st.success("Liste başarıyla hazırlandı!")
            st.download_button(
                label="📥 Borç Listesini İndir (Türkçe)",
                data=csv,
                file_name='site_borc_listesi_guncel.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("İndirilecek borç verisi bulunamadı.")

    st.divider()

    # --- DİNAMİK GRAFİKLER ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🗓️ Aylık Tahsilat Trendi")
        tahsilat_df = get_aylik_tahsilat_verisi(st.session_state.selected_site_id)
        if not tahsilat_df.empty:
            st.bar_chart(tahsilat_df, x='ay', y='toplam', color="#2E7D32")
        else:
            st.info("Henüz tahsilat verisi bulunmuyor.")

    with c2:
        st.subheader("🏢 Blok Bazlı Borç Dağılımı")
        blok_borc_df = get_blok_borc_verisi(st.session_state.selected_site_id)
        if not blok_borc_df.empty:
            st.bar_chart(blok_borc_df, x='Blok', y='Toplam Borç', color="#C62828")
        else:
            st.success("✅ Tüm blokların borcu ödenmiş!")

    st.divider()
    
    # --- ÖZET TABLO ---
    st.subheader("📂 Genel Borç Dağılımı")
    
    engine = get_db_engine()
    if engine:
        dist_query = "SELECT type, SUM(expected_amount) FROM debt_item WHERE status != 'PAID' GROUP BY type"
        dist_df = pd.read_sql(dist_query, engine)
        
        if not dist_df.empty:
            dist_df['type'] = dist_df['type'].replace({'DUES': 'Aidat', 'FUEL': 'Yakıt'})
            st.dataframe(dist_df, use_container_width=True, hide_index=True)
