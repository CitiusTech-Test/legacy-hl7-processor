"""Base handler for HL7v2 message processing."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from src.parsers.hl7_parser import HL7Message

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Abstract base for HL7v2 message handlers."""

    @abstractmethod
    def can_handle(self, message: HL7Message) -> bool:
        ...

    @abstractmethod
    def handle(self, message: HL7Message) -> dict:
        ...

    def _log_processing(self, message: HL7Message) -> None:
        logger.info(
            "Processing %s^%s (control_id=%s)",
            message.message_type,
            message.message_trigger,
            message.message_control_id,
        )
