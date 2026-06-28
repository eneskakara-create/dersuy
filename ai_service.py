import os
from groq import Groq

# API anahtarını ortam değişkeninden çekiyoruz
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Sen sadece akademik bir asistansın. Web araması yapma, link verme. Sadece 50 kelimeyi geçmeyecek şekilde, net ve odaklı yanıtlar ver."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Bir hata oluştu: {e}"
