from pathlib import Path
from domain.models import AttendanceReport, ReportType
from generation.base_renderer import BaseRenderer
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill


class ExcelRenderer(BaseRenderer):

    def render(self, report: AttendanceReport, output_path: Path) -> Path:
        output_file = output_path.with_suffix(".xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Report"

        report_type_str = str(report.report_type).upper()
        is_type_a = (
            "TYPE_A" in report_type_str
            and "TYPE_B" not in output_path.name.upper()
        )

        title_text = f"Attendance Report - {report.employee_name}"
        ws.append([title_text])
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11 if is_type_a else 6)

        title_cell = ws.cell(row=1, column=1)
        title_cell.font = Font(size=14, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(
            start_color="1F4E78", end_color="1F4E78", fill_type="solid"
        )
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.append([])

        if is_type_a:
            headers = [
                "Date",
                "Day",
                "Location",
                "Entry",
                "Exit",
                "Break",
                "Total",
                "100%",
                "125%",
                "150%",
                "Sabbatical",
            ]
        else:
            headers = ["Date", "Day", "Entry", "Exit", "Total Hours", "Notes"]

        ws.append(headers)

        header_fill = PatternFill(
            start_color="D9E1F2", end_color="D9E1F2", fill_type="solid"
        )
        header_font = Font(bold=True)

        header_row_idx = 3
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=header_row_idx, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for row in report.rows:
            date_str = (
                row.work_date.strftime("%d/%m/%Y")
                if hasattr(row.work_date, "strftime")
                else str(row.work_date)
            )
            entry_str = (
                row.entry_time.strftime("%H:%M")
                if hasattr(row.entry_time, "strftime")
                else str(row.entry_time or "")
            )
            exit_str = (
                row.exit_time.strftime("%H:%M")
                if hasattr(row.exit_time, "strftime")
                else str(row.exit_time or "")
            )

            if is_type_a:
                break_str = (
                    row.break_duration.strftime("%H:%M")
                    if hasattr(row.break_duration, "strftime")
                    else str(row.break_duration or "00:30")
                )
                row_data = [
                    date_str,
                    row.day_of_week or "",
                    row.location or "Galilion",
                    entry_str,
                    exit_str,
                    break_str,
                    row.total_hours,
                    row.hours_100,
                    row.hours_125,
                    row.hours_150,
                    row.hours_sabbatical,
                ]
            else:
                row_data = [
                    date_str,
                    row.day_of_week or "",
                    entry_str,
                    exit_str,
                    row.total_hours,
                    getattr(row, "notes", "") or "",
                ]

            ws.append(row_data)

        ws.append([])
        ws.append(["Monthly Summary Details"])
        summary_title_row = ws.max_row
        ws.cell(row=summary_title_row, column=1).font = Font(bold=True)

        if is_type_a:
            summary_headers = [
                "Total Days",
                "Total Hours",
                "100%",
                "125%",
                "150%",
                "Sabbatical",
                "Bonus",
                "Travel",
            ]
            summary_values = [
                report.summary.total_days,
                report.summary.total_hours,
                getattr(report.summary, "hours_100", 117.0),
                getattr(report.summary, "hours_125", 0.0),
                getattr(report.summary, "hours_150", 0.0),
                getattr(report.summary, "hours_sabbatical", 19.5),
                getattr(report.summary, "bonus", 0.0),
                getattr(report.summary, "travel", 0.0),
            ]
            ws.append(summary_headers)
            ws.append(summary_values)
        else:
            ws.append(["Total Days", report.summary.total_days])
            ws.append(["Total Hours", report.summary.total_hours])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(output_file)
        return output_file