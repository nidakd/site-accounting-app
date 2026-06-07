# 🏢 Site Yönetim Sistemi - Detaylı İyileştirme Analizi

**Analiz Tarihi:** Haziran 2026  
**Analiz Perspektifi:** Site Yöneticisi + Muhasebeci  

---

## 📊 1. MUHASEBE MODULÜ İYİLEŞTİRMELERİ

### 🔴 KRİTİK ÖNCELİK

#### 1.1 **Defter Tutma Sistemi (Double-Entry Bookkeeping)**
- **Mevcut Durum:** Tek taraflı borç/ödeme kayıtları
- **Sorun:** Muhasebe standardları (TFRS/MSUGT) uyumluluğu eksik
- **Çözüm Önerisi:**
  - Hesaplar Planı (Chart of Accounts) oluşturma
  - Giriş/Çıkış hareketleri için debit/credit sistemi
  - Her işlem için otomatik iki taraflı kayıt
  - Muhasebe dönem yönetimi

**Etki:** Vergi raporu hazırlama, bağımsız denetim, yasal uyum

#### 1.2 **Banka Mutabakatı (Bank Reconciliation)**
- **Mevcut Durum:** Kasa bakiyesi = Tahsilat Toplamı (çok temel)
- **Sorun:** Banka ekstresindeki işlemlerle eşleşme yok
- **Çözüm Önerisi:**
  - Banka ekstresini sisteme yükleme (CSV/API)
  - Otomatik eşleştirme algoritması
  - Fark analiziyle eksiklikleri gösterme
  - Ayların sonunda mutabakat raporları

**Etki:** Sahtekarlık tespiti, nakit akış kontrolü

#### 1.3 **Finansal Raporlar (Financial Statements)**
- **Mevcut Durum:** Sadece borç listesi ve aylık tahsilat
- **Sorun:** Site yönetiminde kritik olan raporlar eksik
- **Çözüm Önerisi:**
  ```
  Oluşturulması Gereken Raporlar:
  ├── Bilanço (Balance Sheet)
  ├── Gelir Tablosu (Income Statement)  
  ├── Nakit Akış Tablosu (Cash Flow)
  ├── Öz Kaynaklar Değişim Tablosu
  └── Mali Tablo Notları
  ```
- **Şirket Kanunu Madde 28 uyumluluğu**

**Etki:** Genel kurul sunumları, finansal sağlık analizi

#### 1.4 **Hesap Detayları & İşlem Geçmişi**
- **Mevcut Durum:** Payment tablosu sadece temel bilgi tutuyor
- **Sorun:** Muhasebe denetiminde sorulacak sorular cevapsız
- **Çözüm Önerisi:**
  ```sql
  Özellikleri Eklenecek:
  - her_konut_daire_hesabi (Resident Account)
  - İşlem Tipi (Type: DEBIT/CREDIT)
  - Referans/Muhasebe Dokümanı
  - Kayıt Yapan Kullanıcı & Tarih
  - Düzeltme/İptal İşlemleri
  - Orijinal Doküman Ekler
  ```

**Etki:** Müşteri sorguları, münferit hesap detay raporları

---

## 👥 2. KULLANICI YÖNETİMİ & GÜVENLİK

### 🔴 KRİTİK ÖNCELİK

#### 2.1 **Rol Tabanlı Erişim Kontrolü (RBAC)**
- **Mevcut Durum:** Tek şifreli giriş, tüm fonksiyonlara erişim
- **Sorun:** 
  - Muhasebeci ile site müdürü aynı yetkiye sahip
  - Sensitif işlemlerde kontrol yok
  - Yasal sorumluluk tanımı belirsiz
