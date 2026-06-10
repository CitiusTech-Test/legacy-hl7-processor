"""
ORU (Observation Result) Message Handler

Handles HL7v2 ORU messages containing clinical results (lab results, vitals, etc.).
Common triggers:
  - R01: Unsolicited Observation Result
"""

from __future__ import annotations

from src.handlers.base_handler import BaseHandler
from src.parsers.hl7_parser import HL7Message


class ORUHandler(BaseHandler):
    def can_handle(self, message: HL7Message) -> bool:
        return message.message_type == "ORU"

    def handle(self, message: HL7Message) -> dict:
        self._log_processing(message)

        observations = []
        for obx in message.get_segments("OBX"):
            obs: dict = {
                "set_id": obx.get_field_value(1),
                "value_type": obx.get_field_value(2),
                "observation_id": obx.get_field_value(3),
                "observation_value": obx.get_field_value(5),
                "units": obx.get_field_value(6),
                "reference_range": obx.get_field_value(7),
                "abnormal_flags": obx.get_field_value(8),
                "observation_status": obx.get_field_value(11),
                "observation_datetime": obx.get_field_value(14),
            }
            observations.append(obs)

        obr = message.get_segment("OBR")
        test_info = {}
        if obr:
            test_info = {
                "universal_service_id": obr.get_field_value(4),
                "observation_datetime": obr.get_field_value(7),
                "result_status": obr.get_field_value(25),
            }

        return {
            "message_type": "ORU",
            "trigger": message.message_trigger,
            "control_id": message.message_control_id,
            "patient": {
                "id": message.patient_id,
                "name": message.patient_name,
            },
            "test": test_info,
            "observations": observations,
        }
