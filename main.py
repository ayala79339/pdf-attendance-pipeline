import sys
from pathlib import Path
from parsing.classifier import ReportClassifier
from parsing.factory import ParserFactory
from parsing.ocr import extract_text_from_pdf
from transformation.service import TransformationService
from generation.excel_renderer import ExcelRenderer


def process_attendance_report(pdf_path: Path, output_dir: Path, seed: int = 42):
    """
    Executes the complete ETL attendance report pipeline.

    :param pdf_path: Path to input PDF file.
    :param output_dir: Directory where output files will be saved.
    :param seed: Random seed for deterministic transformation.
    """
    print(f"[*] Processing report: {pdf_path.name}")

    # Step 1: OCR / Text Extraction
    raw_text = extract_text_from_pdf(pdf_path)

    # Step 2: Report Type Classification
    classifier = ReportClassifier()
    report_type = classifier.classify(raw_text)
    print(f"[+] Identified report type: {report_type.value}")

    # Step 3: Parsing (Text -> AttendanceReport domain object)
    parser = ParserFactory.get_parser(report_type)
    original_report = parser.parse(raw_text)

    # Step 4: Transformation (Deterministic Variation Generator)
    transformation_service = TransformationService()
    transformed_report = transformation_service.transform(original_report, seed=seed)
    print(f"[+] Transformed {len(transformed_report.rows)} attendance rows successfully.")

    # Step 5: Generation (AttendanceReport -> Excel / PDF files)
    excel_renderer = ExcelRenderer()
    output_path = output_dir / f"{pdf_path.stem}_NEW"
    generated_file = excel_renderer.render(transformed_report, output_path)

    print(f"[✔] Generated output file: {generated_file.name}\n")


if __name__ == "__main__":
    input_file = Path("input_pdfs/a_r_9.pdf")
    output_directory = Path("output")
    output_directory.mkdir(exist_ok=True)

    if input_file.exists():
        process_attendance_report(input_file, output_directory, seed=42)
    else:
        print(f"[!] Input file {input_file} not found.")