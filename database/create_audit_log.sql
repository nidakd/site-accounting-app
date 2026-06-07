-- ============================================================
-- Audit Log Table Creation
-- Tüm sistem işlemlerinin kaydı
-- ============================================================

DROP TABLE IF EXISTS audit_log CASCADE;

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,              -- INSERT, UPDATE, DELETE, PAYMENT, DOWNLOAD, etc.
    table_name VARCHAR(50) NOT NULL,               -- Etkilenen tablo adı
    affected_record_id INTEGER,                    -- Etkilenen satır ID (NULL olabilir)
    details TEXT,                                  -- JSON format detaylar
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- İndeksleme
    CONSTRAINT valid_action_type CHECK (action_type IN (
        'PAYMENT_RECORDED', 'DEBT_CREATED', 'BULK_DUES', 'BULK_FUEL', 'BULK_PAST',
        'REPORT_DOWNLOADED', 'USER_LOGIN', 'USER_LOGOUT', 'DATA_EXPORT',
        'INSERT', 'UPDATE', 'DELETE'
    ))
);

-- Performans İndeksleri
CREATE INDEX idx_audit_user_date ON audit_log(user_id, action_date DESC);
CREATE INDEX idx_audit_action_type ON audit_log(action_type, action_date DESC);
CREATE INDEX idx_audit_table_record ON audit_log(table_name, affected_record_id);
CREATE INDEX idx_audit_date ON audit_log(action_date DESC);

-- Örnek Veri
INSERT INTO audit_log (user_id, action_type, table_name, affected_record_id, details)
VALUES 
    (1, 'USER_LOGIN', 'app_user', 1, '{"timestamp":"2026-06-07"}'),
    (1, 'PAYMENT_RECORDED', 'payment', 101, '{"unit_id":10,"amount":5000,"description":"Aidat"}');

-- Kontrol
SELECT * FROM audit_log ORDER BY action_date DESC LIMIT 5;
