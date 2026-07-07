"""
Turns a file on disk into plain text, regardless of type.
"""
import os
from email import policy
from email.parser import BytesParser


def read_pdf(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def read_eml(path: str) -> str:
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg.get("subject", "")
    sender = msg.get("from", "")
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    return f"From: {sender}\nSubject: {subject}\n\n{body}".strip()


def extract_text(path: str) -> str:
    """
    Dispatch to the right reader based on file extension.
    Returns empty string if the type is unsupported or reading fails.
    """
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return read_pdf(path)
        elif ext in (".txt", ".md"):
            return read_txt(path)
        elif ext == ".eml":
            return read_eml(path)
        else:
            return ""
    except Exception as e:
        print(f"[file_reader] Failed to read {path}: {e}")
        return ""
