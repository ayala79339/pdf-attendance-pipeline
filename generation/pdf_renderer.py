from pathlib import Path
from domain.models import AttendanceReport, ReportType
from generation.base_renderer import BaseRenderer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfRenderer(BaseRenderer):
    """
    Renders an AttendanceReport into a PDF file using ReportLab.
    """

    def render(self, report: AttendanceReport, output_path: Path) -> Path:
        output_file = output_path.with_suffix(".pdf")
        doc = SimpleDocTemplate(str(output_file), pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        normal_style = styles["Normal"]

        # 1. Title & Header Info
        title_text = f"Attendance Report - {report.employee_name}"
        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 12))

        # 2. Table Headers & Data Construction
        table_data = []

        if report.report_type == ReportType.TYPE_A:
            headers = [
                "Date", "Day", "Location", "Entry", "Exit", "Break",
                "Total", "100%", "125%", "150%", "Sabbatical"
            ]
        else:
            headers = ["Date", "Day", "Entry", "Exit", "Total Hours", "Notes"]

        table_data.append(headers)

        for row in report.rows:
            entry_str = row.entry_time.strftime("%H:%M") if row.entry_time else ""
            exit_str = row.exit_time.strftime("%H:%M") if row.exit_time else ""
            date_str = row.work_date.strftime("%d/%m/%Y")

            if report.report_type == ReportType.TYPE_A:
                break_str = (
                    row.break_duration.strftime("%H:%M")
                    if row.break_duration
                    else ""
                )
                table_data.append([
                    date_str, row.day_of_week, row.location or "",
                    entry_str, exit_str, break_str, str(row.total_hours),
                    str(row.hours_100), str(row.hours_125), str(row.hours_150),
                    str(row.hours_sabbatical)
                ])
            else:
                table_data.append([
                    date_str, row.day_of_week, entry_str, exit_str,
                    str(row.total_hours), row.notes or ""
                ])

        # 3. Create PDF Table & Styling
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

        # 4. Summary Section
        summary_text = (
            f"Monthly Summary: Total Days: {report.summary.total_days} | "
            f"Total Hours: {report.summary.total_hours}"
        )
        if report.summary.hourly_rate:
            summary_text += (
                f" | Hourly Rate: {report.summary.hourly_rate:.2f} | "
                f"Total Pay: {report.summary.total_payment:.2f}"
            )

        elements.append(Paragraph(summary_text, normal_style))

        # Build PDF
        doc.build(elements)
        return output_file