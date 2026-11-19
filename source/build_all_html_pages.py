"""
Build all of the HTML pages (summary, long packages page, functions page)
and copy the static files (CSS and FAQ) into the output directory.
Run from the repository root: python3 source/build_all_pages.py
"""

import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "source"
STATIC_DIR = SOURCE_DIR / "build_html_utils" / "static_html_files"

sys.path.insert(0, str(SOURCE_DIR))

from build_html_utils import build_packages_summary_page
from build_html_utils import build_packages_long_page
from build_html_utils import build_functions_page
from build_html_utils import build_stats_page

# Static files copied into the HTML output directory
STATIC_FILES = ["style_main.css", "faq.html"]


def main(packages_file_path='./output/metadata/packages.json', html_dir='./output/html'):
    """
    Build every HTML page and copy the static CSS and FAQ files.
    Args:
        packages_file_path (str): Path to the packages JSON file.
        html_dir (str): Directory the HTML output is written to.
    """
    # Paths in the individual scripts are relative to the repo root
    os.chdir(PROJECT_ROOT)
    os.makedirs(html_dir, exist_ok=True)

    # Static files
    for filename in STATIC_FILES:
        shutil.copy(STATIC_DIR / filename, Path(html_dir) / filename)
        print(f"Copied {filename} to {html_dir}")

    # Pages
    build_packages_summary_page.main(packages_file_path, f'{html_dir}/index.html')
    build_packages_long_page.main(packages_file_path, f'{html_dir}/packages.html')
    build_functions_page.main(packages_file_path, f'{html_dir}/functions.html')
    build_stats_page.main(packages_file_path, f'{html_dir}/stats.html')

    print("All pages built.")


if __name__ == '__main__':
    main()
