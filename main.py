import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


@st.cache_resource
def get_db_engine():
    """SQLAlchemy engine oluşturur ve önbelleğe alır."""
    try:
        db_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası (Engine): {e}")
        return None

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

def check_password():
    """Kullanıcı adı ve şifreyi kontrol eder."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Giriş Ekranı
    st.title("🔐 Yönetim Paneli")
    with st.container():
        user = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if user == "nidakd" and pw == "muhasebe123":
                st.session_state["password_correct"] = True
                st.rerun() # Bilgiler doğruysa sayfayı yenile ve içeri al
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı!")
    return False
    

def toplu_yakit_yukle(data_df, donem):
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
        

def tahsilat_kaydet(unit_id, amount, p_type, description):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 1. Ödemeyi kaydet
            cur.execute("""
                INSERT INTO payment (complex_id, unit_id, amount, payment_type, process_date, description)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s) RETURNING id
            """, (st.session_state.selected_site_id, unit_id, amount, p_type, description))
            
            # 2. BORÇ KAPATMA MANTIĞI: 
            # Dairenin ödenmemiş en eski borçlarını getir
            cur.execute("""
                SELECT id, expected_amount FROM debt_item 
                WHERE unit_id = %s AND status != 'PAID' 
                ORDER BY period_month ASC
            """, (unit_id,))
            
            borclar = cur.fetchall()
            kalan_odeme = float(amount)
            
            for borc_id, borc_tutar in borclar:
                if kalan_odeme >= float(borc_tutar):
                    # Borcun tamamını kapat
                    cur.execute("UPDATE debt_item SET status = 'PAID' WHERE id = %s", (borc_id,))
                    kalan_odeme -= float(borc_tutar)
                elif kalan_odeme > 0:
                    pass
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Hata: {e}")
    return False

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
                df['type'] = df['type'].replace({'DUES': '🏠 Aidat', 'FUEL': '🔥 Yakıt'})
                # Sütun isimlerini Türkçeleştirme
                df.columns = ['Dönem', 'Borç Türü', 'Tutar (TL)']
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

@st.dialog("Daire Cari Hesap Detayı", width="large")
def daire_detay_penceresi(row, borclar):
    st.write(f"### 🚪 Daire No: {row['unit_number']} - {row['owner_name']}")
    
    # Üst Bilgi Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric("Güncel Borç", f"₺{borclar['toplam']:,.2f}")
    
    # Sekmeli yapı (Tabs) kullanarak ekranı daha düzenli yapalım
    tab1, tab2 = st.tabs(["📉 Ödenmemiş Borçlar", "💰 Ödeme Geçmişi (Makbuzlar)"])
    
    with tab1:
        st.write("#### Dönem Bazlı Borç Dökümü")
        extre_df = get_daire_extresi(int(row['id']))
        if not extre_df.empty:
            st.dataframe(extre_df, use_container_width=True, hide_index=True)
        else:
            st.success("Harika! Bu dairenin hiç borcu yok.")
            
    with tab2:
        st.write("#### Yapılan Tahsilatlar")
        odeme_df = get_daire_odemeleri(int(row['id']))
        if not odeme_df.empty:
            st.dataframe(odeme_df, use_container_width=True, hide_index=True)
            st.info("💡 Yukarıdaki liste, sistemde kayıtlı olan tüm banka ve nakit ödemelerini gösterir.")
        else:
            st.warning("Bu daireye ait henüz bir ödeme kaydı bulunamadı.")
    
    st.divider()
    if st.button("Kapat", use_container_width=True):
        st.rerun()

# Ödemeyi veritabanına kaydeden fonksiyon
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
        

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Site Yönetim Paneli", layout="wide")

# --- SİTE SEÇİM MANTIĞI ---
if 'selected_site_id' not in st.session_state:
    # Karşılama Ekranı
    st.title("🏙️ Site Yönetim Sistemine Hoş Geldiniz")
    st.info("Devam etmek için lütfen yönetmek istediğiniz siteyi seçin.")
    
    engine = get_db_engine()
    if engine:
        query = "SELECT id, name FROM complex_properties"
        sites_df = pd.read_sql(query, engine)

        if not sites_df.empty:
            secilen_ad = st.selectbox("Site Seçiniz:", sites_df['name'])
            site_id = int(sites_df[sites_df['name'] == secilen_ad]['id'].values[0])
            
            if st.button("Sisteme Giriş Yap"):
                st.session_state.selected_site_id = site_id
                st.session_state.selected_site_name = secilen_ad
                st.rerun()
else:

    if not check_password():
        st.stop()


    # --- ANA PANEL (SİTE SEÇİLDİKTEN SONRA) ---
    st.sidebar.title(f"📍 {st.session_state.selected_site_name}")
    st.sidebar.success(f"🔓 Giriş: nidakd")
    
    # Sol Menü Modülleri
    menu = st.sidebar.radio(
    "Menü",
    ["📊 Genel Bakış", "💰 Kasa (Tahsilat)", "🏢 Bloklar ve Daireler", "📜 Giderler", "👷 Personeller", "📢 Toplu İşlemler"]
)

    if st.sidebar.button("🔄 Site Değiştir"):
        del st.session_state.selected_site_id
        st.session_state["password_correct"] = False
        st.rerun()


    if menu == "📊 Genel Bakış":
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
                df_indir['Tur'] = df_indir['Tur'].replace({'DUES': 'Aidat', 'FUEL': 'Yakıt'})
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


    elif menu == "🏢 Bloklar ve Daireler":
        st.header("🏢 Blok Bazlı Borç Takip Paneli")
        
        engine = get_db_engine()

        # 1. Blokları çekelim
        bloklar_query = f"SELECT id, name FROM building WHERE complex_id = {st.session_state.selected_site_id}"
        bloklar_df = pd.read_sql(bloklar_query, engine)
        
        # 2. Üstten blok seçimi yapalım
        secilen_blok_adi = st.selectbox("İncelemek istediğiniz bloğu seçin:", bloklar_df['name'])
        secilen_blok_id = bloklar_df[bloklar_df['name'] == secilen_blok_adi]['id'].values[0]
        
        # 3. Seçilen bloğun dairelerini getirelim
        daire_query = f"SELECT id, unit_number, owner_name FROM unit WHERE building_id = {int(secilen_blok_id)} ORDER BY unit_number::int"
        daireler = pd.read_sql(daire_query, engine)

        # 4. Görsel Grid...
        st.write(f"### {secilen_blok_adi} Bloğu Daire Durumları")
        
        # Her satırda 4 daire olacak şekilde kolonlar
        cols = st.columns(4)
        
        for index, row in daireler.iterrows():
            borclar = get_detayli_borc(int(row['id']))
            col_index = index % 4
            
            with cols[col_index]:
                with st.container(border=True):
                    st.markdown(f"### 🚪 Daire {row['unit_number']}")
                    st.caption(f"👤 {row['owner_name']}")
                    
                    # Borç durumuna göre renkli gösterge
                    if borclar["toplam"] > 0:
                        st.error(f"Güncel Borç: ₺{borclar['toplam']:,.2f}")
                    else:
                        st.success("✅ Borç bulunmuyor")
                    
                    if st.button(f"🔍 Detayları Gör", key=f"btn_{row['id']}", use_container_width=True):
                        daire_detay_penceresi(row, borclar)

    elif menu == "💰 Kasa (Tahsilat)":
        st.header("💰 Yeni Tahsilat Girişi")
        
        engine = get_db_engine()

        # 1. Daire listesini çekelim (Seçim kutusu için)
        daire_sorgu = f"""
            SELECT u.id, b.name || ' - Daire ' || u.unit_number || ' (' || u.owner_name || ')' as label
            FROM unit u
            JOIN building b ON u.building_id = b.id
            WHERE b.complex_id = {st.session_state.selected_site_id}
        """
        daireler_df = pd.read_sql(daire_sorgu, engine)
        
        # 2. Ödeme Formu
        with st.form("tahsilat_formu"):
            secilen_daire_label = st.selectbox("Ödeme Yapan Daire:", daireler_df['label'])
            daire_id = int(daireler_df[daireler_df['label'] == secilen_daire_label]['id'].values[0])

            tutar = st.number_input("Ödenen Tutar (TL):", min_value=0.0, step=100.0)
            aciklama = st.text_input("Açıklama:", placeholder="Örn: Ocak 2026 Aidatı")
            
            submit_button = st.form_submit_button("💳 Ödemeyi Sisteme İşle")
            
            if submit_button:
                if tutar > 0:
                    # Tüm sayısal değerleri int() veya float() içine alarak garantiye alıyoruz
                    s_id = int(st.session_state.selected_site_id)
                    d_id = int(daire_id)
                    t_val = float(tutar)
                    
                    basarili = kaydet_odeme(s_id, d_id, t_val, aciklama)
                    if basarili:
                        st.success(f"Başarılı! {secilen_daire_label} için {t_val} TL ödeme alındı.")
                        st.balloons()


    elif menu == "👷 Personeller":
        st.header("👷 Personel Yönetimi ve Maaş Takibi")
        
        tab1, tab2 = st.tabs(["👥 Personel Listesi", "💸 Maaş/Ödeme Yap"])
        
        engine = get_db_engine()

        with tab1:
            st.subheader("Aktif Personeller")
            # Veritabanındaki personelleri çekiyoruz
            personel_df = pd.read_sql(f"SELECT name as \"İsim\", role as \"Görev\", salary as \"Maaş\" FROM employee WHERE complex_id = {st.session_state.selected_site_id}", engine)
            
            if not personel_df.empty:
                st.table(personel_df)
            else:
                st.info("Henüz sisteme kayıtlı personel bulunmuyor.")

        with tab2:
            st.subheader("Ödeme Formu")
            with st.form("personel_odeme_formu", clear_on_submit=True):
                # Personel seçimi için listeyi tekrar çekelim
                p_list = pd.read_sql(f"SELECT id, name FROM employee WHERE complex_id = {st.session_state.selected_site_id}", engine)
                
                if not p_list.empty:
                    secilen_p = st.selectbox("Personel Seçin:", p_list['name'])
                    p_id = p_list[p_list['name'] == secilen_p]['id'].values[0]
                    
                    tutar = st.number_input("Ödeme Tutarı (TL):", min_value=0.0, step=100.0)
                    aciklama = st.text_input("Açıklama:", value=f"{secilen_p} - Ocak 2026 Maaş Ödemesi")
                    
                    if st.form_submit_button("Ödemeyi Onayla"):
                        if tutar > 0:
                            if kaydet_personel_odeme(st.session_state.selected_site_id, int(p_id), tutar, aciklama):
                                st.success(f"{secilen_p} personeline ₺{tutar} ödeme yapıldı ve kasadan düşüldü.")
                        else:
                            st.warning("Lütfen tutar giriniz.")
                else:
                    st.error("Ödeme yapabilmek için önce personel eklemelisiniz.")



    elif menu == "📜 Giderler":
        st.header("💸 Site Gider Yönetimi")
        
        tab1, tab2 = st.tabs(["➕ Yeni Gider Ekle", "📋 Geçmiş Giderler"])
        
        with tab1:
            with st.form("gider_formu", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    miktar = st.number_input("Harcama Tutarı (TL):", min_value=0.0, step=50.0)
                    kategori = st.selectbox("Gider Kategorisi:", 
                        ["Temizlik Ücreti", "Asansör Bakımı", "Elektrik Faturası", "Yakıt Ödemesi", "Su Faturası", "Huzur Hakkı", "Temizlik Malzemesi", "Diğer"])
                with col2:
                    tarih = st.date_input("Harcama Tarihi:")
                    aciklama = st.text_area("Harcama Detayı:", placeholder="Örn: X asansör firması aylık bakım bedeli")
                
                submit = st.form_submit_button("❌ Gideri Kasadan Düş")
                
                if submit:
                    if miktar > 0:
                        if kaydet_gider(st.session_state.selected_site_id, miktar, kategori, aciklama):
                            st.success(f"Başarılı: {kategori} için ₺{miktar} gider kaydedildi.")
                            st.balloons()
                    else:
                        st.warning("Lütfen harcama tutarını giriniz.")

        with tab2:
            st.subheader("📋 Son Harcamalar")
            engine = get_db_engine()
            # account_transaction tablosundaki EXPENSE (Gider) kayıtlarını çekiyoruz
            gider_query = """
                    SELECT process_date as "Tarih", category as "Kategori", amount as "Tutar", description as "Açıklama"
                    FROM account_transaction 
                    WHERE type = 'EXPENSE'
                    ORDER BY process_date DESC
            """
            giderler_df = pd.read_sql(gider_query, engine)
            
            if not giderler_df.empty:
                st.dataframe(giderler_df, use_container_width=True, hide_index=True)
            else:
                st.info("Henüz kaydedilmiş bir gider bulunmuyor.")

    elif menu == "📢 Toplu İşlemler":
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
                    conn = get_connection()
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
                            """, (st.session_state.selected_site_id,))
                            
                            daireler = cur.fetchall()
                            
                            for d in daireler:
                                cur.execute("""
                                    INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                                    VALUES (%s, 'DUES', %s, %s, 'UNPAID')
                                """, (d[0], aidat_tutar, aidat_ay))
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success(f"Başarılı! {len(daireler)} daireye ₺{aidat_tutar} aidat borcu girildi.")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Hata: {e}")

        with tab2:
            st.subheader("Daire Bazlı Farklı Yakıt Girişi")
            st.info("💡 Şablondaki 'Dönem' kısmını YYYY-AA-GG (Örn: 2026-01-01) formatında doldurun.")
            
            engine = get_db_engine()
            # 1. ADIM: Şablon Hazırlama (Dönem sütunu eklendi)
            sablon_sorgu = """
                SELECT u.unit_number as "Daire No", u.owner_name as "Ev Sahibi", 
                       0.0 as "Tutar", '2026-01-01' as "Donem" 
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
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    basarili_sayisi = 0
                    for index, row in df_yuklenen.iterrows():
                        # Daire numarasına göre ID bul
                        cur.execute("""
                            SELECT u.id FROM unit u 
                            JOIN building b ON u.building_id = b.id 
                            WHERE u.unit_number = %s AND b.complex_id = %s
                        """, (str(row['Daire No']), st.session_state.selected_site_id))
                        unit_res = cur.fetchone()
                        
                        # Tutar 0'dan büyükse kaydet
                        if unit_res and float(row['Tutar']) > 0:
                            # Excel'deki 'Donem' sütununu kullanıyoruz
                            cur.execute("""
                                INSERT INTO debt_item (unit_id, type, expected_amount, period_month, status)
                                VALUES (%s, 'FUEL', %s, %s, 'UNPAID')
                            """, (unit_res[0], row['Tutar'], row['Donem']))
                            basarili_sayisi += 1
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"İşlem Tamam! {basarili_sayisi} daireye yakıt borçları tarihleriyle birlikte girildi.")
                    st.balloons()
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
                    ham_dosya = gecmis_dosya.getvalue().decode('utf-8-sig').splitlines()
                    baslik_satiri_index = 0
                    for i, satir in enumerate(ham_dosya):
                        if "Blok" in satir or "Daire No" in satir:
                            baslik_satiri_index = i
                            break
                    
                    gecmis_dosya.seek(0)
                    df_gecmis = pd.read_csv(gecmis_dosya, sep=None, engine='python', encoding='utf-8-sig', skiprows=baslik_satiri_index)
                    df_gecmis.columns = [str(c).strip() for c in df_gecmis.columns]
                    
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    # Önce mevcut yanlış yüklenen eski borçları temizleyelim (Opsiyonel ama önerilir)
                    cur.execute("DELETE FROM debt_item WHERE period_month < '2026-01-01' AND status = 'UNPAID'")
                    
                    kayit_sayisi = 0
                    for index, row in df_gecmis.iterrows():
                        # Blok ve Daireyi beraber sorguluyoruz
                        blok_adi = str(row.get('Blok', '')).strip()
                        d_no = str(row.get('Daire No', '')).strip()
                        
                        cur.execute("""
                            SELECT u.id FROM unit u 
                            JOIN building b ON u.building_id = b.id 
                            WHERE b.name = %s AND u.unit_number = %s AND b.complex_id = %s
                        """, (blok_adi, d_no, st.session_state.selected_site_id))
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
                                    kayit_sayisi += 1
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Başarılı! {kayit_sayisi} adet kayıt doğru bloklara eşlenerek yüklendi.")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Hata: {e}")
