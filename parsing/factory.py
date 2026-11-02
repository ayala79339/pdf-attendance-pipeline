from domain.models import ReportType
from parsing.base_parser import BaseParser
from parsing.type_A_parser import TypeAParser
from parsing.type_B_parser import TypeBParser


class ParserFactory:
    """
    Factory class responsible for instantiating the appropriate BaseParser implementation.
    Follows the Factory Method design pattern to decouple caller code from concrete parsers.
    """

    @staticmethod
    def get_parser(report_type: ReportType) -> BaseParser:
        """
        Returns an instance of BaseParser for the given ReportType.
        :param report_type: The enum value indicating TYPE_A or TYPE_B.
        :return: BaseParser instance (TypeAParser or TypeBParser).
        :raises ValueError: If an unsupported report type is provided.
        """
        if report_type == ReportType.TYPE_A:
            return TypeAParser()
        elif report_type == ReportType.TYPE_B:
            return TypeBParser()

        raise ValueError(f"Unsupported report type for parsing: {report_type}")