from src.processor import HL7Processor


SAMPLE_ADT_A01 = (
    "MSH|^~\\&|EPIC|HOSPITAL_A|RCV|RCV_FAC|20240115103000||ADT^A01|MSG001|P|2.5\r"
    "PID|1||MRN001^^^HOSPITAL_A||Doe^John^A||19850315|M|||123 Oak St^^Springfield^IL^62701||555-1001\r"
    "PV1|1|I|ICU^101^A|||||||||||ADM|||||||||||||||||||||||||20240115103000"
)

SAMPLE_ORU_R01 = (
    "MSH|^~\\&|LAB|HOSP|EPIC|HOSP|20240116090000||ORU^R01|MSG003|P|2.5\r"
    "PID|1||MRN001^^^HOSP||Doe^John\r"
    "OBR|1|ORD001|FIL001|80053^CMP^CPT|||20240116080000\r"
    "OBX|1|NM|2339-0^Glucose^LN||95|mg/dL|74-106|N|||F\r"
    "OBX|2|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F"
)


def test_process_adt() -> None:
    proc = HL7Processor()
    result = proc.process(SAMPLE_ADT_A01)
    assert result["message_type"] == "ADT"
    assert result["action"] == "admit"
    assert result["patient"]["id"] == "MRN001"
    assert result["patient"]["name"] == "Doe, John"


def test_process_oru() -> None:
    proc = HL7Processor()
    result = proc.process(SAMPLE_ORU_R01)
    assert result["message_type"] == "ORU"
    assert len(result["observations"]) == 2
    assert result["observations"][0]["observation_value"] == "95"


def test_unsupported_type() -> None:
    raw = "MSH|^~\\&|APP|FAC|RCV|RF|20240101||ZZZ^Z01|MSG999|P|2.5\r"
    proc = HL7Processor()
    result = proc.process(raw)
    assert "error" in result
