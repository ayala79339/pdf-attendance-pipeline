from domain.models import ReportType
from parsing.factory import ParserFactory


def test_type_a_parser_row():
    parser = ParserFactory.get_parser(ReportType.TYPE_A)
    raw_row = "01/09/2022 | חמישי | גליליון | 08:00 | 16:30 | 00:30 | 8.00 | 8.00 | 0.00 | 0.00 | 0.00"

    assert parser._is_row_line(raw_row) is True
    parsed = parser._parse_row(raw_row)

    assert parsed is not None
    assert parsed.work_date.strftime("%d/%m/%Y") == "01/09/2022"
    assert parsed.total_hours == 8.00
    assert parsed.hours_100 == 8.00


def test_type_b_parser_row():
    parser = ParserFactory.get_parser(ReportType.TYPE_B)
    raw_row = "1/9/22 | ה | 08:00 | 16:00 | 8.00 | עבודה רגילה"

    assert parser._is_row_line(raw_row) is True
    parsed = parser._parse_row(raw_row)

    assert parsed is not None
    assert parsed.total_hours == 8.00
    assert parsed.notes == "עבודה רגילה"