import streamlit as st
from ai_service import get_ai_response

st.set_page_config(page_title="EduAssist AI", layout="centered")

st.title("🎓 Minimalist Eğitim Asistanı")

subjects = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Felsefe", "Tarih", "Coğrafya"]
selected_subject = st.selectbox("Ders Seç:", subjects)
hours = st.slider("Çalışma Süresi (Saat):", 1, 8, 2)

if st.button("Planla"):
    prompt = f"{selected_subject} dersi için {hours} saatlik, adım adım bir çalışma programı hazırla."
    with st.spinner("Plan oluşturuluyor..."):
        st.write(get_ai_response(prompt))

if st.button("Test Soruları"):
    prompt = f"{selected_subject} dersinden 5 adet temel seviye soru ve cevap anahtarı hazırla."
    with st.spinner("Sorular oluşturuluyor..."):
        st.write(get_ai_response(prompt))