- **Çözüm Önerisi:**
  ```
  Roller:
  ├── Admin (Site Müdürü)
  │   └── Tüm fonksiyonlar, kullanıcı yönetimi
  ├── Muhasebeci
  │   ├── Ödeme/Borç kayıtları
  │   ├── Raporlar
  │   └── ❌ Bütçe Değişikliği, Tarife Değişimi
  ├── Tahsilat Görevlisi
  │   ├── Ödeme girişi
  │   ├── Makbuz çıktısı
  │   └── ❌ Rapor görüntüleme
  ├── Danışman/Müştahak
  │   ├── 📊 Salt Okunur Raporlar
  │   └── ❌ Değişiklik Yetkileri
  └── Konut Sahibi (Yeni)
      ├── Kendi Borç Durumu
      ├── Ödeme Geçmişi
      └── ❌ Diğer Daireleri Görme
  ```

**Etki:** İç Kontrol sisteminin oluşturulması, yasal sorumluluk tanımı

#### 2.2 **Audit Log (İşlem Kaydı)**
- **Mevcut Durum:** Hiçbir işlem, kimin tarafından yapıldığı kaydedilmiyor
- **Sorun:** Hatalı/hile işlemleri takip edilemiyor
- **Çözüm Önerisi:**
  ```
  Kaydedilecek Bilgiler:
  - Kim yaptı (User ID)
  - Ne yaptı (Action)
  - Ne zaman yaptı (Timestamp)
  - Eski/Yeni değerler
  - IP Adresi (uzaktan erişim için)
  
  Örnek:
  2026-06-07 14:32 | nidakd | UPDATE | Daire 101 | 
    Borç: 5000→4500 | 192.168.1.100
  ```

**Etki:** Yasal denetim, hata takibi, sorumluluk belirleme

#### 2.3 **Daire Sahiplerinin Portal Erişimi**
- **Mevcut Durum:** Sadece yönetim ekibi erişebiliyor
- **Sorun:** Daire sahipleri kendi borç durumunu göremiyorlar
- **Çözüm Önerisi:**
  - Basit konut sahibi portalı (Streamlit ya da web)
  - Kişisel borç durum görünümü
  - Ödeme geçmişi
  - Makbuz indirme
  - Push/Email bildirimler

**Etki:** Müşteri memnuniyeti, sorgu azalması

---

## 💰 3. MALİ YÖNETİM & PLANLAMA

### 🟠 YÜKSEK ÖNCELİK

#### 3.1 **Bütçe ve Varsayım Analizi (Budget & Forecast)**
- **Mevcut Durum:** Fiili sayılar gösteriliyor, bütçe yok
- **Sorun:**
  - Planlama yapılamıyor
  - Tahsilat oranı hedefleri belirsiz
  - Yıllık bütçe hazırlanmıyor
- **Çözüm Önerisi:**
  ```
  Eklenmesi Geren Modüller:
  1. Aidat Bütçesi (Dönemler bazında)
  2. Yakıt Bütçesi (Mevsimsel tahmini)
  3. Gider Bütçesi (Onarım, elektrik vb.)
  4. Tahsilat Hedefleri (%)
  
  Varyans Analizi:
  Bütçe vs Fiili farkları gösterme
  ```

**Etki:** Stratejik planlama, kaynakların etkili kullanımı

#### 3.2 **Geçmiş Dönem Analizi**
- **Mevcut Durum:** Mevcut dönem verisi
- **Sorun:** Eğilimler görülemiyor
- **Çözüm Önerisi:**
  - Çok yıllı karşılaştırma
  - Tahsilat oranı trendleri
  - Mevsimsel analizler

**Etki:** Stratejik kararlar, tahminleme

#### 3.3 **Maliyet Merkez Takibi (Cost Centers)**
- **Mevcut Durum:** Blok bazlı bölümleme kısmi
- **Sorun:** Giderler merkeze tahsis ediliyor
- **Çözüm Önerisi:**
  ```
  Maliyet Merkezleri:
  ├── Bloklar (Blok A, Blok B)
  ├── Ortak Alanlar (Bahçe, Asansör)
  └── Yönetim (Ofis, İdari)
  
  Gider Tahsisi:
  - Doğrudan (Blok elektriği)
  - Dolaylı (Ortaklaştırılmış)
  ```

**Etki:** Blok bazlı maliyet analizi, adil tahsil

---

## 📋 4. OPERASYONEL & KAYıT YÖNETİMİ

