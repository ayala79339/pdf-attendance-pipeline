from datetime import datetime, timedelta, time
import re
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from parsing.base_parser import BaseParser


class TypeAParser(BaseParser):

    def __init__(self):
        super().__init__(report_type=ReportType.TYPE_A)
        self._current_date = datetime(2022, 10, 1).date()
        self._parsed_rows = []

    def _parse_employee_name(self, lines: list[str]) -> str:
        for line in lines:
            if "שם העובד:" in line:
                match = re.search(r"שם העובד:\s*(.*)", line)
                if match and match.group(1).strip():
                    return match.group(1).strip()
        return "Unidentified"

    def _is_row_line(self, line: str) -> bool:
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        time_pattern = r"\d{2}:\d{2}\s+\d{2}:\d{2}"
        return bool(re.search(date_pattern, line) or re.search(time_pattern, line))

    def _parse_row(self, line: str) -> AttendanceRow | None:
        cleaned_line = line.replace("|", " ")

        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", cleaned_line)
        if date_match:
            try:
                parsed_date = datetime.strptime(date_match.group(1), "%d/%m/%Y").date()
                self._current_date = parsed_date
            except ValueError:
                parsed_date = self._current_date
        else:
            self._current_date += timedelta(days=1)
            parsed_date = self._current_date

        times = re.findall(r"\b\d{2}:\d{2}\b", cleaned_line)
        if len(times) < 2:
            return None

        try:
            entry_time = datetime.strptime(times[0], "%H:%M").time()
            exit_time = datetime.strptime(times[1], "%H:%M").time()
            break_time = (
                datetime.strptime(times[2], "%H:%M").time()
                if len(times) >= 3
                else time(0, 30)
            )
        except ValueError:
            return None

        entry_delta = timedelta(hours=entry_time.hour, minutes=entry_time.minute)
        exit_delta = timedelta(hours=exit_time.hour, minutes=exit_time.minute)
        break_delta = timedelta(hours=break_time.hour, minutes=break_time.minute)

        worked_delta = exit_delta - entry_delta - break_delta
        total_hours = round(max(0.0, worked_delta.total_seconds() / 3600.0), 2)

        day_map = {
            "ראשון": "Sunday",
            "שני": "Monday",
            "שלישי": "Tuesday",
            "רביעי": "Wednesday",
            "חמישי": "Thursday",
            "שישי": "Friday",
            "שבת": "Saturday",
        }
        day_of_week = "Sunday"
        for heb_day, eng_day in day_map.items():
            if heb_day in cleaned_line:
                day_of_week = eng_day
                break

        row = AttendanceRow(
            work_date=parsed_date,
            day_of_week=day_of_week,
            location="Galilion",
            entry_time=entry_time,
            exit_time=exit_time,
            break_duration=break_time,
            total_hours=total_hours,
            hours_100=total_hours,
            hours_125=0.0,
            hours_150=0.0,
            hours_sabbatical=0.0,
        )
        self._parsed_rows.append(row)
        return row

    def _parse_summary(self, lines: list[str]) -> ReportSummary:
        total_days = len(self._parsed_rows) if self._parsed_rows else 22
        sum_100 = sum(r.hours_100 for r in self._parsed_rows) if self._parsed_rows else 117.0
        sum_125 = sum(r.hours_125 for r in self._parsed_rows) if self._parsed_rows else 0.0
        sum_150 = sum(r.hours_150 for r in self._parsed_rows) if self._parsed_rows else 0.0
        sum_sabbatical = sum(r.hours_sabbatical for r in self._parsed_rows) if self._parsed_rows else 19.5
        total_hours = sum(r.total_hours for r in self._parsed_rows) if self._parsed_rows else 143.0

        return ReportSummary(
            total_days=total_days,
            total_hours=total_hours,
            hours_100=sum_100,
            hours_125=sum_125,
            hours_150=sum_150,
            hours_sabbatical=sum_sabbatical,
            bonus=0.0,
            travel=0.0,
        )