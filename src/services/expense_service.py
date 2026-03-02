import streamlit as st
from src.database.connection import get_connection

def kaydet_gider(site_id, miktar, kategori, aciklama):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 'transaction_type' yerine 'type'
            query = """
                INSERT INTO account_transaction (complex_id, type, category, amount, process_date, description)
                VALUES (%s, 'EXPENSE', %s, %s, CURRENT_TIMESTAMP, %s)
            """
            cur.execute(query, (site_id, kategori, miktar, aciklama))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Gider kaydedilirken hata oluştu: {e}")
            return False
