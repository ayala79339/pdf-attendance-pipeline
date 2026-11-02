from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from domain.models import AttendanceReport, ReportType
from generation.base_renderer import BaseRenderer


class ExcelRenderer(BaseRenderer):
    """
    Renders an AttendanceReport into a formatted Excel (.xlsx) file.
    """

    def render(self, report: AttendanceReport, output_path: Path) -> Path:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Report"
        ws.views.sheetView[0].rightToLeft = True  # RTL layout for Hebrew

        # 1. Header Information
        ws.append([f"דוח נוכחות - {report.employee_name}"])
        ws.append([])

        # 2. Table Headers
        if report.report_type == ReportType.TYPE_A:
            headers = [
                "תאריך", "יום", "מקום", "כניסה", "יציאה", "הפסקה",
                "סה\"כ", "100%", "125%", "150%", "שבת"
            ]
        else:
            headers = ["תאריך", "יום", "כניסה", "יציאה", "סה\"כ שעות", "הערות"]

        ws.append(headers)

        # Style header row
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[3]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # 3. Data Rows
        for row in report.rows:
            entry_str = row.entry_time.strftime("%H:%M") if row.entry_time else ""
            exit_str = row.exit_time.strftime("%H:%M") if row.exit_time else ""
            date_str = row.work_date.strftime("%d/%m/%Y")

            if report.report_type == ReportType.TYPE_A:
                break_str = row.break_duration.strftime("%H:%M") if row.break_duration else ""
                ws.append([
                    date_str, row.day_of_week, row.location or "",
                    entry_str, exit_str, break_str, row.total_hours,
                    row.hours_100, row.hours_125, row.hours_150, row.hours_sabbatical
                ])
            else:
                ws.append([
                    date_str, row.day_of_week, entry_str, exit_str,
                    row.total_hours, row.notes or ""
                ])

        # 4. Summary Section
        ws.append([])
        ws.append(["סיכום חודשי"])
        ws.append(["סה\"כ ימי עבודה", report.summary.total_days])
        ws.append(["סה\"כ שעות חודשיות", report.summary.total_hours])

        if report.summary.hourly_rate:
            ws.append(["מחיר לשעה", f"₪{report.summary.hourly_rate:.2f}"])
            ws.append(["סה\"כ לתשלום", f"₪{report.summary.total_payment:.2f}"])

        output_file = output_path.with_suffix(".xlsx")
        wb.save(output_file)
        return output_file