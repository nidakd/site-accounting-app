"""
Audit Log Utility Module
Sistem içindeki tüm işlemleri kaydeder
"""

from src.database.connection import get_connection
from datetime import datetime
import json

def log_action(user_id, action_type, table_name, record_id, details=""):
    """
    Audit log kaydı tutar
    
    Args:
        user_id: İşlemi yapan kullanıcı ID
        action_type: INSERT, UPDATE, DELETE, PAYMENT, DOWNLOAD, etc.
        table_name: Etkilenen tablo adı
        record_id: Etkilenen satır ID
        details: İşlem detayları (JSON string)
    
    Returns:
        bool: Başarı durumu
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log 
            (user_id, action_type, table_name, affected_record_id, details, action_date)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (
            user_id,
            action_type,
            table_name,
            record_id,
            details
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Audit log hatası: {e}")
        return False


def log_payment(user_id, unit_id, amount, description):
    """Ödeme işlemini loglama"""
    details = json.dumps({
        "unit_id": unit_id,
        "amount": float(amount),
        "description": description
    })
    return log_action(user_id, "PAYMENT_RECORDED", "payment", unit_id, details)


def log_debt_created(user_id, unit_id, amount, debt_type, period):
    """Borç oluşturmayı loglama"""
    details = json.dumps({
        "unit_id": unit_id,
        "amount": float(amount),
        "type": debt_type,
        "period": str(period)
    })
    return log_action(user_id, "DEBT_CREATED", "debt_item", unit_id, details)


def log_bulk_operation(user_id, operation_type, count, details=""):
    """Toplu işlem loglama"""
    detail_json = json.dumps({
        "operation": operation_type,
        "affected_records": count,
        "details": details
    })
    return log_action(user_id, f"BULK_{operation_type}", "bulk_operation", None, detail_json)


def log_report_download(user_id, report_type):
    """Rapor indirmesini loglama"""
    return log_action(user_id, "REPORT_DOWNLOADED", "reports", None, f"Report: {report_type}")
