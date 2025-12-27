import sys
import os
import csv
from writer import CCFWriter

def convert_csv_to_ccf(csv_path, ccf_path):
    if not os.path.exists(csv_path):
        print(f"Error: Input file '{csv_path}' not found.")
        sys.exit(1)

    print(f"Converting '{csv_path}' to '{ccf_path}'...")
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                headers = []
            rows = list(reader)
            
        writer = CCFWriter(ccf_path)
        writer.write(headers, rows)
        print("Conversion successful.")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_to_custom.py <input.csv> <output.ccf>")
        sys.exit(1)
    
    convert_csv_to_ccf(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
