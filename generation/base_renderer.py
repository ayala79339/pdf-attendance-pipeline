from abc import ABC, abstractmethod
from pathlib import Path
from domain.models import AttendanceReport


class BaseRenderer(ABC):
    """
    Abstract Base Class for all report renderers (PDF, Excel, HTML).
    Implements the Strategy / Renderer pattern for output generation.
    """

    @abstractmethod
    def render(self, report: AttendanceReport, output_path: Path) -> Path:
        """
        Renders an AttendanceReport domain object into a file on disk.

        :param report: The transformed AttendanceReport object.
        :param output_path: Path where the generated output file should be saved.
        :return: Path to the generated output file.
        """
        pass