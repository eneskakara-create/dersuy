import streamlit as st
import db_utils
import ai_service
import search_utils
import json
import pandas as pd
from datetime import datetime

# Veritabanını ilklendir
db_utils.init_db()

# Sayfa Yapılandırması
st.set_page_config(
    page_title="EduAssist AI - AI Destekli Eğitim Asistanı",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design (Harmonious violet/blue theme, glassmorphism, smooth animations)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium Gradients and Cards */
    .welcome-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .welcome-card::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, rgba(99,102,241,0) 70%);
        border-radius: 50%;
    }
    
    .ai-analysis-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-left: 5px solid #6366f1;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .stat-card {
        background: white;
        border: 1px solid #f3f4f6;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    .badge {
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-easy { background-color: #ecfdf5; color: #059669; }
    .badge-medium { background-color: #fef3c7; color: #d97706; }
    .badge-hard { background-color: #fef2f2; color: #dc2626; }
    
    /* Day Plan Cards */
    .day-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .day-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    }
    
    .day-num {
        background: #4f46e5;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 15px;
    }
    
    /* Custom buttons and actions */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Oturum Durumu Başlatma
if "username" not in st.session_state:
    st.session_state["username"] = "Zeynep"
if "weekly_goal" not in st.session_state:
    st.session_state["weekly_goal"] = 24
if "weekly_progress" not in st.session_state:
    st.session_state["weekly_progress"] = 18.0
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Panel"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""
if "active_quiz_answers" not in st.session_state:
    st.session_state["active_quiz_answers"] = {}
if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False

# SIDEBAR (YAN MENÜ)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 EduAssist AI</h2>", unsafe_allow_html=True)
    
    # Profil Bilgisi
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 25px;">
        <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150" style="border-radius: 50%; width: 80px; height: 80px; border: 3px solid #6366f1; object-fit: cover;">
        <h4 style="margin-top: 10px; margin-bottom: 2px;">{st.session_state['username']}</h4>
        <p style="color: #6b7280; font-size: 0.85rem;">Öğrenci</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigasyon
    st.markdown("### Menü")
    if st.button("📊 Panel", use_container_width=True):
        st.session_state["current_tab"] = "Panel"
    if st.button("🔮 AI Planlama", use_container_width=True):
        st.session_state["current_tab"] = "AI Planlama"
    if st.button("📚 Dersler", use_container_width=True):
        st.session_state["current_tab"] = "Dersler"
    if st.button("👤 Profil", use_container_width=True):
        st.session_state["current_tab"] = "Profil"
        
    st.markdown("---")
    
    # API Key durumları
    st.markdown("### 🔑 API Durumu")
    groq_ok = "✅ Groq Aktif" if ai_service.GROQ_API_KEY else "⚠️ Groq Fallback Modu"
    yt_ok = "✅ YouTube Aktif" if search_utils.YT_API_KEY else "⚠️ YouTube Fallback Modu"
    st.info(f"{groq_ok}\n\n{yt_ok}")
    st.caption("Güvenli API anahtarları için `.env` dosyasını yapılandırın.")

# SEÇİLEN SAYFAYI GÖSTER
current_page = st.session_state["current_tab"]

if current_page == "Panel":
    # ------------------ PANEL (DASHBOARD) ------------------
    st.markdown("<p style='color: #6366f1; font-weight: 700; margin-bottom: 2px; text-transform: uppercase;'>ÖĞRENCİ ÖZETİ</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top: 0px;'>Hoş Geldin, {st.session_state['username']} 👋</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # AI Analizi Kartı
        st.markdown(f"""
        <div class="welcome-card">
            <h3 style="margin-top: 0px; font-weight: 700;">🔮 Yapay Zeka Analizi</h3>
            <p style="font-size: 1.1rem; line-height: 1.6;">Bu hafta Matematik ve Yapay Zeka derslerine odaklandın. Ders çalışma verimliliğin geçen haftaya kıyasla %15 arttı!</p>
            <p style="font-size: 0.95rem; opacity: 0.9; margin-bottom: 15px;">Senin için özel çalışma özetleri ve testler hazırladım. Sol menüden AI Planlama sayfasına geçerek hemen çalışmaya başlayabilirsin.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Derslerim Tablosu
        st.markdown("<h3 style='margin-top: 20px;'>📚 Derslerim</h3>", unsafe_allow_html=True)
        courses = db_utils.get_courses()
        if courses:
            # HTML formatında şık tablo oluşturma
            table_html = """
            <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="border-bottom: 2px solid #f3f4f6; text-align: left; color: #4b5563;">
                        <th style="padding: 12px;">Ders Adı</th>
                        <th style="padding: 12px;">Zorluk</th>
                        <th style="padding: 12px;">Notlar / Detaylar</th>
                    </tr>
                </thead>
                <tbody>
            """
            for c in courses:
                badge_class = "badge-easy" if c['zorluk'] == "Kolay" else ("badge-medium" if c['zorluk'] == "Orta" else "badge-hard")
                table_html += f"""
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px; font-weight: 500; color: #1f2937;">{c['ad']}</td>
                        <td style="padding: 12px;"><span class="badge {badge_class}">{c['zorluk']}</span></td>
                        <td style="padding: 12px; color: #4b5563; font-size: 0.9rem;">{c['notlar'] or ''}</td>
                    </tr>
                """
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Kayıtlı ders bulunamadı. Sağ üstten veya 'Dersler' menüsünden ders ekleyebilirsiniz.")
            
        # Sınav Haftası Hazırlığı Kartı
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 25px; border-radius: 20px; margin-top: 25px; box-shadow: 0 10px 15px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0px; color: #38bdf8; font-weight: 700;">🎯 Sınav Haftası Hazırlığı</h4>
            <p style="font-size: 0.95rem; opacity: 0.85;">Sınav haftanıza özel 5 yeni çalışma kaynağı ve seviye tespit testiniz hazırlandı.</p>
            <div style="margin-top: 10px; margin-bottom: 15px;">
                <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; margin-right: 5px; font-weight: 600;">#MAT102</span>
                <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; margin-right: 5px; font-weight: 600;">#FIZIK</span>
                <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">#AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Hazırlığa Başla", key="btn_exam_prep"):
            st.session_state["current_tab"] = "AI Planlama"
            st.rerun()

    with col2:
        # Haftalık Hedef Kartı
        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <p style="color: #6b7280; font-size: 0.9rem; font-weight: 600; margin-bottom: 5px; text-transform: uppercase;">Haftalık Hedef</p>
            <h1 style="color: #4f46e5; margin: 0; font-size: 3rem; font-weight: 800;">
                {int(st.session_state['weekly_progress'])}/{st.session_state['weekly_goal']}
            </h1>
            <p style="color: #4b5563; font-size: 0.95rem; margin-bottom: 15px;">Saat Çalışıldı</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Custom Progress Bar (Streamlit ile)
        progress_val = min(st.session_state['weekly_progress'] / st.session_state['weekly_goal'], 1.0)
        st.progress(progress_val)
        st.caption(f"📈 Geçen haftaya göre %8 daha iyi durumdasın.")
        
        st.markdown("---")
        
        # Günlük Görevler (Dinamik SQLite Bağlantılı)
        st.markdown("### ✔️ Günlük Görevler")
        tasks = db_utils.get_tasks()
        
        # Görev Ekleme
        new_task_content = st.text_input("Yeni Görev Ekle...", key="new_task_input", label_visibility="collapsed")
        if st.button("Ekle", key="add_task_btn", use_container_width=True):
            if new_task_content.strip():
                db_utils.add_task(new_task_content.strip())
                st.toast("Görev başarıyla eklendi!")
                st.rerun()
                
        # Görev Listesi Checkboxları
        if tasks:
            for t in tasks:
                col_t1, col_t2 = st.columns([5, 1])
                with col_t1:
                    is_checked = st.checkbox(t['icerik'], value=t['tamamlandi'], key=f"task_{t['id']}")
                    if is_checked != t['tamamlandi']:
                        db_utils.toggle_task(t['id'], is_checked)
                        # Haftalık hedefi biraz arttır
                        if is_checked:
                            st.session_state["weekly_progress"] += 0.5
                        else:
                            st.session_state["weekly_progress"] = max(0.0, st.session_state["weekly_progress"] - 0.5)
                        st.rerun()
                with col_t2:
                    if st.button("🗑️", key=f"del_task_{t['id']}"):
                        db_utils.delete_task(t['id'])
                        st.toast("Görev silindi.")
                        st.rerun()
        else:
            st.write("Harika! Bugünlük tüm görevler bitti.")

elif current_page == "AI Planlama":
    # ------------------ AI PLANLAMA & ÇALIŞMA ODASI ------------------
    st.markdown("<p style='color: #6366f1; font-weight: 700; margin-bottom: 2px; text-transform: uppercase;'>YAPAY ZEKA DESTEKLİ HAZIRLIK</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top: 0px;'>Çalışma Odası & AI Planlama</h1>", unsafe_allow_html=True)
    
    # Arama Girişi
    topic = st.text_input("Hangi konuyu öğrenmek istersin?", placeholder="Örn: Newton'un Hareket Yasaları, Veri Yapıları, İntegral...", value=st.session_state["search_query"])
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        generate_btn = st.button("Program Oluştur 🚀", use_container_width=True)
        
    if generate_btn and topic.strip():
        st.session_state["search_query"] = topic.strip()
        st.session_state["quiz_submitted"] = False
        st.session_state["active_quiz_answers"] = {}
        
        with st.spinner("AI sizin için çalışma programı, test soruları ve kaynakları derliyor..."):
            # Planı ve Quizi AI'dan çek
            data = ai_service.generate_study_and_quiz(topic.strip())
            
            # YouTube videolarını ara
            videos = search_utils.search_youtube_videos(topic.strip())
            
            # PDF belgelerini ara
            pdfs = search_utils.search_pdf_documents(topic.strip())
            
            # Veritabanına kaydet (JSON formatında)
            plan_json = json.dumps(data.get("plan", []))
            quiz_json = json.dumps(data.get("quiz", []))
            db_utils.save_plan(topic.strip(), plan_json, quiz_json)
            
            # Kaynakları da session state'te tutalım
            st.session_state[f"videos_{topic.strip()}"] = videos
            st.session_state[f"pdfs_{topic.strip()}"] = pdfs
            st.success("Çalışma programı başarıyla hazırlandı!")
            
    # Kayıtlı Planları Listele/Yükle
    saved_plans = db_utils.get_all_plans()
    if saved_plans:
        saved_topics = [p["konu"] for p in saved_plans]
        selected_past_topic = st.selectbox("Geçmiş Planlarımı Yükle", ["-- Seçin --"] + saved_topics)
        if selected_past_topic != "-- Seçin --" and selected_past_topic != st.session_state["search_query"]:
            st.session_state["search_query"] = selected_past_topic
            st.session_state["quiz_submitted"] = False
            st.session_state["active_quiz_answers"] = {}
            st.rerun()

    # Plan Gösterimi
    active_topic = st.session_state["search_query"]
    if active_topic:
        plan_data = db_utils.get_plan_by_topic(active_topic)
        if plan_data:
            plan_list = json.loads(plan_data[0])
            quiz_list = json.loads(plan_data[1])
            
            # Kayıtlı kaynakları geri getir
            videos = st.session_state.get(f"videos_{active_topic}", search_utils.search_youtube_videos(active_topic))
            pdfs = st.session_state.get(f"pdfs_{active_topic}", search_utils.search_pdf_documents(active_topic))
            
            st.markdown(f"## 📅 {active_topic} Çalışma Programı")
            
            # Günlük Kartlar
            for day in plan_list:
                st.markdown(f"""
                <div class="day-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div class="day-num">{day['gun']}</div>
                        <div>
                            <h4 style="margin: 0; font-weight: 700; color: #1e1b4b;">{day['baslik']}</h4>
                            <span style="color: #6b7280; font-size: 0.85rem;">⏳ Süre: {day['sure']} | 📈 Hedef Seviye: {day['seviye']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Checkbox görevleri
                for g_idx, task in enumerate(day['gorevler']):
                    st.checkbox(task, key=f"plan_task_{day['gun']}_{g_idx}")
            
            # SEVİYE TESPİT TESTİ
            st.markdown("## 📝 Seviye Tespit Testi (AI Üretimi)")
            
            if quiz_list:
                score = 0
                for idx, q in enumerate(quiz_list):
                    st.write(f"**Soru {idx+1}:** {q['soru']}")
                    
                    options_list = list(q['secenekler'].items())
                    options_formatted = [f"{k}) {v}" for k, v in options_list]
                    
                    # Seçilen cevap
                    ans_key = f"q_{active_topic}_{idx}"
                    # Default selection as None (Streamlit index index parameter)
                    selected_opt = st.radio(
                        "Şıkkı Seçiniz:",
                        options_formatted,
                        key=ans_key,
                        index=None if not st.session_state["quiz_submitted"] else options_formatted.index([f"{k}) {v}" for k, v in options_list if k == st.session_state["active_quiz_answers"].get(ans_key)][0]) if st.session_state["active_quiz_answers"].get(ans_key) else None,
                        disabled=st.session_state["quiz_submitted"]
                    )
                    
                    if selected_opt:
                        choice = selected_opt.split(")")[0].strip()
                        st.session_state["active_quiz_answers"][ans_key] = choice
                        
                    st.markdown("---")
                
                if not st.session_state["quiz_submitted"]:
                    if st.button("Testi Bitir 🏁", key="submit_quiz"):
                        st.session_state["quiz_submitted"] = True
                        st.rerun()
                else:
                    # Skoru hesapla ve göster
                    correct_count = 0
                    for idx, q in enumerate(quiz_list):
                        ans_key = f"q_{active_topic}_{idx}"
                        user_ans = st.session_state["active_quiz_answers"].get(ans_key)
                        correct_ans = q['cevap']
                        
                        if user_ans == correct_ans:
                            correct_count += 1
                            st.success(f"Soru {idx+1}: Doğru! (Cevabınız: {user_ans})")
                        else:
                            st.error(f"Soru {idx+1}: Yanlış. Doğru Cevap: {correct_ans} (Sizin Cevabınız: {user_ans or 'Boş bırakıldı'})")
                            
                    st.metric("Test Skoru", f"{correct_count} / {len(quiz_list)}")
                    if st.button("Testi Yeniden Çöz 🔄"):
                        st.session_state["quiz_submitted"] = False
                        st.session_state["active_quiz_answers"] = {}
                        st.rerun()
            
            # ÖNERİLEN KAYNAKLAR
            st.markdown("## 🔗 Önerilen Eğitim Kaynakları")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("### 🎥 Eğitim Videoları (YouTube)")
                if videos:
                    for v in videos:
                        st.markdown(f"**[{v['title']}]({v['url']})**")
                        st.caption(f"Kanal: {v['channel']}")
                        # Videoyu göm
                        try:
                            st.video(v['url'])
                        except:
                            st.caption("Video gömülemedi, linke tıklayarak izleyebilirsiniz.")
                else:
                    st.write("Eğitim videosu bulunamadı.")
                    
            with col_res2:
                st.markdown("### 📄 Ücretsiz PDF Dökümanlar")
                if pdfs:
                    for p in pdfs:
                        st.markdown(f"""
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                            <h5 style="margin: 0; font-weight: bold; color: #1e293b;">📄 {p['title']}</h5>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 5px; margin-bottom: 10px;">{p['snippet']}</p>
                            <a href="{p['url']}" target="_blank" style="background: #6366f1; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600;">Dökümanı Aç</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("Ücretsiz PDF ders notu bulunamadı.")
            
            # AI AKRAN ÖĞRENCİ (CHAT ODASI)
            st.markdown("---")
            st.markdown("### 💬 AI Akran Öğrenci (Tartışma Odası)")
            st.caption("Anlamadığınız yerleri AI arkadaşınıza sorun ve hızlıca öğrenin.")
            
            if f"chat_history_{active_topic}" not in st.session_state:
                st.session_state[f"chat_history_{active_topic}"] = []
                
            for chat in st.session_state[f"chat_history_{active_topic}"]:
                if chat["role"] == "user":
                    st.markdown(f"**Siz:** {chat['content']}")
                else:
                    st.markdown(f"🤖 **AI Arkadaş:** {chat['content']}")
                    
            user_msg = st.text_input("Mesajınızı yazın...", key=f"chat_input_{active_topic}")
            if st.button("Gönder", key=f"send_chat_btn_{active_topic}"):
                if user_msg.strip():
                    st.session_state[f"chat_history_{active_topic}"].append({"role": "user", "content": user_msg})
                    # Groq API ile yanıt üret
                    client = ai_service.get_groq_client()
                    if client:
                        try:
                            prompt_chat = f"Sen '{active_topic}' konusunu çalışan bir öğrenci akranısın. Arkadaşın sana şu soruyu sordu: '{user_msg}'. Bir öğrenci ağzıyla, samimi ama öğretici bir şekilde Türkçe cevap ver."
                            completion = client.chat.completions.create(
                                model="llama3-70b-8192",
                                messages=[{"role": "user", "value": prompt_chat}],
                                temperature=0.5
                            )
                            ai_ans = completion.choices[0].message.content.strip()
                        except:
                            ai_ans = "Harika soru! Ama şu an API bağlantım kesildi. Konuya odaklanmaya devam edelim."
                    else:
                        ai_ans = f"Harika soru! '{active_topic}' konusunda bunu mutlaka araştırmalıyız."
                        
                    st.session_state[f"chat_history_{active_topic}"].append({"role": "assistant", "content": ai_ans})
                    st.rerun()

elif current_page == "Dersler":
    # ------------------ DERS YÖNETİMİ ------------------
    st.markdown("<p style='color: #6366f1; font-weight: 700; margin-bottom: 2px; text-transform: uppercase;'>📚 MÜFREDAT</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top: 0px;'>Derslerim & Notlarım</h1>", unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([1, 2])
    
    with col_d1:
        st.markdown("### ➕ Yeni Ders Ekle")
        d_ad = st.text_input("Ders Adı", placeholder="Örn: Fizik I")
        d_zorluk = st.selectbox("Zorluk Seviyesi", ["Kolay", "Orta", "Zor"])
        d_notlar = st.text_area("Kısa Notlar / Konular", placeholder="Örn: Mekanik, Kinematik, Vektörler...")
        
        if st.button("Dersi Kaydet", use_container_width=True):
            if d_ad.strip():
                db_utils.add_course(d_ad.strip(), d_zorluk, d_notlar.strip())
                st.success("Ders başarıyla kaydedildi!")
                st.rerun()
            else:
                st.error("Ders adı boş bırakılamaz.")
                
    with col_d2:
        st.markdown("### 📂 Ders Listesi")
        courses = db_utils.get_courses()
        
        if courses:
            for c in courses:
                badge_color = "#10b981" if c['zorluk'] == "Kolay" else ("#f59e0b" if c['zorluk'] == "Orta" else "#ef4444")
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #1e293b;">{c['ad']}</h4>
                            <span style="color: {badge_color}; font-weight: bold; font-size: 0.85rem;">{c['zorluk']} Seviye</span>
                            <p style="color: #64748b; font-size: 0.9rem; margin-top: 5px; margin-bottom: 0;">{c['notlar'] or 'Not yok.'}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Dersi Sil", key=f"del_course_{c['id']}"):
                        db_utils.delete_course(c['id'])
                        st.toast("Ders silindi.")
                        st.rerun()
        else:
            st.info("Kayıtlı ders bulunamadı.")

elif current_page == "Profil":
    # ------------------ PROFİL & İSTATİSTİKLER ------------------
    st.markdown("<p style='color: #6366f1; font-weight: 700; margin-bottom: 2px; text-transform: uppercase;'>KULLANICI AYARLARI</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top: 0px;'>Öğrenci Profili</h1>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Profil Bilgilerini Düzenle")
    new_username = st.text_input("Öğrenci Adı", value=st.session_state["username"])
    new_goal = st.number_input("Haftalık Hedef Çalışma Süresi (Saat)", value=int(st.session_state["weekly_goal"]), min_value=1)
    
    if st.button("Profili Güncelle"):
        st.session_state["username"] = new_username
        st.session_state["weekly_goal"] = new_goal
        st.success("Profil başarıyla güncellendi!")
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 📊 Genel İstatistikler")
    
    courses = db_utils.get_courses()
    tasks = db_utils.get_tasks()
    plans = db_utils.get_all_plans()
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Kayıtlı Ders Sayısı", len(courses))
    col_stat2.metric("Günlük Görev Sayısı", len(tasks))
    col_stat3.metric("Üretilen Çalışma Planı", len(plans))
