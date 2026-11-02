from pathlib import Path
import pypdf


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extracts raw text from a PDF file.
    First attempts direct text extraction using pypdf.
    If no text is found (e.g., scanned image PDF), falls back to OCR.

    :param pdf_path: Path object pointing to the PDF file.
    :return: Extracted raw text string from all pages.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    extracted_text = ""

    # Step 1: Direct text extraction (fast and accurate for digitally generated PDFs)
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    except Exception as e:
        print(f"[!] Direct PDF extraction failed: {e}")

    # Step 2: Fallback to OCR if direct text extraction returned no content
    if not extracted_text.strip():
        extracted_text = _ocr_pdf_fallback(pdf_path)

    return extracted_text


def _ocr_pdf_fallback(pdf_path: Path) -> str:
    """
    Fallback method using OCR (pytesseract) for scanned image PDFs.
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract

        # הגדרת נתיב תוכנת Tesseract ב-Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        images = convert_from_path(str(pdf_path))
        ocr_text = ""

        for image in images:
            text = pytesseract.image_to_string(image, lang="heb+eng")
            ocr_text += text + "\n"

        return ocr_text
    except Exception as e:
        print(f"[!] OCR process failed: {e}")
        return ""