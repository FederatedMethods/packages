"""
Function to generate an HTML page with a timeline for each DataSHIELD package,
spanning from the GitHub created date to the last commit date.
Olly Butters
18/11/2026
"""

import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_html_utils.navbar import get_navbar
import html
import json
import os
import shutil


def parse_date(value):
    """Parse an ISO date or datetime string (e.g. '2025-11-25T16:27:20Z' or '2026-11-16') to a date."""
    if not value:
        return None
    try:
        return datetime.datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def main(packages_file_path='./output/metadata/packages.json', html_file_path='./output/html/stats.html'):
    """
    Main function to generate an HTML page with stats about packages.
    Args:
        packages_file_path (str): Path to the JSON file containing package information.
        html_file_path (str): Path to the output HTML file to be generated.
    """

    output_dir = os.path.dirname(html_file_path) or "output/html"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(packages_file_path, 'r', encoding='utf-8') as packages_file:
        packages = json.load(packages_file)


    with open(html_file_path, 'w', encoding='utf-8') as html_file:

        head = '<!DOCTYPE html><html lang="en-GB">'
        head += '<head>'
        head += '<title>DataSHIELD community packages stats</title>'
        head += '<meta charset="UTF-8">'
        head += '<link rel="stylesheet" href="./style_main.css">'
        head += '</head>'
        head += '<body>' + get_navbar('stats.html')
        html_file.write(head)

        top_content = '<div class="top-content" id="top">'
        top_content += '<h1>DataSHIELD community packages stats</h1>'
        html_file.write(top_content)

        # Number of functions (exported in the NAMESPACE files)
        total_functions = sum(len(info.get('repo', {}).get('functions_exported_in_NAMESPACE') or []) for info in packages.values())

        # Number of forks
        total_forks = sum(info.get('gh_api', {}).get('fork_count') or 0 for info in packages.values())

        # Number of stars
        total_stars = sum(info.get('gh_api', {}).get('stargazer_count') or 0 for info in packages.values())

        # Number of watchers
        total_watchers = sum(info.get('gh_api', {}).get('watcher_count') or 0 for info in packages.values())

        # Lines of code. The new function_info structure (roxygen_tags) no longer holds a per-file
        # lines_of_code, so use a package level repo['lines_of_code'] if present and leave the
        # figure out of the text if there is no data.
        total_lines_of_code = sum(info.get('repo', {}).get('function_info', {}).get('number_of_lines_of_code') or 0 for info in packages.values())

        # Number of commits (summed from the total_commits in repo)
        total_commits = sum(info.get('repo', {}).get('total_commits') or 0 for info in packages.values())

        html_file.write(f'<p> There are <strong>{len(packages)}</strong> packages developed by the DataSHIELD community, with <strong>{total_functions}</strong> functions spread over <strong>{total_lines_of_code:,}</strong> lines of source code from <strong>{total_commits:,}</strong> commits. These packages have <strong>{total_forks}</strong> forks, <strong>{total_stars}</strong> stars and <strong>{total_watchers}</strong> watchers between them on GitHub. The timeline below shows the development history of these packages, from when they were first created to their most recent commit, going all the way back to the first commit in dsBase in 2013.</p>')

        ########################################################################################
        # Timeline
        # Collect the dates for each package
        entries = []
        missing = []
        for name, info in packages.items():
            created = parse_date(info.get('gh_api', {}).get('created_at'))
            last_commit = parse_date(info.get('repo', {}).get('last_commit_date'))
            if created is None or last_commit is None:
                missing.append(name)
                continue
            if last_commit < created:
                last_commit = created
            status = (info.get('input', {}).get('status') or '').strip() or 'unknown'
            entries.append({'name': name, 'created': created, 'last_commit': last_commit, 'status': status})

        entries.sort(key=lambda e: (e['created'], e['name']))

        if not entries:
            html_file.write('<p>No packages with both a created date and a last commit date were found.</p></div>')
        else:
            # Shared axis, rounded out to whole years
            first_year = min(e['created'] for e in entries).year
            last_year = max(e['last_commit'] for e in entries).year + 1
            axis_start = datetime.date(first_year, 1, 1)
            axis_end = datetime.date(last_year, 1, 1)
            span_days = (axis_end - axis_start).days

            def pct(date):
                return (date - axis_start).days / span_days * 100

            # Year ticks
            ticks = ''
            for year in range(first_year, last_year + 1):
                left = pct(datetime.date(year, 1, 1))
                ticks += f'<span class="timeline-tick" style="left:{left:.3f}%">{year}</span>'

            html_file.write('<table>\n')
            html_file.write(f'<tr><th></th><th><div class="timeline-axis">{ticks}</div></th></tr>\n')

            for entry in entries:
                name = html.escape(entry['name'])
                left = pct(entry['created'])
                width = max(pct(entry['last_commit']) - left, 0.3)
                tooltip = f"{entry['name']}: created {entry['created']}, last commit {entry['last_commit']}"
                bar = (f'<div class="timeline-bar timeline-{html.escape(entry["status"])}" '
                       f'style="left:{left:.3f}%;width:{width:.3f}%" title="{html.escape(tooltip)}"></div>')
                html_file.write(
                    f'<tr><td class="label"><a href="packages.html#{name}">{name}</a></td>'
                    f'<td class="timeline-cell"><div class="timeline-track">{bar}</div></td></tr>\n'
                )

            html_file.write('</table>\n')

            html_file.write('<p>Bar colour shows package status: '
                            '<span class="timeline-key timeline-production"></span> production '
                            '<span class="timeline-key timeline-development"></span> development '
                            '<span class="timeline-key timeline-retired"></span> retired '
                            '<span class="timeline-key timeline-unknown"></span> unknown.</p>')

            ###################################################################
            # Number of active packages per year. A package is active in every calendar
            # year from the year it was created to the year of its last commit (inclusive).
            active_per_year = {}
            for year in range(first_year, last_year):
                active_per_year[year] = sum(
                    1 for e in entries if e['created'].year <= year <= e['last_commit'].year
                )
            max_active = max(active_per_year.values()) or 1

            html_file.write('<h2>Number of packages actively developed per year</h2>')
            html_file.write('<p>A package is counted as active in each year from the year it was created to the year of its last commit.</p>')
            html_file.write('<div class="yearplot">')
            for year, count in active_per_year.items():
                bar_height = count / max_active * 85  # leave room for the count label
                html_file.write(
                    f'<div class="yearplot-col" title="{year}: {count} active packages">'
                    f'<div class="yearplot-count">{count}</div>'
                    f'<div class="yearplot-bar" style="height:{bar_height:.1f}%"></div>'
                    f'<div class="yearplot-year">{year}</div>'
                    f'</div>'
                )
            html_file.write('</div>')

            if missing:
                html_file.write('<p>Not shown (missing dates): ' + html.escape(', '.join(missing)) + '</p>')

        html_file.write('<p style="text-align:right"><a href="#top">Jump to top of page</a></p>')


        # Footer
        html_file.write('<hr/>')
        html_file.write('Generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_file.write('&nbsp;&nbsp;Made by the <a href="https://github.com/FederatedMethods" target="_blank">Federated Methods team</a>')

        html_file.write('</body>\n</html>')


if __name__ == '__main__':
    main('./output/metadata/packages.json', './output/html/stats.html')
    shutil.copy('source/build_html_utils/static_html_files/style_main.css', './output/html/style_main.css')
    shutil.copy('source/build_html_utils/static_html_files/faq.html', './output/html/faq.html')
