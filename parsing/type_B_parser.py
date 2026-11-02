import re
from datetime import datetime
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from parsing.base_parser import BaseParser


class TypeBParser(BaseParser):
    """
    Parser implementation for Type B attendance reports (Employee Monthly Timecards).
    Handles extraction of daily total hours, notes, hourly rates, and total monthly pay.
    """

    def __init__(self):
        super().__init__(report_type=ReportType.TYPE_B)

    def _parse_employee_name(self, lines: list[str]) -> str:
        """
        Extracts employee name from header lines.
        """
        for line in lines:
            if "שם העובד:" in line:
                match = re.search(r"שם העובד:\s*(.*)", line)
                if match and match.group(1).strip():
                    return match.group(1).strip()
        return "Unidentified"

    def _is_row_line(self, line: str) -> bool:
        """
        Validates if a line is a Type B attendance row by searching for date pattern (D/M/YY or DD/MM/YYYY).
        """
        date_pattern = r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
        return bool(re.search(date_pattern, line))

    def _parse_row(self, line: str) -> AttendanceRow | None:
        """
        Parses a single text line into a Type B AttendanceRow object.
        Tokens expected: Date, Day of Week, Entry Time, Exit Time, Total Hours, Notes.
        """
        tokens = [token.strip() for token in line.split("|") if token.strip()]

        if len(tokens) < 4:
            return None

        try:
            # 1. Parse date (supports both '1/9/22' and '01/09/2022')
            raw_date = tokens[0]
            parsed_date = self._parse_date(raw_date)
            if not parsed_date:
                return None

            day_of_week = tokens[1] if len(tokens) > 1 else ""

            # Check if times exist or if it was a rest day / holiday
            entry_time = None
            exit_time = None
            total_hours = 0.0
            notes = None

            # Standard row with time entries
            if len(tokens) >= 5:
                entry_time = datetime.strptime(tokens[2], "%H:%M").time()
                exit_time = datetime.strptime(tokens[3], "%H:%M").time()
                total_hours = float(tokens[4])
                notes = tokens[5] if len(tokens) > 5 else None
            elif len(tokens) == 4:
                # Alternate token arrangement or note-only row
                notes = tokens[3]

            return AttendanceRow(
                work_date=parsed_date,
                day_of_week=day_of_week,
                location=None,  # Location field is not present in Type B
                entry_time=entry_time,
                exit_time=exit_time,
                break_duration=None,
                total_hours=total_hours,
                notes=notes,
            )
        except (ValueError, IndexError):
            return None

    def _parse_summary(self, lines: list[str]) -> ReportSummary:
        """
        Extracts Type B summary table values (Total Days, Total Hours, Hourly Rate, Total Pay).
        """
        total_days = 0
        total_hours = 0.0
        hourly_rate = None
        total_payment = None

        for line in lines:
            if "סה:\"כ ימי עבודה לחודש" in line or "סה\"כ ימי עבודה" in line:
                days_match = re.findall(r"\d+", line)
                if days_match:
                    total_days = int(days_match[0])

            elif "סה\"כ שעות חודשיות" in line:
                hours_match = re.findall(r"\d+\.?\d*", line)
                if hours_match:
                    total_hours = float(hours_match[0])

            elif "מחיר לשעה" in line:
                # Clean currency symbol '₪' and parse float
                clean_line = line.replace("₪", "").replace(",", "").strip()
                rate_match = re.findall(r"\d+\.?\d*", clean_line)
                if rate_match:
                    hourly_rate = float(rate_match[0])

            elif "סה\"כ לתשלום" in line:
                clean_line = line.replace("₪", "").replace(",", "").strip()
                pay_match = re.findall(r"\d+\.?\d*", clean_line)
                if pay_match:
                    total_payment = float(pay_match[0])

        return ReportSummary(
            total_days=total_days,
            total_hours=total_hours,
            hourly_rate=hourly_rate,
            total_payment=total_payment,
        )

    def _parse_date(self, raw_date_str: str):
        """
        Helper method to parse flexible date string formats (e.g., '1/9/22' or '01/09/2022').
        """
        for fmt in ("%d/%m/%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(raw_date_str, fmt).date()
            except ValueError:
                continue
        return None