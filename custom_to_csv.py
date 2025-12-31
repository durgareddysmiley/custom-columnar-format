import sys
import os
import csv
import argparse
from reader import CCFReader

def convert_ccf_to_csv(ccf_path, csv_path, columns=None):
    if not os.path.exists(ccf_path):
        print(f"Error: Input file '{ccf_path}' not found.")
        sys.exit(1)

    print(f"Converting '{ccf_path}' to '{csv_path}'...")
    
    try:
        reader = CCFReader(ccf_path)
        
        # Determine columns to read
        if columns:
            cols_to_read = columns
        else:
            cols_to_read = [name for name, _ in reader.schema]
            
        vals = reader.read_columns(cols_to_read)
        nrows = reader.nrows
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(cols_to_read)
            
            for i in range(nrows):
                row = []
                for h in cols_to_read:
                    if h in vals and i < len(vals[h]):
                        row.append(str(vals[h][i]))
                    else:
                        row.append("")
                csv_writer.writerow(row)
        print("Conversion successful.")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert CCF file to CSV.")
    parser.add_argument("input", help="Path to input .ccf file")
    parser.add_argument("output", help="Path to output .csv file")
    parser.add_argument("--columns", help="Comma-separated list of columns to extract (e.g. 'name,age')")
    
    args = parser.parse_args()
    
    cols = args.columns.split(",") if args.columns else None
    convert_ccf_to_csv(args.input, args.output, cols)

if __name__ == "__main__":
    main()
