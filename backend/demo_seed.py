from database import get_connection
import random
from datetime import datetime, timedelta

def seed_demo_data():
    conn = get_connection()
    cursor = conn.cursor()

    base_time = datetime.now() - timedelta(hours=2)

    for i in range(200):
        timestamp = base_time + timedelta(minutes=i)
        attempts = random.choice([1,1,1,5,10,50,120])
        event_type = random.choice(["login_success", "login_failed", "file_download"])
        ip = f"192.168.1.{random.randint(10,200)}"

        threat_level = "Low"
        if attempts >= 100:
            threat_level = "Critical"
        elif attempts >= 50:
            threat_level = "High"
        elif attempts >= 10:
            threat_level = "Medium"

        cursor.execute("""
            INSERT INTO logs 
            (timestamp, source_ip, event_type, user, attempts, data_size_mb, port,
             anomaly_score, threat_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            ip,
            event_type,
            "demo_user",
            attempts,
            random.randint(0,50000),
            443,
            random.uniform(-0.5,0.5),
            threat_level
        ))

    conn.commit()
    conn.close()