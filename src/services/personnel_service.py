import streamlit as st
from src.database.connection import get_connection

def kaydet_personel_odeme(site_id, personel_id, miktar, aciklama):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 1. Personel ödemesini kaydet
            cur.execute("""
                INSERT INTO account_transaction (complex_id, type, category, amount, process_date, description)
                VALUES (%s, 'EXPENSE', 'Personel Maaş', %s, CURRENT_TIMESTAMP, %s)
            """, (site_id, miktar, aciklama))
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Ödeme kaydedilirken hata: {e}")
            return False
