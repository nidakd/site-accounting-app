from datetime import datetime
import streamlit as st

def generate_receipt_html(site_name, unit_label, amount, description, date_str):
    """
    Generates HTML content for a payment receipt.
    """
    makbuz_html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <title>Tahsilat Makbuzu</title>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; background-color: #fff;">
        <div style="border: 2px solid #333; padding: 30px; max-width: 700px; margin: auto; background-color: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2c3e50; margin: 0; padding-bottom: 10px; border-bottom: 2px solid #eee;">TAHSİLAT MAKBUZU</h1>
                <p style="color: #7f8c8d; margin-top: 5px;">Otomatik Oluşturulan Resmi Ödeme Belgesi</p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 15px; font-weight: bold; color: #555; width: 150px;">Tarih</td>
                    <td style="padding: 15px; color: #333;">{date_str}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee; background-color: #f9f9f9;">
                    <td style="padding: 15px; font-weight: bold; color: #555;">Site / Yapı</td>
                    <td style="padding: 15px; color: #333;">{site_name}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 15px; font-weight: bold; color: #555;">Daire Bilgisi</td>
                    <td style="padding: 15px; color: #333;">{unit_label}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee; background-color: #f9f9f9;">
                    <td style="padding: 15px; font-weight: bold; color: #555;">Açıklama</td>
                    <td style="padding: 15px; color: #333;">{description}</td>
                </tr>
                <tr style="background-color: #e8f6f3; border-top: 2px solid #1abc9c;">
                    <td style="padding: 20px; font-weight: bold; color: #16a085; font-size: 1.1em;">TAHSİL EDİLEN</td>
                    <td style="padding: 20px; font-weight: bold; color: #16a085; font-size: 1.5em;">₺{amount:,.2f}</td>
                </tr>
            </table>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px dashed #ccc; text-align: center; font-size: 13px; color: #95a5a6;">
                <p>Bu belge elektronik ortamda düzenlenmiştir. Islak imza gerektirmez.</p>
                <p style="font-style: italic;">{site_name} Yönetimi</p>
            </div>
        </div>
        <script>window.print();</script>
    </body>
    </html>
    """
    return makbuz_html

def generate_receipt_text(site_name, unit_label, amount, description, date_str):
    makbuz_metni = f"""
    =========================================
            TAHSİLAT MAKBUZU
    =========================================
    Tarih       : {date_str}
    Site        : {site_name}
    Daire       : {unit_label}
    
    TUTAR       : ₺{amount:,.2f}
    AÇIKLAMA    : {description}
    =========================================
    Bu makbuz elektronik ortamda üretilmiştir.
    """
    return makbuz_metni
