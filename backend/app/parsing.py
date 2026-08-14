from __future__ import annotations

import re
from datetime import date, datetime

from app.models import Measurement, MenuItem

ALLERGY_PATTERN = re.compile(r"\((?P<codes>\d+(?:\.\d+)*)\)")
MEASUREMENT_PATTERN = re.compile(r"(?P<label>[^:]+)\s*:\s*(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z%㎉kcalgmg]+)")


def parse_ymd(value: str) -> date:
    return datetime.strptime(value, "%Y%m%d").date()


def format_ymd(value: date) -> str:
    return value.strftime("%Y%m%d")


def parse_menu(menu_text: str) -> list[MenuItem]:
    items: list[MenuItem] = []
    for raw_line in menu_text.split("<br/>"):
        line = raw_line.strip()
        if not line:
            continue
        allergy_codes: list[str] = []
        match = ALLERGY_PATTERN.search(line)
        if match:
            allergy_codes = [code for code in match.group("codes").split(".") if code]
            line = ALLERGY_PATTERN.sub("", line).strip()
        items.append(MenuItem(name=line or raw_line.strip(), allergyCodes=allergy_codes))
    return items


def parse_measurement(source_text: str, default_label: str) -> Measurement | None:
    match = MEASUREMENT_PATTERN.search(source_text.strip())
    if match is None:
        return None
    return Measurement(
        label=match.group("label").strip() or default_label,
        value=float(match.group("value")),
        unit=match.group("unit").strip(),
        sourceText=source_text.strip(),
    )


def parse_nutrients(source_text: str) -> tuple[list[Measurement], str | None]:
    measurements: list[Measurement] = []
    for part in [item.strip() for item in source_text.split("<br/>") if item.strip()]:
        measurement = parse_measurement(part, "영양소")
        if measurement is not None:
            measurements.append(measurement)
    return measurements, source_text.strip() or None
