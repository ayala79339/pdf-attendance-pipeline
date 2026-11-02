import random
from datetime import datetime
from domain.models import AttendanceReport, AttendanceRow, ReportSummary
from transformation.base_strategy import BaseTransformationStrategy


class TypeBTransformationStrategy(BaseTransformationStrategy):
    """
    Transformation strategy for Type B reports.
    Recalculates total hours, total monthly hours, and total salary pay.
    """

    def transform_report(
        self, report: AttendanceReport, seed: int = 42
    ) -> AttendanceReport:
        rng = random.Random(seed)

        transformed_rows = []
        for row in report.rows:
            new_row = self._transform_row(row, rng)
            transformed_rows.append(new_row)

        total_days = len([r for r in transformed_rows if r.total_hours > 0])
        total_hours = sum(r.total_hours for r in transformed_rows)

        # Recalculate salary if hourly rate exists
        total_payment = None
        if report.summary.hourly_rate is not None:
            total_payment = round(total_hours * report.summary.hourly_rate, 2)

        new_summary = ReportSummary(
            total_days=total_days,
            total_hours=round(total_hours, 2),
            hourly_rate=report.summary.hourly_rate,
            total_payment=total_payment,
        )

        return AttendanceReport(
            report_type=report.report_type,
            employee_name=report.employee_name,
            rows=transformed_rows,
            summary=new_summary,
        )

    def _transform_row(self, row: AttendanceRow, rng: random.Random) -> AttendanceRow:
        if row.entry_time is None or row.exit_time is None:
            return row

        minute_delta = rng.randint(-5, 5)

        new_entry = self._shift_time_minutes(row.entry_time, minute_delta)
        new_exit = self._shift_time_minutes(row.exit_time, minute_delta)

        entry_dt = datetime.combine(row.work_date, new_entry)
        exit_dt = datetime.combine(row.work_date, new_exit)
        total_seconds = max(0.0, (exit_dt - entry_dt).total_seconds())
        total_hours = round(total_seconds / 3600.0, 2)

        return AttendanceRow(
            work_date=row.work_date,
            day_of_week=row.day_of_week,
            location=row.location,
            entry_time=new_entry,
            exit_time=new_exit,
            break_duration=row.break_duration,
            total_hours=total_hours,
            notes=row.notes,
        )