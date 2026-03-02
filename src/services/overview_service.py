import pandas as pd
from src.database.connection import get_db_engine, get_connection

def get_aylik_tahsilat_verisi(site_id):
    engine = get_db_engine()
    if engine:
        try:
            # Son 6 ayın tahsilatlarını getirir
            query = """
                SELECT TO_CHAR(process_date, 'Mon') as ay, SUM(amount) as toplam, MIN(process_date) as sirala
                FROM payment
                WHERE complex_id = %s
                GROUP BY ay
                ORDER BY sirala ASC
            """
            df = pd.read_sql(query, engine, params=(site_id,))
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def get_blok_borc_verisi(site_id):
    engine = get_db_engine()
    if engine:
        try:
            # Bloklara göre toplam borç dağılımı
            query = """
                SELECT b.name as "Blok", SUM(d.expected_amount) as "Toplam Borç"
                FROM debt_item d
                JOIN unit u ON d.unit_id = u.id
                JOIN building b ON u.building_id = b.id
                WHERE b.complex_id = %s AND d.status != 'PAID'
                GROUP BY b.name
                ORDER BY "Toplam Borç" DESC
            """
            df = pd.read_sql(query, engine, params=(site_id,))
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def get_genel_istatistikler(site_id):
    conn = get_connection()
    stats = {"toplam_alacak": 0.0, "toplam_tahsilat": 0.0, "kasa_mevcut": 0.0}
    if conn:
        try:
            cur = conn.cursor()
            # 1. Alacaklar
            cur.execute("SELECT SUM(expected_amount) FROM debt_item WHERE status != 'PAID'")
            stats["toplam_alacak"] = float(cur.fetchone()[0] or 0)

            # 2. Gelirler
            cur.execute("SELECT SUM(amount) FROM payment WHERE complex_id = %s", (site_id,))
            toplam_gelir = float(cur.fetchone()[0] or 0)
            stats["toplam_tahsilat"] = toplam_gelir

            # 3. Giderler 
            cur.execute("SELECT SUM(amount) FROM account_transaction WHERE type = 'EXPENSE'")
            toplam_gider = float(cur.fetchone()[0] or 0)

            stats["kasa_mevcut"] = toplam_gelir - toplam_gider
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"İstatistik hatası: {e}")
    return stats
