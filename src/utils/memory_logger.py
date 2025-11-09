# memory_logger.py
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG – change only these two lines
# ------------------------------------------------------------------
JSON_LOG_PATH = Path("mem0_memories.json")   # One big JSON array
CSV_LOG_PATH  = Path("mem0_memories.csv")    # Human-readable table
# ------------------------------------------------------------------

# Initialise files (run once)
def _init_files():
    if not JSON_LOG_PATH.exists():
        JSON_LOG_PATH.write_text("[]")           # empty array
    if not CSV_LOG_PATH.exists():
        with open(CSV_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "user_id", "role", "content"])

_init_files()

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def log_memory(user_id: str, messages: list[dict]):
    """
    Call this **after** `memory.add(...)`
    `messages` = list of dicts with keys: role, content
    """
    ts = datetime.utcnow().isoformat() + "Z"

    # ---- JSON ----
    data = json.loads(JSON_LOG_PATH.read_text(encoding="utf-8"))
    for m in messages:
        data.append({
            "timestamp": ts,
            "user_id": user_id,
            "role": m.get("role"),
            "content": m.get("content")
        })
    JSON_LOG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- CSV ----
    with open(CSV_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for m in messages:
            writer.writerow([ts, user_id, m.get("role"), m.get("content")])