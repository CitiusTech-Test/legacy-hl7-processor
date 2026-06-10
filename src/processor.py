"""
HL7v2 Message Processor

Routes incoming HL7v2 messages to the appropriate handler based on message type.
This is the main entry point for processing messages from legacy healthcare systems.
"""

from __future__ import annotations

import json
import logging

from src.handlers.adt_handler import ADTHandler
from src.handlers.base_handler import BaseHandler
from src.handlers.orm_handler import ORMHandler
from src.handlers.oru_handler import ORUHandler
from src.parsers.hl7_parser import HL7Message, HL7Parser

logger = logging.getLogger(__name__)


class HL7Processor:
    """Routes HL7v2 messages to registered handlers."""

    def __init__(self) -> None:
        self.parser = HL7Parser()
        self.handlers: list[BaseHandler] = [
            ADTHandler(),
            ORMHandler(),
            ORUHandler(),
        ]

    def process(self, raw_message: str) -> dict:
        message = self.parser.parse(raw_message)
        logger.info(
            "Received %s^%s from %s/%s",
            message.message_type,
            message.message_trigger,
            message.sending_application,
            message.sending_facility,
        )

        for handler in self.handlers:
            if handler.can_handle(message):
                return handler.handle(message)

        logger.warning(
            "No handler for message type: %s^%s",
            message.message_type,
            message.message_trigger,
        )
        return {
            "message_type": message.message_type,
            "trigger": message.message_trigger,
            "error": "Unsupported message type",
            "raw_segments": [s.segment_type for s in message.segments],
        }

    def process_batch(self, raw_messages: list[str]) -> list[dict]:
        results = []
        for i, msg in enumerate(raw_messages):
            try:
                result = self.process(msg)
                results.append(result)
            except Exception as e:
                logger.error("Failed to process message %d: %s", i, e)
                results.append({"error": str(e), "message_index": i})
        return results

    def process_to_json(self, raw_message: str, indent: int = 2) -> str:
        result = self.process(raw_message)
        return json.dumps(result, indent=indent, default=str)
