"""
Function to generate an HTML summary page listing DataSHIELD packages.
Olly Butters
5/8/2026
"""

import datetime
import json
import shutil
import os
from pprint import pprint

def main(packages_file_path = './output/metadata/packages.json', html_file_path = './output/html/index.html'):
    """
    Main function to generate an HTML summary page listing DataSHIELD packages.
    This function processes package information from a JSON file generated in process_packages.py,
    and generates an HTML page summarizing the information.
    Args:
        packages_file_path (str): Path to the JSON file containing package information.
        html_file_path (str): Path to the output HTML file to be generated.
    """
    print(f"Current working directory: {os.getcwd()}")

    if not os.path.exists("output/html"):
        os.makedirs("output/html")

    with open(packages_file_path, 'r', encoding='utf-8') as packages_file:
        packages = json.load(packages_file)

    # Count the number of functions to include in the stats.
    # This is not a particularly accurate way to count as it's derived from the
    # NAMESPACE file, but some packages have a wild card inclusion not an explicit list.
    number_of_packages = len(packages)
    number_of_functions = 0
    for package_name, package_info in packages.items():
        if 'repo' in package_info and 'functions' in package_info['repo']:
            functions = package_info['repo']['functions']
            if functions is not None:
                number_of_functions += len(functions)

    with open(html_file_path, 'w', encoding='utf-8') as html_file:

        # Put html together for this page
        head = '<!DOCTYPE html><html lang="en-GB">'
        head += '<head>'
        head += '<title>DataSHIELD packages</title>'
        head += '<meta charset="UTF-8">'
        head += '<link rel="stylesheet" href="./style_main.css">'
        head += '</head>'
        head += '<body>'

        html_file.write(head)

        top_content = '<div class="top-content">'
        top_content += '<h1>DataSHIELD packages</h1>'
        top_content += '<p>This page lists all the packages that have been developed in the <a href="https://www.datashield.org">DataSHIELD</a> ecosystem. It includes packages that are in production, in development, retired, and unknown status. More info is in the <a href="./faq.html">FAQ</a>.</p>'

        html_file.write(top_content)

        stats = f'<p>There are {number_of_packages} packages and {number_of_functions} functions listed on these pages.</p>'
        html_file.write(stats)

        html_file.write('<table border="1">\n')

        html_file.write('<tr><td></td>')
        html_file.write('<th>Name</th>')
        html_file.write('<th>Description</th>')
        html_file.write('<th>CRAN version</th>')
        html_file.write('<th>CRAN license</th>')
        html_file.write('<th>GitHub last update</th>')
        html_file.write('<th>GitHub version</th>')
        html_file.write('<th>GitHub license</th>')
        html_file.write('<th>GitHub owner</th>')
        html_file.write('</tr>')

        production_rows = ""
        development_rows = ""
        retired_rows = ""
        unknown_rows = ""

        # Counts for each rows
        production_rows_count = 1
        development_rows_count = 1
        retired_rows_count = 1
        unknown_rows_count = 1

        #for row in package_list:
        for this_package_name, this_package_info in packages.items():
            print(f"######\nProcessing package: {this_package_name}")
            pprint(this_package_info)
            this_row = ""

            # Add anchor
            this_row += '<td class="left"><a href="packages.html#' + this_package_name + '">' + this_package_name + '</a></td>'

            # Description
            if len(this_package_info['input']['description']) > 0:
                this_row += '<td class="left">' + this_package_info['input']['description'] + '</td>'
            else:
                this_row += '<td></td>'

            # CRAN version with link
            if len(this_package_info['input'].get('cran_link')) > 0:
                this_row += '<td><a href="' + this_package_info['input']['cran_link'] + '" target="blank">' + this_package_info['cran']['version'] + '</a></td>'
            else:
                this_row += '<td></td>'

            this_row += '<td>' + str(this_package_info['cran'].get('license', "")) + '</td>' # CRAN license
            this_row += '<td>' + str(this_package_info['repo'].get('last_commit_date', "")) + '</td>' # GH last update

            # GH version with link
            if this_package_info['gh_api'].get('release_url') is None:
                this_row += '<td></td>'
            else:
                this_row += '<td><a href="' + this_package_info['gh_api']['release_url'] + '" target="_blank">' + this_package_info['gh_api']['latest_release'] + '</a></td>'

            # GH license
            if this_package_info['gh_api'].get('license') is not None and this_package_info['gh_api'].get('license') != "Other":
                this_row += '<td>' + this_package_info['gh_api'].get('license', "") + '</td>'
            elif this_package_info['repo'].get('license') is not None:
                this_row += '<td>' + this_package_info['repo'].get('license', "") + '</td>'
            else:
                this_row += '<td></td>'

            this_row += '<td class="left"><a href="https://github.com/' + this_package_info['gh_api']['owner'] + '" target="_blank">' + this_package_info['gh_api']['owner'] + '</a></td>' # GH owner

            # Group rows by status and add put a row number in
            if this_package_info['input']['status'].strip() == 'production':
                production_rows += '<tr>'
                production_rows += '<td>' + str(production_rows_count) + '</td>' # Row number
                production_rows += this_row
                production_rows += '</tr>'
                production_rows_count += 1
            elif this_package_info['input']['status'].strip() == 'development':
                development_rows += '<tr>'
                development_rows += '<td>' + str(development_rows_count) + '</td>'
                development_rows += this_row
                development_rows += '</tr>'
                development_rows_count += 1
            elif this_package_info['input']['status'].strip() == 'retired':
                retired_rows += '<tr>'
                retired_rows += '<td>' + str(retired_rows_count) + '</td>'
                retired_rows += this_row
                retired_rows += '</tr>'
                retired_rows_count += 1
            else:
                unknown_rows += '<tr>'
                unknown_rows += '<td>' + str(unknown_rows_count) + '</td>'
                unknown_rows += this_row
                unknown_rows += '</tr>'
                unknown_rows_count += 1

        # Build the table with the rows grouped by status
        html_file.write('<tr><td colspan="9">Production</td></tr>')
        html_file.write(production_rows)
        html_file.write('<tr><td colspan="9">Development</td></tr>')
        html_file.write(development_rows)
        html_file.write('<tr><td colspan="9">Retired</td></tr>')
        html_file.write(retired_rows)
        html_file.write('<tr><td colspan="9">Unknown</td></tr>')
        html_file.write(unknown_rows)
        html_file.write('</table>')

        html_file.write('<hr/>')
        html_file.write('Generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_file.write('&nbsp;&nbsp;Made by the <a href="https://github.com/FederatedMethods" target="_blank">Federated Methods team</a>')

        html_file.write('</body>\n</html>')

if __name__ == '__main__':
    main('./output/metadata/packages.json', './output/html/index.html')
    shutil.copy('source/static_html_files/style_main.css', './output/html/style_main.css')
    shutil.copy('source/static_html_files/faq.html', './output/html/faq.html')
