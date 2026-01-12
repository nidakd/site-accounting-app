/* 
   FILE NAME / DOSYA ADI : inters_past_period_debts.sql
   PROJECT / PROJE      : Sellable Site Management Accounting Interface
                          Satılabilir Site Yönetimi Muhasebe Arayüzü

   PURPOSE / AMAÇ:
   EN: Inserts historical (past-period) debt records for apartments.
       This script is used to initialize dues and fuel debts that
       belong to December 2025 and earlier periods.

   TR: Dairelere ait geçmiş dönem (historical) borç kayıtlarını ekler.
       Bu script, Aralık 2025 ve öncesine ait aidat ve yakıt borçlarının
       sisteme ilk kez tanımlanması amacıyla kullanılır.

   IMPORTANT / ÖNEMLİ:
   EN: This script does NOT generate future debts.
   TR: Bu script geleceğe yönelik borç üretmez.

   NOTES / NOTLAR:
   - EN: Intended to be executed once during system setup or migration.
   - TR: Sistem kurulumu veya veri aktarımı sırasında bir defaya mahsus çalıştırılır.
*/

-----------------------------------------------------------
-- HISTORICAL DUES DEFINITION (DECEMBER 2025)
-- GEÇMİŞ DÖNEM AİDAT BORCU TANIMLAMA (ARALIK 2025)
-----------------------------------------------------------
/*
   EN:
   Creates an UNPAID monthly dues debt for every apartment
   for December 2025.

   TR:
   Aralık 2025 dönemi için tüm dairelere ödenmemiş (UNPAID)
   aidat borcu tanımlar.
*/
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status)
SELECT 
    id,                 -- EN/TR: Apartment identifier / Daire kimliği
    'DUES',              -- EN: Monthly dues / TR: Aidat
    '2025-12-01',        -- EN: Period start date / TR: Dönem başlangıcı
    800.00,              -- EN/TR: Dues amount / Aidat tutarı
    'UNPAID'             -- EN: Initial debt status / TR: Başlangıç durumu
FROM unit;




/* KT1 BLOĞU - ÖDENMEMİŞ GEÇMİŞ BORÇLARIN GİRİŞİ */

-- Tayfun Arapoğlu (ID: 4) - Toplam Birikmiş Borç
-- 2024-12-01 tarihini 'devir tarihi' olarak kullanıyoruz.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (4, 'OTHER', '2024-12-01', 13468.00, 'UNPAID');

-- Fatih Ercan (ID: 5) - Kasım ve Aralık Borcu (Ekranda 1600 görünüyor)
-- Zaten Aralık aidatını (800) otomatik eklemiştik, şimdi Kasım'ı ekleyelim.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (5, 'DUES', '2025-11-01', 800.00, 'UNPAID');

-- Yakup Akyüz (ID: 6) - Ekim, Kasım ve Aralık Borcu (Ekranda 2400 görünüyor)
-- Aralık zaten var, Ekim ve Kasım'ı ekleyelim.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (6, 'DUES', '2025-10-01', 800.00, 'UNPAID'),
       (6, 'DUES', '2025-11-01', 800.00, 'UNPAID');


/* CELAL ŞEN (ID: 10) BORÇ DÜZELTME */

-- 1. Daha önce girdiğimiz 800 TL'lik Aralık aidatını 200 TL'ye indiriyoruz
UPDATE debt_item 
SET expected_amount = 200.00 
WHERE unit_id = 10 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';

-- 2. Temmuz'dan Kasım sonuna kadar olan toplam 700 TL birikmiş borcu ekliyoruz
-- (Temmuz-Ağustos-Eylül: 3x100 + Ekim-Kasım: 2x200 = 700 TL)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (10, 'OTHER', '2025-11-01', 700.00, 'UNPAID');

/* MURAT KIROĞLU (ID: 34) BORÇ DÜZELTME */

-- 1. Daha önce otomatik atanan 800 TL'lik Aralık aidatını 200 TL'ye indiriyoruz
UPDATE debt_item 
SET expected_amount = 200.00 
WHERE unit_id = 34 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';