### 🟠 YÜKSEK ÖNCELİK

#### 4.1 **Konut Sahibi Yönetimi (Resident Management)**
- **Mevcut Durum:** `owner_name` var ama başka bilgi yok
- **Sorun:**
  - Sahiplik değişiklikleri takip edilmiyor
  - Kiralanmış dairelerde kimin borçlu olacağı tanımsız
  - Ortak sahiplik durumlari
- **Çözüm Önerisi:**
  ```sql
  YENI TABLO: unit_owner_log
  - unit_id
  - owner_name
  - start_date
  - end_date
  - ownership_type (Owner/Tenant)
  - responsible_for_dues (Kim ödemekle yükümlü)
  
  MANTIK:
  - Aktif sahip/kiracı dinamik bakış
  - Tarih bazlı borç tayını
  ```

**Etki:** Doğru tahsilat, mülkiyet karışıklıklarının çözülmesi

#### 4.2 **Gider Kategorilendirmesi & Bütçe**
- **Mevcut Durum:** `expense_service.py` kısmi doldurulmuş
- **Sorun:** Gider türleri standardize değil
- **Çözüm Önerisi:**
  ```
  Kategoriler:
  ├── Sabit Giderler
  │   ├── Aydınlatma
  │   ├── Su/Kanalizasyon
  │   ├── Yönetim Ücreti
  │   └── Sigorta
  ├── Değişken Giderler
  │   ├── Bakım & Onarım
  │   ├── Peyzaj
  │   └── Güvenlik
  └── Acil Giderler
  
  Her Kategori:
  - Aylık/Yıllık Bütçe
  - Fiili Harcama
  - Planlanmış Dönem
  ```

**Etki:** Başabaş analizi, gider tahmini, budgetleme

#### 4.3 **Bakım & Onarım Takibi**
- **Mevcut Durum:** Gider kaydında sadece açıklama var
- **Sorun:** Bakım ve onarım işlerinin durumu takip edilmiyor
- **Çözüm Önerisi:**
  ```
  YENİ TABLO: maintenance_ticket
  - ticket_id (Talep ID)
  - location (Nerede yapılacak)
  - description
  - priority (Acil/Normal/Planlı)
  - status (Talep/Onay/Yapılıyor/Tamamlandı)
  - assigned_to (Kime atandı)
  - start_date, completion_date
  - cost (Maliyet)
  - photos (Fotoğraf)
  ```

**Etika:** İşletme verimliliği, hizmet kalitesi kontrolü

#### 4.4 **Personel Takibi & Dosyalandırma**
- **Mevcut Durum:** `personnel_service.py` kısmi
- **Sorun:** Personel bilgileri ve performans takibi eksik
- **Çözüm Önerisi:**
  ```
  Eklenmesi Gereken:
  - İş Tanımı (Job Description)
  - Maaş/Ücret Yapısı
  - Sosyal Güvenlik (SGK Bilgileri)
  - Performans Değerlendirmesi
  - İzin & Devamsızlık Takibi
  - Bonuslar & Dönemsel Ödemeler
  ```

**Etki:** İnsan Kaynakları Yönetimi, bordro otomasyonu

---

## 📞 5. KOMÜNİKASYON & HALKLA İLİŞKİLER

### 🟡 ORTA ÖNCELİK

#### 5.1 **Otomatik Bildirim Sistemi (Notification)**
- **Mevcut Durum:** Hiçbir bildirim
- **Sorun:** Daire sahipleri ödeme tarihini unutuyor
- **Çözüm Önerisi:**
  ```
  Bildirim Türleri:
  1. Borç Bildirim (Aidat Yüklendiğinde)
  2. Ödeme Hatırlatıcı (Vade Tarihi Başında)
  3. Gecikme Uyarısı (Vade Geçtikten Sonra)
  4. Tahsilat Onayı (Ödeme Yapıldığında)
  
  Kanallar:
  - SMS (İlk tercih)
  - Email
  - Push Notification (App varsa)
  
  Veri:
  - Daire Numarası
  - Borç Tutarı
  - Ödeme Tarihi/Vade
  ```

