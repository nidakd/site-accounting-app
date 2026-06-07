# 🔧 Site Yönetim Sistemi - Pratik İmplementasyon Önerileri

---

## 1. ROL TABANLI ERIŞIM KONTROL (RBAC) - Kod Örneğı

### Adım 1: Veritabanı Tabloları

```sql
-- Roller tablosu
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO role (name, description) VALUES
('admin', 'Tüm erişim'),
('accountant', 'Muhasebe ve raporlar'),
('collector', 'Tahsilat görevlisi'),
('advisor', 'Salt-okunur danışman');

-- Kullanıcılar tablosu (users yerine app_user)
ALTER TABLE app_user ADD COLUMN role_id INTEGER REFERENCES role(id);
ALTER TABLE app_user ADD COLUMN complex_id INTEGER REFERENCES complex_properties(id);

-- Permissions tablosu
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE role_permission (
    role_id INTEGER REFERENCES role(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permission(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
```

### Adım 2: Python Auth Modülü

```python
# src/auth/rbac.py
import streamlit as st
from src.database.connection import get_connection

def get_user_permissions(user_id):
    """Kullanıcının izinlerini getirir"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name 
            FROM app_user u
            JOIN role r ON u.role_id = r.id
            JOIN role_permission rp ON r.id = rp.role_id
            JOIN permission p ON rp.permission_id = p.id
            WHERE u.id = %s
        """, (user_id,))
        
        permissions = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return permissions
    except:
        return []

def check_permission(permission_name):
    """İzin kontrolü decorator'ı"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if "user_permissions" not in st.session_state:
                st.error("❌ Yetkisiz erişim!")
                return
            
            if permission_name not in st.session_state.user_permissions:
                st.error(f"❌ Bu işlemi yapma yetkiniz yok: {permission_name}")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Örnek Kullanım:
@check_permission("view_reports")
def render_reports_page():
    st.header("📊 Mali Raporlar")
    # Rapor kodu...
```

### Adım 3: Giriş Ekranında Roller

```python
# src/auth/auth.py (Mevcut kodu genişlet)

def check_password():
    """Şifre kontrolü ve rol yükleme"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Giriş Yap")
            
            if submit:
                # Basit örnek - gerçekte hash'lenmeli
                if username == "admin" and password == "your_secure_password":
                    st.session_state.password_correct = True
                    st.session_state.username = username
                    st.session_state.user_id = 1  # DB'den çek
                    
                    # İzinleri yükle
                    from src.auth.rbac import get_user_permissions
                    st.session_state.user_permissions = get_user_permissions(1)
                    
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı/şifre")
        
        return False
    
    return True
```

---

## 2. AUDIT LOG SİSTEMİ

### Veritabanı Tablosu

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50)
);

-- Index
CREATE INDEX idx_audit_user_date ON audit_log(user_id, created_at);
CREATE INDEX idx_audit_table ON audit_log(table_name, record_id);
```

### Python Yardımcı Fonksiyon

```python
# src/utils/audit.py
from src.database.connection import get_connection
from datetime import datetime
import json