-- 2. Nisan - Kasım arası birikmiş 1000 TL borcu ekliyoruz
-- (Nisan-Eylül: 6 ay x 100 TL = 600 TL)
-- (Ekim-Kasım: 2 ay x 200 TL = 400 TL)
-- TOPLAM: 1000 TL Geçmiş Borç
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (34, 'OTHER', '2025-11-01', 1000.00, 'UNPAID');

/* KT2 BLOĞU - KALAN EKSİKLERİN TAMAMLANMASI */

-- 1. Ali Erdem (ID: 9) - Ekim ve Kasım Aidatları (Aralık zaten var)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(9, 'DUES', '2025-10-01', 800.00, 'UNPAID'),
(9, 'DUES', '2025-11-01', 800.00, 'UNPAID');

-- 2. Okan Şener (ID: 13) - Sadece Kasım Aidatı (Aralık zaten var)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(13, 'DUES', '2025-11-01', 800.00, 'UNPAID');

-- 3. Durhan Bay (ID: 12) - YÖNETİCİ MUAFİYETİ
-- Aralık aidatını 'ÖDENDİ' olarak işaretleyip kapatıyoruz.
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 12 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';

  /* KT4 BLOĞU - MALİ DURUM GÜNCELLEME 
   (Murat Çilli'nin geçmiş borcu ve Yönetici muafiyeti dahil)
*/

-- 1. CİDDİ BİRİKMİŞ BORÇLARIN GİRİŞİ (Emrah Kurt ve Murat Say)
-- Aralık ayı aidatı (800 TL) sistemde zaten tanımlı olduğu için toplam bakiyeden 800 TL düşerek giriyoruz.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(31, 'OTHER', '2025-11-01', 6600.00, 'UNPAID'), -- Emrah Kurt: Toplam 7400 (6600 Geçmiş + 800 Aralık)
(32, 'OTHER', '2025-11-01', 6100.00, 'UNPAID'); -- Murat Say: Toplam 6900 (6100 Geçmiş + 800 Aralık)

-- 2. MURAT ÇİLLİ (ID: 28) - GEÇMİŞTEN KALAN EKSİK BORÇ
-- Belirttiğin Eylül döneminden sarkan 500 TL'lik borcu ekliyoruz.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (28, 'OTHER', '2025-09-01', 500.00, 'UNPAID');

-- 3. BEYTULLAH İNCE (ID: 26) - YÖNETİCİ MUAFİYETİ
-- Apartman yöneticisi olduğu için Aralık ayı borcunu "ÖDENDİ" olarak kapatıyoruz.
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 26 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';

  /* KT5 BLOĞU - GEÇMİŞ BORÇ GİRİŞİ */

-- Tuncay Kadan (ID: 33)
-- Toplam 3400 TL borç (Aralık 800 dahil).
-- Geçmiş borç: 3400 - 800 = 2600 TL.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (33, 'OTHER', '2025-11-01', 2600.00, 'UNPAID');


/* KT6 BLOĞU - MALİ DURUM GÜNCELLEME */

-- 1. MEHMET YAP (ID: 45) - KASIM AİDATI EKLEME
-- Aralık aidatı (800 TL) zaten var, yanına Kasım'ı (800 TL) ekliyoruz. Toplam 1600 TL olacak.
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (45, 'DUES', '2025-11-01', 800.00, 'UNPAID');

-- 2. MUSTAFA ALTINDAL (ID: 42) - YÖNETİCİ MUAFİYETİ
-- Yönetici olduğu için Aralık aidatını "ÖDENDİ" olarak işaretliyoruz.
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 42 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';


  /* KT7 BLOĞU - YÖNETİCİ MUAFİYETİ */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 51 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';


  /* 1. TÜM SİTEYE OCAK 2026 AİDATI ATAMA */
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status)
SELECT id, 'DUES', '2026-01-01', 800.00, 'UNPAID'
FROM unit;

/* 2. ÖZEL ANLAŞMALI DAİRELERİN DÜZELTİLMESİ (200 TL) */
UPDATE debt_item 
SET expected_amount = 200.00 
WHERE period_month = '2026-01-01' 
  AND unit_id IN (10, 34); -- Celal Şen ve Murat Kıroğlu

/* 3. YÖNETİCİ MUAFİYETLERİNİN UYGULANMASI */
UPDATE debt_item 
SET status = 'PAID'
WHERE period_month = '2026-01-01' 
  AND unit_id IN (12, 26, 42, 51); -- Durhan, Beytullah, Mustafa, Güler


  /* KT1 BLOĞU - YAKIT BORÇLARI KESİN LİSTE */

