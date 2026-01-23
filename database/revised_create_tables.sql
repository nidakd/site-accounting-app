/* 
   FILE NAME / DOSYA ADI : revised_create_tables.sql
   PROJECT / PROJE      : Sellable Site Management Accounting Interface
                          Satılabilir Site Yönetimi Muhasebe Arayüzü

   DESCRIPTION / AÇIKLAMA:
   This script creates all core tables required for a site/apartment
   management and accounting system.

   Bu script, site/apartman yönetimi ve muhasebe sistemi için
   gerekli olan tüm temel tabloları oluşturur.
*/

-----------------------------------------------------------
-- 0. CLEANUP STEP / TEMİZLİK ADIMI
-----------------------------------------------------------
-- Drops existing tables in dependency order.
-- Tablolar, bağımlılık sırasına göre silinir.

DROP TABLE IF EXISTS payment_debt;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS debt_item;
DROP TABLE IF EXISTS account_transaction; -- renamed from "transaction"
DROP TABLE IF EXISTS app_user;            -- renamed from "user"
DROP TABLE IF EXISTS unit;
DROP TABLE IF EXISTS unit_type;
DROP TABLE IF EXISTS building;
DROP TABLE IF EXISTS complex_properties;
DROP TABLE IF EXISTS employee;

--üstteki hali hata verirse
--alttakini çalıştır

-- Her şeyi kökten ve güvenli bir şekilde silmek için:
DROP TABLE IF EXISTS payment_debt CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS debt_item CASCADE;
DROP TABLE IF EXISTS account_transaction CASCADE;
DROP TABLE IF EXISTS "transaction" CASCADE; -- Eski tablo ismi
DROP TABLE IF EXISTS app_user CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;         -- Eski tablo ismi
DROP TABLE IF EXISTS unit CASCADE;
DROP TABLE IF EXISTS unit_type CASCADE;
DROP TABLE IF EXISTS building CASCADE;
DROP TABLE IF EXISTS complex_properties CASCADE;
DROP TABLE IF EXISTS employee CASCADE;

-----------------------------------------------------------
-- 1. STRUCTURAL AND PARAMETER TABLES
-- 1. YAPISAL VE PARAMETRE TABLOLARI
-----------------------------------------------------------

/*
    TABLE / TABLO : complex_properties

    PURPOSE / AMAÇ:
    Stores general configuration settings of a site/complex.
    Siteye ait genel ayarları tutar.

    Examples / Örnekler:
    - Site name
    - Total number of units
    - Currency
*/
CREATE TABLE complex_properties (
    id SERIAL PRIMARY KEY,                      -- Unique site identifier / Site benzersiz kimliği
    name VARCHAR(100) NOT NULL UNIQUE,           -- Site name / Site adı
    total_units INTEGER DEFAULT 0,               -- Total apartments / Toplam daire sayısı
    currency VARCHAR(5) NOT NULL DEFAULT 'TRY',  -- Currency type / Para birimi
    dues_collection_day INTEGER DEFAULT 1        -- Monthly dues day / Aidat toplama günü
);

/*
    TABLE / TABLO : building

    PURPOSE / AMAÇ:
    Represents each building or block inside a site.
    Site içerisindeki her bir bina veya bloğu temsil eder.
*/
CREATE TABLE building (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE CASCADE NOT NULL,               -- Related site / Bağlı olduğu site
    name VARCHAR(50) NOT NULL,                    -- Building name / Blok adı
    UNIQUE (complex_id, name)                     -- Unique per site / Site bazlı benzersiz
);

/*
    TABLE / TABLO : unit_type

    PURPOSE / AMAÇ:
    Defines apartment types such as 2+1, 3+1.
    2+1, 3+1 gibi daire tiplerini tanımlar.

    NOTE / NOT:
    complex_id enables multi-tenancy support.
    complex_id çoklu site desteği sağlar.
*/
CREATE TABLE unit_type (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE CASCADE NOT NULL,               -- Site reference / Site referansı
    name VARCHAR(50) NOT NULL,                    -- Type name / Daire tipi
    default_dues NUMERIC(10,2) NOT NULL,          -- Default monthly dues / Varsayılan aidat
    UNIQUE (complex_id, name)                     -- Scoped uniqueness / Site bazlı benzersizlik
);

/*
    TABLE / TABLO : unit

    PURPOSE / AMAÇ:
    Represents an individual apartment.
    Her bir daireyi temsil eder.

    NOTE / NOT:
    unit_number is VARCHAR to support formats like A-1, B-10.
*/
CREATE TABLE unit (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES building(id)
        ON DELETE RESTRICT NOT NULL,              -- Building reference / Blok referansı
    unit_type_id INTEGER REFERENCES unit_type(id)
        ON DELETE RESTRICT NOT NULL,              -- Apartment type / Daire tipi
    unit_number VARCHAR(20) NOT NULL,             -- Apartment number / Daire numarası
    owner_name VARCHAR(100) NOT NULL,             -- Owner name / Ev sahibi
    tenant_name VARCHAR(100),                     -- Tenant name / Kiracı
    phone VARCHAR(20),                            -- Contact phone / Telefon
    UNIQUE (building_id, unit_number)             -- Unique per building / Blok bazlı benzersiz
);

-----------------------------------------------------------
-- 2. ACCOUNTING AND MANAGEMENT TABLES
-- 2. MUHASEBE VE YÖNETİM TABLOLARI
-----------------------------------------------------------

