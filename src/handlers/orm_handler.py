"""
ORM (Order) Message Handler

Handles HL7v2 ORM messages for clinical orders (lab tests, radiology, etc.).
Common triggers:
  - O01: Order Message
"""

from __future__ import annotations

from src.handlers.base_handler import BaseHandler
from src.parsers.hl7_parser import HL7Message


class ORMHandler(BaseHandler):
    def can_handle(self, message: HL7Message) -> bool:
        return message.message_type == "ORM"

    def handle(self, message: HL7Message) -> dict:
        self._log_processing(message)

        orders = []
        for orc in message.get_segments("ORC"):
            obr_segments = message.get_segments("OBR")
            obr = obr_segments[0] if obr_segments else None

            order: dict = {
                "order_control": orc.get_field_value(1),
                "placer_order_number": orc.get_field_value(2),
                "filler_order_number": orc.get_field_value(3),
                "order_status": orc.get_field_value(5),
                "ordering_provider": orc.get_field_value(12),
                "order_datetime": orc.get_field_value(9),
            }

            if obr:
                order["test"] = {
                    "universal_service_id": obr.get_field_value(4),
                    "priority": obr.get_field_value(5),
                    "requested_datetime": obr.get_field_value(6),
                    "observation_datetime": obr.get_field_value(7),
                    "specimen_source": obr.get_field_value(15),
                    "clinical_info": obr.get_field_value(13),
                }

            orders.append(order)

        return {
            "message_type": "ORM",
            "trigger": message.message_trigger,
            "control_id": message.message_control_id,
            "patient": {
                "id": message.patient_id,
                "name": message.patient_name,
            },
            "orders": orders,
        }
