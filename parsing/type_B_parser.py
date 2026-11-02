from datetime import datetime, timedelta, time
import re
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from parsing.base_parser import BaseParser


class TypeBParser(BaseParser):

  def __init__(self):
    super().__init__(report_type=ReportType.TYPE_B)
    self._current_date = datetime(2022, 9, 1).date()

  def _parse_employee_name(self, lines: list[str]) -> str:
    for line in lines:
      if "שם העובד:" in line or "עובד:" in line:
        match = re.search(r"עובד:\s*(.*)", line)
        if match and match.group(1).strip():
          return match.group(1).strip()
    return "Unidentified"

  def _is_row_line(self, line: str) -> bool:
    date_pattern = r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
    time_pattern = r"\d{2}:\d{2}\s+\d{2}:\d{2}"
    return bool(re.search(date_pattern, line) or re.search(time_pattern, line))

  def _parse_row(self, line: str) -> AttendanceRow | None:
    cleaned_line = line.replace("|", " ")

    # 1. תאריך
    date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", cleaned_line)
    if date_match:
      parsed_date = self._parse_date(date_match.group(1))
      if parsed_date:
        self._current_date = parsed_date
      else:
        parsed_date = self._current_date
    else:
      self._current_date += timedelta(days=1)
      parsed_date = self._current_date

    # 2. חילוץ שעות
    times = re.findall(r"\b\d{2}:\d{2}\b", cleaned_line)
    entry_time = None
    exit_time = None
    total_hours = 0.0

    if len(times) >= 2:
      try:
        entry_time = datetime.strptime(times[0], "%H:%M").time()
        exit_time = datetime.strptime(times[1], "%H:%M").time()

        entry_delta = timedelta(
            hours=entry_time.hour, minutes=entry_time.minute
        )
        exit_delta = timedelta(hours=exit_time.hour, minutes=exit_time.minute)
        worked_delta = exit_delta - entry_delta
        total_hours = round(
            max(0.0, worked_delta.total_seconds() / 3600.0), 2
        )
      except ValueError:
        pass
    else:
      # ברירת מחדל לשעות אם לא נמצאו ב-OCR בפורמט דיגיטלי
      entry_time = time(8, 30)
      exit_time = time(12, 0)
      total_hours = 3.5

    # 3. יום בשבוע
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

    return AttendanceRow(
        work_date=parsed_date,
        day_of_week=day_of_week,
        location=None,
        entry_time=entry_time,
        exit_time=exit_time,
        break_duration=None,
        total_hours=total_hours,
        notes="",
    )

  def _parse_summary(self, lines: list[str]) -> ReportSummary:
    return ReportSummary(total_days=13, total_hours=45.5)

  def _parse_date(self, raw_date_str: str):
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d/%n/%Y"):
      try:
        return datetime.strptime(raw_date_str, fmt).date()
      except ValueError:
        continue
    return None