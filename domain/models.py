from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Optional


class ReportType(Enum):
  TYPE_A = "TYPE_A"
  TYPE_B = "TYPE_B"


@dataclass
class AttendanceRow:
  work_date: date
  day_of_week: Optional[str] = None
  location: Optional[str] = None
  entry_time: Optional[time] = None
  exit_time: Optional[time] = None
  break_duration: Optional[time] = None
  total_hours: float = 0.0
  hours_100: float = 0.0
  hours_125: float = 0.0
  hours_150: float = 0.0
  hours_sabbatical: float = 0.0
  notes: Optional[str] = None


@dataclass
class ReportSummary:
  total_days: int = 0
  total_hours: float = 0.0
  hourly_rate: Optional[float] = None
  total_payment: Optional[float] = None
  hours_100: float = 0.0
  hours_125: float = 0.0
  hours_150: float = 0.0
  hours_sabbatical: float = 0.0
  bonus: float = 0.0
  travel: float = 0.0


@dataclass
class AttendanceReport:
  employee_name: str
  report_type: ReportType
  rows: list[AttendanceRow] = field(default_factory=list)
  summary: ReportSummary = field(default_factory=ReportSummary)