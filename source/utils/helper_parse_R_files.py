import re

def extract_value(lines, pattern):
    """Return the text inside the first matched roxygen tag block."""
    pattern_roxygen = r"^\s*#'"
    pattern_any_tag = r"^\s*#'\s*@"

    matches = [idx for idx, line in enumerate(lines) if re.search(pattern, line)]
    if not matches:
        return ""

    start = matches[0]
    following = lines[start + 1 :]
    block_end = None

    for offset, line in enumerate(following, start=1):
        if re.match(pattern_roxygen, line) is None or re.match(pattern_any_tag, line):
            block_end = offset
            break

    continuation = following[: max(0, block_end - 1)] if block_end is not None else following
    value = " ".join([
        re.sub(pattern, "", lines[start]),
        *[re.sub(r"^\s*#'\s*", "", line) for line in continuation],
    ])
    return re.sub(r"\s+", " ", value).strip()


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
