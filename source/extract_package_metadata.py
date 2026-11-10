import csv
import json
import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "source") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "source"))

from utils.extract_package import extract_package


def main():
    if len(sys.argv) < 2:
        raise SystemExit("No arguments provided")

    input_package = sys.argv[1]

    config_path = PROJECT_ROOT / "config" / "metadata_fields.yml"
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    arch = config["architecture"]
    fields = {field["name"]: field for field in config["fields"]}
    value_fields = [name for name, field in fields.items() if field.get("extract") == "value"]

    input_file = PROJECT_ROOT / config["input"]["file"]
    with input_file.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=config["input"]["separator"]))

    datashield_functions = []
    for row in rows:
        name = (row.get("name") or "").strip()
        github_link = (row.get("github_link") or "").strip()
        if name != input_package or not github_link:
            continue
        try:
            package_functions = extract_package(name, github_link, fields, config["cache"]["dir"])
            if package_functions is None:
                continue
            datashield_functions.extend(package_functions)
        except Exception as exc:  # pragma: no cover - defensive path
            print(f"Failed on {name}: {exc}", file=sys.stderr)

    normalized = []
    for item in datashield_functions:
        function_name = item.get("function_name", "")
        architecture_name = "other"
        if re.search(arch["client_function_pattern"], function_name):
            architecture_name = "client"
        elif re.search(arch["server_function_pattern"], function_name):
            architecture_name = "server"

        exported = bool(item.get("exported", False))
        if exported:
            architecture_type = architecture_name
        elif architecture_name != "other":
            architecture_type = f"{architecture_name} (no export)"
        else:
            architecture_type = None

        if architecture_type is None:
            continue

        calls_assign = bool(item.get("calls_assign", False))
        calls_aggregate = bool(item.get("calls_aggregate", False))
        if calls_assign and calls_aggregate:
            function_type = "hybrid"
        elif calls_assign:
            function_type = "assign"
        elif calls_aggregate:
            function_type = "aggregate"
        else:
            function_type = "other"

        output_item = {
            "package": item.get("package"),
            "function_name": function_name,
            "architecture_type": architecture_type,
            "function_type": function_type,
        }
        for field_name in value_fields:
            output_item[field_name] = item.get(field_name)
        output_item["test_file"] = bool(item.get("test_file", False))
        normalized.append(output_item)

    normalized.sort(key=lambda item: (item["package"], item["function_name"]))
    print(json.dumps(normalized, ensure_ascii=False))


if __name__ == "__main__":
    main()
