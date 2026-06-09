def parse_package_info(package_file_path):
    import csv
    # Initialize a dictionary to hold package information
    package_info = {}

    # Parse the package information from the CSV file
    with open(package_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)

        for row in reader:
            package_name = row[0]
            package_info[package_name] = {
                "short_description": row[1],
                "cran_link": row[2],
                "cran_version": row[3],
                "cran_license": row[4],
                "github_link": row[5],
                "github_last_update": row[6],
                "github_version": row[7],
                "github_version_url": row[8],
                "github_license": row[9],
                "github_owner": row[10],
                "status": row[11]
            }
        
    return package_info
