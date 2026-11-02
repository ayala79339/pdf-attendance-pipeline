from abc import ABC, abstractmethod
import random
from domain.models import AttendanceReport, AttendanceRow


class BaseTransformationStrategy(ABC):
    """
    Abstract Base Class for transformation strategies.
    Implements the Strategy Design Pattern.
    """

    @abstractmethod
    def transform_report(
        self, report: AttendanceReport, seed: int = 42
    ) -> AttendanceReport:
        """
        Transforms an entire AttendanceReport deterministically using a fixed random seed.

        :param report: The original AttendanceReport domain object.
        :param seed: Integer seed ensuring reproducible variation generation.
        :return: A brand new AttendanceReport instance with transformed values.
        """
        pass

    def _shift_time_minutes(
        self, original_time, minute_delta: int
    ):
        """
        Helper method to add/subtract minutes from a datetime.time object safely.
        """
        if original_time is None:
            return None

        total_minutes = original_time.hour * 60 + original_time.minute + minute_delta
        # Keep within a valid 24-hour boundary (0 to 1439 minutes)
        total_minutes = max(0, min(1439, total_minutes))

        new_hour = total_minutes // 60
        new_minute = total_minutes % 60
        return original_time.replace(hour=new_hour, minute=new_minute)