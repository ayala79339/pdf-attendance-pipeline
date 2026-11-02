import re
from domain.models import ReportType


class ReportClassifier:
    """
    Analyzes raw extracted text to determine whether the report is Type A or Type B.
    """

    # Identifiers specific to Type A reports
    TYPE_A_KEYWORDS = [
        r"% 100",
        r"% 125",
        r"% 150",
        r"הפסיקה",
        r"נ\.ע\. הנשר",
    ]

    # Identifiers specific to Type B reports
    TYPE_B_KEYWORDS = [
        r"כרטיס עובד לחודש",
        r"מחיר לשעה",
        r"סה\"כ לתשלום",
        r"Attendance Report - Tуре В",
    ]

    def classify(self, raw_text: str) -> ReportType:
        """
        Classifies raw report text based on unique keyword patterns.

        :param raw_text: Raw string output from OCR/text extraction.
        :return: ReportType.TYPE_A or ReportType.TYPE_B.
        :raises ValueError: If the report type cannot be uniquely identified.
        """
        type_a_score = sum(
            1 for pattern in self.TYPE_A_KEYWORDS if re.search(pattern, raw_text)
        )
        type_b_score = sum(
            1 for pattern in self.TYPE_B_KEYWORDS if re.search(pattern, raw_text)
        )

        if type_a_score > type_b_score:
            return ReportType.TYPE_A
        elif type_b_score > type_a_score:
            return ReportType.TYPE_B

        raise ValueError(
            "Could not determine report type automatically from OCR text."
        )