def log_action(user_id, action, table_name, record_id, old_value=None, new_value=None, ip_address="127.0.0.1"):
    """
    Audit log kaydeder
    
    action: INSERT, UPDATE, DELETE, PAYMENT, DOWNLOAD, etc.
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log 
            (user_id, action, table_name, record_id, old_value, new_value, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            action,
            table_name,
            record_id,
            json.dumps(old_value) if old_value else None,
            json.dumps(new_value) if new_value else None,
            ip_address
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Audit log hatası: {e}")
        return False

# Örnek Kullanım:
from src.utils.audit import log_action

# Ödeme kaydeder ve log tutar
def kaydet_odeme_with_audit(site_id, daire_id, tutar, aciklama, user_id):
    # Ödeme kaydı
    result = kaydet_odeme(site_id, daire_id, tutar, aciklama)
    
    if result:
        # Audit log
        log_action(
            user_id=user_id,
            action="PAYMENT_RECORDED",
            table_name="payment",
            record_id=None,  # Ya da son INSERT ID'yi al
            new_value={"unit_id": daire_id, "amount": tutar}
        )
    
    return result
```

---

## 3. TEMEL MUHASEBE MODÜLÜ (Double-Entry)

### Tablo Yapısı

```sql
-- Hesaplar Planı
CREATE TABLE chart_of_accounts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,  -- 1.00.01
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20),  -- ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    complex_id INTEGER REFERENCES complex_properties(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- Muhasebe Girdileri (Journal Entries)
CREATE TABLE journal_entry (
    id BIGSERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id),
    entry_date DATE NOT NULL,
    description TEXT,
    reference_document VARCHAR(50),  -- Payment ID, Invoice ID, etc.
    created_by INTEGER REFERENCES app_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'DRAFT'  -- DRAFT, POSTED, REVERSED
);

-- Muhasebe Satırları
CREATE TABLE journal_entry_line (
    id BIGSERIAL PRIMARY KEY,
    journal_entry_id BIGSERIAL REFERENCES journal_entry(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES chart_of_accounts(id),
    debit_amount DECIMAL(12, 2),
    credit_amount DECIMAL(12, 2),
    description TEXT,
    CHECK (debit_amount > 0 OR credit_amount > 0),
    CHECK (debit_amount IS NULL OR credit_amount IS NULL)  -- Sadece biri dolu
);

-- Başlangıç Verisi
INSERT INTO chart_of_accounts (code, name, account_type, complex_id) VALUES
('1000', 'Banka Hesabı', 'ASSET', 1),
('1100', 'Kasa', 'ASSET', 1),
('2000', 'Alınan Aidatlar (Borç)', 'LIABILITY', 1),
('4000', 'Aidat Gelirleri', 'INCOME', 1),
('4100', 'Yakıt Gelirleri', 'INCOME', 1),
('6000', 'Elektrik Gideri', 'EXPENSE', 1),
('6100', 'Su Gideri', 'EXPENSE', 1);
```

### Python Servis

```python
# src/services/accounting_service.py
from src.database.connection import get_connection, get_db_engine
import pandas as pd
from decimal import Decimal

def post_payment_entry(complex_id, unit_id, amount, payment_description):
    """
    Ödeme işlemini muhasebe girişine çevirir:
    DR. Banka Hesabı (1000)
    CR. Aidat Alacağı (2000)
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # 1. Journal Entry kaydı
        cur.execute("""
            INSERT INTO journal_entry (complex_id, entry_date, description, reference_document, status)
            VALUES (%s, CURRENT_DATE, %s, %s, 'POSTED')
            RETURNING id
        """, (complex_id, payment_description, f"PAYMENT-{unit_id}"))
        
        entry_id = cur.fetchone()[0]
        
        # 2. Debit: Banka Hesabı
        cur.execute("""
            INSERT INTO journal_entry_line (journal_entry_id, account_id, debit_amount)
            SELECT %s, id, %s
            FROM chart_of_accounts
            WHERE code = '1000' AND complex_id = %s
        """, (entry_id, amount, complex_id))
        
        # 3. Credit: Aidat Alacağı
        cur.execute("""
            INSERT INTO journal_entry_line (journal_entry_id, account_id, credit_amount)
            SELECT %s, id, %s
            FROM chart_of_accounts
            WHERE code = '2000' AND complex_id = %s
        """, (entry_id, amount, complex_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Muhasebe girdisi hatası: {e}")
        return False

def get_trial_balance(complex_id):
    """
    Uygulama Bilançosu (Trial Balance)
    Debit toplamı = Credit toplamı kontrolü
    """
    engine = get_db_engine()
    if not engine:
        return None
    
    query = """
    SELECT 
        ca.code,
        ca.name,
        ca.account_type,
        COALESCE(SUM(jel.debit_amount), 0) as debit_total,
        COALESCE(SUM(jel.credit_amount), 0) as credit_total,
        COALESCE(SUM(jel.debit_amount), 0) - COALESCE(SUM(jel.credit_amount), 0) as balance
    FROM chart_of_accounts ca
    LEFT JOIN journal_entry_line jel ON ca.id = jel.account_id
    LEFT JOIN journal_entry je ON jel.journal_entry_id = je.id
    WHERE ca.complex_id = %s AND je.status = 'POSTED'
    GROUP BY ca.id, ca.code, ca.name, ca.account_type
    ORDER BY ca.code
    """
    
    df = pd.read_sql(query, engine, params=(complex_id,))
    return df
```

---

## 4. OTOMATIK BİLDİRİM SİSTEMİ

### Temel SMS/Email Modülü

```python
# src/services/notification_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
    
    def send_email(self, recipient_email, subject, body):
        """Email gönder"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email gönderim hatası: {e}")
            return False
    
    def notify_dues_created(self, unit_owner_email, unit_number, amount, period):
        """Aidat yükleme bildirim"""
        subject = f"🏢 Aidat Bildirimi - {period}"
        body = f"""
        <h2>Aidat Bildirimi</h2>
        <p>Sayın Site Sahibi,</p>
        <p>Daire <strong>No: {unit_number}</strong> için 
        <strong>{period}</strong> aidatı yüklendi.</p>
        <p><strong>Tutar: ₺{amount:,.2f}</strong></p>
        <p>Lütfen portala giriş yaparak borç durumunuzu görüntüleyebilirsiniz.</p>
        <hr/>
        <p>Site Yönetim Sistemi</p>
        """
        
        return self.send_email(unit_owner_email, subject, body)
    
    def notify_payment_received(self, unit_owner_email, unit_number, amount):
        """Ödeme alındı bildirimi"""
        subject = f"✅ Ödeme Alındı - Makbuz"
        body = f"""
        <h2>Ödeme Alındı</h2>
        <p>Sayın Site Sahibi,</p>
        <p>Daire <strong>No: {unit_number}</strong> için 
        <strong>₺{amount:,.2f}</strong> tutarındaki ödemeniz alınmıştır.</p>
        <p>Makbuz için portala giriş yapabilirsiniz.</p>
        <hr/>
        <p>Site Yönetim Sistemi</p>
        """
        
        return self.send_email(unit_owner_email, subject, body)

# Planlı iş (Cron Job) - Ödeme hatırlatıcısı
def send_payment_reminders():
    """Vadesi yaklaşan borçlar için hatırlatıcı"""
    from src.database.connection import get_db_engine
    
    engine = get_db_engine()
    conn = engine.connect()
    
    # Vade tarihi geçmiş borçları bul
    query = """
    SELECT u.owner_email, u.unit_number, 
           SUM(di.expected_amount) as total_debt
    FROM debt_item di
    JOIN unit u ON di.unit_id = u.id
    WHERE di.status != 'PAID'
    AND (CURRENT_DATE - di.period_month) > interval '30 days'
    GROUP BY u.id, u.owner_email, u.unit_number
    """
    
    result = conn.execute(query)
    rows = result.fetchall()
    
    notifier = NotificationService()
    for row in rows:
        email, unit_no, debt = row
        if email:
            notifier.send_email(
                email,
                f"⚠️ Aidat Ödeme Hatırlatması",
                f"Sayın Site Sahibı,<br/>Daire {unit_no} için ₺{debt:,.2f} tutarında ödenmemiş aidat bulunmaktadır."
            )
    
    conn.close()

# .env örneği
"""
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=siteyonetim@example.com
SENDER_PASSWORD=your_app_password
"""
```

---

## 5. KONUT SAHİBİ PORTALI (Basit Versiyon)

### Ana Sayfa Streamlit

```python
# portal.py (Ayrı dosya - streamlit run portal.py)
import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from datetime import datetime

st.set_page_config(page_title="Daire Sahibi Portalı", layout="wide")

st.title("🏠 Daire Sahibi Portalı")

# Giriş
if "unit_id" not in st.session_state:
    with st.form("unit_login"):
        unit_number = st.text_input("Daire Numarası")
        daire_password = st.text_input("Şifreniz", type="password")
        submit = st.form_submit_button("Giriş Yap")
        
        if submit:
            # DB'de kontrol
            engine = get_db_engine()
            result = pd.read_sql(
                "SELECT id FROM unit WHERE unit_number = %s AND password_hash = crypt(%s, password_hash)",
                engine,
                params=(unit_number, daire_password)
            )
            
            if not result.empty:
                st.session_state.unit_id = result.iloc[0]['id']
                st.rerun()
            else:
                st.error("❌ Hatalı giriş")
else:
    unit_id = st.session_state.unit_id
    
    # Daire bilgileri
    engine = get_db_engine()
    
    # Borç Durumu
    debt_query = """
    SELECT type, expected_amount, period_month, status
    FROM debt_item
    WHERE unit_id = %s
    ORDER BY period_month DESC
    """
    
    debt_df = pd.read_sql(debt_query, engine, params=(unit_id,))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unpaid = debt_df[debt_df['status'] != 'PAID']['expected_amount'].sum()
        st.metric("Ödenmesi Gereken", f"₺{unpaid:,.2f}")
    
    with col2:
        dues = debt_df[(debt_df['type'] == 'DUES') & (debt_df['status'] != 'PAID')]['expected_amount'].sum()
        st.metric("Aidat Borcu", f"₺{dues:,.2f}")
    
    with col3:
        fuel = debt_df[(debt_df['type'] == 'FUEL') & (debt_df['status'] != 'PAID')]['expected_amount'].sum()
        st.metric("Yakıt Borcu", f"₺{fuel:,.2f}")
    
    # Borç Tablosu
    st.subheader("Borç Detayları")
    if not debt_df.empty:
        debt_df['period_month'] = pd.to_datetime(debt_df['period_month']).dt.strftime('%m/%Y')
        debt_df['type'] = debt_df['type'].replace({'DUES': 'Aidat', 'FUEL': 'Yakıt'})
        debt_df['status'] = debt_df['status'].replace({'PAID': '✅ Ödendi', 'UNPAID': '⏳ Beklemede'})
        st.dataframe(debt_df, use_container_width=True, hide_index=True)
    
    # Ödeme Geçmişi
    st.subheader("Ödeme Geçmişi")
    payment_query = """
    SELECT process_date, amount, description
    FROM payment
    WHERE unit_id = %s
    ORDER BY process_date DESC
    LIMIT 20
    """
    
    payment_df = pd.read_sql(payment_query, engine, params=(unit_id,))
    if not payment_df.empty:
        payment_df['process_date'] = pd.to_datetime(payment_df['process_date']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(payment_df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz ödeme yapılmamış")
    
    if st.button("Çıkış Yap"):
        del st.session_state.unit_id
        st.rerun()
```

---

## 6. MALİ TABLO RAPORLARI

```python
# src/services/financial_reporting.py
import pandas as pd
from src.database.connection import get_db_engine
from decimal import Decimal

def generate_balance_sheet(complex_id, as_of_date):
    """
    Bilanço Raporu (Balance Sheet)
    """
    engine = get_db_engine()
    
    query = """
    SELECT 
        'ASSETS' as section,
        'Current Assets' as subsection,
        'Bank Accounts' as account,
        COALESCE(SUM(CASE WHEN coa.code LIKE '10%' THEN jel.debit_amount - jel.credit_amount ELSE 0 END), 0) as amount
    FROM chart_of_accounts coa
    LEFT JOIN journal_entry_line jel ON coa.id = jel.account_id
    WHERE coa.complex_id = %s AND coa.account_type = 'ASSET'
    
    UNION ALL
    
    SELECT 
        'LIABILITIES' as section,
        'Current Liabilities' as subsection,
        'Dues Payable' as account,
        COALESCE(SUM(CASE WHEN coa.code LIKE '20%' THEN jel.credit_amount - jel.debit_amount ELSE 0 END), 0) as amount
    FROM chart_of_accounts coa
    LEFT JOIN journal_entry_line jel ON coa.id = jel.account_id
    WHERE coa.complex_id = %s AND coa.account_type = 'LIABILITY'
    
    UNION ALL
    
    SELECT 
        'EQUITY' as section,
        'Owner Equity' as subsection,
        'Retained Earnings' as account,
        COALESCE(SUM(jel.credit_amount - jel.debit_amount), 0) as amount
    FROM journal_entry_line jel
    WHERE jel.account_id IN (
        SELECT id FROM chart_of_accounts WHERE complex_id = %s AND account_type = 'EQUITY'
    )
    """
    
    df = pd.read_sql(query, engine, params=(complex_id, complex_id, complex_id))
    
    # Bilanço dosyası
    report = f"""
    ═════════════════════════════════════════════
    BALANÇO (Balance Sheet)
    {as_of_date.strftime('%d/%m/%Y')} Tarihi İtibarıyla
    ═════════════════════════════════════════════
    
    VARLIKLAR (ASSETS)
    ─────────────────────
    Dönen Varlıklar:
      Banka Hesapları:        ₺{df[df['code'] == '10%']['amount'].sum():>15,.2f}
      Kasa:                   ₺{df[df['code'] == '11%']['amount'].sum():>15,.2f}
    ─────────────────────
    TOPLAM VARLIKLAR:         ₺{df['amount'].sum():>15,.2f}
    
    KAYNAKLAR (LIABILITIES & EQUITY)
    ─────────────────────
    Kısa Vadeli Yükümlülükler:
      Aidat Alacağı:          ₺{df[df['code'] == '20%']['amount'].sum():>15,.2f}
    
    Özkaynaklar:
      Birikmiş Kâr/Zarar:     ₺{df[df['code'] == '30%']['amount'].sum():>15,.2f}
    ─────────────────────
    TOPLAM KAYNAKLAR:         ₺{df['amount'].sum():>15,.2f}
    """
    
    return report

def generate_income_statement(complex_id, start_date, end_date):
    """
    Gelir Tablosu (Income Statement)
    """
    engine = get_db_engine()
    
    query = """
    SELECT 
        CASE 
            WHEN account_type = 'INCOME' THEN 'INCOME'
            WHEN account_type = 'EXPENSE' THEN 'EXPENSE'
        END as category,
        ca.name,
        SUM(jel.credit_amount) - SUM(jel.debit_amount) as amount
    FROM chart_of_accounts ca
    LEFT JOIN journal_entry_line jel ON ca.id = jel.account_id
    WHERE ca.complex_id = %s 
      AND ca.account_type IN ('INCOME', 'EXPENSE')
    GROUP BY ca.account_type, ca.name
    """
    
    df = pd.read_sql(query, engine, params=(complex_id,))
    
    total_income = df[df['category'] == 'INCOME']['amount'].sum()
    total_expense = df[df['category'] == 'EXPENSE']['amount'].sum()
    net_income = total_income - total_expense
    
    report = f"""
    ═════════════════════════════════════════════
    GELİR TABLOSU (Income Statement)
    {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')} Dönemi
    ═════════════════════════════════════════════
    
    GELİRLER (INCOME)
    ─────────────────────
    Aidat Gelirleri:                ₺{total_income:>15,.2f}
    
    GİDERLER (EXPENSES)
    ─────────────────────
    Elektrik Gideri:                ₺{total_expense:>15,.2f}
    
    ─────────────────────
    NET KÂR/ZARAR:                  ₺{net_income:>15,.2f}
    """
    
    return report
```

---

## 7. KPİ PANOU

```python
# src/views/kpi_dashboard.py
import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine

def render_kpi_dashboard():
    st.header("📊 KPİ Panou")
    
    engine = get_db_engine()
    complex_id = st.session_state.selected_site_id
    
    # 1. Tahsilat Oranı
    query_tahsilat = """
    SELECT 
        SUM(CASE WHEN status = 'PAID' THEN expected_amount ELSE 0 END) as paid,
        SUM(expected_amount) as total
    FROM debt_item
    WHERE unit_id IN (
        SELECT id FROM unit 
        WHERE building_id IN (
            SELECT id FROM building WHERE complex_id = %s
        )
    )
    """
    
    df_tahsilat = pd.read_sql(query_tahsilat, engine, params=(complex_id,))
    tahsilat_orani = (df_tahsilat['paid'].sum() / df_tahsilat['total'].sum() * 100) if df_tahsilat['total'].sum() > 0 else 0
    
    # 2. Ortalama Borç Süresi
    query_sure = """
    SELECT 
        EXTRACT(DAY FROM CURRENT_DATE - MAX(period_month)) as gun
    FROM debt_item
    WHERE status != 'PAID'
        AND unit_id IN (
            SELECT id FROM unit 
            WHERE building_id IN (
                SELECT id FROM building WHERE complex_id = %s
            )
        )
    """
    
    df_sure = pd.read_sql(query_sure, engine, params=(complex_id,))
    avg_days = df_sure['gun'].iloc[0] if not df_sure.empty else 0
    
    # 3. Vadegeçmiş Borç Yüzdesi
    query_vadegecmis = """
    SELECT 
        COUNT(*) as toplam_borç,
        SUM(CASE WHEN CURRENT_DATE - period_month > interval '30 days' THEN expected_amount ELSE 0 END) as overdue
    FROM debt_item
    WHERE status != 'PAID'
    """
    
    df_vadegecmis = pd.read_sql(query_vadegecmis, engine)
    overdue_pct = (df_vadegecmis['overdue'].sum() / df_vadegecmis['toplam_borç'].sum() * 100) if df_vadegecmis['toplam_borç'].sum() > 0 else 0
    
    # KPİ Kartları
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Tahsilat Oranı", f"{tahsilat_orani:.1f}%", delta="Hedef: 95%")
    
    with col2:
        st.metric("📅 Ort. Borç Süresi", f"{avg_days:.0f} gün", delta="Azalmalı")
    
    with col3:
        st.metric("⏰ Vadegeçmiş Borç", f"{overdue_pct:.1f}%", delta="Azalmalı")
    
    with col4:
        st.metric("📊 Toplam Bekleyen", f"₺{df_tahsilat['total'].sum() - df_tahsilat['paid'].sum():,.2f}")
```

---

## 📝 Implementasyon Kontrol Listesi

```
FÂZ 1 - ACIL (1-2 Hafta):
- [ ] RBAC Tabloları oluştur
- [ ] Audit Log Sistemi entegre et
- [ ] Temel muhasebe tabloları oluştur
- [ ] KPİ Panou tasarla

FÂZ 2 - YÜKSEK (2-4 Hafta):
- [ ] Daire Sahipli Portali oluştur
- [ ] Bildirim Servisi entegre et
- [ ] Mali Tablo raporları oluştur
- [ ] Bilanço/Gelir Tablosu oluştur

FÂZ 3 - NORMAL (4-8 Hafta):
- [ ] Banka Mutabakatı modülü
- [ ] Gider kategorilendirmesi
- [ ] Gelişmiş raporlama
- [ ] Mobil uyumluluk
```

---

**Not:** Bu kod örnekleri başlangıç noktası olarak sunulmuştur. Üretim ortamında güvenlik, hata yönetimi ve performans optimizasyonları uygulanmalıdır.
