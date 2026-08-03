import os
import csv
import re
import json
import subprocess
# only using this for date grabbing, could just dump to file or capture output of os.system?
import git
from pprint import pprint


def process_packages(clone = False):
    # Input and output file paths
    package_list_file = "package_list.csv"
    cache_dir = "cache3"

    packages = dict()

    # Read the package list and tidy up a little
    with open(package_list_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for row in reader:
            print(row)
            name = row.get("name", "").strip()
            description = (row.get("description", "")).strip()
            cran_link = row.get("cran_link", "").strip()
            github_link = row.get("github_link", "").strip()
            status = row.get("status", "").strip()

            packages[name] = {
                "name": name,
                "description": description,
                "cran_link": cran_link,
                "github_link": github_link,
                "status": status
            }

            break

    print(packages)


    # Clone all of the repos into the cache directory
    os.chdir(cache_dir)
    if clone:
        for package_name, package_info in packages.items():
            print(f"Package: {package_name}")
            os.system("git clone {}".format(package_info['github_link']))
            #repo = git.Repo.clone_from('https://github.com/datashield/dsBase.git', 'dsBase2')


    # Get relevant information from each cloned repo
    for package_name, package_info in packages.items():
        print(f"Package: {package_name}")

        
        if os.path.exists(package_name):

            # Get the last commit date
            this_repo = git.Repo(package_name)
            last_commit_date = this_repo.git.log('-1', '--pretty=format:%cs')
            print(f"Last commit date: {last_commit_date}")
            packages[package_name]['last_commit_date'] = last_commit_date

            # If there is a NAMESPACE file then parse it to get the function list
            if os.path.exists(package_name + "/NAMESPACE"):
                print("NAMESPACE file found")
                gh_functions = re.findall(r'export\((.*?)\)', open(package_name + "/NAMESPACE", encoding="utf-8").read())
                #gh_functions=$(sed -n "s/^export(\(.*\))$/\1/p" NAMESPACE | tr '\n' ',')
                print(f"GitHub functions: {gh_functions}")
                packages[package_name]['github_functions'] = gh_functions

            os.chdir(package_name)           
            result = subprocess.run(['gh', 'repo', 'view', '--json', 'codeOfConduct,description,homepageUrl,latestRelease,licenseInfo,owner,parent,updatedAt'], capture_output=True, text=True, check=True)
            print(result.stdout)
            os.chdir("..")
            gh_repo_info = json.loads(result.stdout)
            packages[package_name]['gh_owner'] = gh_repo_info['owner']['login'] if 'owner' in gh_repo_info else None


    #os.system('gh repo view --json codeOfConduct,description,homepageUrl,latestRelease,licenseInfo,owner,parent,updatedAt > gh_repo_info.json')


    print(packages)
    pprint(packages)




if __name__ == "__main__":
    process_packages(clone=True)
