from src.parsers.hl7_parser import HL7Parser


SAMPLE_ADT = (
    "MSH|^~\\&|EPIC|HOSPITAL_A|RCV|RCV_FAC|20240115103000||ADT^A01|MSG001|P|2.5\r"
    "PID|1||MRN001^^^HOSPITAL_A||Doe^John^A||19850315|M\r"
    "PV1|1|I|ICU^101^A"
)


def test_parse_segments() -> None:
    parser = HL7Parser()
    msg = parser.parse(SAMPLE_ADT)
    segment_types = [s.segment_type for s in msg.segments]
    assert segment_types == ["MSH", "PID", "PV1"]


def test_message_type() -> None:
    parser = HL7Parser()
    msg = parser.parse(SAMPLE_ADT)
    assert msg.message_type == "ADT"
    assert msg.message_trigger == "A01"


def test_patient_info() -> None:
    parser = HL7Parser()
    msg = parser.parse(SAMPLE_ADT)
    assert msg.patient_id == "MRN001"
    assert msg.patient_name == "Doe, John"
    assert msg.patient_dob == "19850315"
    assert msg.patient_gender == "M"


def test_header_fields() -> None:
    parser = HL7Parser()
    msg = parser.parse(SAMPLE_ADT)
    assert msg.sending_application == "EPIC"
    assert msg.sending_facility == "HOSPITAL_A"
    assert msg.version == "2.5"
    assert msg.message_control_id == "MSG001"
