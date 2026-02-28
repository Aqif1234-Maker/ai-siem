import requests
from database import get_connection

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_explanation(log):
    prompt = f"""
You are a cybersecurity assistant for a small business owner 
with no technical background. Explain this security alert 
in simple, clear language. Be concise — maximum 4 sentences per section.

Alert Data:
- Event Type: {log["event_type"]}
- Source IP: {log["source_ip"]}
- User: {log["user"]}
- Attempts: {log["attempts"]}
- Data Size (MB): {log["data_size_mb"]}
- Threat Score: {log["threat_score"]}
- Threat Level: {log["threat_level"]}
- Time: {log["timestamp"]}

Write your response in exactly this format:

WHAT HAPPENED:
WHY IT MATTERS:
WHAT TO DO:
THREAT LEVEL:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def generate_ai_reports():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM logs
        WHERE (threat_level = 'High' OR threat_level = 'Critical')
        AND ai_explanation IS NULL
    """)

    rows = cursor.fetchall()

    for row in rows:
        log = {
            "id": row[0],
            "timestamp": row[1],
            "source_ip": row[2],
            "event_type": row[3],
            "user": row[4],
            "attempts": row[5],
            "data_size_mb": row[6],
            "port": row[7],
            "threat_score": row[8],
            "threat_level": row[9]
        }

        explanation = generate_explanation(log)

        cursor.execute("""
            UPDATE logs
            SET ai_explanation = ?
            WHERE id = ?
        """, (explanation, log["id"]))

    conn.commit()
    conn.close()