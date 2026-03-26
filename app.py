import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Okul Yazılım Satın Alma SWOT Analizi")

st.title("🏫 Yazılım Firmaları Değerlendirme Panosu")
st.markdown("Toplantı esnasında canlı veri girişi yapabilirsiniz.")

# --- Veritabanı Bağlantısı (Google Sheets) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Sayfa1", ttl=0)
except:
    st.warning("Google Sheets bağlantısı bulunamadı. Yerel modda çalışılıyor (Veriler kaydedilmez).")
    df = pd.DataFrame(columns=["Sirket", "Kategori", "Yorum", "Ekleyen"])

# Şirket listesini dinamik olarak belirle (Eğer veri varsa oradan al, yoksa boş)
if not df.empty and "Sirket" in df.columns and len(df["Sirket"].dropna().unique()) > 0:
    sirketler = list(df["Sirket"].dropna().unique())
else:
    sirketler = []

# --- Yan Menü (Veri Girişi) ---
with st.sidebar:
    st.header("📝 Yeni Görüş Ekle")
    
    # Yeni şirket eklemeye izin veren seçim kutusu
    firma_secimi_secenekler = sirketler + ["➕ Yeni Şirket Ekle"] if sirketler else ["➕ Yeni Şirket Ekle"]
    firma_secimi = st.selectbox("Hangi Şirket?", firma_secimi_secenekler)
    
    if firma_secimi == "➕ Yeni Şirket Ekle":
        secilen_sirket = st.text_input("Yeni Şirket Adı:", placeholder="Örn: X Yazılım")
    else:
        secilen_sirket = firma_secimi
        
    kategori = st.selectbox("SWOT Kategorisi", ["Güçlü Yön (Strengths)", "Zayıf Yön (Weaknesses)", "Fırsat (Opportunities)", "Tehdit (Threats)"])
    yorum = st.text_area("Görüşünüz:", height=100)
    ekleyen = st.text_input("Adınız (İsteğe bağlı):", placeholder="Örn: Ahmet Hoca")
    
    if st.button("Kaydet ve Gönder", type="primary"):
        if yorum and secilen_sirket:
            yeni_veri = pd.DataFrame([{"Sirket": secilen_sirket, "Kategori": kategori, "Yorum": yorum, "Ekleyen": ekleyen}])
            df_yeni = pd.concat([df, yeni_veri], ignore_index=True)
            try:
                conn.update(worksheet="Sayfa1", data=df_yeni)
                st.success("Görüş kaydedildi! Listeyi görmek için sayfayı yenileyebilirsiniz.")
                st.rerun()
            except:
                st.error("Veritabanı bağlantısı olmadığı için kayıt yapılamadı.")
        else:
            st.warning("Lütfen şirket adını ve yorumu eksiksiz yazınız.")

    st.divider()
    with st.expander("⚙️ Şirket Adını Düzenle / Değiştir"):
        if not sirketler:
            st.info("Değiştirilecek kayıtlı bir şirket yok.")
        else:
            eski_isim = st.selectbox("Mevcut Şirket:", sirketler, key="eski")
            yeni_isim = st.text_input("Yeni İsim:", key="yeni")
            if st.button("İsmi Güncelle"):
                if yeni_isim and yeni_isim != eski_isim and not df.empty:
                    df.loc[df["Sirket"] == eski_isim, "Sirket"] = yeni_isim
                    try:
                        conn.update(worksheet="Sayfa1", data=df)
                        st.success(f"{eski_isim}, {yeni_isim} olarak güncellendi!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Güncelleme başarısız: {e}")
                else:
                    st.warning("Geçerli ve farklı bir yeni isim yazın.")

# --- Ana Ekran (Görselleştirme) ---
if not sirketler:
    st.info("Henüz tabloya kayıtlı bir veriniz yok. Lütfen sol menüden 'Yeni Şirket Ekle' adımını kullanarak ilk görüşünüzü ekleyin.")
else:
    tabs = st.tabs(sirketler)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_company = sirketler[i]
            st.subheader(f"{current_company} Analizi")
            
            company_data = df[df["Sirket"] == current_company]
            
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
            
            # --- AI Analizi Bölümü ---
            st.divider()
            st.markdown("### 🤖 Trinity AI Şirket Değerlendirmesi")
            st.markdown("💡 *Ekibe ait tüm yorumları inceleterek ortak bir analiz çıkarılmasını sağlayabilirsiniz.*")
            
            if st.button(f"✨ {current_company} İçin Ortak Analiz Çıkar", key=f"ai_btn_{i}"):
                if company_data.empty:
                    st.warning("Analiz edilecek yorum bulunamadı.")
                else:
                    with st.spinner("Trinity AI yorumları derliyor, lütfen bekleyin..."):
                        try:
                            from openai import OpenAI
                            # OpenRouter API Key (Kendi ayarlarından alır, yoksa yazılan anahtarı kullanır)
                            api_key = st.secrets.get("OPENROUTER_API_KEY", "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")
                            client = OpenAI(
                                base_url="https://openrouter.ai/api/v1",
                                api_key=api_key,
                            )
                            
                            yorumlar_metni = ""
                            for _, row in company_data.iterrows():
                                yorumlar_metni += f"- [{row['Kategori']}] {row['Yorum']} ({row['Ekleyen']})\n"
                                
                            prompt = f"Şu ana kadar ekibimiz '{current_company}' isimli şirket hakkında aşağıdaki yorumları yaptı:\n\n{yorumlar_metni}\n\nLütfen bu yorumları okuyarak sadece 1-2 paragraflık ortak, özetleyici ve net bir değerlendirme yaz. Yorumların ortak kanısını aktar. Tamamen Türkçe yaz ve madde imi kullanmadan doğrudan düz yazı (paragraf) olarak ver."
                            
                            response = client.chat.completions.create(
                                model="arcee-ai/trinity-large-preview:free",
                                messages=[
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            
                            st.success("Analiz başarıyla tamamlandı!")
                            st.write(response.choices[0].message.content)
                            
                        except Exception as e:
                            st.error(f"Yapay zeka ile iletişim sağlanamadı: {e}")