import subprocess
from pathlib import Path
from warnings import warn

from .extract_fields import extract_fields


def extract_package(name, github_link, fields, cache_dir):
    """Clone a package repo and extract metadata for its R files."""
    print(f"Extracting {name}")

    repo_path = Path(cache_dir) / name
    if not repo_path.exists():
        result = subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1", github_link, str(repo_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            warn(f"Could not clone {github_link}, skipping {name}")
            return None

    tests_dir = repo_path / "tests" / "testthat"
    test_files = []
    if tests_dir.exists():
        test_files = [path.name for path in tests_dir.iterdir() if path.is_file()]

    r_dir = repo_path / "R"
    package_files = []
    if r_dir.exists():
        package_files = sorted(
            path for path in r_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".r", ".R"}
        )

    description_path = repo_path / "DESCRIPTION"
    package_name = name
    if description_path.exists():
        with description_path.open("r", encoding="utf-8", errors="replace") as handle:
            contents = handle.read().splitlines()
        for line in contents:
            if line.startswith("Package:"):
                package_name = line.split(":", 1)[1].strip()
                break

    rows = []
    for file_path in package_files:
        function_name = file_path.stem
        test_file = any(function_name in test_file_name for test_file_name in test_files)
        metadata = extract_fields(str(file_path), fields)
        row = {
            "file": str(file_path),
            "package": package_name,
            "function_name": function_name,
            "test_file": test_file,
            **metadata,
        }
        rows.append(row)

    return rows