-- 1. Murat Özçelik (ID: 1) - Aralık Borcu
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (1, 'FUEL', '2025-12-01', 1571.00, 'UNPAID');

-- 2. Halenur Demirel (ID: 2) - Aralık Borcu
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (2, 'FUEL', '2025-12-01', 1425.00, 'UNPAID');

-- 3. Azmi Kayacı (ID: 3) - Aralık + Eksik Kalan Bakiye (50 TL)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(3, 'FUEL', '2025-12-01', 1194.00, 'UNPAID'),
(3, 'FUEL', '2025-11-01', 50.00, 'UNPAID'); -- Eksik ödeme bakiyesi

-- 4. Tayfun Arapoğlu (ID: 4) - Aralık + Geçen Kış Devri (5930 TL - Lacivert)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(4, 'FUEL', '2025-12-01', 1273.00, 'UNPAID'),
(4, 'FUEL', '2024-01-01', 5930.00, 'UNPAID'); -- Gerçek geçen kış borcu

-- 5. Fatih Ercan (ID: 5) - Ekim, Kasım, Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(5, 'FUEL', '2025-10-01', 744.50, 'UNPAID'),
(5, 'FUEL', '2025-11-01', 849.31, 'UNPAID'),
(5, 'FUEL', '2025-12-01', 1194.00, 'UNPAID');

-- 6. Yakup Akyüz (ID: 6) - Ekim, Kasım, Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(6, 'FUEL', '2025-10-01', 876.20, 'UNPAID'),
(6, 'FUEL', '2025-11-01', 1235.00, 'UNPAID'),
(6, 'FUEL', '2025-12-01', 1699.00, 'UNPAID');

-- 8. Nurgül Kumaş (ID: 8) - Aralık Borcu
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (8, 'FUEL', '2025-12-01', 1462.00, 'UNPAID');

/* KT2 BLOĞU - YAKIT BORÇLARI (KESİN TUTARLAR) */

-- 1. Ali Erdem (ID: 9) - Ekim, Kasım, Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(9, 'FUEL', '2025-10-01', 1837.00, 'UNPAID'),
(9, 'FUEL', '2025-11-01', 1795.00, 'UNPAID'),
(9, 'FUEL', '2025-12-01', 2110.00, 'UNPAID');

-- 2. Celal Şen (ID: 10) - Ekim, Kasım, Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(10, 'FUEL', '2025-10-01', 248.00, 'UNPAID'),
(10, 'FUEL', '2025-11-01', 850.00, 'UNPAID'),
(10, 'FUEL', '2025-12-01', 1194.00, 'UNPAID');

-- 3. Emriye Sürer (ID: 11) - Sadece Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (11, 'FUEL', '2025-12-01', 1522.00, 'UNPAID');

-- 4. Durhan Bay (ID: 12) - Sadece Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (12, 'FUEL', '2025-12-01', 1043.00, 'UNPAID');

/* KT3 BLOĞU - YAKIT BORÇLARI VE EKSİK BAKİYELER (KESİN LİSTE) */

-- 1. Kamil Önay (ID: 24) - Aralık Yakıt Borcu
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (24, 'FUEL', '2025-12-01', 1172.00, 'UNPAID');

-- 2. Eksik Kalan Bakiyelerin Girilmesi
-- (Tutar ve isim eşleştirmelerini senin verdiğin verilere göre güncelledim)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(17, 'FUEL', '2025-11-01', 35.00, 'UNPAID'),  -- Murat Sakallı (ID: 17)
(18, 'FUEL', '2025-11-01', 35.00, 'UNPAID'),  -- Ahmet Yap (ID: 18)
(19, 'FUEL', '2025-11-01', 737.00, 'UNPAID'), -- Selçuk Yıldırım (ID: 19)
(20, 'FUEL', '2025-11-01', 70.00, 'UNPAID');  -- Zafer Sakaoğlu (ID: 20)

/* KT4 BLOĞU - YAKIT BORÇLARI VE GEÇMİŞ KIŞ DEVİRLERİ */

