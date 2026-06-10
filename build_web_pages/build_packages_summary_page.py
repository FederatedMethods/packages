import datetime
import shutil
import os
from utils import parse_package_info

def main(csv_file_path, html_file_path, functions_file_path):
    print(f"Current working directory: {os.getcwd()}")

    if not os.path.exists("output"):
        os.makedirs("output")

    # Count the number of functions in the functions file to include in the stats.
    # This is not a particularly accurate way to count as it's derived from the 
    # NAMESPACE file, but some packages have a wild card inclusion not an explicit list.
    with open(functions_file_path, 'r', encoding='utf-8') as functions_file:
        full_function_file_text = functions_file.read()

        number_of_functions = full_function_file_text.count(",")

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

        package_info = parse_package_info(csv_file_path)

        stats = f'<p>There are {len(package_info)} packages and {number_of_functions} functions listed on these pages.</p>'
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
        for this_package_name, this_package_info in package_info.items():
            print(this_package_name)
            print(this_package_info)
            this_row = ""

            # Add GitHub link if available, otherwise just the name
            this_row += '<td class="left"><a href="packages.html#' + this_package_name + '">' + this_package_name + '</a></td>'

            # Description
            if len(this_package_info['short_description']) > 0:
                this_row += '<td class="left">' + this_package_info['short_description'] + '</td>'
            else:
                this_row += '<td></td>'

            # CRAN version with link
            if len(this_package_info.get('cran_link')) > 0:
                this_row += '<td><a href="' + this_package_info['cran_link'] + '" target="blank">' + this_package_info['cran_version'] + '</a></td>' 
            else:
                this_row += '<td></td>'

            this_row += '<td>' + this_package_info.get('cran_license', "") + '</td>' # CRAN license
            this_row += '<td>' + this_package_info.get('github_last_update', "") + '</td>' # GH last update
            
                # GH version with link
            if this_package_info.get('github_version_url') == "null":
                this_row += '<td></td>'
            else:
                this_row += '<td><a href="' + this_package_info['github_version_url'] + '" target="_blank">' + this_package_info['github_version'] + '</a></td>'
            
            # GH license
            if this_package_info.get('github_license') == "null":
                this_row += '<td></td>'
            else:
                this_row += '<td>' + this_package_info.get('github_license', "") + '</td>'
            
            this_row += '<td class="left"><a href="https://github.com/' + this_package_info['github_owner'] + '" target="_blank">' + this_package_info['github_owner'] + '</a></td>' # GH owner

            # Group rows by status and add put a row number in
            if this_package_info['status'].strip() == 'production':
                production_rows += '<tr>'
                production_rows += '<td>' + str(production_rows_count) + '</td>' # Row number
                production_rows += this_row
                production_rows += '</tr>'
                production_rows_count += 1
            elif this_package_info['status'].strip() == 'development':
                development_rows += '<tr>'
                development_rows += '<td>' + str(development_rows_count) + '</td>'
                development_rows += this_row
                development_rows += '</tr>'
                development_rows_count += 1
            elif this_package_info['status'].strip() == 'retired':
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
        html_file.write('&nbsp;&nbsp;Made by the <a href="https://github.com/FederatedMethods">Federated Methods team</a>')

        html_file.write('</body>\n</html>')

if __name__ == '__main__':
    main('./cache/output.csv', './output/index.html', './cache/functions.txt')
    shutil.copy('./build_web_pages/template/style_main.css', './output/style_main.css')
