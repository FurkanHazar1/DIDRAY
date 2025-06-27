import sqlite3
from datetime import datetime
import bcrypt
import csv
import os

class DBManager:
    def __init__(self, db_path='detections.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_detection_table()
        self.create_user_table()
        self.create_log_table()
        self.create_user_log_table()
        self.check_and_update_detection_table()

    # Tespit kayıtları tablosu (operator ve role eklendi)
    def create_detection_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                classes TEXT,
                bboxes TEXT,
                confidences TEXT,
                image_path TEXT,
                mode TEXT,
                operator TEXT,
                role TEXT
            )
        ''')
        self.conn.commit()

    # Kullanıcı tablosu
    def create_user_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        self.conn.commit()

    # Kullanıcı giriş-çıkış log tablosu
    def create_user_log_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                role TEXT,
                login_time TEXT,
                logout_time TEXT
            )
        ''')
        self.conn.commit()

    # Sistem log tablosu
    def create_log_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                action TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    # Eğer eski detections tablosu varsa kolonları güncelle
    def check_and_update_detection_table(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(detections)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'operator' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN operator TEXT")
            self.conn.commit()
        if 'role' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN role TEXT")
            self.conn.commit()

    # Kullanıcı giriş logu
    def log_user_login(self, username, role):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO user_logs (username, role, login_time) VALUES (?, ?, ?)', (username, role, now))
        self.conn.commit()

    # Kullanıcı çıkış logu
    def log_user_logout(self, username):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE user_logs SET logout_time = ?
            WHERE username = ? AND logout_time IS NULL
            ORDER BY id DESC LIMIT 1
        ''', (now, username))
        self.conn.commit()

    # Tespit kaydı ekleme (operator ve role dahil)
    def insert_detection(self, classes, image_path, mode, bboxes=None, confidences=None, operator=None, role=None):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        class_str = ', '.join(classes)
        bbox_str = ';'.join([str(b) for b in bboxes]) if bboxes else ''
        conf_str = ';'.join([f"{c:.2f}" for c in confidences]) if confidences else ''

        cursor.execute('''
            INSERT INTO detections (timestamp, classes, bboxes, confidences, image_path, mode, operator, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (now, class_str, bbox_str, conf_str, image_path, mode, operator, role))
        self.conn.commit()

    # Tüm tespit kayıtlarını çekme
    def fetch_all_detections(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, classes, confidences, mode, image_path, operator, role FROM detections ORDER BY id DESC")
        return cursor.fetchall()

    # Tespit kaydı silme
    def delete_detection(self, timestamp):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM detections WHERE timestamp = ?", (timestamp,))
        self.conn.commit()

    # Kullanıcı ekleme (hashlenmiş şifre)
    def add_user(self, username, password, role):
        hashed_password = self.hash_password(password)
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    # Şifre hashleme
    def hash_password(self, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    # Şifre doğrulama
    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    # Kullanıcı doğrulama
    def validate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            hashed_password, role = result
            if self.check_password(password, hashed_password):
                return role
        return None

    # Tüm kullanıcıları çek
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, role FROM users ORDER BY id")
        return cursor.fetchall()

    # Kullanıcı silme
    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    # Yönetim logları (action log)
    def add_log(self, user, action):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO logs (user, action, timestamp) VALUES (?, ?, ?)', (user, action, timestamp))
        self.conn.commit()

    def get_all_logs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user, action, timestamp FROM logs ORDER BY id DESC")
        return cursor.fetchall()

    # Kullanıcı giriş/çıkış loglarını çek
    def get_all_user_logs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username, role, login_time, logout_time FROM user_logs ORDER BY id DESC")
        return cursor.fetchall()

    # İstatistik raporu
    def get_detection_statistics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT classes FROM detections")
        data = cursor.fetchall()

        class_count = {}
        for row in data:
            classes = row[0].split(', ')
            for cls in classes:
                class_count[cls] = class_count.get(cls, 0) + 1

        return class_count

    # Export CSV
    def export_detections_to_csv(self, filename):
        data = self.fetch_all_detections()
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "classes", "confidences", "mode", "image_path", "operator", "role"])
            for row in data:
                writer.writerow(row)

    # Yetki sorgulama
    def get_user_role(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()
