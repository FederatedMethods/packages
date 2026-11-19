import os
import re
import sys
from pathlib import Path
import yaml
from .helper_parse_R_files import extract_fields

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT / "source") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "source"))


def parse_R_files(package_name=None, github_link_end_part=None):

    # Load configuration
    config_path = PROJECT_ROOT / "config" / "metadata_fields.yml"
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    # Extract configuration values
    arch = config["architecture"]
    fields = {field["name"]: field for field in config["fields"]}

    # Get the list of R files in the package's R directory
    r_dir = github_link_end_part + "/R"
    package_r_files = []
    if os.path.exists(r_dir):
        package_r_files = sorted(
            path for path in os.listdir(r_dir)
            if os.path.isfile(os.path.join(r_dir, path)) and os.path.splitext(path)[1].lower() in {".r", ".R"}
        )

    # Get the list of test files in the package's tests/testthat directory
    tests_dir = github_link_end_part + "/tests/testthat"
    test_files = []
    if os.path.exists(tests_dir):
        test_files = [path for path in os.listdir(tests_dir) if os.path.isfile(os.path.join(tests_dir, path))]

    functions_metadata = []
    for this_r_file in package_r_files:

        print(f"Extracting metadata from {this_r_file} in package {package_name}")
        # Extract metadata from each R file according to the specified fields in the config file
        function_name = os.path.basename(this_r_file)
        test_file = any(function_name in test_file_name for test_file_name in test_files)
        metadata = extract_fields(str(github_link_end_part + "/R/" + this_r_file), fields)
        row = {
            "file": str(github_link_end_part + "/R/" + this_r_file),
            "package": package_name,
            "function_name": function_name,
            "test_file": test_file,
            **metadata,
        }

        architecture_type = "other"
        if re.search(arch["client_function_pattern"], function_name):
            architecture_type = "client"
        elif re.search(arch["server_function_pattern"], function_name):
            architecture_type = "server"

        row["architecture_type"] = architecture_type


        calls_assign = bool(row.get("calls_assign", False))
        calls_aggregate = bool(row.get("calls_aggregate", False))
        if calls_assign and calls_aggregate:
            function_type = "hybrid"
        elif calls_assign:
            function_type = "assign"
        elif calls_aggregate:
            function_type = "aggregate"
        else:
            function_type = "other"

        row["function_type"] = function_type

        functions_metadata.append(row)

    return functions_metadata


if __name__ == "__main__":
    parse_R_files("dsAnalysis", "dsAnalysis")
