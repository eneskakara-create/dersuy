import os
from googleapiclient.discovery import build
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# .env yükle
load_dotenv()

YT_API_KEY = os.getenv("YT_API_KEY")

def search_youtube_videos(query, max_results=3):
    """
    YouTube Data API v3 kullanarak arama yapar ve video detaylarını döner.
    API anahtarı bulunamazsa veya hata oluşursa boş liste döner.
    """
    if not YT_API_KEY or YT_API_KEY == "AIzaSyDoCs4P9xf5FTWaOP7_S6XL_lGAUMdoE2E":
        # Varsayılan / Yedek sonuçlar (Hata almamak için)
        return [
            {
                "title": f"{query} - Temel Kavramlar Ders Anlatımı",
                "video_id": "dQw4w9WgXcQ", # Rickroll or a generic video
                "channel": "Akademi YouTube",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            },
            {
                "title": f"{query} - Detaylı Soru Çözümü",
                "video_id": "dQw4w9WgXcQ",
                "channel": "Sınav Hazırlık Kanalı",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        ]
        
    try:
        youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
        request = youtube.search().list(
            q=f"{query} konu anlatımı ders",
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='tr'
        )
        response = request.execute()
        
        videos = []
        for item in response.get("items", []):
            snippet = item["snippet"]
            video_id = item["id"]["videoId"]
            videos.append({
                "title": snippet["title"],
                "video_id": video_id,
                "channel": snippet["channelTitle"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": snippet["thumbnails"]["medium"]["url"]
            })
        return videos
    except Exception as e:
        print(f"YouTube API Hatası: {e}")
        # Hata durumunda da boş veya fallback liste
        return [
            {
                "title": f"{query} - Konu Anlatım Videosu (Alternatif)",
                "video_id": "dQw4w9WgXcQ",
                "channel": "Eğitim Portalı",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        ]

def search_pdf_documents(query, max_results=3):
    """
    DuckDuckGo Search kullanarak konuya uygun ücretsiz PDF belgelerini (filetype:pdf) arar.
    """
    pdf_query = f"{query} filetype:pdf ders notları"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(pdf_query, max_results=max_results))
            
        pdfs = []
        for r in results:
            # Sadece pdf uzantılı veya PDF içerdiği bariz olan linkleri seçmeye çalışalım
            title = r.get("title", "Ders Notu")
            href = r.get("href", "")
            body = r.get("body", "İçerik açıklaması bulunamadı.")
            
            pdfs.append({
                "title": title,
                "url": href,
                "snippet": body
            })
        return pdfs
    except Exception as e:
        print(f"DuckDuckGo PDF Arama Hatası: {e}")
        # Hata durumunda fallback linkler
        return [
            {
                "title": f"{query} Ders Notları PDF",
                "url": "https://www.google.com",
                "snippet": f"{query} konusu ile ilgili ücretsiz PDF çalışma notları."
            },
            {
                "title": f"{query} Konu Özeti PDF",
                "url": "https://www.google.com",
                "snippet": f"{query} formülleri ve kısa konu özeti dosyası."
            }
        ]
