/* 
   FILE NAME / DOSYA ADI : insert_initial_data.sql

   PURPOSE / AMAÇ:
   EN: Inserts all initial (seed) data fully compatible with the revised schema.
       Includes Site Info, Buildings, Unit Types, 56 Units (Correct List),
       Employees, and exemptions/custom dues settings.

   TR: Yeni şema ile tamamen uyumlu başlangıç verilerini ekler.
       Site Bilgisi, Bloklar, Daire Tipleri, 56 Daire (Doğru Liste),
       Çalışanlar ve muafiyet/özel aidat ayarlarını içerir.
*/

-----------------------------------------------------------
-- 1. SITE INFORMATION / SİTE BİLGİSİ
-----------------------------------------------------------
INSERT INTO complex_properties (name, total_units, currency, dues_collection_day)
VALUES (
    'DUZCE ILI KAYNASLI ILCESI KARACALI MAHALLESI TOPLU KONUTLARI',
    56,        
    'TRY',     
    1          
);

-----------------------------------------------------------
-- 2. BUILDINGS / BLOKLAR
-----------------------------------------------------------
INSERT INTO building (complex_id, name) VALUES 
(1, 'KT1'), (1, 'KT2'), (1, 'KT3'),
(1, 'KT4'), (1, 'KT5'), (1, 'KT6'), (1, 'KT7');

-----------------------------------------------------------
-- 3. UNIT TYPES / DAİRE TİPLERİ
-----------------------------------------------------------
/*
   EN: Defines standard apartment types (2+1, 3+1).
   TR: Standart daire tipleri (2+1, 3+1) tanımlanır.
*/
INSERT INTO unit_type (complex_id, name, default_dues) VALUES
(1, '2+1', 800.00),
(1, '3+1', 800.00);

-----------------------------------------------------------
-- 4. SYSTEM USERS / SİSTEM KULLANICILARI
-----------------------------------------------------------
INSERT INTO app_user (complex_id, username, password_hash, role) VALUES 
(1, 'nidakd', 'muhasebe123', 'admin');

-----------------------------------------------------------
-- 5. ALL APARTMENTS (56 UNITS) / TÜM DAİRELER (56 ADET)
-----------------------------------------------------------
/*
   EN:
   Inserts all apartment records grouped by building.
   Each building contains 8 apartments.

   TR:
   Tüm daire kayıtları blok bazlı olarak eklenir.
   Her blokta 8 daire bulunmaktadır.
*/

-- KT1 (building_id = 1)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(1, 1, '1', 'MURAT ÖZÇELİK'), (1, 2, '2', 'HALENUR DEMİREL'),
(1, 1, '3', 'AZMİ KAYACI'),   (1, 2, '4', 'TAYFUN ARAPOĞLU'),
(1, 1, '5', 'FATİH ERCAN'),   (1, 2, '6', 'YAKUP AKYÜZ'),
(1, 1, '7', 'ASUMAN MADENCİOĞLU'), (1, 2, '8', 'NİRGÜL KUMAŞ');

-- KT2 (building_id = 2)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(2, 2, '1', 'ALİ ERDEM'), (2, 1, '2', 'CELAL ŞEN'),
(2, 2, '3', 'EMRİYE SÜRER'), (2, 1, '4', 'DURHAN BAY'),
(2, 2, '5', 'OKAN ŞENER'), (2, 1, '6', 'FİKRET DEMİREL'),
(2, 2, '7', 'KEREM VEZİROĞLU'), (2, 1, '8', 'NERMİN KAHRAMAN');

-- KT3 (building_id = 3)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(3, 2, '1', 'MURAT SAKALLI'), (3, 1, '2', 'AHMET YAP'),
(3, 2, '3', 'EMEL KURAL'), (3, 1, '4', 'GÜRDAL ÇUBUKÇU'),
(3, 2, '5', 'ÖZKAN KAHRAMAN'), (3, 1, '6', 'KAMİL ÖNAY'),
(3, 2, '7', 'SELÇUK YILDIRIM'), (3, 1, '8', 'ZAFER SAKAOĞLU');

