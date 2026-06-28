import sqlite3
import os

DB_NAME = "ders_takip.db"

def get_connection():
    """Veritabanı bağlantısı oluşturur."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Veritabanı tablolarını oluşturur ve varsayılan verileri ekler (eğer boşsa)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Dersler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dersler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        zorluk TEXT NOT NULL,
        notlar TEXT
    )
    """)
    
    # Günlük Görevler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gorevler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        icerik TEXT NOT NULL,
        tamamlandi INTEGER DEFAULT 0
    )
    """)
    
    # AI Çalışma Planları tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        konu TEXT NOT NULL,
        plan_json TEXT NOT NULL,
        quiz_json TEXT NOT NULL,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    
    # Başlangıç verilerini ekle (eğer tablolar boşsa)
    cursor.execute("SELECT COUNT(*) FROM dersler")
    if cursor.fetchone()[0] == 0:
        default_courses = [
            ("İleri Matematik II", "Zor", "İntegral ve Diferansiyel Denklemler"),
            ("Yapay Zeka Temelleri", "Orta", "Nöral Ağlar ve Geri Yayılım"),
            ("Termodinamik", "Kolay", "Enerji Korunumu ve Entropi")
        ]
        cursor.executemany("INSERT INTO dersler (ad, zorluk, notlar) VALUES (?, ?, ?)", default_courses)
        
    cursor.execute("SELECT COUNT(*) FROM gorevler")
    if cursor.fetchone()[0] == 0:
        default_tasks = [
            ("Matematik Problem Seti #4", 0),
            ("Fizik Raporunu Gözden Geçir", 0),
            ("AI Makale Özetini Oku", 0)
        ]
        cursor.executemany("INSERT INTO gorevler (icerik, tamamlandi) VALUES (?, ?)", default_tasks)
        
    conn.commit()
    conn.close()

# DERS İŞLEMLERİ
def add_course(ad, zorluk, notlar):
    """Yeni ders ekler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dersler (ad, zorluk, notlar) VALUES (?, ?, ?)", (ad, zorluk, notlar))
    conn.commit()
    conn.close()

def get_courses():
    """Tüm dersleri liste halinde döner."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad, zorluk, notlar FROM dersler")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "ad": r[1], "zorluk": r[2], "notlar": r[3]} for r in rows]

def delete_course(course_id):
    """Belirtilen dersi siler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dersler WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()

# GÖREV İŞLEMLERİ
def add_task(icerik):
    """Yeni bir günlük görev ekler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gorevler (icerik, tamamlandi) VALUES (?, 0)", (icerik,))
    conn.commit()
    conn.close()

def get_tasks():
    """Tüm günlük görevleri listeler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, icerik, tamamlandi FROM gorevler")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "icerik": r[1], "tamamlandi": bool(r[2])} for r in rows]

def toggle_task(task_id, tamamlandi):
    """Görevin tamamlanma durumunu değiştirir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE gorevler SET tamamlandi = ? WHERE id = ?", (1 if tamamlandi else 0, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Görevi siler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gorevler WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# PLAN İŞLEMLERİ
def save_plan(konu, plan_json, quiz_json):
    """AI tarafından üretilen plan ve quizi veritabanına kaydeder."""
    conn = get_connection()
    cursor = conn.cursor()
    # Aynı konudan varsa eskisini silebiliriz veya güncelleyebiliriz
    cursor.execute("DELETE FROM planlar WHERE konu = ?", (konu,))
    cursor.execute("INSERT INTO planlar (konu, plan_json, quiz_json) VALUES (?, ?, ?)", (konu, plan_json, quiz_json))
    conn.commit()
    conn.close()

def get_plan_by_topic(konu):
    """Belirtilen konuya ait planı döner."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plan_json, quiz_json FROM planlar WHERE konu = ? ORDER BY tarih DESC LIMIT 1", (konu,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None

def get_all_plans():
    """Tüm kayıtlı çalışma planlarını listeler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, konu, tarih FROM planlar ORDER BY tarih DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "konu": r[1], "tarih": r[2]} for r in rows]
