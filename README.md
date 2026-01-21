# 🏢 Apartman & Site Yönetim Sistemi (Apartment Management System)

---

## 🇹🇷 Türkçe

### 📌 Proje Hakkında
Bu proje, **site / bina yönetimleri** ve küçük ölçekli işletmeler için geliştirilmiş profesyonel bir **Muhasebe Arayüz Programı**dır.  
Uygulama; aidat, yakıt ve geçmişten devreden borç kalemlerinin takibini, tahsilat süreçlerini ve **blok bazlı finansal analizi** kullanıcı dostu bir arayüz üzerinden sunar.

### 🎯 Projenin Amacı
- Gelir ve gider (aidat / yakıt) kayıtlarını düzenli ve sürdürülebilir şekilde tutmak  
- **Blok bazlı borç takibi** ile çok binalı sitelerde veri karışıklığını önlemek  
- Muhasebe verilerini **PostgreSQL** üzerinde güvenli ve ilişkisel bir yapıda saklamak  
- CSV entegrasyonu sayesinde karmaşık Excel listelerini saniyeler içinde dijital sisteme aktarmak  

### 🧾 Temel Özellikler
- **Toplu Borçlandırma:** Tek tıkla tüm siteyi borçlandırma ve yönetici muafiyet kontrolü  
- **Akıllı Veri Aktarımı:** CSV dosyalarından otomatik veri temizleme ve dinamik satır atlama desteği  
- **FIFO Tahsilat Mantığı:** Ödemelerin otomatik olarak en eski borçtan mahsup edilmesi  
- **Detaylı Kategorizasyon:** Aidat, Yakıt ve Eksik Ödeme (Diğer) kalemlerinin bağımsız takibi  
- **Güvenlik:** Kimlik bilgilerinin koddan bağımsız `.env` katmanında korunması  

### 🧰 Kullanılan Teknolojiler
- **Python & Streamlit** – Arayüz ve uygulama mantığı  
- **PostgreSQL** – İlişkisel veritabanı  
- **Pandas** – Veri işleme  
- **python-dotenv** – Ortam değişkenleri ve güvenlik  

### 📂 Veritabanı Dokümantasyonu

Veritabanı kurulum dosyaları `database/` klasöründe yer alır. İşletim mantığı aşağıdaki gibidir:

| Dosya Adı | Açıklama | Sıra |
| :--- | :--- | :---: |
| **`revised_create_tables.sql`** | Tabloları ve şemayı oluşturur. | 1 |
| **`create_payment_transaction_trigger.sql`** | Ödeme (`payment`) tablosuna kayıt girildiğinde `account_transaction` (kasa) tablosuna otomatik gelir kaydı işleyen tetikleyiciyi kurar. | 2 |
| **`insert_initial_data.sql`** | Bloklar ve daireler gibi sabit verileri yükler. | 3 |
| **`insert_past_period_debts.sql`** | Geçmiş dönem borçlarını, devir bakiyelerini ve özel durumları (yönetici muafiyetleri vb.) sisteme işler. | 4 |

**Önemli Notlar:**
- **Otomasyon:** `trg_after_payment_insert` tetikleyicisi sayesinde tahsilat yapıldığında muhasebe defterine manuel kayıt girmeye gerek yoktur.
- **Geçmiş Borçlar:** `insert_past_period_debts.sql` dosyası sistem canlıya alınırken bir kez çalıştırılır. İçinde Aralık 2025 devir bakiyeleri ve Ocak 2026 tanımları bulunur.

### ▶️ Kurulum ve Çalıştırma

#### 🔹 Sanal Ortam Kurulumu
    python3 -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt

#### 🔹 Veritabanı Kurulumu
Aşağıdaki komutları sırasıyla çalıştırarak veritabanını hazırlayın:

    psql -U postgres -d site_yonetim_db -f database/revised_create_tables.sql
    psql -U postgres -d site_yonetim_db -f database/create_payment_transaction_trigger.sql
    psql -U postgres -d site_yonetim_db -f database/insert_initial_data.sql
    psql -U postgres -d site_yonetim_db -f database/insert_past_period_debts.sql

Proje kök dizininde `.env` dosyası oluşturup veritabanı bağlantı bilgilerinizi girmeyi unutmayın.

#### 🔹 Uygulamayı Çalıştırma
    streamlit run main.py

---

## 🇬🇧 English

### 📌 About the Project
This project is a professional **Accounting Interface Application** developed for apartment and residential site management systems.  
It provides an intuitive and secure web-based interface to manage dues, fuel expenses, carried-over debts, collection processes, and **block-based financial analysis**.

### 🎯 Project Objectives
- Maintain consistent and sustainable records of income and expenses (dues / fuel)  
- Prevent data confusion in multi-building sites through **block-based debt tracking**  
- Store accounting data securely using a relational **PostgreSQL** database  
- Import complex Excel-based records into the system within seconds using CSV integration  

### 🧾 Core Features
- **Bulk Invoicing:** One-click debt assignment for all residents with manager exemption handling  
- **Smart Import:** Automatic data cleaning and dynamic row skipping during CSV imports  
- **FIFO Payment Logic:** Payments are automatically applied to the oldest outstanding debts  
- **Detailed Categorization:** Independent tracking of Dues, Fuel, and Other payment types  
- **Security:** Sensitive credentials are isolated using environment variables (`.env`)  

### 🧰 Technologies Used
- **Python & Streamlit** – Frontend & Backend  
- **PostgreSQL** – Relational Database  
- **Pandas** – Data Processing  
- **python-dotenv** – Environment Variable Management  

### ▶️ Installation & Run

#### 🔹 Setup Virtual Environment
    python3 -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt

#### 🔹 Database Setup
Execute the following SQL files in order for a complete setup:
- `database/revised_create_tables.sql`
- `database/create_payment_transaction_trigger.sql` (Automation)
- `database/insert_initial_data.sql` (Blocks/Units)
- `database/insert_past_period_debts.sql` (Historical Data)

Create a `.env` file in the project root and define database credentials.

#### 🔹 Run the Application
    streamlit run main.py

---

### 👩‍💻 Developer
**Nida Akdoğan**

---

## 🗂️ Project Structure

    SITE-ACCOUNTING-APP/
    │
    ├── database/
    │   ├── revised_create_tables.sql
    │   ├── create_payment_transaction_trigger.sql
    │   ├── insert_initial_data.sql
    │   ├── insert_past_period_debts.sql
    │   └── test_queries.sql
    │
    ├── main.py
    ├── requirements.txt
    └── README.md
