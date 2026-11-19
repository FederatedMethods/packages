"""
Function to generate an HTML page listing DataSHIELD package functions and their metadata.
Olly Butters
18/11/2026
"""

import datetime
import html
import json
import os
from pathlib import Path
from pprint import pprint
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_html_utils.navbar import get_navbar

def format_metadata_value(value, default = '-'):
    """Format a metadata value for safe display in an HTML table cell."""
    if value is None:
        return default
    if isinstance(value, bool):
        return str(value)
    text = str(value).strip()
    if not text:
        return default
    return html.escape(text)


def main(packages_file_path = './output/metadata/packages.json', html_file_path = './output/html/functions.html'):
    """
    Main function to generate an HTML page listing DataSHIELD functions per package.
    This function processes package and function metadata from a JSON file,
    and generates an HTML page with one section and function table per package.
    Args:
        packages_file_path (str): Path to the JSON file containing package information.
        html_file_path (str): Path to the output HTML file to be generated.
    """

    print(f"Current working directory: {os.getcwd()}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(html_file_path) or "output/html"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(packages_file_path, 'r', encoding='utf-8') as packages_file:
        packages = json.load(packages_file)

    # Count packages and functions, and check whether 'exported' metadata is present
    number_of_packages = len(packages)
    number_of_functions = 0
    include_exported = False

    for package_info in packages.values():
        repo_info = package_info.get('repo', {})
        if isinstance(repo_info, dict):
            function_info = repo_info.get('function_info')
            if isinstance(function_info, list):
                number_of_functions += len(function_info)
                if not include_exported:
                    include_exported = any(
                        isinstance(func, dict) and 'exported' in func
                        for func in function_info
                    )

    # Generate the HTML page
    with open(html_file_path, 'w', encoding='utf-8') as html_file:

        # Put html together for this page
        head = '<!DOCTYPE html><html lang="en-GB">'
        head += '<head>'
        head += '<title>DataSHIELD community package functions</title>'
        head += '<meta charset="UTF-8">'
        head += '<link rel="stylesheet" href="./style_main.css">'
        head += '</head>'
        head += '<body>' + get_navbar('functions.html')

        html_file.write(head)

        top_content = '<div class="top-content" id="top">'
        top_content += '<h1>DataSHIELD community package functions</h1><a href="#top"></a>'
        top_content += '<p>This page lists all the functions and their metadata for packages that have been developed in the <a href="https://www.datashield.org">DataSHIELD</a> community. It includes packages that are in production, in development, retired, and unknown status. More info is in the <a href="./faq.html">FAQ</a>. If you want to find a specific type of analysis then just search on this page (Ctrl+F) for some relevant keywords.</p>'

        html_file.write(top_content)

        stats = f'<p>There are {number_of_packages} packages and {number_of_functions} functions listed on these pages.</p></div>'
        html_file.write(stats)

        for this_package_name, this_package_info in packages.items():
            try:
                print(f"Processing package: {this_package_name}")
                pprint(this_package_info)

                escaped_package_name = html.escape(this_package_name)
                html_content = f'\n<h2 id="{escaped_package_name}"><a href="#{escaped_package_name}">{escaped_package_name}</a></h2>\n'

                repo_info = this_package_info.get('repo', {})
                function_info = repo_info.get('function_info') if isinstance(repo_info, dict) else None

                if function_info == 'Error':
                    html_content += '<p>Error retrieving function metadata for this package.</p>\n'
                elif isinstance(function_info, list) and len(function_info) > 0:
                    html_content += '<table>\n'
                    html_content += '<tr>'
                    html_content += '<th>Function name</th>'
                    html_content += '<th>Title</th>'
                    html_content += '<th>Description</th>'
                    html_content += '</tr>\n'

                    for func in function_info:
                        if not isinstance(func, dict):
                            continue

                        function_name = format_metadata_value(func.get('function_name'))
                        title = format_metadata_value(func.get('title'))
                        description = format_metadata_value(func.get('description'))

                        html_content += '<tr>'
                        html_content += f'<td class="left">{function_name}</td>'
                        html_content += f'<td class="left">{title}</td>'
                        html_content += f'<td class="left">{description}</td>'
                        html_content += '</tr>\n'

                    html_content += '</table>\n'
                else:
                    html_content += '<p>No functions listed.</p>\n'

                html_content += '<p style="text-align:right"><a href="#top">Jump to top of page</a></p>\n'

                html_file.write(html_content)
            except Exception as e:
                print(f"Error processing package {this_package_name}: {e}")
                continue

        # Footer
        html_file.write('<hr/>')
        html_file.write('Generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_file.write('&nbsp;&nbsp;Made by the <a href="https://github.com/FederatedMethods" target="_blank">Federated Methods team</a>')

        html_file.write('</body>\n</html>')


if __name__ == '__main__':
    main('./output/metadata/packages.json', './output/html/functions.html')
    shutil.copy('source/build_html_utils/static_html_files/style_main.css', './output/html/style_main.css')
