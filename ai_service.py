import os
import json
from groq import Groq
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_client():
    """Groq istemcisini başlatır ve döndürür."""
    if not GROQ_API_KEY or GROQ_API_KEY == "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":
        return None
    return Groq(api_key=GROQ_API_KEY)

def generate_study_and_quiz(topic):
    """
    Groq API (llama3-70b-8192) kullanarak verilen konu için 
    3 günlük çalışma programı ve 5 test sorusu üretir.
    Eğer API başarısız olursa yedek (fallback) bir şablon döner.
    """
    client = get_groq_client()
    
    prompt = f"""
    Lütfen "{topic}" konusu için 3 günlük bir çalışma programı ve 5 soruluk çoktan seçmeli bir seviye tespit testi oluştur.
    Aşağıdaki JSON yapısına tam olarak uy:
    {{
      "plan": [
        {{
          "gun": 1,
          "baslik": "Giriş ve Temel Kavramlar",
          "sure": "1.5 Saat",
          "seviye": "15%",
          "gorevler": [
            "Konu anlatım videolarını izle (45 dk)",
            "Zihin haritası çıkar (20 dk)",
            "Temel seviye 20 soru çöz (25 dk)"
          ]
        }},
        {{
          "gun": 2,
          "baslik": "Derinleşme ve Pratik",
          "sure": "2 Saat",
          "seviye": "50%",
          "gorevler": [
            "Detaylı konu analizi ve formüllerin çıkartılması (60 dk)",
            "Özet notları oku ve formülleri ezberle (30 dk)",
            "Orta seviye 30 soru çöz (30 dk)"
          ]
        }},
        {{
          "gun": 3,
          "baslik": "Ustalaşma ve Değerlendirme",
          "sure": "2 Saat",
          "seviye": "85%",
          "gorevler": [
            "Çıkmış sınav sorularının çözümü ve analizi (50 dk)",
            "Konu tekrarı ve eksiklerin kapatılması (30 dk)",
            "Simülasyon testi çözümü - 50 Soru (40 dk)"
          ]
        }}
      ],
      "quiz": [
        {{
          "soru_no": 1,
          "soru": "Soru metni buraya gelecek?",
          "secenekler": {{
            "A": "Seçenek A",
            "B": "Seçenek B",
            "C": "Seçenek C",
            "D": "Seçenek D"
          }},
          "cevap": "Doğru şık harfi (A, B, C veya D)"
        }}
      ]
    }}

    Kurallar:
    1. Yanıt YALNIZCA geçerli bir JSON olmalıdır. Öncesinde veya sonrasında markdown blokları (```json gibi), açıklama, selamlaşma veya metin ekleme.
    2. Dil tamamen Türkçe olmalıdır.
    3. Quiz dizisinde tam olarak 5 adet soru bulunmalıdır.
    4. Plan dizisinde tam olarak 3 gün bulunmalıdır.
    """
    
    if client:
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "value": "Sen Türkçe eğitim planları ve test soruları hazırlayan, sadece JSON formatında yanıt veren bir eğitim uzmanı yapay zekasın."},
                    {"role": "user", "value": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result_text = completion.choices[0].message.content.strip()
            data = json.loads(result_text)
            return data
            
        except Exception as e:
            print(f"Groq API hatası oluştu, fallback çalıştırılıyor: {e}")
            
    # Fallback / Yedek mekanizması
    return get_fallback_data(topic)

def get_fallback_data(topic):
    """API anahtarı eksik veya hatalı olduğunda çalışan yerel şablon üreteci."""
    return {
        "plan": [
            {
                "gun": 1,
                "baslik": f"1. Gün: {topic} Temel Kavramlar",
                "sure": "1.5 Saat",
                "seviye": "15%",
                "gorevler": [
                    f"{topic} hakkında konu anlatım videolarını izle (45 dk)",
                    "Konu ile ilgili zihin haritası çıkar (20 dk)",
                    "Temel seviye 20 soru çöz (25 dk)"
                ]
            },
            {
                "gun": 2,
                "baslik": f"2. Gün: {topic} Derinleşme",
                "sure": "2 Saat",
                "seviye": "50%",
                "gorevler": [
                    "Karmaşık problemler ve vaka analizlerini incele (60 dk)",
                    "Konu özet notlarını oku ve çıkarımlarda bulun (30 dk)",
                    "Orta seviye 30 soru çöz (30 dk)"
                ]
            },
            {
                "gun": 3,
                "baslik": f"3. Gün: {topic} Ustalaşma",
                "sure": "2 Saat",
                "seviye": "85%",
                "gorevler": [
                    "Son 5 yılın çıkmış sınav sorularını analiz et (50 dk)",
                    "Hızlı konu tekrarı ve eksik kısımları tamamlama (30 dk)",
                    "Simülasyon testi çöz - 50 Soru (40 dk)"
                ]
            }
        ],
        "quiz": [
            {
                "soru_no": 1,
                "soru": f"Aşağıdakilerden hangisi {topic} konusunun temel uygulama alanlarından biridir?",
                "secenekler": {
                    "A": "Veri analitiği ve optimizasyon",
                    "B": "Tarihsel kronoloji incelemesi",
                    "C": "Edebi metin eleştirisi",
                    "D": "Basit mekanik kaldıraç tasarımı"
                },
                "cevap": "A"
            },
            {
                "soru_no": 2,
                "soru": f"{topic} konusunu çalışırken izlenmesi gereken en etkili ilk adım hangisidir?",
                "secenekler": {
                    "A": "Doğrudan ileri düzey sınav sorularını çözmek",
                    "B": "Temel tanım, kavram ve teorik altyapıyı öğrenmek",
                    "C": "Konuyu çalışmadan ezber yapmak",
                    "D": "Sadece formülleri yazıp bırakmak"
                },
                "cevap": "B"
            },
            {
                "soru_no": 3,
                "soru": f"{topic} sürecinde karşılaşılan zorlukları aşmak için hangisi tavsiye edilir?",
                "secenekler": {
                    "A": "Dersi tamamen bırakmak",
                    "B": "Görsel zihin haritaları ve aktif soru çözümü kullanmak",
                    "C": "Yalnızca tek bir kaynaktan okuma yapmak",
                    "D": "Her şeyi ezberlemeye çalışmak"
                },
                "cevap": "B"
            },
            {
                "soru_no": 4,
                "soru": f"{topic} kapsamında 'Derinleşme' aşaması neyi amaçlar?",
                "secenekler": {
                    "A": "Kavramları yüzeysel geçmeyi",
                    "B": "Vaka analizleri ve karmaşık problemleri çözerek pratik kazanmayı",
                    "C": "Sınavı ertelemeyi",
                    "D": "Sadece video izlemeyi"
                },
                "cevap": "B"
            },
            {
                "soru_no": 5,
                "soru": f"{topic} ile ilgili bir simülasyon testinde başarılı olmak için ne yapılmalıdır?",
                "secenekler": {
                    "A": "Zaman yönetimi ve tüm soru tiplerinin analizine dikkat edilmelidir",
                    "B": "Sorular hızlıca tahmin edilmelidir",
                    "C": "Sadece ilk soru çözülüp bırakılmalıdır",
                    "D": "Formülsüz ilerlenmelidir"
                },
                "cevap": "A"
            }
        ]
    }
