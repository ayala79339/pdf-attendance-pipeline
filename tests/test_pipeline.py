from pathlib import Path
from generation.excel_renderer import ExcelRenderer
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType
from datetime import date, time


def test_excel_renderer_generates_file(tmp_path):
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
        summary=ReportSummary(total_days=1, total_hours=8.0)
    )

    renderer = ExcelRenderer()
    output_file = renderer.render(report, tmp_path / "test_report")

    assert output_file.exists()
    assert output_file.suffix == ".xlsx"