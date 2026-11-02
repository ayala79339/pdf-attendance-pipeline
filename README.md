# Attendance Report Generator & Variations Engine

An automated Python ETL & OCR pipeline designed to parse scanned or digital attendance reports (PDF), deterministically transform working hour variations while enforcing domain mathematical invariants, and export polished Excel (.xlsx) and PDF reports.

---

## Architecture & Pipeline Flow

All components communicate exclusively through a unified domain contract (AttendanceReport):

[ Input PDF ] ---> [ OCR / Classifier ] ---> [ BaseParser (Template Method) ]
                                                            |
                                                            v
[ Output Files ] <--- [ BaseRenderer (Renderer) ] <--- [ TransformationService (Strategy) ]

### Key Design Patterns
1. Template Method (BaseParser): Defines the invariant parsing flow in the base class, delegating type-specific parsing to TypeAParser and TypeBParser.
2. Strategy Pattern (BaseTransformationStrategy): Decouples transformation rules per report type (Type A overtime vs. Type B salary math).
3. Factory Pattern (ParserFactory): Dynamically instantiates the correct parser based on classifier results.
4. Frozen Domain Model (AttendanceRow): Enforces immutability (frozen=True) during transformation to preserve original data.

---

## Quick Start

### Local Setup
1. Install Dependencies:
   pip install -r requirements.txt

2. Run Pipeline:
   mkdir -p input_pdfs output
   python main.py

---

## Docker Setup

Docker guarantees an identical runtime environment with Python 3.11, tesseract-ocr, tesseract-ocr-heb, and poppler-utils.

1. Build Image:
   docker build -t attendance-generator .

2. Run Container:
   docker run --rm -v "$(pwd)/input_pdfs:/app/input_pdfs" -v "$(pwd)/output:/app/output" attendance-generator

3. Run Unit Tests inside Container:
   docker run --rm attendance-generator pytest tests/