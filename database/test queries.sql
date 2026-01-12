-- Daire (UNIT) Sayısı Kontrolü: 56 olmalı.
SELECT COUNT(*) FROM unit;

-- Blok (BUILDING) Sayısı Kontrolü: 7 olmalı.
SELECT COUNT(*) FROM building;

-- Site (COMPLEX_PROPERTIES) Sayısı Kontrolü: 1 olmalı.
SELECT COUNT(*) FROM complex_properties;



SELECT id, username, role FROM "user";
-- Çıktıda 'muhasebe_yoneticisi' ve 'MANAGER' rolünü görmelisiniz.




SELECT 
    u.unit_number,              -- Daire numarası
    u.owner_name,               -- Ev sahibi
    b.name AS building_name,    -- Blok adı
    ut.name AS unit_type        -- Daire tipi
FROM unit u
JOIN building b 
    ON u.building_id = b.id
JOIN unit_type ut 
    ON u.unit_type_id = ut.id
JOIN complex_properties cp
    ON b.complex_id = cp.id
WHERE cp.id = 1                -- İlgili site (örnek: complex_id = 1)
ORDER BY u.id
LIMIT 5;
