import os

def parse_description_file(file_path):
    """Parses a DESCRIPTION file and returns a dictionary of key-value pairs."""

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    parsed_data = {}
    current_key = None
    current_value = []

    with open(file_path, 'r') as file:
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

    return parsed_data


def main():
    input_file = "DESCRIPTION.txt"  # Path to the DESCRIPTION file

    # Parse the DESCRIPTION file
    parsed_data = parse_description_file(input_file)

    print(parsed_data['Title'])
    print(parsed_data['Description'])


if __name__ == "__main__":
    main()