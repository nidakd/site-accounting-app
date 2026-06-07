import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.overview_service import get_genel_istatistikler, get_aylik_tahsilat_verisi, get_blok_borc_verisi

def render_overview_page():
    st.set_page_config(layout="wide")
    
    # Başlık ve İstatistikler
    col_title, col_date = st.columns([3, 1])
    with col_title:
        st.title(f"📊 {st.session_state.selected_site_name}")
    with col_date:
        st.metric("📅 Bugün", pd.Timestamp.now().strftime('%d/%m/%Y'))
    
    # Fonksiyonu çağırıp istatistikleri alıyoruz
    stats = get_genel_istatistikler(st.session_state.selected_site_id)
    engine = get_db_engine()
    
    # --- TEMEL İSTATİSTİKLER (Kompakt 6 Sütun) ---
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("💰 Kasa", f"₺{stats['kasa_mevcut']:,.0f}", help="Toplam tahsilanan para")
    
    with col2:
        st.metric("💳 Beklenen", f"₺{stats['toplam_alacak']:,.0f}", help="Ödenmemiş borç")
    
    with col3:
        # Tahsilat Oranı
        try:
            df = pd.read_sql("""
                SELECT CASE WHEN SUM(expected_amount) > 0 THEN
                    (SUM(CASE WHEN status = 'PAID' THEN expected_amount ELSE 0 END) / SUM(expected_amount) * 100)
                ELSE 0 END as oran
                FROM debt_item WHERE unit_id IN (SELECT id FROM unit WHERE building_id IN (
                    SELECT id FROM building WHERE complex_id = %s))
            """, engine, params=(st.session_state.selected_site_id,))
            tahsilat_orani = float(df['oran'].iloc[0] or 0)
            delta_color = "🟢" if tahsilat_orani >= 80 else "🟡" if tahsilat_orani >= 60 else "🔴"
        except:
            tahsilat_orani = 0.0
            delta_color = "🔴"
        
        st.metric(f"{delta_color} Tahsilat", f"{tahsilat_orani:.0f}%", delta="Hedef: 95%")
    
    with col4:
        # Vadegeçmiş Yüzde
        try:
            df = pd.read_sql("""
                SELECT CASE WHEN SUM(expected_amount) > 0 THEN
                    (SUM(CASE WHEN CURRENT_DATE - period_month > interval '30 days' 
                              THEN expected_amount ELSE 0 END) / SUM(expected_amount) * 100)
                ELSE 0 END as pct
                FROM debt_item WHERE status != 'PAID' AND unit_id IN (
                    SELECT id FROM unit WHERE building_id IN (
                        SELECT id FROM building WHERE complex_id = %s))
            """, engine, params=(st.session_state.selected_site_id,))
            vadegecmis = float(df['pct'].iloc[0] or 0)
            vade_delta = "🟢" if vadegecmis < 10 else "🟡" if vadegecmis < 25 else "🔴"
        except:
            vadegecmis = 0.0
            vade_delta = "🔴"
        
        st.metric(f"{vade_delta} Vade Geçmiş", f"{vadegecmis:.0f}%", delta="En az olmalı")
    
    with col5:
        # Ortalama Borç
        try:
            df = pd.read_sql("""
                SELECT AVG(expected_amount) as ort FROM debt_item 
                WHERE status != 'PAID' AND unit_id IN (
                    SELECT id FROM unit WHERE building_id IN (
                        SELECT id FROM building WHERE complex_id = %s))
            """, engine, params=(st.session_state.selected_site_id,))
            ort_borc = float(df['ort'].iloc[0] or 0)
        except:
            ort_borc = 0.0
        
        st.metric("💸 Ort. Borç", f"₺{ort_borc:,.0f}")
    
    with col6:
        # Toplam Daire
        try:
            df = pd.read_sql("""
                SELECT COUNT(*) as total FROM unit 
                WHERE building_id IN (SELECT id FROM building WHERE complex_id = %s)
            """, engine, params=(st.session_state.selected_site_id,))
            total_daire = int(df['total'].iloc[0])
        except:
            total_daire = 0
        
        st.metric("🏘️ Toplam Daire", total_daire)
    
    st.divider()
    
    # --- GÖRSEL VERİ (3 Grafik yan yana) ---
    chart1, chart2, chart3 = st.columns(3)
    
    # --- GÖRSEL VERİ (3 Grafik yan yana) ---
    chart1, chart2, chart3 = st.columns(3)
    
    with chart1:
        st.subheader("🗓️ Aylık Tahsilat")
        tahsilat_df = get_aylik_tahsilat_verisi(st.session_state.selected_site_id)
        if not tahsilat_df.empty:
            st.bar_chart(tahsilat_df, x='ay', y='toplam', color="#2E7D32")
        else:
            st.info("Veri yok")

    with chart2:
        st.subheader("🏢 Blok Borç Dağılımı")
        blok_borc_df = get_blok_borc_verisi(st.session_state.selected_site_id)
        if not blok_borc_df.empty:
            st.bar_chart(blok_borc_df, x='Blok', y='Toplam Borç', color="#C62828")
        else:
            st.success("✅ Borç yok")

    with chart3:
        st.subheader("📊 Borç Türü Dağılımı")
        try:
            dist_query = """
                SELECT type, SUM(expected_amount) as toplam 
                FROM debt_item WHERE status != 'PAID' GROUP BY type
            """
            dist_df = pd.read_sql(dist_query, engine)
            if not dist_df.empty:
                dist_df['type'] = dist_df['type'].replace({'DUES': 'Aidat', 'FUEL': 'Yakıt', 'OTHER': 'Diğer'})
                st.bar_chart(dist_df.set_index('type'), color="#FF6B35")
            else:
                st.success("✅ Borç yok")
        except:
            st.info("Veri yok")
    
    st.divider()
    
    # --- EN YÜKSEK BORÇLULAR (4 Sütun - Kompakt) ---
    st.subheader("🚨 En Yüksek 8 Borçlu (Acil Müdahale Gereken)")
    
    try:
        top_debtors = """
        SELECT 
            b.name as blok,
            u.unit_number as daire,
            u.owner_name as sahibi,
            SUM(di.expected_amount) as borc,
            MIN(di.period_month) as ilk_borc_tarihi,
            EXTRACT(DAY FROM CURRENT_DATE - MIN(di.period_month)) as gun
        FROM debt_item di
        JOIN unit u ON di.unit_id = u.id
        JOIN building b ON u.building_id = b.id
        WHERE di.status != 'PAID' AND b.complex_id = %s
        GROUP BY b.id, u.id, b.name, u.unit_number, u.owner_name
        ORDER BY borc DESC
        LIMIT 8
        """
        
        df_top = pd.read_sql(top_debtors, engine, params=(st.session_state.selected_site_id,))
        
        if not df_top.empty:
            # 4 sütuna böl, her sütunda 2 borçlu
            cols = st.columns(4)
            
            for idx, row in enumerate(df_top.itertuples()):
                col_idx = (idx // 2) % 4  # Her 2 satır = 1 sütun
                with cols[col_idx]:
                    # Risk seviyesine göre renk
                    if row.borc > 5000:
                        emoji = "🔴"
                        risk = "CRİTİK"
                    elif row.borc > 2000:
                        emoji = "🟠"
                        risk = "YÜKSEK"
                    else:
                        emoji = "🟡"
                        risk = "ORTA"
                    
                    st.info(f"""
                    {emoji} **{row.blok} - Daire {row.daire}**
                    
                    👤 {row.sahibi}
                    
                    💰 Borç: ₺{row.borc:,.0f}
                    ⏰ {int(row.gun)} gün gecikmiş
                    
                    **Risk:** {risk}
                    """)
        else:
            st.success("✅ Herhangi bir borç bulunmamaktadır!")
    except Exception as e:
        st.warning(f"Veri yüklenemedi: {e}")
    
    st.divider()
    
    # --- RAPORLAR VE İNDİRMELER (2 sütun) ---
    rep1, rep2 = st.columns(2)
    
    with rep1:
        st.subheader("📥 Borç Listesi İndir")
        if st.button("📊 Güncel Tüm Borçları Hazırla", key="debt_export"):
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
                
                st.download_button(
                    label="📥 Tüm Borçları Excel'e İndir",
                    data=csv,
                    file_name=f'site_borc_listesi_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
                st.success("✅ Dosya hazır!")
    
    with rep2:
        st.subheader("🚨 Vadegeçmiş Borçlar")
        try:
            overdue_query = """
            SELECT 
                b.name as "Blok",
                u.unit_number as "Daire",
                u.owner_name as "Sahibi",
                SUM(di.expected_amount) as "Tutar",
                EXTRACT(DAY FROM CURRENT_DATE - MIN(di.period_month)) as "Gün"
            FROM debt_item di
            JOIN unit u ON di.unit_id = u.id
            JOIN building b ON u.building_id = b.id
            WHERE di.status != 'PAID' 
                AND CURRENT_DATE - di.period_month > interval '60 days'
                AND b.complex_id = %s
            GROUP BY b.name, u.unit_number, u.owner_name
            ORDER BY "Tutar" DESC
            LIMIT 5
            """
            
            df_overdue = pd.read_sql(overdue_query, engine, params=(st.session_state.selected_site_id,))
            
            if not df_overdue.empty:
                st.dataframe(df_overdue, use_container_width=True, hide_index=True)
                
                # İndirme butonu
                csv = df_overdue.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Vadegeçmiş Listesi İndir",
                    data=csv,
                    file_name=f'vadegecmis_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            else:
                st.success("✅ 60 günden fazla vadegeçmiş borç yok!")
        except Exception as e:
            st.warning(f"Hata: {e}")
