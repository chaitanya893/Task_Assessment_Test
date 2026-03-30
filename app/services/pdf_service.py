import fitz  # PyMuPDF
import re

def clean_text(text):
    # Remove weird unicode characters
    text = text.encode("utf-8", "ignore").decode("utf-8")

    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Fix broken spacing (multiple spaces → single)
    text = re.sub(r'\s+', ' ', text)

    # Remove unwanted symbols
    text = re.sub(r'[^\w\s.,@\-:/]', '', text)

    return text.strip()


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = ""

    for page in doc:
        text = page.get_text()
        text = clean_text(text)
        full_text += text + "\n"

    return full_text