-- 1. Küçük Bakiye Eksikleri (Ocak sütunundaki 35 TL'ler)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(25, 'FUEL', '2025-11-01', 35.00, 'UNPAID'), -- Emre Al
(26, 'FUEL', '2025-11-01', 35.00, 'UNPAID'); -- Beytullah İnce

-- 2. Aylık Yakıt Borçları (Gülizar, Emrah D., Yusuf Yasin)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(27, 'FUEL', '2025-10-01', 493.00, 'UNPAID'),  -- Gülizar Usta (Ekim)
(29, 'FUEL', '2025-12-01', 896.00, 'UNPAID'),  -- Emrah Durkan (Aralık)
(30, 'FUEL', '2025-11-01', 1284.80, 'UNPAID'), -- Yusuf Yasin (Kasım)
(30, 'FUEL', '2025-12-01', 1608.00, 'UNPAID'); -- Yusuf Yasin (Aralık)

-- 3. Emrah Kurt (ID: 31) - Ekim, Kasım, Aralık + 9332 TL Lacivert Devir
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(31, 'FUEL', '2025-10-01', 795.00, 'UNPAID'),
(31, 'FUEL', '2025-11-01', 1576.78, 'UNPAID'),
(31, 'FUEL', '2025-12-01', 1783.00, 'UNPAID'),
(31, 'FUEL', '2024-01-01', 9332.00, 'UNPAID'); -- Lacivert (Geçmiş Kış)

-- 4. Murat Say (ID: 32) - Ekim, Kasım, Aralık + 11288 TL Lacivert Devir
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(32, 'FUEL', '2025-10-01', 752.00, 'UNPAID'),
(32, 'FUEL', '2025-11-01', 1062.91, 'UNPAID'),
(32, 'FUEL', '2025-12-01', 1751.00, 'UNPAID'),
(32, 'FUEL', '2024-01-01', 11288.00, 'UNPAID'); -- Lacivert (Geçmiş Kış)

/* KT5 BLOĞU - YAKIT BORÇLARI VE ÖZEL BAKİYELER */

-- 1. Tuncay Kadan (ID: 33) - 3 Ay Ödenmemiş
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(33, 'FUEL', '2025-10-01', 646.50, 'UNPAID'),
(33, 'FUEL', '2025-11-01', 1007.00, 'UNPAID'),
(33, 'FUEL', '2025-12-01', 1515.00, 'UNPAID');

-- 2. Murat Kıroğlu (ID: 34) - Aralık + 500 TL Gider/Bakiye
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(34, 'FUEL', '2025-12-01', 1315.00, 'UNPAID'),
(34, 'FUEL', '2025-11-01', 500.00, 'UNPAID'); -- '500 gider' notuna istinaden

-- 3. Fahri Aktaş (ID: 37) - Aralık + 128 TL Borç
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(37, 'FUEL', '2025-12-01', 1515.00, 'UNPAID'),
(37, 'FUEL', '2025-11-01', 128.00, 'UNPAID');

-- 4. Ertuğrul Kaya (ID: 39) - Sadece Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (39, 'FUEL', '2025-12-01', 1515.00, 'UNPAID');
/* KT6 BLOĞU - MEHMET YAP VE YUSUF KARAL YAKIT GÜNCELLEMESİ */

-- 1. MEHMET YAP (ID: 45) Borçları
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(45, 'FUEL', '2025-11-01', 807.00, 'UNPAID'),
(45, 'FUEL', '2025-12-01', 1315.00, 'UNPAID'),
(45, 'FUEL', '2025-11-15', 500.00, 'UNPAID'); -- '500 Gider' borcu

-- MEHMET YAP (ID: 45) 300 TL Artı Bakiye (Gelecek borçtan düşmek üzere)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (45, 'FUEL', '2025-12-31', -300.00, 'PAID'); 


-- 2. YUSUF KARAL (ID: 47) Borçları
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(47, 'FUEL', '2025-11-01', 807.00, 'UNPAID'),
(47, 'FUEL', '2025-12-01', 1315.00, 'UNPAID');
/* KT7 BLOĞU - YAKIT BORÇLARI GİRİŞİ */

-- 1. Samet Aydın (ID: 50) - Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (50, 'FUEL', '2025-12-01', 1463.00, 'UNPAID');

-- 2. Caner Yılmaz (ID: 53) - Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (53, 'FUEL', '2025-12-01', 1663.00, 'UNPAID');

-- 3. Bekir Helimergün (ID: 55) - Kasım ve Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) VALUES 
(55, 'FUEL', '2025-11-01', 1269.00, 'UNPAID'),
(55, 'FUEL', '2025-12-01', 1663.00, 'UNPAID');

