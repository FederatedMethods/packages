import csv
import datetime
import shutil
import os

def main(csv_file_path, html_file_path):
    print(f"Current working directory: {os.getcwd()}")

    if not os.path.exists("output"):
        os.makedirs("output")

    with open(html_file_path, 'w') as html_file:

        # Put html together for this page
        head = '<!DOCTYPE html><html lang="en-GB">'
        head += '<head>'
        head += '<title>DataSHIELD packages</title>'
        head += '<meta charset="UTF-8">'
        head += '<link rel="stylesheet" href="./style_main.css">'
        head += '</head>'
        head += '<body>'

        html_file.write(head)

        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)

            html_file.write('<h1>DataSHIELD packages</h1>\n')
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

            row_count = 0
            for row in reader:
                print(row)
                row_count += 1
                html_file.write('<tr>')
                html_file.write('<td>' + str(row_count) + '</td>') # Row number

                # Add GitHub link if available, otherwise just the name
                if len(row[5]) > 0:
                    html_file.write('<td class="left"><a href="' + row[5] + '" target="blank">' + row[0] + '</a></td>') # GH repository link with name
                else:
                    html_file.write('<td class="left">' + row[0] + '</td>')

                # Description
                if len(row[1]) > 0:
                    html_file.write('<td class="left">' + row[1] + '</td>') # Description
                else:
                    html_file.write('<td></td>')

                if len(row[2]) > 0:
                    html_file.write('<td><a href="' + row[2] + '" target="blank">' + row[3] + '</a></td>') # CRAN link
                else:
                    html_file.write('<td></td>')


                # html_file.write('<td>' + row[3] + '</td>') # CRAN version
                html_file.write('<td>' + row[4] + '</td>') # CRAN license
                html_file.write('<td>' + row[6] + '</td>') # GH last update
                html_file.write('<td>' + row[7] + '</td>') # GH version
                html_file.write('<td>' + row[8] + '</td>') # GH license
                html_file.write('<td class="left">' + row[9] + '</td>') # GH owner
                html_file.write('</tr>\n')

            html_file.write('</table>')

        html_file.write('Generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        html_file.write('</body>\n</html>')

if __name__ == '__main__':
    main('output.csv', './output/index.html')
    shutil.copy('./web_pages/template/style_main.css', './output/style_main.css')
