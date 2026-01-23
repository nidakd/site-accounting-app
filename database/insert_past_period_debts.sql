/* 
   FILE NAME: insert_past_period_debts.sql
   PURPOSE: clean start for Jan 2026.
*/

-- 1. Create Jan 2026 Dues for ALL units
-- Auto-handles Exempt units (marked PAID)
-- Auto-handles Custom Dues (200 TL instead of 800)
INSERT INTO debt_item (unit_id, type, period_month, expected_amount, status)
SELECT 
    id,
    'DUES',
    '2026-01-01',
    COALESCE(custom_dues_amount, 800.00),
    CASE 
        WHEN is_exempt = TRUE THEN 'PAID' -- Exempt users are auto-paid
        ELSE 'UNPAID' 
    END
FROM unit;