-- 4. Recai Uluışık (ID: 56) - Aralık
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status) 
VALUES (56, 'FUEL', '2025-12-01', 1463.00, 'UNPAID');

/* 1. AZMİ KAYACI (ID: 3) - ELDEN ÖDEME */
-- Kasaya girmemesi için direkt borç tablosunu güncelliyoruz
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 3 
  AND period_month = '2025-12-01' 
  AND type = 'DUES';

/* 2. BANKAYA YATAN DİĞER ÖDEMELER */
-- Hem created_at hem de process_date sütunlarını dolduruyoruz
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) VALUES 
(1, 1, 800.00, '2025-12-07', '2025-12-07', 'Aralık 2025 Aidat Ödemesi'),
(1, 2, 800.00, '2025-12-05', '2025-12-05', 'Aralık 2025 Aidat Ödemesi'),
(1, 7, 800.00, '2025-12-23', '2025-12-23', 'Aralık 2025 Aidat Ödemesi'),
(1, 8, 800.00, '2025-12-05', '2025-12-05', 'Aralık 2025 Aidat Ödemesi');

/* KT2 BLOĞU - ARALIK 2025 AİDAT TAHSİLATLARI */

-- 1. Fikret Demirel (ID: 13)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 13, 800.00, '2025-12-02', '2025-12-02', 'Aralık 2025 Aidat Ödemesi');

-- 2. Kerem Veziroğlu (ID: 14)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 14, 800.00, '2025-12-25', '2025-12-25', 'Aralık 2025 Aidat Ödemesi');

-- 3. Nermin Kahraman (ID: 15)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 15, 800.00, '2025-12-06', '2025-12-06', 'Aralık 2025 Aidat Ödemesi');

/* KT3 BLOĞU - ARALIK 2025 AİDAT TAHSİLATLARI */

-- 1. Murat Sakallı (ID: 17)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 17, 800.00, '2025-12-06', '2025-12-06', 'Aralık 2025 Aidat Ödemesi');

-- 2. Ahmet Yap (ID: 18)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 18, 800.00, '2025-12-26', '2025-12-26', 'Aralık 2025 Aidat Ödemesi');

-- 3. Emel Kural (ID: 19)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 19, 800.00, '2025-12-12', '2025-12-12', 'Aralık 2025 Aidat Ödemesi');

-- 4. Gürdal Çubukçu (ID: 20)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 20, 800.00, '2025-12-03', '2025-12-03', 'Aralık 2025 Aidat Ödemesi');

-- 5. Özkan Kahraman (ID: 21)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 21, 800.00, '2025-12-26', '2025-12-26', 'Aralık 2025 Aidat Ödemesi');

-- 6. Kamil Önay (ID: 22)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 22, 800.00, '2025-12-01', '2025-12-01', 'Aralık 2025 Aidat Ödemesi');

-- 7. Selçuk Yıldırım (ID: 23) - Erken Ödeme (Temmuz)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 23, 800.00, '2025-07-05', '2025-07-05', 'Aralık 2025 Aidat Ödemesi (Peşin/Avans)');

-- 8. Zafer Sakaoğlu (ID: 24) - Erken Ödeme (Kasım)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 24, 800.00, '2025-11-05', '2025-11-05', 'Aralık 2025 Aidat Ödemesi (Ön Ödeme)');
/* Beytullah İnce (ID: 26) - Yönetici Muafiyeti Uygulaması */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 26 
  AND type = 'DUES' 
  AND period_month = '2025-12-01';

/* KT4 BLOĞU - ARALIK 2025 AİDAT TAHSİLATLARI */

-- 1. Emre Al (ID: 25)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 25, 800.00, '2025-12-15', '2025-12-15', 'Aralık 2025 Aidat Ödemesi');

-- 2. Gülizar Usta (ID: 27)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 27, 800.00, '2025-12-15', '2025-12-15', 'Aralık 2025 Aidat Ödemesi');

