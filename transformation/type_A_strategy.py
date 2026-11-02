import random
from datetime import datetime
from domain.models import AttendanceReport, AttendanceRow, ReportSummary
from transformation.base_strategy import BaseTransformationStrategy


class TypeATransformationStrategy(BaseTransformationStrategy):
    """
    Transformation strategy for Type A reports.
    Shifts entry/exit times and recalculates overtime breakdowns (100%, 125%, 150%).
    """

    def transform_report(
        self, report: AttendanceReport, seed: int = 42
    ) -> AttendanceReport:
        # Initialize random generator with a seed for deterministic behavior
        rng = random.Random(seed)

        transformed_rows = []
        for row in report.rows:
            new_row = self._transform_row(row, rng)
            transformed_rows.append(new_row)

        # Recalculate summary sums based on transformed rows
        total_days = len([r for r in transformed_rows if r.total_hours > 0])
        total_hours = sum(r.total_hours for r in transformed_rows)

        new_summary = ReportSummary(
            total_days=total_days,
            total_hours=round(total_hours, 2),
        )

        return AttendanceReport(
            report_type=report.report_type,
            employee_name=report.employee_name,
            rows=transformed_rows,
            summary=new_summary,
        )

    def _transform_row(self, row: AttendanceRow, rng: random.Random) -> AttendanceRow:
        if row.entry_time is None or row.exit_time is None:
            return row  # Rest days or non-working rows remain unchanged

        # Generate a small deterministic variation (-10 to +10 minutes)
        minute_delta = rng.randint(-10, 10)

        new_entry = self._shift_time_minutes(row.entry_time, minute_delta)
        new_exit = self._shift_time_minutes(row.exit_time, minute_delta)

        # Calculate exact total working hours: (Exit - Entry - Break)
        entry_dt = datetime.combine(row.work_date, new_entry)
        exit_dt = datetime.combine(row.work_date, new_exit)
        diff_seconds = (exit_dt - entry_dt).total_seconds()

        # Convert break duration if present
        break_seconds = 0
        if row.break_duration:
            break_seconds = (
                row.break_duration.hour * 3600 + row.break_duration.minute * 60
            )

        total_seconds = max(0.0, diff_seconds - break_seconds)
        total_hours = round(total_seconds / 3600.0, 2)

        # Basic overtime allocation (Standard workday: 8 hours = 100%, rest = 125%)
        h_100 = min(total_hours, 8.0)
        h_125 = max(0.0, total_hours - 8.0)

        # Construct and return a new AttendanceRow (frozen dataclass enforcement)
        return AttendanceRow(
            work_date=row.work_date,
            day_of_week=row.day_of_week,
            location=row.location,
            entry_time=new_entry,
            exit_time=new_exit,
            break_duration=row.break_duration,
            total_hours=total_hours,
            hours_100=h_100,
            hours_125=h_125,
            hours_150=0.0,
            hours_sabbatical=row.hours_sabbatical,
        )