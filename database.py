import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports.db")

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea TEXT NOT NULL,
            keywords TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            report_json TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_report(idea: str, keywords: str, overall_score: int, report_data: dict) -> int:
    """Saves an analysis report to the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    report_json = json.dumps(report_data)
    
    cursor.execute("""
        INSERT INTO validation_reports (idea, keywords, overall_score, report_json, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (idea, keywords, overall_score, report_json, timestamp))
    
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def get_all_reports() -> list:
    """Fetches a summary of all saved reports from the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, idea, keywords, overall_score, timestamp 
        FROM validation_reports 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    
    reports = []
    for row in rows:
        reports.append({
            "id": row["id"],
            "idea": row["idea"],
            "keywords": row["keywords"],
            "overall_score": row["overall_score"],
            "timestamp": row["timestamp"]
        })
        
    conn.close()
    return reports

def get_report_by_id(report_id: int) -> dict:
    """Fetches a detailed report by its ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, idea, keywords, overall_score, report_json, timestamp 
        FROM validation_reports 
        WHERE id = ?
    """, (report_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    report = {
        "id": row["id"],
        "idea": row["idea"],
        "keywords": row["keywords"],
        "overall_score": row["overall_score"],
        "report": json.loads(row["report_json"]),
        "timestamp": row["timestamp"]
    }
    
    conn.close()
    return report

def delete_report(report_id: int) -> bool:
    """Deletes a report by its ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM validation_reports WHERE id = ?", (report_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
