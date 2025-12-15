import csv
import struct
import zlib


MAGIC = b"CCF"
VERSION = 1


def infer_type(values):
    """Infer data type of a column."""
    try:
        for v in values:
            int(v)
        return "int"
    except ValueError:
        pass

    try:
        for v in values:
            float(v)
        return "float"
    except ValueError:
        pass

    return "string"


def encode_column(values, dtype):
    """Encode column values into binary."""
    data = b""

    for v in values:
        if dtype == "int":
            data += struct.pack("<i", int(v))
        elif dtype == "float":
            data += struct.pack("<d", float(v))
        else:  # string
            encoded = v.encode("utf-8")
            data += struct.pack("<I", len(encoded))
            data += encoded

    return data


def write_ccf(csv_path, out_path):
    """Convert CSV to custom columnar binary format."""

    # --- Read CSV ---
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    # --- Convert rows to columns ---
    columns = {h: [] for h in headers}
    for row in rows:
        for h, v in zip(headers, row):
            columns[h].append(v)

    # --- Write binary file ---
    with open(out_path, "wb") as f:
        # Header
        f.write(MAGIC)
        f.write(struct.pack("<I", VERSION))
        f.write(struct.pack("<I", len(headers)))  # column count
        f.write(struct.pack("<I", len(rows)))     # row count

        # Schema
        schema_info = []
        for name in headers:
            values = columns[name]
            dtype = infer_type(values)
            schema_info.append((name, dtype, values))

            name_bytes = name.encode("utf-8")
            type_bytes = dtype.encode("utf-8")

            f.write(struct.pack("<I", len(name_bytes)))
            f.write(name_bytes)

            f.write(struct.pack("<I", len(type_bytes)))
            f.write(type_bytes)

            f.write(struct.pack("<I", len(values)))

        # Column data
        for name, dtype, values in schema_info:
            encoded = encode_column(values, dtype)
            compressed = zlib.compress(encoded)

            f.write(struct.pack("<I", len(compressed)))
            f.write(compressed)
