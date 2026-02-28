from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ml_model import train_model, score_logs
from ai_explainer import generate_ai_reports
from auto_response import execute_auto_response
from database import init_db, insert_log, get_all_logs, get_connection
from demo_seed import seed_demo_data
from report_generator import generate_pdf_report

import csv
import io
import re
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# ==============================
# WebSocket Manager
# ==============================

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==============================
# Basic Routes
# ==============================

@app.get("/")
def root():
    return {"status": "AI-SIEM Backend Running"}

@app.get("/logs")
def fetch_logs():
    return get_all_logs()

# ==============================
# Upload Logs
# ==============================

@app.post("/upload-logs")
async def upload_logs(file: UploadFile = File(...)):

    filename = file.filename.lower()
    contents = await file.read()
    decoded = contents.decode("utf-8")

    if filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(decoded))

        for row in reader:
            insert_log({
                "timestamp": row["timestamp"],
                "source_ip": row["source_ip"],
                "event_type": row["event_type"],
                "user": row["user"],
                "attempts": int(row["attempts"]),
                "data_size_mb": int(row["data_size_mb"]),
                "port": int(row["port"]),
                "anomaly_score": None,
                "threat_level": None
            })

    elif filename.endswith(".log"):
        lines = decoded.splitlines()
        pattern = r"(.+?) \| IP: (.+?) \| EVENT: (.+?) \| USER: (.+?) \| ATTEMPTS: (\d+) \| SIZE_MB: (\d+) \| PORT: (\d+)"

        for line in lines:
            match = re.match(pattern, line)
            if match:
                insert_log({
                    "timestamp": match.group(1),
                    "source_ip": match.group(2),
                    "event_type": match.group(3),
                    "user": match.group(4),
                    "attempts": int(match.group(5)),
                    "data_size_mb": int(match.group(6)),
                    "port": int(match.group(7)),
                    "anomaly_score": None,
                    "threat_level": None
                })
    else:
        raise HTTPException(status_code=400, detail="Only .csv and .log files supported")

    return {"message": "Logs uploaded successfully"}

# ==============================
# ML + Detection
# ==============================

@app.post("/train-model")
def train():
    model = train_model()
    if model is None:
        return {"message": "Not enough data to train"}
    return {"message": "Model trained successfully"}

@app.post("/analyze")
async def analyze():

    score_logs()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, source_ip, event_type, threat_level
        FROM logs
        WHERE threat_level IN ('High', 'Critical')
    """)

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        await manager.broadcast({
            "id": row[0],
            "source_ip": row[1],
            "event_type": row[2],
            "threat_level": row[3]
        })

    return {"message": "Threat analysis completed"}

# ==============================
# AI + Auto Response
# ==============================

@app.post("/generate-ai-reports")
def generate_reports():
    generate_ai_reports()
    return {"message": "AI reports generated"}

@app.post("/auto-respond")
def auto_respond():
    execute_auto_response()
    return {"message": "Auto response executed"}

# ==============================
# Seed Demo Data
# ==============================

@app.post("/seed-demo")
def seed_demo():
    seed_demo_data()
    return {"message": "Demo data inserted successfully"}

# ==============================
# Simulate Live Attack
# ==============================

@app.post("/simulate-attack")
async def simulate_attack():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs
        (timestamp, source_ip, event_type, user, attempts, data_size_mb, port,
         anomaly_score, threat_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "203.0.113.99",
        "login_failed",
        "admin",
        150,
        0,
        22,
        -0.8,
        "Critical"
    ))

    conn.commit()
    conn.close()

    await manager.broadcast({
        "source_ip": "203.0.113.99",
        "event_type": "login_failed",
        "threat_level": "Critical"
    })

    return {"message": "Attack simulated successfully"}

# ==============================
# PDF Report
# ==============================

@app.post("/generate-report")
def generate_report():
    generate_pdf_report()
    return {"message": "PDF report generated"}