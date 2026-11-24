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

    values["lines_of_code"] = sum(1 for line in lines)
    
    return values

def parse_roxygen_blocks(r_source: str) -> list[dict]:
    """Extract all #' roxygen blocks (including arbitrary custom @tags) from an R file."""
    # Remove empty lines before parsing so blank lines inside or after a roxygen header don't matter
    lines = [line for line in r_source.splitlines() if line.strip()]
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("#'"):
            comment_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("#'"):
                comment_lines.append(re.sub(r"^\s*#'\s?", "", lines[i]))
                i += 1
            
            # Grab the function name from the next line of code. Skip blank lines and plain
            # "#" comment lines (e.g. separator lines like #~~~~) that sit between the #' block
            # and the function definition. A new #' block means this block has no function.
            while i < len(lines):
                stripped = lines[i].strip()
                if not stripped or (stripped.startswith("#") and not stripped.startswith("#'")):
                    i += 1
                else:
                    break
            fn_match = re.match(r"^\s*([`.\w]+)\s*(?:<-|=)\s*function\b", lines[i]) if i < len(lines) else None
            fn_name = fn_match.group(1).strip("`") if fn_match else None
            # Split comment lines into raw @tag -> [values]
            tags = {}
            current_tag = "_intro"  # title/description before the first @tag
            buf = []
            for cl in comment_lines:
                m = re.match(r"^@([A-Za-z][A-Za-z0-9_]*)\b\s*(.*)", cl)
                if m:
                    if buf:
                        tags.setdefault(current_tag, []).append("\n".join(buf).strip())
                    current_tag, buf = m.group(1), [m.group(2)]
                else:
                    buf.append(cl)
            if buf:
                tags.setdefault(current_tag, []).append("\n".join(buf).strip())
            blocks.append({"function": fn_name, "tags": tags})
        else:
            i += 1
    return blocks
