"""
Script to convert a data file into a Python dictionary definition.
- Dictionary: str key, value is list of strings
- Reads file, finds 'Param Lights' section, parses until 'Old X-Plane 8 Lights'
- Outputs a .txt file with Python code defining the dictionary
"""
import sys

def convert_file_to_dict(input_path, output_path):
    data_dict = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        found_section = False
        while True:
            line = f.readline()
            if not line:
                break
            if not found_section:
                if line.strip().startswith("Param Lights (Light name, followed by parameters required)"):
                    found_section = True
                    f.readline()  # skip next line
                    break
        if not found_section:
            print("Section header not found.")
            return
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            if line.strip().startswith("Old X-Plane 8 Lights"):
                break
            if not line.strip():
                continue
            key = line.strip()
            value_line = f.readline()
            if not value_line:
                break
            value = value_line.strip().split()
            data_dict[key] = value
    # Write output as Python code
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("# Auto-generated dictionary from data file\n")
        out.write("param_lights_dict = ")
        out.write(repr(data_dict))
        out.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_param_lights.py <input_file> <output_txt>")
    else:
        convert_file_to_dict(sys.argv[1], sys.argv[2])