-- 3. Murat Çilli (ID: 28)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 28, 800.00, '2025-12-02', '2025-12-02', 'Aralık 2025 Aidat Ödemesi');

-- 4. Yusuf Yasin Çillioğlu (ID: 30)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 30, 800.00, '2025-12-04', '2025-12-04', 'Aralık 2025 Aidat Ödemesi');

/* KT5 BLOĞU - ARALIK 2025 AİDAT TAHSİLATLARI */

-- 1. Ahmet Akdoğan (ID: 36)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 36, 800.00, '2025-12-13', '2025-12-13', 'Aralık 2025 Aidat Ödemesi');

-- 2. Fahri Aktaş (ID: 37)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 37, 800.00, '2025-12-09', '2025-12-09', 'Aralık 2025 Aidat Ödemesi');

-- 3. Oktay Dik (ID: 38)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 38, 800.00, '2025-12-19', '2025-12-19', 'Aralık 2025 Aidat Ödemesi');

-- 4. Ertuğrul Kaya (ID: 39)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 39, 800.00, '2025-12-03', '2025-12-03', 'Aralık 2025 Aidat Ödemesi');

-- 5. Ersin Toprak (ID: 40)
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 40, 800.00, '2025-12-07', '2025-12-07', 'Aralık 2025 Aidat Ödemesi');

/* KT6 BLOĞU TAHSİLATLARI VE MUAFİYETLER */

-- Mustafa Altındal (ID: 42) - Muafiyet (Kasaya para girmeden borç kapatma)
UPDATE debt_item SET status = 'PAID' WHERE unit_id = 42 AND type = 'DUES' AND period_month = '2025-12-01';

-- KT6 Ödemeleri
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) VALUES 
(1, 41, 800.00, '2025-12-23', '2025-12-23', 'Aralık 2025 Aidat Ödemesi'), -- Çetin Özkan
(1, 43, 800.00, '2025-12-21', '2025-12-21', 'Aralık 2025 Aidat Ödemesi'), -- Mücahit Tunç
(1, 44, 800.00, '2025-12-15', '2025-12-15', 'Aralık 2025 Aidat Ödemesi'), -- Huri Palazoğlu
(1, 46, 800.00, '2025-12-15', '2025-12-15', 'Aralık 2025 Aidat Ödemesi'), -- Murat Özkan
(1, 47, 800.00, '2025-11-14', '2025-11-14', 'Aralık 2025 Aidat (Ön Ödeme)'), -- Yusuf Karal
(1, 48, 800.00, '2025-11-16', '2025-11-16', 'Aralık 2025 Aidat (Ön Ödeme)'); -- Davut Öztürk

/* KT7 BLOĞU TAHSİLATLARI VE MUAFİYETLER */

-- Güler Akdoğan (ID: 51) - Muafiyet
UPDATE debt_item SET status = 'PAID' WHERE unit_id = 51 AND type = 'DUES' AND period_month = '2025-12-01';

-- KT7 Ödemeleri
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) VALUES 
(1, 49, 800.00, '2025-12-21', '2025-12-21', 'Aralık 2025 Aidat Ödemesi'), -- Ümmühan Ardıç
(1, 50, 800.00, '2025-12-26', '2025-12-26', 'Aralık 2025 Aidat Ödemesi'), -- Samet Aydın
(1, 52, 800.00, '2025-12-25', '2025-12-25', 'Aralık 2025 Aidat Ödemesi'), -- Fazlı Tezcan
(1, 53, 800.00, '2025-12-10', '2025-12-10', 'Aralık 2025 Aidat Ödemesi'), -- Caner Yıldırım
(1, 54, 800.00, '2025-11-21', '2025-11-21', 'Aralık 2025 Aidat (Ön Ödeme)'), -- Murat Koca
(1, 55, 800.00, '2025-12-01', '2025-12-01', 'Aralık 2025 Aidat Ödemesi'); -- Bekir Helimergün


/* 1. CELAL ŞEN'İN TÜM BORÇLARINI ÖDENDİ OLARAK GÜNCELLE */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 10 
  AND status = 'UNPAID'
  AND period_month <= '2025-12-01';

