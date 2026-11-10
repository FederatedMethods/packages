import re

from .extract_value import extract_value


def extract_fields(file_path, fields):
    """Read an R file and extract configured metadata fields."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()

    values = {}
    for field_name, field in fields.items():
        extract_mode = field.get("extract", "")
        pattern = field.get("pattern")
        if extract_mode == "flag":
            values[field_name] = any(re.search(pattern, line) for line in lines)
        elif extract_mode == "value":
            values[field_name] = extract_value(lines, pattern)
        else:
            raise ValueError(f"Unsupported extraction type: {extract_mode!r}")
    return values
