"""
Unit Debt Status Viewer
Konut sahipleri kendi borç durumlarını görebilecekleri sayfa
"""

import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine

def render_unit_debt_status():
    """
    Konut Sahibi Borç Sorgusu Sayfası
    """
    st.title("🏠 Daire Borç Durumu Sorgulama")
    
    st.info("💡 Dairenizi seçerek borç durumunuzu ve ödeme geçmişinizi görebilirsiniz.")
    
    engine = get_db_engine()
    
    # Daire Listesi
    try:
        daireler_query = """
        SELECT u.id, b.name || ' - Daire ' || u.unit_number as label
        FROM unit u
        JOIN building b ON u.building_id = b.id
        WHERE b.complex_id = %s
        ORDER BY b.name ASC, u.unit_number::int ASC
        """
        daireler_df = pd.read_sql(
            daireler_query, 
            engine, 
            params=(st.session_state.selected_site_id,)
        )
        
        if daireler_df.empty:
            st.warning("Daire verisi bulunamadı")
            return
        
        secilen_label = st.selectbox("Dairenizi Seçin:", daireler_df['label'])
        daire_id = int(daireler_df[daireler_df['label'] == secilen_label]['id'].values[0])
        
        # Daire Detayları
        daire_info_query = """
        SELECT b.name as blok, u.unit_number as daire_no, u.owner_name as sahibi
        FROM unit u
        JOIN building b ON u.building_id = b.id
        WHERE u.id = %s
        """
        daire_info = pd.read_sql(daire_info_query, engine, params=(daire_id,))
        
        if not daire_info.empty:
            row = daire_info.iloc[0]
            st.write(f"**Blok:** {row['blok']} | **Daire:** {row['daire_no']} | **Sahibi:** {row['sahibi']}")
        
        st.divider()
        
        # --- BORÇ ÖZETİ ---
        st.subheader("💰 Borç Özeti")
        
        # Borç toplamları
        debt_summary_query = """
        SELECT 
            type,
            COUNT(*) as borc_sayisi,
            SUM(expected_amount) as toplam
        FROM debt_item
        WHERE unit_id = %s AND status != 'PAID'
        GROUP BY type
        """
        
        debt_summary = pd.read_sql(debt_summary_query, engine, params=(daire_id,))
        
        aidat = 0.0
        yakit = 0.0
        diger = 0.0
        
        for idx, row in debt_summary.iterrows():
            if row['type'] == 'DUES':
                aidat = float(row['toplam'] or 0)
            elif row['type'] == 'FUEL':
                yakit = float(row['toplam'] or 0)
            elif row['type'] == 'OTHER':
                diger = float(row['toplam'] or 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏠 Aidat Borcu", f"₺{aidat:,.2f}")
        
        with col2:
            st.metric("🔥 Yakıt Borcu", f"₺{yakit:,.2f}")
        
        with col3:
            st.metric("📦 Diğer Borç", f"₺{diger:,.2f}")
        
        with col4:
            st.metric("📊 Toplam Borç", f"₺{aidat + yakit + diger:,.2f}")
        
        st.divider()
        
        # --- DETAYLI BORÇ LİSTESİ ---
        st.subheader("📋 Ödenmesi Gereken Borçlar")
        
        debt_detail_query = """
        SELECT 
            period_month,
            type,
            expected_amount,
            status
        FROM debt_item
        WHERE unit_id = %s
        ORDER BY period_month DESC
        """
        
        debt_detail = pd.read_sql(debt_detail_query, engine, params=(daire_id,))
        
        if not debt_detail.empty:
            debt_detail['period_month'] = pd.to_datetime(debt_detail['period_month']).dt.strftime('%m/%Y')
            debt_detail['type'] = debt_detail['type'].replace({
                'DUES': '🏠 Aidat', 
                'FUEL': '🔥 Yakıt',
                'OTHER': '📦 Diğer'
            })
            debt_detail['status'] = debt_detail['status'].replace({
                'PAID': '✅ Ödendi', 
                'UNPAID': '⏳ Bekleniyor'
            })
            
            debt_detail.columns = ['Dönem', 'Tür', 'Tutar (TL)', 'Durum']
            
            st.dataframe(debt_detail, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Herhangi bir borç bulunmamaktadır!")
        
        st.divider()
        
        # --- ÖDEME GEÇMİŞİ ---
        st.subheader("✅ Son Ödemeler")
        
        payment_query = """
        SELECT 
            process_date,
            amount,
            description
        FROM payment
        WHERE unit_id = %s
        ORDER BY process_date DESC
        LIMIT 10
        """
        
        payments = pd.read_sql(payment_query, engine, params=(daire_id,))
        
        if not payments.empty:
            payments['process_date'] = pd.to_datetime(payments['process_date']).dt.strftime('%d/%m/%Y %H:%M')
            payments.columns = ['Tarih', 'Tutar (TL)', 'Açıklama']
            st.dataframe(payments, use_container_width=True, hide_index=True)
        else:
            st.info("Henüz ödeme yapılmamış")
            
    except Exception as e:
        st.error(f"❌ Hata oluştu: {e}")