/* 2. TAHSİLAT KAYDINI OLUŞTUR (Trigger sayesinde kasaya otomatik işlenir) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 10, 3200.00, CURRENT_DATE, CURRENT_DATE, 'Celal Şen - Tüm borçlar kapatıldı (Aralık dahil)');

/* 1. EMRIYE SÜRER (ID: 11) BORÇLARINI 'ÖDENDİ' YAP */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 11 
  AND status = 'UNPAID'
  AND period_month <= '2025-12-01';

/* 2. TAHSİLAT KAYDINI GİR (2320 TL) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 11, 2320.00, CURRENT_DATE, CURRENT_DATE, 'Emriye Sürer - Aralık borçları kapatıldı');


--kt5d7
/* 1. TÜM BORÇLARI (ARALIK 2025 VE OCAK 2026) 'ÖDENDİ' YAP */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 39 
  AND status = 'UNPAID'
  AND (period_month = '2025-12-01' OR period_month = '2026-01-01');

/* 2. TOPLAM TAHSİLAT KAYDINI GİR (3115 TL) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 39, 3115.00, '2025-12-28', '2025-12-28', 'Ertuğrul Kaya - Aralık Yakıt+Aidat ve Ocak Aidat Peşin Ödemesi');


/* 1. YAKUP AKYÜZ (ID: 6) TÜM GEÇMİŞ BORÇLARI 'ÖDENDİ' YAP */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 6 
  AND status = 'UNPAID'
  AND period_month <= '2025-12-01';

/* 2. TAHSİLAT KAYDINI OLUŞTUR (29.12.2025) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 6, 6211.00, '2025-12-29', '2025-12-29', 'Yakup Akyüz (KT1 D6) - Ekim-Kasım-Aralık Tüm Borçlar Kapatıldı');


/* 1. KASIM YAKIT BORCUNU TAMAMEN KAPAT (En eski borç) */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 30 
  AND type = 'FUEL' 
  AND period_month = '2025-11-01';

/* 2. ARALIK YAKIT BORCUNU 30 TL OLARAK GÜNCELLE */
-- Mevcut borcun sadece 30 TL'lik kısmını ödenmemiş olarak bırakıyoruz
UPDATE debt_item 
SET expected_amount = 30.00
WHERE unit_id = 30 
  AND type = 'FUEL' 
  AND period_month = '2025-12-01';

/* 1. OCAK AİDATINI (800 TL) 'ÖDENDİ' OLARAK KAPAT */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 22 
  AND type = 'DUES' 
  AND period_month = '2026-01-01';

/* 2. ARALIK YAKITINI 35 TL KALACAK ŞEKİLDE GÜNCELLE */
-- 1172 TL olan borcun 1137 TL'si ödendi, 35 TL bakiye kaldı.
UPDATE debt_item 
SET expected_amount = 35.00
WHERE unit_id = 22 
  AND type = 'FUEL' 
  AND period_month = '2025-12-01';

/* 3. TAHSİLAT KAYDINI OLUŞTUR (Toplam 1937 TL) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 22, 1937.00, CURRENT_DATE, CURRENT_DATE, 'Kamil Önay - Ocak Aidat (Tam) ve Aralık Yakıt (1137 TL ödendi, 35 TL kaldı)');

/* 1. ARALIK YAKIT BORCUNU 35 TL BAKİYE KALACAK ŞEKİLDE GÜNCELLE */
UPDATE debt_item 
SET expected_amount = 35.00
WHERE unit_id = 29 
  AND type = 'FUEL' 
  AND period_month = '2025-12-01';

/* 2. TAHSİLAT KAYDINI GİR (861 TL) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 29, 861.00, CURRENT_DATE, CURRENT_DATE, 'Emrah Durkan - Aralık Yakıt (861 TL ödendi, 35 TL kaldı)');

/* 1. OCAK AİDATINI 'ÖDENDİ' OLARAK KAPAT */
UPDATE debt_item 
SET status = 'PAID'
WHERE unit_id = 14 
  AND type = 'DUES' 
  AND period_month = '2026-01-01';

/* 2. TAHSİLAT KAYDINI GİR (800 TL) */
INSERT INTO payment (complex_id, unit_id, amount, created_at, process_date, description) 
VALUES (1, 14, 800.00, CURRENT_DATE, CURRENT_DATE, 'Fikret Demirel - Ocak Aidat Ödemesi');