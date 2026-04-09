import streamlit as st
import pandas as pd
import joblib
import re

st.set_page_config(page_title="Phishing Tespit Sistemi", page_icon="🛡️", layout="wide")
st.title("🛡️ NLP Destekli Zararlı Link Tespiti")
st.markdown("Doğal Dil İşleme (TF-IDF) kullanılarak eğitilmiş makine öğrenimi modeli.")

def url_temizle(url):
    url = str(url).lower().strip().strip('"').strip("'")
    url = re.sub(r'^https?:\/\/', '', url)
    url = re.sub(r'^www\.', '', url)
    return url

@st.cache_resource
def sistemi_yukle():
    model = joblib.load('phishing_model_nlp.pkl')
    vektorizor = joblib.load('tfidf_vectorizer.pkl')
    return model, vektorizor

try:
    model, vectorizer = sistemi_yukle()
except FileNotFoundError:
    st.error("Model dosyaları bulunamadı! Lütfen önce model.py dosyasını çalıştırın.")
    st.stop()

tab1, tab2 = st.tabs(["🔍 Tekli Link Analizi", "📁 Toplu Dosya Analizi (TXT/CSV)"])

with tab1:
    kullanici_url = st.text_input("URL Giriniz:", placeholder="Örn: https://www.google.com")
    if st.button("Analiz Et", key="tekli_btn"):
        if kullanici_url:
            temiz_url = url_temizle(kullanici_url)
            url_vektoru = vectorizer.transform([temiz_url])
            tahmin = model.predict(url_vektoru)[0]
            
            if tahmin == 1:
                st.error("🚨 DİKKAT! Bu bağlantı ZARARLI (Phishing) olabilir!")
            else:
                st.success("✅ Güvenli görünüyor!")
        else:
            st.warning("Lütfen bir bağlantı girin.")

with tab2:
    st.markdown("İçerisinde alt alta URL'ler bulunan bir `.txt` veya `.csv` dosyası yükleyin.")
    yuklenen_dosya = st.file_uploader("Dosya Seçin", type=['txt', 'csv'])
    
    if yuklenen_dosya is not None:
        if st.button("Toplu Analizi Başlat", key="toplu_btn"):
            with st.spinner('Doğal Dil İşleme algoritmaları çalışıyor...'):
                try:
                    if yuklenen_dosya.name.endswith('.txt'):
                        satirlar = yuklenen_dosya.getvalue().decode("utf-8").splitlines()
                        df = pd.DataFrame(satirlar, columns=['URL'])
                    else:
                        df = pd.read_csv(yuklenen_dosya, header=None)
                        df = df.iloc[:, [0]]
                        df.columns = ['URL']

                    df = df.dropna().reset_index(drop=True)
                    df['Temiz_URL'] = df['URL'].apply(url_temizle)
                    
                    X_yeni = vectorizer.transform(df['Temiz_URL'].astype(str))
                    tahminler = model.predict(X_yeni)
                    
                    df['Durum'] = ['🚨 Zararlı' if t == 1 else '✅ Güvenli' for t in tahminler]
                    gosterilecek_df = df[['URL', 'Durum']]
                    
                    st.success(f"Toplam {len(df)} bağlantı başarıyla analiz edildi!")
                    st.dataframe(gosterilecek_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Dosya işlenirken hata oluştu: {e}")