import struct
import zlib
import csv
import sys
import argparse

MAGIC = b'CCF1'

TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_STRING = 3


def read_custom(file_path, selected=None):
    with open(file_path, 'rb') as f:

        if f.read(4) != MAGIC:
            raise ValueError("Invalid file format")

        version = struct.unpack('<B', f.read(1))[0]
        ncols = struct.unpack('<I', f.read(4))[0]
        nrows = struct.unpack('<Q', f.read(8))[0]

        schema = []
        for _ in range(ncols):
            l = struct.unpack('<H', f.read(2))[0]
            name = f.read(l).decode()
            dtype = struct.unpack('<B', f.read(1))[0]
            schema.append((name, dtype))

        meta = {}
        for name, dtype in schema:
            off, cs, us = struct.unpack('<QQQ', f.read(24))
            meta[name] = (off, cs, us, dtype)

        if selected is None:
            selected = [name for name, _ in schema]

        data = {}

        for name in selected:
            off, cs, _, dtype = meta[name]
            f.seek(off)
            raw = zlib.decompress(f.read(cs))

            values = []

            if dtype == TYPE_INT:
                for i in range(nrows):
                    values.append(struct.unpack_from('<i', raw, i * 4)[0])

            elif dtype == TYPE_FLOAT:
                for i in range(nrows):
                    values.append(struct.unpack_from('<d', raw, i * 8)[0])

            else:
                pos = 0
                offsets = []
                for _ in range(nrows):
                    offsets.append(struct.unpack_from('<I', raw, pos)[0])
                    pos += 4
                blob = raw[pos:]

                s = 0
                for e in offsets:
                    values.append(blob[s:e].decode())
                    s = e

            data[name] = values

        return data, nrows


def write_csv(out_file, data, nrows):
    headers = list(data.keys())

    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for i in range(nrows):
            w.writerow([data[h][i] for h in headers])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--columns")
    args = parser.parse_args()

    cols = args.columns.split(",") if args.columns else None

    data, nrows = read_custom(args.input, cols)
    write_csv(args.output, data, nrows)


if __name__ == "__main__":
    main()
