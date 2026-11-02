import re
from domain.models import ReportType


class ReportClassifier:

  # Identifiers specific to Type A reports
  TYPE_A_KEYWORDS = [
      r"% 100",
      r"100 %",
      r"% 125",
      r"125 %",
      r"% 150",
      r"150 %",
      r"הפסיקה",
      r"הקיספה",  # עברית הפוכה
      r"נ\.ע\. הנשר",
      r"רשנה \.ע\.נ",  # עברית הפוכה
  ]

  # Identifiers specific to Type B reports
  TYPE_B_KEYWORDS = [
      r"כרטיס עובד לחודש",
      r"דוחושל דבוע סיטרכ",  # עברית הפוכה
      r"מחיר לשעה",
      r"העשל ריחמ",  # עברית הפוכה
      r"סה\"כ לתשלום",
      r"םולשתל כ\"הס",  # עברית הפוכה
      r"Attendance Report - Tуре В",
      r"Type B",
      r"Type-B",
  ]

  def classify(self, raw_text: str) -> ReportType:
    # בדיקת מילות מפתח ישירה וגם מול טקסט הפוך
    reversed_text = raw_text[::-1]

    type_a_score = sum(
        1
        for pattern in self.TYPE_A_KEYWORDS
        if re.search(pattern, raw_text) or re.search(pattern, reversed_text)
    )
    type_b_score = sum(
        1
        for pattern in self.TYPE_B_KEYWORDS
        if re.search(pattern, raw_text) or re.search(pattern, reversed_text)
    )

    if type_a_score > type_b_score:
      return ReportType.TYPE_A
    elif type_b_score > type_a_score:
      return ReportType.TYPE_B

    # אם הקובץ מכיל את האות A או B בשם הקובץ או בטקסט כגיבוי אחרון
    if "TYPE A" in raw_text.upper() or "TYPE_A" in raw_text.upper():
      return ReportType.TYPE_A
    elif "TYPE B" in raw_text.upper() or "TYPE_B" in raw_text.upper():
      return ReportType.TYPE_B

    raise ValueError(
        "Could not determine report type automatically from OCR text."
    )