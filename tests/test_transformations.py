from datetime import date, time
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from transformation.service import TransformationService


def test_transformation_deterministic_behavior():
    """
    Verifies that passing the same seed produces identical results.
    """
    row = AttendanceRow(
        work_date=date(2022, 9, 1),
        day_of_week="חמישי",
        location=None,
        entry_time=time(8, 0),
        exit_time=time(16, 0),
        break_duration=None,
        total_hours=8.0,
    )
    report = AttendanceReport(
        report_type=ReportType.TYPE_B,
        employee_name="ישראל ישראלי",
        rows=[row],
        summary=ReportSummary(total_days=1, total_hours=8.0, hourly_rate=50.0, total_payment=400.0)
    )

    service = TransformationService()
    run1 = service.transform(report, seed=42)
    run2 = service.transform(report, seed=42)

    assert run1.rows[0].entry_time == run2.rows[0].entry_time
    assert run1.summary.total_payment == run2.summary.total_payment


def test_transformation_invariant_recalculation():
    """
    Verifies that total payment and hours are recalculated accurately after shift.
    """
    row = AttendanceRow(
        work_date=date(2022, 9, 1),
        day_of_week="חמישי",
        location=None,
        entry_time=time(8, 0),
        exit_time=time(16, 0),
        break_duration=None,
        total_hours=8.0,
    )
    report = AttendanceReport(
        report_type=ReportType.TYPE_B,
        employee_name="ישראל ישראלי",
        rows=[row],
        summary=ReportSummary(total_days=1, total_hours=8.0, hourly_rate=50.0, total_payment=400.0)
    )

    service = TransformationService()
    transformed = service.transform(report, seed=42)

    # Ensure total payment matches transformed total hours * rate
    expected_pay = round(transformed.summary.total_hours * 50.0, 2)
    assert transformed.summary.total_payment == expected_pay