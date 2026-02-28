from database import get_connection

def execute_auto_response():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT source_ip, event_type
        FROM logs
        WHERE threat_level = 'Critical'
        AND response_status IS NULL
    """)

    rows = cursor.fetchall()

    for source_ip, event_type in rows:

        action = "IP BLOCKED"

        if event_type == "file_download":
            action = "USER SESSION FROZEN"

        cursor.execute("""
            UPDATE logs
            SET response_action = ?, response_status = ?
            WHERE source_ip = ?
            AND threat_level = 'Critical'
        """, (action, "EXECUTED", source_ip))

    conn.commit()
    conn.close()