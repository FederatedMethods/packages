"""
Function to generate an HTML page listing DataSHIELD packages.
Olly Butters
5/8/2026
"""

import datetime
import json
import os
from pprint import pprint
import shutil

def main(packages_file_path = './output/metadata/packages.json', html_file_path = './output/html/packages.html'):
    """
    Main function to generate an HTML page listing DataSHIELD packages.
    This function processes package information from a JSON file,
    and generates an HTML page summarizing the information.
    Args:
        packages_file_path (str): Path to the JSON file containing package information.
        html_file_path (str): Path to the output HTML file to be generated.
    """

    print(f"Current working directory: {os.getcwd()}")

    # Ensure the output directory exists
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
        top_content += '<h1>DataSHIELD packages</h1><a href="#top"></a>'
        top_content += '<p>This page lists all the packages that have been developed in the <a href="https://www.datashield.org">DataSHIELD</a> ecosystem. It includes packages that are in production, in development, retired, and unknown status. More info is in the <a href="./faq.html">FAQ</a>.</p>'

        html_file.write(top_content)

        stats = f'<p>There are {number_of_packages} packages and {number_of_functions} functions listed on these pages.</p>'
        html_file.write(stats)

        for this_package_name, this_package_info in packages.items():
            try:

                print(f"Processing package: {this_package_name}")
                pprint(this_package_info)

                html_content = f"""
                
                <h2 id="{this_package_name}"><a href="#{this_package_name}">{this_package_name}</a></h2>

                <table>
                    <tr><td class="label">Short description</td><td class="left">{this_package_info['input'].get('description', 'No short description available.')}</td></tr>
                    <tr><td class="label">Long description</td><td class="left">{this_package_info['repo'].get('Description', 'No long description available.')}</td></tr>
                """

                if this_package_info['input'].get('cran_link'):
                    html_content += f"""
                    <tr><td class="label">CRAN link</td><td class="left"><a href="{this_package_info['input'].get('cran_link')}" target="_blank">{this_package_info['input'].get('cran_link')}</a></td></tr>
                    """
                else:
                    html_content += '<tr><td class="label">CRAN link</td><td class="left">-</td></tr>'

                html_content += f"""
                    <tr><td class="label">CRAN version</td><td class="left">{this_package_info['cran'].get('version', '-')}</td></tr>
                    <tr><td class="label">CRAN licence</td><td class="left">{this_package_info['cran'].get('license', '-')}</td></tr>
                    <tr><td class="label">GitHub last update</td><td class="left">{this_package_info['repo'].get('last_commit_date', 'No GitHub last update available.')}</td></tr>
                """

                # GH link
                if this_package_info['input'].get('github_link'):
                    html_content += f"""
                    <tr><td class="label">GitHub link</td><td class="left"><a href="{this_package_info['input'].get('github_link')}" target="_blank">{this_package_info['input'].get('github_link')}</a></td></tr>
                    """
                else:
                    html_content += '<tr><td class="label">GitHub link</td><td class="left">-</td></tr>'

                # GH version
                if this_package_info['gh_api'].get('release_url') is None:
                    html_content += '<tr><td class="label">GitHub version</td><td class="left">-</td></tr>'
                else:
                    html_content += f"""
                    <tr><td class="label">GitHub version</td><td class="left"><a href="{this_package_info['gh_api'].get('release_url')}" target="_blank">{this_package_info['gh_api'].get('latest_release')}</a></td></tr>
                    """

                # GH license
                if this_package_info['gh_api'].get('license') is not None and this_package_info['gh_api'].get('license') != "Other":
                    html_content += f"""
                    <tr><td class="label">GitHub license</td><td class="left">{this_package_info['gh_api'].get('license')}</td></tr>
                    """
                elif this_package_info['repo'].get('license') is not None:
                    html_content += f"""
                    <tr><td class="label">GitHub license</td><td class="left">{this_package_info['repo'].get('license')}</td></tr>
                    """
                else:
                    html_content += '<tr><td class="label">GitHub license</td><td class="left">-</td></tr>'
                
                html_content += f"""
                    <tr><td class="label">GitHub owner</td><td class="left">{this_package_info['gh_api'].get('owner', 'No GitHub owner available.')}</td></tr>
                    <tr><td class="label">Status</td><td class="left">{this_package_info['input'].get('status', 'Unknown')}</td></tr>
                """

                if this_package_info['repo'].get('maintainer_string'):
                    html_content += f"""<tr><td class="label">Maintainer</td><td class="left">{this_package_info['repo'].get('maintainer_string')}</td></tr>"""
                else:
                    html_content += '<tr><td class="label">Maintainer</td><td class="left"></td></tr>'

                html_content += f"""
                    <tr><td class="label">Functions</td><td class="left">{', '.join(this_package_info['repo'].get('functions', [])) if 'functions' in this_package_info['repo'] else 'No functions listed.'}</td></tr>
                </table>
                <p style="text-align:right"><a href=#top>Jump to top of page</a></p>
                """

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
    main('./output/metadata/packages.json', './output/html/packages.html')
    shutil.copy('source/static_html_files/style_main.css', './output/html/style_main.css')
    shutil.copy('source/static_html_files/faq.html', './output/html/faq.html')
