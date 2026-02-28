import sqlite3

DB_NAME = "ai_siem.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source_ip TEXT,
        event_type TEXT,
        user TEXT,
        attempts INTEGER,
        data_size_mb INTEGER,
        port INTEGER,
        anomaly_score REAL,
        threat_level TEXT,
        ai_explanation TEXT,
        response_action TEXT,
        response_status TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_log(log):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs 
        (timestamp, source_ip, event_type, user, attempts, data_size_mb, port,
         anomaly_score, threat_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log["timestamp"],
        log["source_ip"],
        log["event_type"],
        log["user"],
        log["attempts"],
        log["data_size_mb"],
        log["port"],
        log.get("anomaly_score"),
        log.get("threat_level")
    ))

    conn.commit()
    conn.close()

def get_all_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()
    conn.close()
    return rows