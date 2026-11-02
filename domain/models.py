from dataclasses import dataclass
from datetime import date, time
from enum import Enum


class ReportType(Enum):
    """
    Enumeration representing the supported attendance report types.
    """
    TYPE_A = "TYPE_A"
    TYPE_B = "TYPE_B"


@dataclass(frozen=True)
class AttendanceRow:
    """
    Represents a single daily attendance record in a report.
    Marked as frozen=True to enforce immutability during transformation.
    """
    work_date: date
    day_of_week: str
    location: str | None
    entry_time: time | None
    exit_time: time | None
    break_duration: time | None
    total_hours: float

    # Type A specific fields (overtime calculations)
    hours_100: float = 0.0
    hours_125: float = 0.0
    hours_150: float = 0.0
    hours_sabbatical: float = 0.0

    # Type B specific fields
    notes: str | None = None


@dataclass(frozen=True)
class ReportSummary:
    """
    Represents the monthly summary data of an attendance report.
    """
    total_days: int
    total_hours: float
    hourly_rate: float | None = None  # Relevant for Type B
    total_payment: float | None = None  # Relevant for Type B


@dataclass(frozen=True)
class AttendanceReport:
    """
    Represents the complete attendance report.
    Acts as the single domain model contract passed between pipeline stages.
    """
    report_type: ReportType
    employee_name: str
    rows: list[AttendanceRow]
    summary: ReportSummary