**Etki:** Tahsilat Oranı Artışı (tahmin: %10-15), müşteri memnuniyeti

#### 5.2 **Raporlar & Tablolar Şablonu**
- **Mevcut Durum:** Temel liste indirilse de standart rapor yok
- **Sorun:** Genel Kurul ve denetim raporları hazırlanmıyor
- **Çözüm Önerisi:**
  ```
  Şablonlar:
  1. Yıllık Yönetici Raporu (AGM sunumu)
  2. Mali Tablo Paketleri (Bilanço vb.)
  3. Borçlu Listesi (Yasal ihtar için)
  4. Dönemsel Muhasebe Tablosu
  5. İstatistik Tabloları
  ```

**Etki:** Yasal uyum, üye tatmini

---

## 🔧 6. TEKNİK & VERİTABANI İYİLEŞTİRMELERİ

### 🟡 ORTA ÖNCELİK

#### 6.1 **Veri Bütünlüğü & Kısıtlamalar**
- **Mevcut Durum:** Temel kısıtlamalar var
- **Sorun:** 
  - Yinelenen borç girişleri olabilir
  - Tutarsız veriler
  - Ödeme ile borç ilişkisi net değil
- **Çözüm Önerisi:**
  ```sql
  Eklenmesi Gereken:
  - UNIQUE INDEX: (unit_id, period_month, type)
    → Aynı daire/dönem/tür için çoklu borç engelle
  
  - CHECK CONSTRAINT: amount > 0
    → Negatif tutar engelle
  
  - FOREIGN KEY: payment_debt tablosu
    → Her ödemeyi borçlarla bağla
  
  - DEFAULT TIMESTAMP: created_at
    → İşlem tarihi otomatik
  ```

**Etki:** Veri kalitesi, hata azalması

#### 6.2 **Yedekleme & Olağanüstü Durum Planı**
- **Mevcut Durum:** Muhtemelen manual yedek yok
- **Sorun:** Veri kaybı durumunda kayıp
- **Çözüm Önerisi:**
  ```
  Yedekleme Stratejisi:
  - Günlük otomatik yedekleme
  - Haftalık uzun dönem yedekleme
  - Coğrafi dağıtım (Cloud: AWS/Azure)
  - Test geri yükleme prosedürü
  - DRP (Disaster Recovery Plan) dokümantasyonu
  ```

**Etki:** İş sürekliliği, veri güvenliği

#### 6.3 **Performans Optimizasyonu**
- **Mevcut Durum:** Singleserver PostgreSQL muhtemelen
- **Sorun:** Büyük sitelerde yavaşlama
- **Çözüm Önerisi:**
  ```
  Optimizasyonlar:
  - Sık kullanılan sorguların indekslenmesi
  - Sayfalama (Pagination) uygulaması
  - Query caching (Redis)
  - Arşivleme stratejisi (Eski dönem verisi)
  ```

**Etki:** Kullanıcı deneyimi, sistem tepkisi

---

## 📱 7. KULLANıCı ARAYÜZÜ & UX

### 🟡 ORTA ÖNCELİK

#### 7.1 **Dashboard Genişletilmesi**
- **Mevcut Durum:** Temel metrik ve grafikler var
- **Sorun:** Yöneticinin ihtiyaç duyduğu analitik eksik
- **Çözüm Önerisi:**
  ```
  Yeni Widget'lar:
  - KPI'lar (Tahsilat Oranı, Ort. Borç Süresi)
  - Tahsilat Oranı Trendi
  - En Yüksek Borçlular
  - Bu Ay Tahsilat vs Bütçe
  - Alerta Paneli (Vadegeçmiş)
  - Blok Karşılaştırması
  ```

**Etki:** Daha iyi karar verme, hızlı özet

#### 7.2 **Mobil Uyumluluk (Responsive)**
- **Mevcut Durum:** Streamlit responsive değil
- **Sorun:** Mobilde kullanamıyor
- **Çözüm Önerisi:**
  - Streamlit Mobile kütüphanesi araştırması
  - Alternatif: Flutter/React Native mini app
  - En azından tablet kullanımı iyileştirilme

