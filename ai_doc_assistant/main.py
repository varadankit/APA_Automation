"""
AI Document Assistant

Watches a folder for new files and runs each one through the pipeline:
read -> classify with AI -> extract fields -> log to CSV + summary.

Run it, then drop a PDF, txt, or eml file into inbox/.
"""
import os
import shutil
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
import file_reader
import ai_engine
import output_writer


def process_file(path: str):
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in config.SUPPORTED_EXTENSIONS:
        print(f"[main] Skipping unsupported file: {filename}")
        return

    print(f"[main] Processing: {filename}")

    text = file_reader.extract_text(path)
    if not text:
        print(f"[main] No readable text found in {filename}, skipping.")
        return

    analysis = ai_engine.analyze_document(text)

    output_writer.append_to_csv(filename, analysis)
    output_writer.write_summary(filename, analysis)

    # Move the file out of inbox so it doesn't get reprocessed
    dest = os.path.join(config.PROCESSED_DIR, filename)
    shutil.move(path, dest)

    print(f"[main] Done: {filename} -> classified as '{analysis.get('document_type')}'")


class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # give the file a second to finish writing before we read it
        time.sleep(1)
        process_file(event.src_path)


def process_existing_files():
    """Process any files that were already sitting in inbox/ before we started."""
    for filename in os.listdir(config.INBOX_DIR):
        full_path = os.path.join(config.INBOX_DIR, filename)
        if os.path.isfile(full_path):
            process_file(full_path)


def main():
    os.makedirs(config.INBOX_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    os.makedirs(config.SUMMARIES_DIR, exist_ok=True)

    print(f"[main] Watching folder: {config.INBOX_DIR}")
    print(f"[main] Using LLM provider: {config.LLM_PROVIDER}")

    process_existing_files()

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, config.INBOX_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[main] Stopped.")
    observer.join()


if __name__ == "__main__":
    main()
