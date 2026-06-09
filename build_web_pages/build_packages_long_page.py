import datetime
import shutil
import os
import re
from parse_DESCRIPTION_file import parse_description_file
from utils import parse_package_info

def main(package_file_path, functions_file_path, html_file_path):
    """
    Main function to generate an HTML page listing DataSHIELD packages.
    This function processes package information from a CSV file, parses function
    details from a text file, extracts additional metadata from DESCRIPTION files,
    and generates an HTML page summarizing the information.
    Args:
        package_file_path (str): Path to the CSV file containing package information.
        functions_file_path (str): Path to the text file containing package functions.
        html_file_path (str): Path to the output HTML file to be generated.
    """

    print(f"Current working directory: {os.getcwd()}")

    # Ensure the output directory exists
    if not os.path.exists("output"):
        os.makedirs("output")

    # Dictionary to hold package information
    package_info = parse_package_info(package_file_path)

    # Parse the functions.txt file
    with open(functions_file_path, 'r', encoding='utf-8') as file:

        for line in file:
        # Match lines with the format: groupName: function1,function2,...
            match = re.match(r"^(\w+):\s*(.+)$", line.strip())
            if match:
                package_name = match.group(1)
                functions = match.group(2).split(',')
                package_info[package_name]["functions"] = functions

    with open(functions_file_path, 'r', encoding='utf-8') as functions_file:
        full_function_file_text = functions_file.read()
        number_of_functions = full_function_file_text.count(",")

    # Parse the DESCRIPTION files
    for package_name in package_info.keys():
        try:
            # Some packages have a different format of their GitHub link than the package name.
            github_name = package_info[package_name]['github_link'].rsplit('/', 1)[-1]
            github_name = github_name.rstrip('/')

            description_file_path = f"./cache/{github_name}/DESCRIPTION"
            description_data = parse_description_file(description_file_path)
            package_info[package_name]["DESCRIPTION"] = description_data
        except FileNotFoundError as e:
            print(f"No DESCRIPTION file found: {e}")

    print(package_info)

    # Generate the HTML page
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

        stats = f'<p>There are {len(package_info)} packages and {number_of_functions} functions listed on these pages.</p>'
        html_file.write(stats)

        for this_package_name, this_package_info in package_info.items():
            try:
                html_content = f"""
                
                <h2><h2 id="{this_package_name}"><a href="#{this_package_name}">{this_package_name}</a></h2></h2>

                <table>
                    <tr><td class="label">Short description</td><td class="left">{this_package_info.get('short_description', 'No short description available.')}</td></tr>
                    <tr><td class="label">Long description</td><td class="left">{this_package_info.get('DESCRIPTION', {}).get('Description', 'No long description available.')}</td></tr>
                """

                if this_package_info.get('cran_link'):
                    html_content += f"""
                    <tr><td class="label">CRAN link</td><td class="left"><a href="{this_package_info.get('cran_link')}" target="_blank">{this_package_info.get('cran_link')}</a></td></tr>
                    """
                else:
                    html_content += '<tr><td class="label">CRAN link</td><td class="left"></td></tr>'
                
                html_content += f"""
                    <tr><td class="label">CRAN version</td><td class="left">{this_package_info.get('cran_version', '-')}</td></tr>
                    <tr><td class="label">CRAN licence</td><td class="left">{this_package_info.get('cran_license', '-')}</td></tr>
                    <tr><td class="label">GitHub last update</td><td class="left">{this_package_info.get('github_last_update', 'No GitHub last update available.')}</td></tr>
                """

                if this_package_info.get('github_link'):
                    html_content += f"""
                    <tr><td class="label">GitHub link</td><td class="left"><a href="{this_package_info.get('github_link')}" target="_blank">{this_package_info.get('github_link')}</a></td></tr>
                    """
                else:
                    html_content += '<tr><td class="label">CRAN link</td><td class="left">N/A</td></tr>'

                if this_package_info.get('github_version_url') == 'null':
                    html_content += '<tr><td class="label">GitHub version</td><td class="left"></td></tr>'
                else:
                    html_content += f"""
                    <tr><td class="label">GitHub version</td><td class="left"><a href="{this_package_info.get('github_version_url')}" target="_blank">{this_package_info.get('github_version')}</a></td></tr>
                    """

                html_content += f"""
                    <tr><td class="label">GitHub license</td><td class="left">{this_package_info.get('github_license', 'No GitHub license available.')}</td></tr>
                    <tr><td class="label">GitHub owner</td><td class="left">{this_package_info.get('github_owner', 'No GitHub owner available.')}</td></tr>
                    <tr><td class="label">Status</td><td class="left">{this_package_info.get('status', 'Unknown')}</td></tr> 
                    <tr><td class="label">Functions</td><td class="left">{', '.join(this_package_info.get('functions', [])) if 'functions' in this_package_info else 'No functions listed.'}</td></tr>
                </table>
                """

                html_file.write(html_content)
            except Exception as e:
                print(f"Error processing package {this_package_name}: {e}")
                continue

        # Footer
        html_file.write('<hr/>')
        html_file.write('Generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_file.write('&nbsp;&nbsp;Made by the <a href="https://github.com/FederatedMethods">Federated Methods team</a>')

        html_file.write('</body>\n</html>')

if __name__ == '__main__':
    main('cache/output.csv', 'cache/functions.txt', './output/packages.html')
    shutil.copy('./build_web_pages/template/style_main.css', './output/style_main.css')
    shutil.copy('./build_web_pages/template/faq.html', './output/faq.html')
