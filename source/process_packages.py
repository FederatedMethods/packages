"""
Function to process the package list and gather information from GitHub and CRAN, saving in a JSON file.
If running locally you will need to authenticate with GitHub CLI first using `gh auth login` and have the gh CLI installed.
Olly Butters
5/8/2026
"""

import os
import csv
import json
import re
from pprint import pprint
import shutil
import subprocess
import urllib.request as urllib2
from parse_DESCRIPTION_file import parse_description_file


def main(clone = False, cache_dir = "cache",delete_cache = False, package_input_file = "package_list.csv"):
    """
    Main function to process the package list and gather information from GitHub and CRAN.
    Args:
        clone (bool): Whether to clone the GitHub repositories. Default is False.
        cache_dir (str): Directory to store cloned repositories. Default is "cache".
        delete_cache (bool): Whether to delete the cache directory before processing. Default is False.
        package_input_file (str): Path to the CSV file containing package information. Default is "package_list.csv".
    """

    packages = {}

    # Read the package input and tidy up a little
    with open(package_input_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for row in reader:
            pprint(row)
            name = row.get("name", "").strip()
            description = (row.get("description", "")).strip()
            cran_link = row.get("cran_link", "").strip()
            github_link = row.get("github_link", "").strip()
            status = row.get("status", "").strip()

            # Initialise this package with empty dictionaries for each of the sections
            packages[name] = {'input': {}, 'repo': {}, 'gh_api': {}, 'cran': {}}

            packages[name]['input'] = {
                "name": name,
                "description": description,
                "cran_link": cran_link,
                "github_link": github_link,
                "status": status
            }

    pprint(packages)

    # Delete the cache dir if flag is set
    # There is a problem here with Windows if the cache dir has read only files in it.
    # Need to handle this better.
    if delete_cache and os.path.exists(cache_dir):
        print(f"Deleting cache directory: {cache_dir}")
        shutil.rmtree(cache_dir, ignore_errors=False)

    if not os.path.exists(cache_dir + "/cran"):
        print(f"Creating cache directory: {cache_dir}")
        os.makedirs(cache_dir + "/cran")

    # Clone all of the repos into the cache directory
    os.chdir(cache_dir)
    if clone:
        for package_name, package_info in packages.items():
            github_link_end_part = package_info['input']['github_link'].split("/")[-1]
            if not os.path.exists(github_link_end_part):
                print(f"Cloning package: {github_link_end_part}")
                subprocess.run(['git', 'clone', package_info['input']['github_link']], capture_output=True, text=True, check=True)

    # Cycle through each package and get data from cloned repo, GitHub API, and CRAN
    for package_name, package_info in packages.items():
        print(f"\n################\nPackage: {package_name}")

        github_link_end_part = package_info['input']['github_link'].split("/")[-1]

        ################################################
        # Get relevant information from each cloned repo
        if os.path.exists(github_link_end_part):
            print(f"Processing cloned repo: {github_link_end_part}")

            # If there is a DESCRIPTION file then parse it
            if os.path.exists(github_link_end_part + "/DESCRIPTION"):
                print("DESCRIPTION file found")
                description_file_path = github_link_end_part + "/DESCRIPTION"
                parsed_description = parse_description_file(description_file_path)
                package_info['repo'] = parsed_description
            else:
                print("DESCRIPTION file not found")

            # Get the last commit date
            try:
                last_commit_date = subprocess.run(['git', 'log', '-1', '--pretty=format:%cs'], capture_output=True, text=True, check=True).stdout.strip()
                print(f"Repo last commit date: {last_commit_date}")
                package_info['repo']['last_commit_date'] = last_commit_date
            except Exception as e:
                print(f"Error getting last commit date for package {github_link_end_part}: {e}")
                package_info['repo']['last_commit_date'] = None

            # If there is a NAMESPACE file then parse it to get the function input
            if os.path.exists(github_link_end_part + "/NAMESPACE"):
                print("NAMESPACE file found")
                with open(github_link_end_part + "/NAMESPACE", "r", encoding="utf-8") as namespace_file:
                    gh_functions = re.findall(r'export\((.*?)\)', namespace_file.read())
                    print(f"Repo functions: {gh_functions}")
                    package_info['repo']['functions'] = gh_functions
            else:
                print("NAMESPACE file not found")
                package_info['repo']['functions'] = None

            # Get the LICENSE file in the repo and parse it to get the license type
            if os.path.exists(github_link_end_part + "/LICENSE.md"):
                print("LICENSE.md file found")
                with open(github_link_end_part + "/LICENSE.md", "r", encoding="utf-8") as license_file:
                    license_content = license_file.read()
            elif os.path.exists(github_link_end_part + "/LICENSE"):
                print("LICENSE file found")
                with open(github_link_end_part + "/LICENSE", "r", encoding="utf-8") as license_file:
                    license_content = license_file.read()
            else:
                print("LICENSE file not found")
                license_content = None
                package_info['repo']['license'] = None

            if 'license_content' in locals() and license_content is not None:
                if "GPL" in license_content:
                    package_info['repo']['license'] = "GPL"
                elif "MIT" in license_content:
                    package_info['repo']['license'] = "MIT"
                elif "Apache" in license_content:
                    package_info['repo']['license'] = "Apache"
                else:
                    package_info['repo']['license'] = "Other"

        ######################################################
        # Get the GitHub repo information using the GitHub CLI
        os.chdir(github_link_end_part)
        result = subprocess.run(['gh', 'repo', 'view', '--json', 'codeOfConduct,description,homepageUrl,latestRelease,licenseInfo,owner,parent,updatedAt'], capture_output=True, text=True, check=True)
        print(result.stdout)
        os.chdir("..")
        gh_api_info = json.loads(result.stdout)

        package_info['gh_api']['owner'] = gh_api_info['owner']['login'] if 'owner' in gh_api_info else None
        package_info['gh_api']['code_of_conduct'] = gh_api_info['codeOfConduct'] if 'codeOfConduct' in gh_api_info else None
        package_info['gh_api']['description'] = gh_api_info['description'] if 'description' in gh_api_info else None
        package_info['gh_api']['homepage_url'] = gh_api_info['homepageUrl'] if 'homepageUrl' in gh_api_info else None

        # Get the latest release information
        if 'latestRelease' in gh_api_info and gh_api_info['latestRelease'] is not None:
            if 'name' in gh_api_info['latestRelease'] and gh_api_info['latestRelease']['name'] is not None and gh_api_info['latestRelease']['name'] != "":
                package_info['gh_api']['latest_release'] = gh_api_info['latestRelease']['name']
            elif 'tagName' in gh_api_info['latestRelease'] and gh_api_info['latestRelease']['tagName'] is not None and gh_api_info['latestRelease']['tagName'] != "":
                package_info['gh_api']['latest_release'] = gh_api_info['latestRelease']['tagName']
            else:
                package_info['gh_api']['latest_release'] = None

            package_info['gh_api']['release_url'] = gh_api_info['latestRelease']['url'] if 'url' in gh_api_info['latestRelease'] else None
        else:
            package_info['gh_api']['latest_release'] = None
            package_info['gh_api']['release_url'] = None


        # Get the license information
        if 'licenseInfo' in gh_api_info and gh_api_info['licenseInfo'] is not None:
            if 'nickname' in gh_api_info['licenseInfo'] and gh_api_info['licenseInfo']['nickname'] is not None and gh_api_info['licenseInfo']['nickname'] != "":
                package_info['gh_api']['license'] = gh_api_info['licenseInfo']['nickname']
            elif 'name' in gh_api_info['licenseInfo'] and gh_api_info['licenseInfo']['name'] is not None and gh_api_info['licenseInfo']['name'] != "":
                package_info['gh_api']['license'] = gh_api_info['licenseInfo']['name']
        else:
            package_info['gh_api']['license'] = None

        #############################
        # Get info from CRAN
        if packages[package_name]['input']['cran_link']:
            cran_package_name = (packages[package_name]['input']['cran_link']).split("=")[-1]

            print(f"CRAN package name: {cran_package_name}")

            cran_description_file_link="https://cran.r-project.org/web/packages/" + cran_package_name + "/DESCRIPTION"

            try:
                urllib2.urlretrieve(cran_description_file_link, "cran/" + cran_package_name + "_DESCRIPTION")
                with open("cran/" + cran_package_name + "_DESCRIPTION", "r", encoding="utf-8") as cran_description_file:
                    cran_description_content = cran_description_file.read()

                    temp = re.findall(r"Version:\s*([a-zA-Z0-9\. _-]+)\s*", cran_description_content)
                    if temp:
                        package_info['cran']['version'] = temp[0]

                    temp = re.findall(r"License:\s*([a-zA-Z0-9\. _\-\(\)><=\+]+)\s*", cran_description_content)
                    if temp:
                        package_info['cran']['license'] = temp[0]

            except urllib2.URLError as e:
                print(type(e))


    pprint(packages)

    # Output to file
    os.chdir("..")
    if not os.path.exists('output/metadata'):
        os.makedirs('output/metadata')

    with open("output/metadata/packages.json", "w", encoding="utf-8") as json_file:
        json.dump(packages, json_file, indent=4)



if __name__ == "__main__":
    main(clone=True, cache_dir="cache")
    #main(clone=False, cache_dir="cache")
