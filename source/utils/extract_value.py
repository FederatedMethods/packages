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
