from abc import ABC, abstractmethod
from domain.models import AttendanceReport, AttendanceRow, ReportSummary, ReportType


class BaseParser(ABC):
    """
    Abstract base class for all report parsers.
    Implements the Template Method pattern to define the parsing flow.
    """

    def __init__(self, report_type: ReportType):
        """
        Initializes the parser with its specific report type.

        :param report_type: ReportType enum indicating TYPE_A or TYPE_B.
        """
        self.report_type = report_type

    def parse(self, raw_text: str) -> AttendanceReport:
        """
        Template method defining the skeleton of the parsing algorithm.

        :param raw_text: Raw string output from OCR.
        :return: AttendanceReport domain object.
        """
        cleaned_text = self._clean_text(raw_text)
        lines = cleaned_text.splitlines()

        employee_name = self._parse_employee_name(lines)
        summary = self._parse_summary(lines)

        rows = []
        for line in lines:
            if self._is_row_line(line):
                parsed_row = self._parse_row(line)
                if parsed_row:
                    rows.append(parsed_row)

        return AttendanceReport(
            report_type=self.report_type,
            employee_name=employee_name,
            rows=rows,
            summary=summary,
        )

    def _clean_text(self, text: str) -> str:
        """
        Shared utility method to clean raw OCR text noises.

        :param text: Raw input string.
        :return: Cleaned string with standardized characters.
        """
        # Standardize OCR pipe artifacts and remove extra whitespace
        text = text.replace("│", "|").replace("I", "|")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    @abstractmethod
    def _parse_employee_name(self, lines: list[str]) -> str:
        """Abstract method: Extracts the employee name from header lines."""
        pass

    @abstractmethod
    def _parse_summary(self, lines: list[str]) -> ReportSummary:
        """Abstract method: Extracts the summary metadata table."""
        pass

    @abstractmethod
    def _is_row_line(self, line: str) -> bool:
        """Abstract method: Determines if a given text line represents a valid data row."""
        pass

    @abstractmethod
    def _parse_row(self, line: str) -> AttendanceRow | None:
        """Abstract method: Parses a single text line into an AttendanceRow object."""
        pass