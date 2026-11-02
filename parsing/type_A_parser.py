import re
from datetime import datetime
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from parsing.base_parser import BaseParser


class TypeAParser(BaseParser):
    """
    Parser implementation for Type A attendance reports (e.g., Eagle Manpower).
    Handles extraction of overtime hours (100%, 125%, 150%, sabbatical).
    """

    def __init__(self):
        super().__init__(report_type=ReportType.TYPE_A)

    def _parse_employee_name(self, lines: list[str]) -> str:
        """
        Extracts the employee name from the header lines.
        Defaults to 'Unidentified' if not found.
        """
        for line in lines:
            if "שם העובד:" in line:
                match = re.search(r"שם העובד:\s*(.*)", line)
                if match and match.group(1).strip():
                    return match.group(1).strip()
        return "Unidentified"

    def _is_row_line(self, line: str) -> bool:
        """
        Checks if a line represents a valid attendance row by verifying
        the presence of a date pattern (DD/MM/YYYY).
        """
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        return bool(re.search(date_pattern, line))

    def _parse_row(self, line: str) -> AttendanceRow | None:
        """
        Parses a single line of Type A report into an AttendanceRow object.
        Expected format contains pipe-separated values or tokens for date, day, times, and overtime.
        """
        tokens = [token.strip() for token in line.split("|") if token.strip()]

        if len(tokens) < 7:
            return None

        try:
            # Parsing date (e.g., '08/10/2022')
            raw_date = tokens[0]
            parsed_date = datetime.strptime(raw_date, "%d/%m/%Y").date()

            day_of_week = tokens[1]
            location = tokens[2] if len(tokens) > 8 else None

            # Time columns: entry, exit, break
            entry_time = datetime.strptime(tokens[3], "%H:%M").time()
            exit_time = datetime.strptime(tokens[4], "%H:%M").time()
            break_time = datetime.strptime(tokens[5], "%H:%M").time()

            total_hours = float(tokens[6])

            # Overtime hours extraction (optional columns in Type A)
            h_100 = float(tokens[7]) if len(tokens) > 7 else 0.0
            h_125 = float(tokens[8]) if len(tokens) > 8 else 0.0
            h_150 = float(tokens[9]) if len(tokens) > 9 else 0.0
            h_sabbatical = float(tokens[10]) if len(tokens) > 10 else 0.0

            return AttendanceRow(
                work_date=parsed_date,
                day_of_week=day_of_week,
                location=location,
                entry_time=entry_time,
                exit_time=exit_time,
                break_duration=break_time,
                total_hours=total_hours,
                hours_100=h_100,
                hours_125=h_125,
                hours_150=h_150,
                hours_sabbatical=h_sabbatical,
            )
        except (ValueError, IndexError):
            # Safe fail on malformed OCR lines
            return None

    def _parse_summary(self, lines: list[str]) -> ReportSummary:
        """
        Parses monthly summary information at the bottom of Type A reports.
        """
        total_days = 0
        total_hours = 0.0

        for line in lines:
            if "סה\"כ שעות" in line or "סה כ שעות" in line:
                numbers = re.findall(r"\d+\.?\d*", line)
                if numbers:
                    total_hours = float(numbers[0])
            elif "ימים" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    total_days = int(numbers[0])

        return ReportSummary(
            total_days=total_days,
            total_hours=total_hours,
        )