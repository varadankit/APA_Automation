"""
Writes results to a running CSV file and a short summary text file
for each processed document.
"""
import os
from datetime import datetime

import pandas as pd

import config


def append_to_csv(filename: str, analysis: dict):
    row = {
        "filename": filename,
        "processed_at": datetime.now().isoformat(timespec="seconds"),
        "document_type": analysis.get("document_type", ""),
        "sender": analysis.get("key_fields", {}).get("sender", ""),
        "date": analysis.get("key_fields", {}).get("date", ""),
        "amount": analysis.get("key_fields", {}).get("amount", ""),
        "deadline": analysis.get("key_fields", {}).get("deadline", ""),
        "suggested_action": analysis.get("suggested_action", ""),
        "priority": analysis.get("priority", ""),
        "summary": analysis.get("summary", ""),
    }

    df_new = pd.DataFrame([row])

    if os.path.exists(config.CSV_PATH):
        df_existing = pd.read_csv(config.CSV_PATH)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(config.CSV_PATH, index=False)


def write_summary(filename: str, analysis: dict):
    base_name = os.path.splitext(filename)[0]
    summary_path = os.path.join(config.SUMMARIES_DIR, f"{base_name}_summary.txt")

    lines = [
        f"File: {filename}",
        f"Type: {analysis.get('document_type', '')}",
        f"Priority: {analysis.get('priority', '')}",
        "",
        "Summary:",
        analysis.get("summary", ""),
        "",
        "Suggested action:",
        analysis.get("suggested_action", ""),
    ]

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
