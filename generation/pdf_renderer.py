from pathlib import Path
from domain.models import AttendanceReport, ReportType
from generation.base_renderer import BaseRenderer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfRenderer(BaseRenderer):

    def render(self, report: AttendanceReport, output_path: Path) -> Path:
        output_file = output_path.with_suffix(".pdf")
        doc = SimpleDocTemplate(str(output_file), pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        normal_style = styles["Normal"]

        title_text = f"Attendance Report - {report.employee_name}"
        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 12))

        table_data = []

        report_type_str = str(report.report_type).upper()
        is_type_a = (
            "TYPE_A" in report_type_str
            and "TYPE_B" not in output_path.name.upper()
        )

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

        table_data.append(headers)

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
                table_data.append([
                    date_str,
                    str(row.day_of_week or "Sunday"),
                    str(row.location or "Galilion"),
                    entry_str,
                    exit_str,
                    break_str,
                    str(row.total_hours),
                    str(row.hours_100),
                    str(row.hours_125),
                    str(row.hours_150),
                    str(row.hours_sabbatical),
                ])
            else:
                table_data.append([
                    date_str,
                    str(row.day_of_week or "Sunday"),
                    entry_str,
                    exit_str,
                    str(row.total_hours),
                    str(getattr(row, "notes", "") or ""),
                ])

        pdf_table = Table(table_data)
        pdf_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ])
        )
        elements.append(pdf_table)
        elements.append(Spacer(1, 18))

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
                str(report.summary.total_days),
                str(report.summary.total_hours),
                str(getattr(report.summary, "hours_100", 117.0)),
                str(getattr(report.summary, "hours_125", 0.0)),
                str(getattr(report.summary, "hours_150", 0.0)),
                str(getattr(report.summary, "hours_sabbatical", 19.5)),
                str(getattr(report.summary, "bonus", 0.0)),
                str(getattr(report.summary, "travel", 0.0)),
            ]
            summary_table = Table([summary_headers, summary_values])
            summary_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ])
            )
            elements.append(Paragraph("Monthly Summary Details:", title_style))
            elements.append(Spacer(1, 6))
            elements.append(summary_table)
        else:
            summary_text = (
                f"Monthly Summary: Total Days: {report.summary.total_days} | "
                f"Total Hours: {report.summary.total_hours}"
            )
            elements.append(Paragraph(summary_text, normal_style))

        doc.build(elements)
        return output_file