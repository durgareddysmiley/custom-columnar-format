import argparse
import sys
import os
import csv
from writer import CCFWriter
from reader import CCFReader
# Assume exceptions will be available, or catch generic ones for now until we add them.

def handle_pack(args):
    """Convert CSV to CCF"""
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    print(f"Packing '{args.input}' to '{args.output}'...")
    
    try:
        with open(args.input, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                headers = []
            rows = list(reader)
            
        writer = CCFWriter(args.output)
        writer.write(headers, rows)
        print("Done.")
    except Exception as e:
        print(f"Error packing file: {e}")
        sys.exit(1)

def handle_unpack(args):
    """Convert CCF to CSV"""
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    print(f"Unpacking '{args.input}' to '{args.output}'...")
    
    columns = args.columns.split(",") if args.columns else None
    
    try:
        reader = CCFReader(args.input)
        vals = reader.read_columns(columns)
        
        # Determine headers: use requested columns or all from schema
        if columns:
            headers = columns
        else:
            headers = [name for name, _ in reader.schema]
            
        nrows = reader.nrows
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(headers)
            
            for i in range(nrows):
                row = []
                for h in headers:
                    if h in vals and i < len(vals[h]):
                        row.append(str(vals[h][i]))
                    else:
                        row.append("")
                csv_writer.writerow(row)
        print("Done.")
        
    except Exception as e:
        print(f"Error unpacking file: {e}")
        sys.exit(1)

def handle_inspect(args):
    """View metadata of a CCF file"""
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    try:
        reader = CCFReader(args.input)
        print(f"File: {args.input}")
        print(f"Version: {reader.header.get('version')}")
        print(f"Rows: {reader.nrows}")
        print(f"Columns: {reader.header.get('ncols')}")
        print("\nSchema:")
        print(f"{'Name':<20} | {'Type':<10}")
        print("-" * 33)
        
        # We need a way to get type names. 
        # Since we might not have direct access to TYPE_MAP here without importing constants,
        # let's assume we can map it or import it.
        # But actually reader.schema has (name, dtype_int).
        # Let's import constants to be safe.
        from constants import TYPE_MAP
        
        for name, dtype in reader.schema:
            type_str = TYPE_MAP.get(dtype, "unknown")
            print(f"{name:<20} | {type_str:<10}")
            
    except Exception as e:
        print(f"Error inspecting file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Custom Columnar Format (CCF) Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Pack
    p_pack = subparsers.add_parser("pack", help="Convert CSV to CCF")
    p_pack.add_argument("input", help="Input CSV file")
    p_pack.add_argument("output", help="Output CCF file")
    p_pack.set_defaults(func=handle_pack)
    
    # Unpack
    p_unpack = subparsers.add_parser("unpack", help="Convert CCF to CSV")
    p_unpack.add_argument("input", help="Input CCF file")
    p_unpack.add_argument("output", help="Output CSV file")
    p_unpack.add_argument("--columns", help="Comma-separated list of columns to extract")
    p_unpack.set_defaults(func=handle_unpack)

    # Inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect CCF metadata")
    p_inspect.add_argument("input", help="Input CCF file")
    p_inspect.set_defaults(func=handle_inspect)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
