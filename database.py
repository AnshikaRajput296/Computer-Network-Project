import sqlite3

conn = sqlite3.connect("traffic.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hour INTEGER,
    day INTEGER,
    month INTEGER,
    temp REAL,
    weather INTEGER,
    predicted_volume REAL,
    congestion TEXT,
    response_time REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()