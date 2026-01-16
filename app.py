import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Okul Yazılım Satın Alma SWOT Analizi")

st.title("🏫 Yazılım Firmaları Değerlendirme Panosu")
st.markdown("Toplantı esnasında canlı veri girişi yapabilirsiniz.")

# --- Veritabanı Bağlantısı (Google Sheets) ---
# Bağlantı kurulana kadar hata vermemesi için try-except bloğu
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Veriyi çekiyoruz (Cache süresini 0 yapıyoruz ki anlık güncellensin)
    df = conn.read(worksheet="Sayfa1", ttl=0)
except:
    # Eğer bağlantı yoksa (henüz deploy etmediysek) boş bir dataframe ile çalış
    st.warning("Google Sheets bağlantısı bulunamadı. Yerel modda çalışılıyor (Veriler kaydedilmez).")
    df = pd.DataFrame(columns=["Sirket", "Kategori", "Yorum", "Ekleyen"])

# --- Yan Menü (Veri Girişi) ---
with st.sidebar:
    st.header("📝 Yeni Görüş Ekle")
    secilen_sirket = st.selectbox("Hangi Şirket?", ["Şirket A", "Şirket B", "Şirket C", "Şirket D"])
    kategori = st.selectbox("SWOT Kategorisi", ["Güçlü Yön (Strengths)", "Zayıf Yön (Weaknesses)", "Fırsat (Opportunities)", "Tehdit (Threats)"])
    yorum = st.text_area("Görüşünüz:", height=100)
    ekleyen = st.text_input("Adınız (İsteğe bağlı):", placeholder="Örn: Ahmet Hoca")
    
    if st.button("Kaydet ve Gönder", type="primary"):
        if yorum:
            # Yeni veriyi dataframe'e ekle
            yeni_veri = pd.DataFrame([{"Sirket": secilen_sirket, "Kategori": kategori, "Yorum": yorum, "Ekleyen": ekleyen}])
            df_yeni = pd.concat([df, yeni_veri], ignore_index=True)
            
            try:
                # Veriyi Google Sheets'e geri yaz
                conn.update(worksheet="Sayfa1", data=df_yeni)
                st.success("Görüş kaydedildi! Listeyi görmek için sayfayı yenileyebilirsiniz.")
                st.rerun() # Sayfayı yenile ki yeni veri görünsün
            except:
                st.error("Veritabanı bağlantısı olmadığı için kayıt yapılamadı.")
        else:
            st.warning("Lütfen bir yorum yazınız.")

# --- Ana Ekran (Görselleştirme) ---
# Sekmeler ile şirketleri ayıralım
tab1, tab2, tab3, tab4 = st.tabs(["Şirket A", "Şirket B", "Şirket C", "Şirket D"])

sirketler = ["Şirket A", "Şirket B", "Şirket C", "Şirket D"]
tabs = [tab1, tab2, tab3, tab4]

for i, tab in enumerate(tabs):
    with tab:
        current_company = sirketler[i]
        st.subheader(f"{current_company} Analizi")
        
        # O şirkete ait verileri süz
        company_data = df[df["Sirket"] == current_company]
        
        # 4 Sütunlu SWOT Matrisi
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            st.info(f"**💪 Güçlü Yönler**")
            items = company_data[company_data["Kategori"] == "Güçlü Yön (Strengths)"]
            for _, row in items.iterrows():
                st.write(f"- {row['Yorum']} *({row['Ekleyen']})*")
                
        with col2:
            st.error(f"**🔻 Zayıf Yönler**")
            items = company_data[company_data["Kategori"] == "Zayıf Yön (Weaknesses)"]
            for _, row in items.iterrows():
                st.write(f"- {row['Yorum']} *({row['Ekleyen']})*")
                
        with col3:
            st.success(f"**✨ Fırsatlar**")
            items = company_data[company_data["Kategori"] == "Fırsat (Opportunities)"]
            for _, row in items.iterrows():
                st.write(f"- {row['Yorum']} *({row['Ekleyen']})*")
                
        with col4:
            st.warning(f"**⚠️ Tehditler**")
            items = company_data[company_data["Kategori"] == "Tehdit (Threats)"]
            for _, row in items.iterrows():
                st.write(f"- {row['Yorum']} *({row['Ekleyen']})*")