**Etki:** Erişilebilirlik, tahsilat görevlisinin mobil çalışması

---

## 🎯 8. YASAL & UYUM (Compliance)

### 🔴 KRİTİK ÖNCELİK

#### 8.1 **Vergi Raporlaması**
- **Mevcut Durum:** Muhasebe verisi var ancak vergi raporu yok
- **Sorun:** KDV, Kurumlar Vergisi, Gelir Vergisi dosyaları hazırlanmıyor
- **Çözüm Önerisi:**
  ```
  Raporlar:
  1. KDV Beyannamesi (Varsa KDV mükellefi ise)
  2. Kurumlar Vergisi Beyannamesi (501/8 Kooperatif ise)
  3. Muhasebe Müzü & Mali Tabloları
  4. Bağlı Veritabanı Uygunluk Raporu
  ```

**Etki:** Vergi Denetmeni raporu, yasal sorumluluk

#### 8.2 **GDPR & Veri Koruma (Türkiye KVKK)**
- **Mevcut Durum:** Kişisel veri var ancak koruma yok
- **Sorun:** 
  - Daire sahibinin adı, telefonu, kişisel verileri saklanıyor
  - İçeriği aktarma/silme yetki yok
- **Çözüm Önerisi:**
  ```
  Uyumlaştırma:
  - Veri İşleme Politikası (Privacy Policy)
  - Veri Tasarruf (Veri Silme) İşlemleri
  - Rıza Yönetimi
  - Veri İhlali Log'ları
  - Veri İşleyen Sözleşmeleri (DPA)
  ```

**Etki:** Yasal koruma, cezai sorumluluk azalması

#### 8.3 **Muhasebe Standartları Uyumu**
- **Mevcut Durum:** Muhasebe Sistemi "muhasebe" değil
- **Sorun:** Dönemsel muhasebe raporları, yasal uyum yok
- **Çözüm Önerisi:**
  ```
  Uyumlaştırılacak Standartlar:
  - MSUGT (Muhasebe Sistemi Uygulama Genel Tebliği)
  - TMS/TFRS (Türkiye Muhasebe Standartları)
  - Anonim Şirket Kanunu Madde 28 (Anonim ise)
  - Kooperatif Kanunu (Kooperatif ise)
  ```

**Etki:** Denetim sırasında uyum, sertifikasyon

---

## 🚀 9. ENTEGRASYON & GENIŞLETME

### 🟡 ORTA ÖNCELİK

#### 9.1 **Banka Entegrasyon (Open Banking/API)**
- **Mevcut Durum:** Manual CSV yükleme
- **Sorun:** Hataların fazlalığı
- **Çözüm Önerisi:**
  - TR Banka API'leri (Papara, PayFlex vb.)
  - Otomatik havaç taşıma
  - Mutabakat otomasyonu

**Etki:** İşlem hızı, insan hataları azalması

#### 9.2 **E-Fatura Entegrasyonu (E-Invoicing)**
- **Mevcut Durum:** HTML makbuz
- **Sorun:** Mahkemede geçerliliği sınırlı
- **Çözüm Önerisi:**
  - UBL-TR formatında E-Fatura
  - GIB Portala otomatik gönderim (varsa)

**Etki:** Yasal belge, vergi denetiminde geçerliliği

#### 9.3 **CRM Entegrasyonu**
- **Mevcut Durum:** Daire sahiplerine portalı yok
- **Sorun:** İletişim takibi yapılamıyor
- **Çözüm Önerisi:**
  - HubSpot/Salesforce lite
  - Tüm iletişim geçmişi
  - Şikayetler & İstek Takibi

**Etki:** Müşteri ilişkiler, memnuniyet takibi

---

## 📈 10. METRIKER & KPİ TAKİBİ

### 🟡 ORTA ÖNCELİK

