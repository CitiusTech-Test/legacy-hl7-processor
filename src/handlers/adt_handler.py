"""
ADT (Admit/Discharge/Transfer) Message Handler

Handles HL7v2 ADT messages which track patient movement through a healthcare
facility. Common triggers:
  - A01: Patient Admit
  - A02: Patient Transfer
  - A03: Patient Discharge
  - A04: Patient Registration
  - A08: Patient Information Update
  - A11: Cancel Admit
"""

from __future__ import annotations

from src.handlers.base_handler import BaseHandler
from src.parsers.hl7_parser import HL7Message

ADT_TRIGGERS = {
    "A01": "admit",
    "A02": "transfer",
    "A03": "discharge",
    "A04": "registration",
    "A08": "update",
    "A11": "cancel_admit",
}


class ADTHandler(BaseHandler):
    def can_handle(self, message: HL7Message) -> bool:
        return message.message_type == "ADT"

    def handle(self, message: HL7Message) -> dict:
        self._log_processing(message)
        action = ADT_TRIGGERS.get(message.message_trigger, "unknown")

        pid = message.get_segment("PID")
        pv1 = message.get_segment("PV1")

        result: dict = {
            "message_type": "ADT",
            "trigger": message.message_trigger,
            "action": action,
            "control_id": message.message_control_id,
            "patient": {
                "id": message.patient_id,
                "name": message.patient_name,
                "dob": message.patient_dob,
                "gender": message.patient_gender,
                "phone": pid.get_field_value(13) if pid else "",
                "address": pid.get_field_value(11) if pid else "",
                "ssn": pid.get_field_value(19) if pid else "",
            },
            "visit": {},
        }

        if pv1:
            result["visit"] = {
                "patient_class": pv1.get_field_value(2),
                "assigned_location": pv1.get_field_value(3),
                "attending_doctor": pv1.get_field_value(7),
                "visit_number": pv1.get_field_value(19),
                "admit_datetime": pv1.get_field_value(44),
                "discharge_datetime": pv1.get_field_value(45),
            }

        return result
