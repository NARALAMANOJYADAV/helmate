import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, '../database/challans.db'))

def init_db():
    try:
        # Ensure directory exists
        db_folder = os.path.dirname(DB_PATH)
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_no TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Init Error: {e}")

def add_challan(vehicle_no, image_path):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO challans (vehicle_no, image_path) VALUES (?, ?)', (vehicle_no, image_path))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Add Challan Error: {e}")

def get_all_challans():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM challans ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        challans = [dict(row) for row in rows]
        conn.close()
        return challans
    except Exception as e:
        print(f"Get Challans Error: {e}")
        return []

def delete_challan(challan_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM challans WHERE id = ?', (challan_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Delete Challan Error: {e}")
        return False

if __name__ == '__main__':
    init_db()
