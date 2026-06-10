"""CLI for processing HL7v2 messages from files or stdin."""

from __future__ import annotations

import json
import sys

import click

from src.processor import HL7Processor


@click.group()
def cli() -> None:
    """Legacy HL7v2 Message Processor — parse and process HL7v2 messages."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.option("--pretty/--compact", default=True, help="Pretty-print JSON output")
def parse(input_file: str | None, pretty: bool) -> None:
    """Parse an HL7v2 message file and output structured JSON."""
    if input_file:
        with open(input_file) as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    processor = HL7Processor()
    result = processor.process(raw)
    indent = 2 if pretty else None
    click.echo(json.dumps(result, indent=indent, default=str))


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def info(input_file: str) -> None:
    """Display summary information about an HL7v2 message."""
    with open(input_file) as f:
        raw = f.read()

    from src.parsers import HL7Parser
    parser = HL7Parser()
    msg = parser.parse(raw)

    click.echo(f"Message Type:    {msg.message_type}^{msg.message_trigger}")
    click.echo(f"Control ID:      {msg.message_control_id}")
    click.echo(f"HL7 Version:     {msg.version}")
    click.echo(f"Sending App:     {msg.sending_application}")
    click.echo(f"Sending Facility:{msg.sending_facility}")
    click.echo(f"Timestamp:       {msg.timestamp}")
    click.echo(f"Patient ID:      {msg.patient_id}")
    click.echo(f"Patient Name:    {msg.patient_name}")
    click.echo(f"Segments:        {', '.join(s.segment_type for s in msg.segments)}")


if __name__ == "__main__":
    cli()
