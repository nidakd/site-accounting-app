import streamlit as st
import pandas as pd
from src.database.connection import get_connection, get_db_engine

def toplu_yakit_yukle(data_df, donem):
    # This was defined in main.py but seemingly not used inside the tab implementation in main.py?
    # Actually in main.py tab logic, it implemented its own loop.
    # I'll rewrite the unified logic here.
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            for index, row in data_df.iterrows():
                # Daire numarasına göre unit_id'yi buluyoruz
                cur.execute("SELECT id FROM unit WHERE unit_number = %s", (str(row['Daire No']),))
                unit_res = cur.fetchone()
                if unit_res:
                    unit_id = unit_res[0]
                    tutar = row['Tutar']
                    cur.execute("""
                        INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                        VALUES (%s, 'FUEL', %s, %s, 'UNPAID')
                    """, (unit_id, tutar, donem))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Yükleme hatası: {e}")
            return False

def add_bulk_dues(site_id, amount, period_date):
    conn = get_connection()
    success_count = 0
    if conn:
        try:
            cur = conn.cursor()
            # --- unit tablosunda complex_id olmadığı için JOIN kullanıyoruz ---
            cur.execute("""
                SELECT u.id 
                FROM unit u
                JOIN building b ON u.building_id = b.id
                WHERE b.complex_id = %s 
                AND (u.is_exempt IS DISTINCT FROM TRUE)
            """, (site_id,))
            
            daireler = cur.fetchall()
            
            for d in daireler:
                cur.execute("""
                    INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                    VALUES (%s, 'DUES', %s, %s, 'UNPAID')
                """, (d[0], amount, period_date))
            
            conn.commit()
            success_count = len(daireler)
            cur.close()
            conn.close()
            return success_count
        except Exception as e:
            st.error(f"Hata: {e}")
            return 0
    return 0

def process_bulk_fuel_csv(site_id, df_yuklenen):
    conn = get_connection()
    success_count = 0
    if conn:
        try:
            cur = conn.cursor()
            for index, row in df_yuklenen.iterrows():
                # Daire numarasına göre ID bul
                cur.execute("""
                    SELECT u.id FROM unit u 
                    JOIN building b ON u.building_id = b.id 
                    WHERE u.unit_number = %s AND b.complex_id = %s
                """, (str(row['Daire No']), site_id))
                unit_res = cur.fetchone()
                
                # Tutar 0'dan büyükse kaydet
                if unit_res and float(row['Tutar']) > 0:
                    # Excel'deki 'Donem' sütununu kullanıyoruz
                    cur.execute("""
                        INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                        VALUES (%s, 'FUEL', %s, %s, 'UNPAID')
                    """, (unit_res[0], row['Tutar'], row['Donem']))
                    success_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            return success_count
        except Exception as e:
            st.error(f"Dosya işlenirken hata oluştu: {e}")
            return 0
    return 0

def process_past_debts_csv(site_id, df_gecmis):
    conn = get_connection()
    success_count = 0
    if conn:
        try:
            cur = conn.cursor()
            
            # Önce mevcut yanlış yüklenen eski borçları temizleyelim (Opsiyonel ama önerilir)
            cur.execute("DELETE FROM debt_item WHERE period_month < '2026-01-01' AND status = 'UNPAID'")
            
            for index, row in df_gecmis.iterrows():
                # Blok ve Daireyi beraber sorguluyoruz
                blok_adi = str(row.get('Blok', '')).strip()
                d_no = str(row.get('Daire No', '')).strip()
                
                cur.execute("""
                    SELECT u.id 
                    FROM unit u
                    JOIN building b ON u.building_id = b.id 
                    WHERE b.name = %s AND u.unit_number = %s AND b.complex_id = %s
                """, (blok_adi, d_no, site_id))
                unit_res = cur.fetchone()
                
                if unit_res:
                    u_id = unit_res[0]
                    borc_kalemleri = [
                        (row.get('Geçmiş Aidat Borcu', 0), 'DUES', '2025-12-31'),
                        (row.get('Ekim Yakıt', 0), 'FUEL', '2025-10-01'),
                        (row.get('Kasım Yakıt', 0), 'FUEL', '2025-11-01'),
                        (row.get('Aralık Yakıt', 0), 'FUEL', '2025-12-01'),
                        (row.get('Diğer Eksik Ödemeler', 0), 'OTHER', '2025-12-30')
                    ]
                    
                    for tutar, tur, tarih in borc_kalemleri:
                        try:
                            tutar_val = float(str(tutar).replace(',', '.')) if pd.notnull(tutar) else 0
                        except: tutar_val = 0

                        if tutar_val > 0:
                            cur.execute("""
                                INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                                VALUES (%s, %s, %s, %s, 'UNPAID')
                                ON CONFLICT (unit_id, type, period_month) DO UPDATE SET expected_amount = EXCLUDED.expected_amount
                            """, (u_id, tur, tutar_val, tarih))
                            success_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            return success_count
        except Exception as e:
            st.error(f"Hata: {e}")
            return 0
    return 0
