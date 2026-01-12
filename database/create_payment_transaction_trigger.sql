/* 
   FILE NAME / DOSYA ADI : create_payment_transaction_trigger.sql
   PROJECT / PROJE      : Sellable Site Management Accounting Interface
                          Satılabilir Site Yönetimi Muhasebe Arayüzü

   PURPOSE / AMAÇ:
   EN: Automatically creates an INCOME transaction record whenever a new payment is inserted.
       This ensures that the accounting ledger (account_transaction) stays consistent with
       payment records (payment).

   TR: payment tablosuna yeni bir ödeme kaydı eklendiğinde, otomatik olarak
       account_transaction tablosuna bir GELİR (INCOME) hareketi ekler.
       Böylece ödeme kayıtları ile muhasebe kayıtları senkron kalır.

   WHEN IT RUNS? / NE ZAMAN ÇALIŞIR?
   EN: After a row is inserted into the payment table (AFTER INSERT).
   TR: payment tablosuna yeni satır eklendikten sonra (AFTER INSERT).

   NOTES / NOTLAR:
   - EN: Implemented as a PostgreSQL trigger + PL/pgSQL function.
   - TR: PostgreSQL trigger + PL/pgSQL fonksiyonu kullanılarak uygulanmıştır.
*/

-----------------------------------------------------------
-- 1) TRIGGER FUNCTION / TETİKLEYİCİ FONKSİYON
-----------------------------------------------------------
/*
   EN:
   This function is executed by the trigger after a payment insert.
   It inserts a corresponding row into account_transaction as an INCOME.

   TR:
   Bu fonksiyon, payment tablosuna ödeme eklendikten sonra tetikleyici tarafından çalıştırılır.
   account_transaction tablosuna INCOME türünde bir kayıt ekler.

   INPUT / GİRDİ:
   - NEW: The newly inserted payment row (payment tablosuna eklenen yeni satır)

   OUTPUT / ÇIKTI:
   - Returns NEW so that the original insert operation proceeds normally.
   - NEW döndürülür; ödeme ekleme işlemi normal şekilde devam eder.
*/
CREATE OR REPLACE FUNCTION fn_create_payment_transaction()
RETURNS TRIGGER AS $$
BEGIN
    /*
      EN:
      Insert an accounting transaction that mirrors the payment record.

      TR:
      Ödeme kaydını yansıtan bir muhasebe hareketi oluşturulur.
    */
    INSERT INTO account_transaction (
        complex_id,      -- EN: Which site/complex this belongs to / TR: Hangi siteye ait
        type,            -- EN: Transaction type (INCOME/EXPENSE) / TR: İşlem türü
        category,        -- EN: Sub-category for reporting / TR: Raporlama kategorisi
        unit_id,         -- EN: Related apartment/unit / TR: İlgili daire
        amount,          -- EN: Monetary amount / TR: Tutar
        process_date,    -- EN: Effective date of the transaction / TR: İşlem tarihi
        description      -- EN: Human-readable description / TR: Açıklama metni
    )
    VALUES (
        NEW.complex_id,                 -- EN/TR: from payment row
        'INCOME',                       -- EN: Always income for received payments
                                       -- TR: Daireden alınan ödeme = gelir
        'PAYMENT_RECEIVED',             -- EN: Category for traceability/reporting
                                       -- TR: İzlenebilirlik/raporlama kategorisi
        NEW.unit_id,                    -- EN/TR: paying unit
        NEW.amount,                     -- EN/TR: paid amount
        NEW.process_date,               -- EN/TR: payment process date

        /*
          EN:
          Build a description string. If NEW.description is NULL,
          COALESCE converts it to empty string to avoid NULL concatenation issues.

          TR:
          Açıklama metni oluşturulur. NEW.description NULL ise,
          COALESCE bunu boş string'e çevirerek birleştirme hatasını önler.
        */
        'Daireden gelen ödeme: ' || COALESCE(NEW.description, '')
    );

    /*
      EN:
      Return NEW to confirm trigger execution and keep the original INSERT intact.

      TR:
      NEW döndürülür; tetikleyici başarılı çalışır ve ödeme INSERT işlemi bozulmaz.
    */
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------
-- 2) TRIGGER DEFINITION / TETİKLEYİCİ TANIMI
-----------------------------------------------------------
/*
   EN:
   This trigger fires AFTER INSERT on payment table, for each inserted row,
   and executes fn_create_payment_transaction().

   TR:
   Bu tetikleyici payment tablosunda AFTER INSERT olayında,
   eklenen her satır için çalışır ve fn_create_payment_transaction() fonksiyonunu çağırır.
*/
CREATE TRIGGER trg_after_payment_insert
AFTER INSERT ON payment
FOR EACH ROW
EXECUTE FUNCTION fn_create_payment_transaction();
