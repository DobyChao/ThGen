import argparse
import json
import os
import re
import subprocess



def generate_json(script_path, args_path=None):
    # Run the script with the -h option and capture the output
    result = subprocess.run(['python', script_path, '-h'], capture_output=True, text=True)

    # Split the output into lines
    lines = result.stdout.split('\n')

    # The first line is the script's description
    description = lines[0]

    # The rest of the lines are the arguments
    args_lines = lines[1:]

    # Initialize the list of arguments
    args = []

    # Regular expression to match argument lines
    arg_line_re = re.compile(r'^\s*--(\w+)\s*(\w*)\s*(.*)$')

    # Process each line
    for line in args_lines:
        match = arg_line_re.match(line)
        if match:
            # If the line matches the regular expression, it's an argument
            name, type_, help_ = match.groups()
            # If the type is not specified, assume it's a string
            if type_ == '':
                type_ = 'str'
            # Add the argument to the list
            args.append({'name': name, 'help': help_})

    script_name = os.path.basename(script_path).split('.')[0]

    # Construct the JSON structure
    json_structure = {
        script_name: {
            'entry': script_path,
            'description': description,
            'args': args
        }
    }

    if args_path:
        if os.path.exists(args_path):
            print(f'Updating existing JSON file: {args_path}')
            with open(args_path, 'r') as f:
                existing_json = json.load(f)
                existing_json.update(json_structure)
                json_structure = existing_json

        print(f'Writing JSON to file: {args_path}')
        with open(args_path, 'w') as f:
            json.dump(json_structure, f, indent=2)

    # Convert the JSON structure to a JSON string
    json_string = json.dumps(json_structure, indent=2)

    return json_string


# Add command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--script_path', type=str, help='Path to the script to generate JSON for')
parser.add_argument('--args_path', type=str, default="./extensions/arguments.json", help='Path to the file to write the JSON to')
args = parser.parse_args()

# Generate the JSON
json_string = generate_json(args.script_path, args.args_path)

# Print the JSON
print(json_string)
