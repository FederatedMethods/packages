import os
from pprint import pprint
import re

def parse_description_file(file_path):
    """Parses a DESCRIPTION file and returns a dictionary of key-value pairs."""

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    parsed_data = {}
    current_key = None
    current_value = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue

            # Check if the line starts a new key-value pair
            if not line.startswith(" ") and ":" in line:
                # Save the previous key-value pair
                if current_key:
                    parsed_data[current_key] = "\n".join(current_value).strip()
                # Start a new key-value pair
                key, value = line.split(":", 1)
                current_key = key.strip()
                current_value = [value.strip()]
            else:
                # Continuation of the current value
                current_value.append(line.strip())

        # Save the last key-value pair
        if current_key:
            parsed_data[current_key] = "\n".join(current_value).strip()
    pprint(parsed_data)

    # Parse the Authors@R part if it is present
    if 'Authors@R' in parsed_data:
        print("Parsing Authors@R REGEX")
        authors_string = parsed_data['Authors@R']
        authors_string = authors_string.replace('\n', "")
        authors_string = authors_string.replace(" ", "")
        authors_string = authors_string.replace(",,", ",")

        # Sometimes there are multiple authors, sometimes just one. The regex is different for each case.
        if len(re.findall("c\(person\(", authors_string)) > 0:
            print("Multiple authors")
            authors_string = authors_string.replace("c(person(", "")
            authors_string = authors_string[:-2]
        else:
            authors_string = authors_string.replace("person(", "")
            authors_string = authors_string[:-1]

        temp = authors_string.split("),person(")

        parsed_data["Authors"] = []

        for this_author in temp:
            print("RAW: " + this_author)
            # Email
            email = re.findall("[email=]?\"([\w\-\.]+@[\w\-\.]+\.+[\w\-]+)\"", this_author)
            if len(email):
                # if there is an email then remove it from the string so we can parse the rest of the author info
                this_author = re.sub("[email]?=\"([\w\-\.]+@[\w\-\.]+\.+[\w\-]+)\"","", this_author)
                email = email[0]
            else:
                email = ""
            print("email: " + email)

            #ORCID
            orcid = re.findall("comment=c\(ORCID=\"([0-9]+-[0-9]+-[0-9]+-[0-9]+)\"\)", this_author)
            if len(orcid):
                this_author = re.sub("comment=c\(ORCID=\"([0-9]+-[0-9]+-[0-9]+-[0-9]+)\"\)","", this_author)
                orcid = orcid[0]
            else:
                orcid = ""
            print("orcid: " + orcid)

            #Role
            role = re.findall("role=c?\(?([\"\w+\",?]+)\)?", this_author)
            this_author = re.sub("role=c?\(?([\"\w+\",?]+)\)?","", this_author)
            print("role: " + str(role))

            # The only thing left should be the name, either with or without given/family
            this_author = this_author.replace(",,",",")
            temp = this_author.split(",")
            given = temp[0]
            given = given.replace("given=","").replace('"',"")
            print("given: " + given)
            family = temp[1]
            family = family.replace("family=","").replace('"',"")
            print("family: " + family)

            parsed_data["Authors"].append({"given":given, "family":family, "orcid":orcid, "role":role, "email":email})

            # Create a maintainer_string out of the relevant author
            if "cre" in str(role):
                print("IS MAINTAINER")
                parsed_data["maintainer_string"] = f"""{given} {family} ({email})"""

    elif 'Maintainer' in parsed_data:
        # The old way was to have an explicit Maintainer item.
        parsed_data['maintainer_string'] = parsed_data['Maintainer'].replace("<","").replace(">","")

    return parsed_data


def main():
    input_file = "./DESCRIPTION"  # Path to the DESCRIPTION file

    # Parse the DESCRIPTION file
    parsed_data = parse_description_file(input_file)

    print(parsed_data)

    print(parsed_data['Title'])
    print(parsed_data['Description'])
    print(parsed_data['Authors@R'])
    print("############")

    print(parsed_data)


if __name__ == "__main__":
    main()
