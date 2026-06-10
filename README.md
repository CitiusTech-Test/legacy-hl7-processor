# Legacy HL7v2 Message Processor

A Python-based HL7v2 message parser and processor, representing the **"legacy"** side of healthcare system modernization. This project demonstrates how traditional healthcare data exchange works using the pipe-delimited HL7v2 standard — the format that modern FHIR-based systems are designed to replace.

## What is HL7v2?

HL7 Version 2 (HL7v2) is the most widely used healthcare messaging standard globally. Despite being decades old, it remains the backbone of most hospital system integrations. Messages are pipe-delimited (`|`) with segments like:

```
MSH|^~\&|EPIC|HOSPITAL_A|LAB|LAB_FAC|20240115||ADT^A01|MSG001|P|2.5
PID|1||MRN001||Doe^John||19850315|M
PV1|1|I|ICU^101^A
```

## Features

- **HL7v2 Parser** — Parses raw pipe-delimited messages into structured Python objects
- **ADT Handler** — Admit/Discharge/Transfer messages (A01–A11)
- **ORM Handler** — Order messages (lab, radiology, pharmacy orders)
- **ORU Handler** — Observation results (lab results, vitals)
- **CLI Tool** — Parse messages from files or stdin
- **Sample Messages** — Example HL7v2 messages for testing

## Quick Start

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Parse a sample message
python -m src.cli parse examples/adt_a01_admit.hl7

# Get message info
python -m src.cli info examples/oru_r01_lab_result.hl7

# Run tests
pytest tests/ -v
```

## Supported Message Types

| Type | Trigger | Description |
|------|---------|-------------|
| ADT  | A01     | Patient Admit |
| ADT  | A02     | Patient Transfer |
| ADT  | A03     | Patient Discharge |
| ADT  | A04     | Patient Registration |
| ADT  | A08     | Patient Update |
| ORM  | O01     | New Order |
| ORU  | R01     | Lab/Observation Results |

## Project Structure

```
legacy-hl7-processor/
├── src/
│   ├── parsers/
│   │   └── hl7_parser.py      # Core HL7v2 message parser
│   ├── handlers/
│   │   ├── base_handler.py     # Abstract handler interface
│   │   ├── adt_handler.py      # ADT message processing
│   │   ├── orm_handler.py      # Order message processing
│   │   └── oru_handler.py      # Result message processing
│   ├── processor.py            # Message routing & orchestration
│   └── cli.py                  # Command-line interface
├── examples/                   # Sample HL7v2 message files
├── tests/                      # Unit tests
└── requirements.txt
```

## Why This Matters

This project illustrates the challenges of the legacy HL7v2 approach:
- **Brittle parsing** — pipe-delimited format is error-prone and hard to validate
- **Implicit semantics** — field meaning depends on position, not self-describing
- **No standard API** — each integration requires custom point-to-point interfaces
- **Limited data types** — everything is essentially strings

These are the problems that modern FHIR-based systems solve. See the companion [fhir-integration-service](https://github.com/zolfran/fhir-integration-service) repo for the modern approach.

## Related Repos

- [healthcare-modernization](https://github.com/zolfran/healthcare-modernization) — Full-stack healthcare platform
- [fhir-integration-service](https://github.com/zolfran/fhir-integration-service) — FHIR R4 integration microservice
- [patient-portal](https://github.com/zolfran/patient-portal) — Patient-facing web app
- [clinical-analytics](https://github.com/zolfran/clinical-analytics) — Clinical analytics dashboard

## License

MIT