-- KT4 (building_id = 4)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(4, 1, '1', 'EMRE AL'), (4, 2, '2', 'BEYTULLAH İNCE'),
(4, 1, '3', 'GÜLİZAR USTA'), (4, 2, '4', 'MURAT ÇİLLİ'),
(4, 1, '5', 'EMRAH DURKAN'), (4, 2, '6', 'YUSUF YASİN ÇİLLİOĞLU'),
(4, 1, '7', 'EMRAH KURT'), (4, 2, '8', 'MURAT SAY');

-- KT5 (building_id = 5)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(5, 2, '1', 'TUNCAY KADAN'), (5, 1, '2', 'MURAT KIROĞLU'),
(5, 2, '3', 'ÖMER BAYRAM'), (5, 1, '4', 'AHMET AKDOĞAN'),
(5, 2, '5', 'FAHRİ AKTAŞ'), (5, 1, '6', 'OKTAY DİK'),
(5, 2, '7', 'ERTUĞRUL KAYA'), (5, 1, '8', 'ERSİN TOPRAK');

-- KT6 (building_id = 6)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(6, 1, '1', 'ÇETİN ÖZKAN'), (6, 2, '2', 'MUSTAFA ALTUNDAL'),
(6, 1, '3', 'MÜCAHİT TUNÇ'), (6, 2, '4', 'HURİ PALAZOĞLU'),
(6, 1, '5', 'MEHMET YAP'), (6, 2, '6', 'MURAT ÖZKAN'),
(6, 1, '7', 'YUSUF KARAL'), (6, 2, '8', 'DAVUT ÖZTÜRK');

-- KT7 (building_id = 7)
INSERT INTO unit (building_id, unit_type_id, unit_number, owner_name) VALUES
(7, 2, '1', 'ÜMMÜHAN ARDIÇ'), (7, 1, '2', 'SAMET AYDIN'),
(7, 2, '3', 'GÜLER AKDOĞAN'), (7, 1, '4', 'FAZLI TEZCAN'),
(7, 2, '5', 'CANER YILMAZ'), (7, 1, '6', 'MURAT KOCA'),
(7, 2, '7', 'BEKİR HELİMERGÜN'), (7, 1, '8', 'RECAİ ULUIŞIK');


-----------------------------------------------------------
-- 6. EMPLOYEES / ÇALIŞANLAR
-----------------------------------------------------------
INSERT INTO employee (complex_id, name, role, salary) VALUES 
(1, 'Hamiyet Özaltın', 'Temizlik Görevlisi', 4500),
(1, 'Durhan Bay', 'Yönetici (KT1-KT2)', 0),
(1, 'Beytullah İnce', 'Yönetici (KT3-KT4)', 0),
(1, 'Mustafa Altundal', 'Yönetici (KT5-KT6)', 0),
(1, 'Sadettin Akdoğan', 'Yönetici (KT7)', 0),
(1, 'Sadettin Akdoğan', 'Genel Toki Başkanı', 1500);


-----------------------------------------------------------
-- 7. SPECIAL AGREEMENTS & EXEMPTIONS / ÖZEL ANLAŞMALAR VE MUAFİYETLER
-----------------------------------------------------------

/* 1. CUSTOM DUES (200 TL) / ÖZEL AİDATLILAR */
-- Celal Şen (KT2, Daire 2)
UPDATE unit SET custom_dues_amount = 200.00 
WHERE owner_name = 'CELAL ŞEN';

-- Murat Kıroğlu (KT5, Daire 2)
UPDATE unit SET custom_dues_amount = 200.00 
WHERE owner_name = 'MURAT KIROĞLU';


/* 2. EXEMPT MANAGERS / MUAF YÖNETİCİLER */
-- Durhan Bay (KT2, Daire 4)
UPDATE unit SET is_exempt = TRUE WHERE owner_name = 'DURHAN BAY';

-- Beytullah İnce (KT4, Daire 2)
UPDATE unit SET is_exempt = TRUE WHERE owner_name = 'BEYTULLAH İNCE';

-- Mustafa Altundal (KT6, Daire 2)
UPDATE unit SET is_exempt = TRUE WHERE owner_name = 'MUSTAFA ALTUNDAL';

-- Güler Akdoğan (KT7, Daire 3)
UPDATE unit SET is_exempt = TRUE WHERE owner_name = 'GÜLER AKDOĞAN';

