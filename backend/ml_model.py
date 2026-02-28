import pandas as pd
from sklearn.ensemble import IsolationForest
from database import get_connection

model = None


def train_model():
    global model

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()

    if df.empty or len(df) < 10:
        return None

    features = df[["attempts", "data_size_mb", "port"]]

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    model.fit(features)

    return model


def score_logs():
    global model

    if model is None:
        train_model()

    if model is None:
        return

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM logs", conn)

    if df.empty:
        conn.close()
        return

    features = df[["attempts", "data_size_mb", "port"]]

    scores = model.decision_function(features)
    predictions = model.predict(features)

    cursor = conn.cursor()

    for i, row in df.iterrows():
        score = scores[i]

        if score < -0.2:
            level = "Critical"
        elif score < -0.1:
            level = "High"
        elif score < 0:
            level = "Medium"
        else:
            level = "Low"

        cursor.execute("""
            UPDATE logs
            SET threat_score = ?, threat_level = ?
            WHERE id = ?
        """, (
            float(score),
            level,
            int(row["id"])
        ))

    conn.commit()
    conn.close()