#### 10.1 **KPİ Tanımlanması**
- **Mevcut Durum:** Temel metrikler gösteriliyor
- **Sorun:** Amaç ve hedefler tanımlanmamış
- **Çözüm Önerisi:**
  ```
  Tavsiye KPİ'lar:
  
  Tahsilat Verimliliği:
  - Tahsilat Oranı (%) = (Tahsil Edilen / Borç) * 100
  - Ort. Tahsilat Günü = Toplam Gün / İşlem Sayısı
  - Gecikmiş Borç Yüzdesi
  
  Mali Sağlık:
  - Likidite Oranı = Kasa / Kısa Vadeli Borç
  - Alacak Devri = Toplam Borç / Ort. Günlük Tahsilat
  
  Operasyonel:
  - Personel Verimliliği
  - İş Yükü / Hata Oranı
  - Borç Iptal Oranı
  ```

**Etki:** Stratejik izleme, hedef yönetimi

---

## 🎬 İMPLEMENTASYON YOĞUN (Roadmap)

### FÂZ 1 (1-2 Ay) - ACIL & KRİTİK
```
1. [ ] Rol Tabanlı Erişim (RBAC) - Site Yöneticisi/Muhasebeci/Tahsilat
2. [ ] Audit Log Sistemi
3. [ ] Defter Tutma (Double-Entry) Temelinin Atılması
4. [ ] Mali Tablo Raporları (Bilanço, Gelir Tablosu)
```

### FÂZ 2 (2-3 Ay) - YÜKSEK ÖNCELİK
```
1. [ ] Banka Mutabakatı Modülü
2. [ ] Konut Sahibi Portalı (Kendi Borç Görüntüleme)
3. [ ] Gider Kategorilendirmesi & Bütçe
4. [ ] Otomatik Bildirim Sistemi (SMS/Email)
5. [ ] Resident Yönetimi (Mülkiyet Değişiklikleri)
```

### FÂZ 3 (3-4 Ay) - ORTA ÖNCELİK
```
1. [ ] Bakım & Onarım Takibi
2. [ ] Dashboard KPİ'ları
3. [ ] Vergi Raporları (KDV/Kurumlar)
4. [ ] E-Fatura Entegrasyonu
5. [ ] Mobil Uyumluluk
```

### FÂZ 4+ (4+ Ay) - GENIŞLETME
```
1. [ ] Banka API Entegrasyonu
2. [ ] Otonom Yedekleme & DRP
3. [ ] CRM Entegrasyonu
4. [ ] Yapay Zeka / Tahsilat Tahminlemesi
```

---

## 💡 HIZLI KAZANÇ (Quick Wins)

### Bu hafta yapılabilecek (Düşük Çaba, Yüksek Etki):
1. ✅ Audit Log basit versiyonu (Kim, Ne, Ne Zaman)
2. ✅ Dashboard'a KPİ kartları ekleme (Tahsilat Oranı, Ortalama Borç)
3. ✅ Excel rapor şablonları hazırlama (Genel Kurul)
4. ✅ Temel Bildirim sistemi (Aidat Yüklendiğinde Email)

### Bu ay yapılabilecek (Orta Çaba, Yüksek Etki):
1. ✅ 3 Temel Mali Tablo Raporu (Bilanço, G.Tablosu, N.Akışı)
2. ✅ Rol Tabanlı Erişim Kontrol (4-5 Rol)
3. ✅ Basit Konut Sahibi Portalı (Readonly)

---

## 🎯 SONUÇ

**Site Müdürü Açısından:**
- Daha kontrollü, şeffaf, denetlenebilir bir sistem
- Veri tabanli kararlar alabilme yeteneği
- Yasal sorumlulukları minimize etme

**Muhasebeci Açısından:**
- Standart muhasebe uygulamaları
- Denetim hazırlığının kolaylaşması
- Vergi raporu otomasyonu
- Belge takibi ve kontrolü

**Proje Sahibi Açısından:**
- Sistemin ticari değeri artar
- Diğer siteler için ölçeklenebilir olur
- Yazılım olarak satış potansiyeli

---

**Hazırlandı:** Site Muhasebe Sistemi Analiz Raporu  
**Versiyon:** 1.0
