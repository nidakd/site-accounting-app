import streamlit as st
import pandas as pd
from src.database.connection import get_db_engine
from src.services.debt_service import get_detayli_borc, get_daire_extresi
from src.services.payment_service import get_daire_odemeleri

@st.dialog("Daire Cari Hesap Detayı", width="large")
def daire_detay_penceresi(row, borclar):
    # --- YENİ TASARIM BAŞLANGICI ---
    
    # 1. BAŞLIK VE DURUM UYARISI
    durum_renk = "red" if borclar['toplam'] > 0 else "green"
    durum_ikon = "⚠️" if borclar['toplam'] > 0 else "✅"
    durum_mesaj = "ÖDEME BEKLİYOR" if borclar['toplam'] > 0 else "BORCU YOK"
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.markdown(f"## 🚪 Daire {row['unit_number']}")
        st.markdown(f"**Kat Maliki:** {row['owner_name']}")
    with col_r:
        if borclar['toplam'] > 0:
            st.error(f"{durum_ikon}\n{durum_mesaj}")
        else:
            st.success(f"{durum_ikon}\n{durum_mesaj}")
            
    st.divider()
    
    # 2. RENKLİ KARTLAR (METRİK YERİNE KUTU TASARIMI)
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.info(f"🏠 **AİDAT BORCU**\n# ₺{borclar['aidat']:,.2f}")
    
    with k2:
        st.warning(f"🔥 **YAKIT BORCU**\n# ₺{borclar['yakit']:,.2f}")
        
    with k3:
        if borclar['toplam'] > 0:
            st.error(f"🚨 **GENEL TOPLAM**\n# ₺{borclar['toplam']:,.2f}")
        else:
            st.success(f"🎉 **GENEL TOPLAM**\n# ₺{borclar['toplam']:,.2f}")

    # 3. GÖRSEL GRAFİK (YENİ)
    if borclar['toplam'] > 0:
        st.markdown("##### 📊 Borç Dağılımı")
        grafik_data = pd.DataFrame({
            "Borç Tipi": ["Aidat", "Yakıt"],
            "Miktar": [borclar['aidat'], borclar['yakit']]
        })
        st.bar_chart(grafik_data, x="Borç Tipi", y="Miktar", color="Borç Tipi", horizontal=True, height=200)

    # 4. TABLOLAR
    st.write("") # Boşluk
    tab1, tab2 = st.tabs(["📉 DETAYLI BORÇ LİSTESİ", "💰 GEÇMİŞ ÖDEMELER"])
    
    with tab1:
        st.write("#### 📋 Ödenmesi Gereken Kalemler")
        extre_df = get_daire_extresi(int(row['id']))
        
        if not extre_df.empty:
            st.dataframe(
                extre_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Tutar (TL)": st.column_config.NumberColumn(format="₺%.2f"),
                    "Borç Türü": st.column_config.TextColumn("Tür", help="Borcun kaynağı (Aidat/Yakıt)"),
                    "Dönem": st.column_config.TextColumn("Dönem", help="Borcun ait olduğu ay"),
                }
            )
            st.info("💡 Borçlar eskiden yeniye doğru sıralanmıştır. Ödeme yapıldığında sistem otomatik olarak en eski borcu kapatır.")
        else:
            st.success("🎉 Harika! Bu dairenin ödenmemiş hiç borcu yok.")
            st.balloons()
            
    with tab2:
        st.write("#### 🧾 Yapılan Tahsilatlar")
        odeme_df = get_daire_odemeleri(int(row['id']))
        if not odeme_df.empty:
            st.dataframe(
                odeme_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Tutar (TL)": st.column_config.NumberColumn(format="₺%.2f"),
                    "Açıklama": st.column_config.TextColumn("Açıklama"),
                }
            )
            st.info("💡 Bu liste sisteme işlenmiş resmi ödeme makbuzlarıdır.")
        else:
             st.warning("Bu daireye ait henüz bir ödeme kaydı bulunamadı.")
    
    st.divider()
    if st.button("Kapat", use_container_width=True):
        st.rerun()

def render_buildings_page():
    st.header("🏢 Blok Bazlı Borç Takip Paneli")
    
    engine = get_db_engine()

    # 1. Blokları çekelim
    bloklar_query = f"SELECT id, name FROM building WHERE complex_id = {st.session_state.selected_site_id}"
    bloklar_df = pd.read_sql(bloklar_query, engine)
    
    # 2. Üstten blok seçimi yapalım
    secilen_blok_adi = st.selectbox("İncelemek istediğiniz bloğu seçin:", bloklar_df['name'])
    secilen_blok_id = bloklar_df[bloklar_df['name'] == secilen_blok_adi]['id'].values[0]
    
    # 3. Seçilen bloğun dairelerini getirelim
    daire_query = f"SELECT id, unit_number, owner_name FROM unit WHERE building_id = {int(secilen_blok_id)} ORDER BY unit_number::int"
    daireler = pd.read_sql(daire_query, engine)
    # 4. Görsel Grid...
    st.write(f"### {secilen_blok_adi} Bloğu Daire Durumları")
    # Her satırda 4 daire olacak şekilde kolonlar
    cols = st.columns(4)
    
    for index, row in daireler.iterrows():
        borclar = get_detayli_borc(int(row['id']))
        col_index = index % 4
        
        with cols[col_index]:
            with st.container(border=True):
                st.markdown(f"### 🚪 Daire {row['unit_number']}")
                st.caption(f"👤 {row['owner_name']}")
                
                # Borç durumuna göre renkli gösterge
                if borclar["toplam"] > 0:
                    st.error(f"Güncel Borç: ₺{borclar['toplam']:,.2f}")
                else:
                    st.success("✅ Borç bulunmuyor")
                
                if st.button("🔍 Detay Gör", key=f"btn_{row['id']}", use_container_width=True):
                    daire_detay_penceresi(row, borclar)
