from pathlib import Path
import pypdfium2 as pdfium
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)


def extract_text_from_pdf(pdf_path: Path) -> str:
  if not pdf_path.exists():
    raise FileNotFoundError(f'PDF file not found at: {pdf_path}')

  ocr_text = ''
  try:
    pdf = pdfium.PdfDocument(str(pdf_path))
    for page in pdf:
      image = page.render(scale=2).to_pil()
      # הגדרת psm 6 גורמת ל-Tesseract להתייחס לבלוק כטבלה אחידה שורה-אחר-שורה
      custom_config = r'--oem 3 --psm 6'
      text = pytesseract.image_to_string(
          image, lang='heb+eng', config=custom_config
      )
      ocr_text += text + '\n'
  except Exception as e:
    print(f'[!] OCR extraction failed: {e}')

  return ocr_text