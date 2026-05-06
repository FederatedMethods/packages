import csv

def main(csv_file_path, html_file_path):
    with open(html_file_path, 'w') as html_file:

        html_file.write('<html>\n<head>\n<title>Packages</title>\n</head>\n<body>\n')
        html_file.write('<h1>Packages</h1>\n')

        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)

            html_file.write('<table border="1">\n')
            html_file.write('<tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr>\n')

            for row in reader:
                html_file.write('<tr>')
                html_file.write('<td>' + row[0] + '</td>') # Name
                html_file.write('<td>' + row[1] + '</td>') # Description
                if len(row[2]) > 0:
                    html_file.write('<td><a href="' + row[2] + '" target="blank">Link</a></td>') # CRAN link
                else:
                    html_file.write('<td></td>')
                html_file.write('<td>' + row[3] + '</td>') # CRAN version
                html_file.write('<td>' + row[4] + '</td>') # CRAN license
                if len(row[5]) > 0:
                    html_file.write('<td><a href="' + row[5] + '" target="blank">Link</a></td>') # GH repository
                else:
                    html_file.write('<td></td>')
                html_file.write('<td>' + row[6] + '</td>') # GH last update
                html_file.write('<td>' + row[7] + '</td>') # GH version
                html_file.write('</tr>\n')

            html_file.write('</table>')

        html_file.write('</body>\n</html>')

if __name__ == '__main__':
    main('output.csv', 'table.html')
