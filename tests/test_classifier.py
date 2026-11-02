import pytest
from domain.models import ReportType
from parsing.classifier import ReportClassifier


def test_classify_type_a():
    classifier = ReportClassifier()
    sample_text_a = "חברת נ.ע. הנשר בע\"מ \n שעות % 100 \n שעות % 125 \n הפסיקה"
    assert classifier.classify(sample_text_a) == ReportType.TYPE_A


def test_classify_type_b():
    classifier = ReportClassifier()
    sample_text_b = "כרטיס עובד לחודש \n מחיר לשעה \n סה\"כ לתשלום"
    assert classifier.classify(sample_text_b) == ReportType.TYPE_B


def test_classify_unknown_raises_value_error():
    classifier = ReportClassifier()
    unknown_text = "טקסט רנדומלי ללא מילות מפתח"
    with pytest.raises(ValueError):
        classifier.classify(unknown_text)