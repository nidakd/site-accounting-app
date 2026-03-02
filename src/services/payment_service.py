import pandas as pd
from src.database.connection import get_db_engine, get_connection
import streamlit as st

def get_daire_odemeleri(daire_id):
    engine = get_db_engine()
    if engine:
        try:
            # Dairenin yaptığı tüm ödemeleri en yeni tarihten başlayarak getiriyoruz
            query = """
                SELECT process_date, amount, description 
                FROM payment 
                WHERE unit_id = %s 
                ORDER BY process_date DESC
            """
            df = pd.read_sql(query, engine, params=(daire_id,))
            
            if not df.empty:
                # Tarihi gg/aa/yyyy formatına çevirelim
                df['process_date'] = pd.to_datetime(df['process_date']).dt.strftime('%d/%m/%Y')
                # Sütunları Türkçeleştirelim
                df.columns = ['Ödeme Tarihi', 'Tutar (TL)', 'Açıklama']
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def kaydet_odeme(site_id, daire_id, tutar, aciklama):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 1. Ödemeyi Kaydet
            cur.execute("""
                INSERT INTO payment (complex_id, unit_id, amount, process_date, description)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
            """, (site_id, daire_id, tutar, aciklama))
            
            # 2. BORÇ KAPATMA MANTIĞI:
            # Dairenin ödenmemiş en eski borçlarını tek tek bulalım
            cur.execute("""
                SELECT id, expected_amount FROM debt_item 
                WHERE unit_id = %s AND status != 'PAID' 
                ORDER BY period_month ASC
            """, (daire_id,))
            
            borclar = cur.fetchall()
            kalan_para = float(tutar)
            
            for borc_id, borc_tutar in borclar:
                if kalan_para >= float(borc_tutar):
                    # Borcun tamamını ödeyecek kadar para var
                    cur.execute("UPDATE debt_item SET status = 'PAID' WHERE id = %s", (borc_id,))
                    kalan_para -= float(borc_tutar)
                else:
                    # Para bitti, diğer borçlar ödenmemiş kalmaya devam eder
                    break
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Kayıt hatası: {e}")
            return False
    return False

def tahsilat_kaydet(unit_id, amount, p_type, description):
    # Bu fonksiyon main.py'de var ama kullanılmıyor gibi ya da kaydet_odeme ile aynı işi yapıyor.
    # main.py'den baktığımızda kaydet_odeme kullanılıyor UI'da. 
    # tahsilat_kaydet fonksiyonu tanımlanmış ama UI'da "kaydet_odeme" çağrılıyor.
    # Yine de taşıyalım.
    return kaydet_odeme(st.session_state.selected_site_id, unit_id, amount, description) 
