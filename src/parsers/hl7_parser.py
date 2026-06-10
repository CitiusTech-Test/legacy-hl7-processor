"""
HL7v2 Message Parser

Parses pipe-delimited HL7v2 messages (the legacy standard for healthcare data
exchange) into structured Python objects. Supports ADT, ORM, ORU, and SIU
message types.

HL7v2 message structure:
  - Messages are composed of segments separated by \\r
  - Segments are composed of fields separated by |
  - Fields can contain components separated by ^
  - Components can contain sub-components separated by &
  - Fields can repeat, separated by ~

Field numbering follows the HL7 standard (1-based). For MSH, field 1 is the
field separator character itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HL7Field:
    """A single HL7 field, potentially with components and repetitions."""

    raw: str
    components: list[str] = field(default_factory=list)
    repetitions: list[list[str]] = field(default_factory=list)

    def __str__(self) -> str:
        return self.raw

    @property
    def value(self) -> str:
        return self.components[0] if self.components else self.raw


@dataclass
class HL7Segment:
    """A single HL7 segment (e.g., MSH, PID, PV1).

    Field access uses HL7 standard 1-based numbering.
    """

    segment_type: str
    fields: list[HL7Field]
    raw: str

    def get_field(self, index: int) -> HL7Field | None:
        """Get field by 1-based HL7 field number."""
        idx = index - 1
        if 0 <= idx < len(self.fields):
            return self.fields[idx]
        return None

    def get_field_value(self, index: int, component: int = 0) -> str:
        """Get field value by 1-based HL7 field number."""
        f = self.get_field(index)
        if f is None:
            return ""
        if component == 0:
            return f.value
        if component < len(f.components):
            return f.components[component]
        return ""


@dataclass
class HL7Message:
    """A parsed HL7v2 message."""

    raw: str
    segments: list[HL7Segment]
    message_type: str = ""
    message_trigger: str = ""
    message_control_id: str = ""
    sending_application: str = ""
    sending_facility: str = ""
    receiving_application: str = ""
    receiving_facility: str = ""
    timestamp: str = ""
    version: str = ""

    def get_segments(self, segment_type: str) -> list[HL7Segment]:
        return [s for s in self.segments if s.segment_type == segment_type]

    def get_segment(self, segment_type: str) -> HL7Segment | None:
        segs = self.get_segments(segment_type)
        return segs[0] if segs else None

    @property
    def patient_id(self) -> str:
        pid = self.get_segment("PID")
        return pid.get_field_value(3) if pid else ""

    @property
    def patient_name(self) -> str:
        pid = self.get_segment("PID")
        if not pid:
            return ""
        name_field = pid.get_field(5)
        if not name_field:
            return ""
        last = name_field.components[0] if len(name_field.components) > 0 else ""
        first = name_field.components[1] if len(name_field.components) > 1 else ""
        return f"{last}, {first}" if first else last

    @property
    def patient_dob(self) -> str:
        pid = self.get_segment("PID")
        return pid.get_field_value(7) if pid else ""

    @property
    def patient_gender(self) -> str:
        pid = self.get_segment("PID")
        return pid.get_field_value(8) if pid else ""


class HL7Parser:
    """Parses raw HL7v2 message strings into HL7Message objects."""

    FIELD_SEP = "|"
    COMPONENT_SEP = "^"
    REPEAT_SEP = "~"
    ESCAPE_CHAR = "\\"
    SUBCOMPONENT_SEP = "&"

    def parse(self, raw_message: str) -> HL7Message:
        raw_message = raw_message.strip()
        lines = raw_message.replace("\r\n", "\r").replace("\n", "\r").split("\r")
        lines = [line for line in lines if line.strip()]

        segments: list[HL7Segment] = []
        for line in lines:
            segment = self._parse_segment(line)
            if segment:
                segments.append(segment)

        msg = HL7Message(raw=raw_message, segments=segments)
        self._extract_header(msg)
        return msg

    def _parse_segment(self, line: str) -> HL7Segment | None:
        if len(line) < 3:
            return None

        parts = line.split(self.FIELD_SEP)
        segment_type = parts[0]

        fields: list[HL7Field] = []

        # For MSH, field 1 is the separator character itself — add a placeholder
        # so that 1-based indexing aligns with the HL7 standard.
        if segment_type == "MSH":
            fields.append(HL7Field(raw=self.FIELD_SEP, components=[self.FIELD_SEP]))

        for raw_field in parts[1:]:
            components = raw_field.split(self.COMPONENT_SEP)
            repetitions: list[list[str]] = []
            if self.REPEAT_SEP in raw_field:
                repetitions = [
                    rep.split(self.COMPONENT_SEP)
                    for rep in raw_field.split(self.REPEAT_SEP)
                ]
            fields.append(
                HL7Field(raw=raw_field, components=components, repetitions=repetitions)
            )

        return HL7Segment(segment_type=segment_type, fields=fields, raw=line)

    def _extract_header(self, msg: HL7Message) -> None:
        msh = msg.get_segment("MSH")
        if not msh:
            return

        msg.sending_application = msh.get_field_value(3)
        msg.sending_facility = msh.get_field_value(4)
        msg.receiving_application = msh.get_field_value(5)
        msg.receiving_facility = msh.get_field_value(6)
        msg.timestamp = msh.get_field_value(7)
        msg.message_control_id = msh.get_field_value(10)
        msg.version = msh.get_field_value(12)

        msg_type_field = msh.get_field(9)
        if msg_type_field:
            msg.message_type = msg_type_field.components[0] if len(msg_type_field.components) > 0 else ""
            msg.message_trigger = msg_type_field.components[1] if len(msg_type_field.components) > 1 else ""
