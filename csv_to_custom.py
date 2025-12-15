import csv
import struct
import zlib
import sys

MAGIC = b'CCF1'
VERSION = 1

TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_STRING = 3


def infer_type(value):
    try:
        int(value)
        return TYPE_INT
    except:
        try:
            float(value)
            return TYPE_FLOAT
        except:
            return TYPE_STRING


def write_custom(csv_file, output_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    ncols = len(headers)
    nrows = len(rows)

    cols = list(zip(*rows))
    types = [infer_type(col[0]) for col in cols]

    with open(output_file, 'wb') as f:

        # ---------- HEADER ----------
        f.write(MAGIC)
        f.write(struct.pack('<B', VERSION))
        f.write(struct.pack('<I', ncols))
        f.write(struct.pack('<Q', nrows))

        # ---------- SCHEMA ----------
        for name, dtype in zip(headers, types):
            name_bytes = name.encode('utf-8')
            f.write(struct.pack('<H', len(name_bytes)))
            f.write(name_bytes)
            f.write(struct.pack('<B', dtype))

        meta_pos = f.tell()

        # Placeholder for column metadata
        for _ in range(ncols):
            f.write(struct.pack('<QQQ', 0, 0, 0))

        col_meta = []

        # ---------- DATA BLOCKS ----------
        for col, dtype in zip(cols, types):
            start = f.tell()

            raw = b''

            if dtype == TYPE_INT:
                for v in col:
                    raw += struct.pack('<i', int(v))

            elif dtype == TYPE_FLOAT:
                for v in col:
                    raw += struct.pack('<d', float(v))

            else:  # STRING
                offsets = []
                blob = b''
                cur = 0
                for v in col:
                    b = v.encode('utf-8')
                    cur += len(b)
                    offsets.append(cur)
                    blob += b

                for o in offsets:
                    raw += struct.pack('<I', o)
                raw += blob

            compressed = zlib.compress(raw)

            f.write(compressed)

            col_meta.append((start, len(compressed), len(raw)))

        # ---------- WRITE METADATA ----------
        f.seek(meta_pos)
        for offset, csize, usize in col_meta:
            f.write(struct.pack('<QQQ', offset, csize, usize))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_custom.py input.csv output.ccf")
        sys.exit(1)

    write_custom(sys.argv[1], sys.argv[2])
