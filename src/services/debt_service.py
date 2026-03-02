import pandas as pd
from src.database.connection import get_db_engine, get_connection

def get_detayli_borc(daire_id):
    conn = get_connection()
    detay = {"aidat": 0.0, "yakit": 0.0, "toplam": 0.0}
    if conn:
        try:
            cur = conn.cursor()
            # Aidat ve Yakıtı ayrı ayrı topluyoruz
            query = """
                SELECT type, SUM(expected_amount) 
                FROM debt_item 
                WHERE unit_id = %s AND status != 'PAID'
                GROUP BY type
            """
            cur.execute(query, (daire_id,))
            rows = cur.fetchall()
            for row in rows:
                if row[0] == 'DUES': detay["aidat"] = float(row[1])
                if row[0] == 'FUEL': detay["yakit"] = float(row[1])
            
            detay["toplam"] = detay["aidat"] + detay["yakit"]
            cur.close()
            conn.close()
        except:
            pass
    return detay

def get_daire_extresi(daire_id):
    engine = get_db_engine()
    if engine:
        try:
            query = """
                SELECT period_month, type, expected_amount 
                FROM debt_item 
                WHERE unit_id = %s AND status != 'PAID'
                ORDER BY period_month ASC
            """
            df = pd.read_sql(query, engine, params=(daire_id,))
            
            if not df.empty:
                # Tarihleri Türkçeleştirme
                df['period_month'] = pd.to_datetime(df['period_month']).dt.strftime('%m/%Y')
                # Türleri Türkçeleştirme
                df['type'] = df['type'].replace({
                    'DUES': '🏠 Aidat', 
                    'FUEL': '🔥 Yakıt',
                    'OTHER': '📦 Diğer'
                })
                # Sütun isimlerini Türkçeleştirme
                df.columns = ['Dönem', 'Borç Türü', 'Tutar (TL)']
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()
