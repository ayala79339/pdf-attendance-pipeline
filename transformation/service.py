from domain.models import AttendanceReport, ReportType
from transformation.type_A_strategy import TypeATransformationStrategy
from transformation.type_B_strategy import TypeBTransformationStrategy


class TransformationService:

    def __init__(self):
        self._strategies = {
            ReportType.TYPE_A: TypeATransformationStrategy(),
            ReportType.TYPE_B: TypeBTransformationStrategy(),
        }

    def transform(
        self, report: AttendanceReport, seed: int = 42
    ) -> AttendanceReport:
        strategy = self._strategies.get(report.report_type)
        if not strategy:
            raise ValueError(
                f"No transformation strategy found for type: {report.report_type}"
            )

        return strategy.transform_report(report, seed=seed)