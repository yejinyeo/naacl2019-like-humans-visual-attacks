# SAMPLE USAGE:
# python3 unicode_extractor.py NamesList.txt mychars.txt

import re
import argparse

def extract_unicode_characters(input_file, output_file):
    """
    Extract Unicode characters from an input file containing Unicode codepoints
    and save them line by line in an output file.
    
    Parameters:
    - input_file (str): Path to the input file containing Unicode codepoints.
    - output_file (str): Path to the output file to save extracted characters.
    """
    characters = []
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r'^([0-9A-F]{4,6})', line)
            if match:
                codepoint = int(match.group(1), 16)
                try:
                    characters.append(chr(codepoint))
                except ValueError:
                    pass  # Skip invalid Unicode points

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(characters))

    print(f"Extracted {len(characters)} characters to {output_file}")

if __name__ == "__main__":
    # Argument parsing for input and output file
    parser = argparse.ArgumentParser(description="Extract Unicode characters from a text file.")
    parser.add_argument("input_file", help="Path to the input file containing Unicode codepoints (e.g., NamesList.txt)")
    parser.add_argument("output_file", help="Path to the output file to save extracted characters (e.g., mychars.txt)")
    
    args = parser.parse_args()

    # Run the function with provided arguments
    extract_unicode_characters(args.input_file, args.output_file)
