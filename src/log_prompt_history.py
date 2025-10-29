# src/log_prompt_history.py
import os
import csv
import json
import shutil
from datetime import datetime

def append_story_log(
    quote,
    story_id,
    story_title,
    storyboard_path="outputs/storyboard.json",
    output_dir="outputs/logs",
    truncate_json=True,
    max_json_chars=3000
):
    """
    Philosophy-Unfolded – Story Logging System (v3)
    Logs all story generation activities to CSV and saves a backup of each storyboard in JSON format.
    Each log entry includes:
        Timestamp – time of creation
        Story_ID – unique identifier for the story
        Quote – source philosophical quote
        Story_Title – generated title
        JSON_Short – compact summary of the storyboard content
        JSON_File – full JSON file stored as a separate backup
    """

    # Create log directory if not already exists
    os.makedirs(output_dir, exist_ok=True)
    story_archive_dir = os.path.join(output_dir, "storyboard_history")
    os.makedirs(story_archive_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "story_log.csv")

    # Read the original JSON content 
    story_json_str = ""
    json_filename = f"{story_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    if os.path.exists(storyboard_path):
        try:
            with open(storyboard_path, "r", encoding="utf-8") as f:
                story_json = json.load(f)
                story_json_str = json.dumps(story_json, ensure_ascii=False, separators=(",", ":"))
                if truncate_json and len(story_json_str) > max_json_chars:
                    story_json_str = story_json_str[:max_json_chars] + "… (truncated)"
        except Exception as e:
            story_json_str = f"Error reading JSON: {e}"
    else:
        story_json_str = "storyboard.json not found."

    # Backup the full storyboard.json file to history folder
    json_copy_path = os.path.join(story_archive_dir, json_filename)
    try:
        if os.path.exists(storyboard_path):
            shutil.copy2(storyboard_path, json_copy_path)
            print(f"Saved storyboard snapshot → {json_copy_path}")
    except Exception as e:
        print(f"Failed to copy storyboard: {e}")

    # Write log to CSV file
    write_header = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([
                "Timestamp",
                "Story_ID",
                "Quote",
                "Story_Title",
                "JSON_Short",
                "JSON_File"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            story_id,
            quote.strip(),
            story_title.strip() if story_title else "N/A",
            story_json_str,
            json_filename
        ])
    print(f"Logged story → {log_path}")

    # Check log size warning
    try:
        size_mb = os.path.getsize(log_path) / (1024 * 1024)
        if size_mb > 10:
            print(f"story_log.csv is {size_mb:.1f}MB — consider archiving old entries.")
    except Exception:
        pass