/*
    TABLE / TABLO : app_user

    PURPOSE / AMAÇ:
    Stores application users.
    Sistem kullanıcılarını tutar.

    NOTE / NOT:
    Renamed to avoid SQL reserved keyword "user".
*/
CREATE TABLE app_user (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE RESTRICT NOT NULL,              -- Site reference / Site referansı
    username VARCHAR(100) NOT NULL UNIQUE,        -- Username / Kullanıcı adı
    password_hash VARCHAR(255) NOT NULL,          -- Password hash / Şifre özeti
    role VARCHAR(50) DEFAULT 'admin',             -- Role / Rol
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*
    TABLE / TABLO : employee

    PURPOSE / AMAÇ:
    Stores employee records.
    Çalışan kayıtlarını tutar.

    NOTE / NOT:
    Employees are linked to complexes, not individual units.
*/
CREATE TABLE employee (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE RESTRICT NOT NULL,              -- Related site / İlgili site
    name VARCHAR(100) NOT NULL,                    -- Employee name / Çalışan adı
    role VARCHAR(100),                            -- Job role / Görev rolü
    salary NUMERIC(10,2) DEFAULT 0.00              -- Salary / Maaş
);

/*
    TABLE / TABLO : account_transaction

    PURPOSE / AMAÇ:
    Stores income and expense records.
    Gelir ve gider işlemlerini tutar.

    NOTE / NOT:
    created_at is used for audit tracking.
*/
CREATE TABLE account_transaction (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE RESTRICT NOT NULL,              -- Site reference / Site referansı
    type VARCHAR(10) NOT NULL
        CHECK (type IN ('INCOME', 'EXPENSE')),    -- Transaction type / İşlem türü
    category VARCHAR(50) NOT NULL,                -- Category / Kategori
    unit_id INTEGER REFERENCES unit(id)
        ON DELETE SET NULL,                       -- Related unit / İlgili daire
    amount NUMERIC(10,2) NOT NULL,                -- Amount / Tutar
    process_date TIMESTAMP NOT NULL,              -- Effective date / İşlem tarihi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Insert timestamp / Kayıt zamanı
    description TEXT                              -- Description / Açıklama
);

/*
    TABLE / TABLO : debt_item

    PURPOSE / AMAÇ:
    Represents expected monthly debts per unit.
    Daire bazlı aylık borçları temsil eder.
*/
CREATE TABLE debt_item (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES unit(id)
        ON DELETE CASCADE NOT NULL,               -- Related unit / İlgili daire
    type VARCHAR(10) NOT NULL
        CHECK (type IN ('DUES', 'FUEL', 'OTHER')),-- Debt type / Borç türü
    period_month DATE NOT NULL,                   -- Debt period / Borç dönemi
    expected_amount NUMERIC(10,2) NOT NULL,       -- Expected amount / Beklenen tutar
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('UNPAID', 'PAID', 'PARTIAL')), -- Payment status / Durum
    UNIQUE (unit_id, type, period_month)
);

/*
    TABLE / TABLO : payment

    PURPOSE / AMAÇ:
    Stores received payments.
    Alınan ödemeleri tutar.
*/
CREATE TABLE payment (
    id SERIAL PRIMARY KEY,
    complex_id INTEGER REFERENCES complex_properties(id)
        ON DELETE RESTRICT NOT NULL,              -- Site reference / Site referansı
    unit_id INTEGER REFERENCES unit(id)
        ON DELETE RESTRICT NOT NULL,              -- Paying unit / Ödeme yapan daire
    amount NUMERIC(10,2) NOT NULL,                -- Paid amount / Ödenen tutar
    process_date TIMESTAMP NOT NULL,              -- Receipt date / Dekont tarihi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Entry time / Giriş zamanı
    reference_no VARCHAR(50),                     -- Reference number / Referans no
    description TEXT                              -- Description / Açıklama
);

/*
    TABLE / TABLO : payment_debt

    PURPOSE / AMAÇ:
    Creates a many-to-many relationship between payments and debts.
    Ödemeler ile borçlar arasında çoktan-çoğa ilişki kurar.
*/
CREATE TABLE payment_debt (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payment(id)
        ON DELETE CASCADE NOT NULL,               -- Payment reference / Ödeme referansı
    debt_item_id INTEGER REFERENCES debt_item(id)
        ON DELETE CASCADE NOT NULL,               -- Debt reference / Borç referansı
    covered_amount NUMERIC(10,2) NOT NULL,        -- Covered amount / Karşılanan tutar
    UNIQUE (payment_id, debt_item_id)
);

------------------------------
/*
    TABLE: unit
    PURPOSE (EN): Indicates whether a unit (apartment) is exempt from payments
                  such as dues or fees.
    PURPOSE (TR): Dairenin aidat veya benzeri ödemelerden muaf olup olmadığını
                  belirtir.
*/
ALTER TABLE unit
ADD COLUMN IF NOT EXISTS is_exempt BOOLEAN DEFAULT FALSE;

/*
    TABLE: unit (Custom Dues)
    PURPOSE (EN): Allows setting a custom dues amount for specific units
                  (e.g., specific agreements or discounts).
    PURPOSE (TR): Belirli daireler için özel aidat tutarı tanımlamaya izin verir
                  (ör. özel anlaşmalar veya indirimler).
    
    DEFAULT: NULL (Use standard dues / Standart aidat kullanılır)
*/
ALTER TABLE unit
ADD COLUMN IF NOT EXISTS custom_dues_amount NUMERIC(10,2) DEFAULT NULL;
