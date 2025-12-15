import struct
import zlib


MAGIC = b"CCF"


class CCFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.schema = []
        self.column_offsets = {}
        self.row_count = 0

        self._parse_file()

    def _parse_file(self):
        """Parse header and schema, record column offsets."""
        with open(self.file_path, "rb") as f:
            # ---- Header ----
            magic = f.read(3)
            if magic != MAGIC:
                raise ValueError("Not a valid CCF file")

            version = struct.unpack("<I", f.read(4))[0]
            column_count = struct.unpack("<I", f.read(4))[0]
            self.row_count = struct.unpack("<I", f.read(4))[0]

            # ---- Schema ----
            for _ in range(column_count):
                name_len = struct.unpack("<I", f.read(4))[0]
                name = f.read(name_len).decode("utf-8")

                type_len = struct.unpack("<I", f.read(4))[0]
                dtype = f.read(type_len).decode("utf-8")

                value_count = struct.unpack("<I", f.read(4))[0]

                self.schema.append((name, dtype, value_count))

            # ---- Column offsets ----
            for name, dtype, count in self.schema:
                offset = f.tell()  # 🔥 THIS IS COLUMN PRUNING
                comp_size = struct.unpack("<I", f.read(4))[0]
                f.seek(comp_size, 1)

                self.column_offsets[name] = (offset, dtype, count)

    def _decode_column(self, data, dtype, count):
        """Decode binary column data."""
        values = []
        pos = 0

        if dtype == "int":
            for _ in range(count):
                values.append(struct.unpack("<i", data[pos:pos+4])[0])
                pos += 4

        elif dtype == "float":
            for _ in range(count):
                values.append(struct.unpack("<d", data[pos:pos+8])[0])
                pos += 8

        else:  # string
            for _ in range(count):
                length = struct.unpack("<I", data[pos:pos+4])[0]
                pos += 4
                values.append(data[pos:pos+length].decode("utf-8"))
                pos += length

        return values

    def read_all(self):
        """Read entire file (all columns)."""
        result = {}

        with open(self.file_path, "rb") as f:
            for name, (offset, dtype, count) in self.column_offsets.items():
                f.seek(offset)

                comp_size = struct.unpack("<I", f.read(4))[0]
                compressed = f.read(comp_size)

                raw = zlib.decompress(compressed)
                result[name] = self._decode_column(raw, dtype, count)

        return result

    def read_columns(self, column_names):
        """Read only selected columns (column pruning)."""
        result = {}

        with open(self.file_path, "rb") as f:
            for name in column_names:
                if name not in self.column_offsets:
                    raise ValueError(f"Column not found: {name}")

                offset, dtype, count = self.column_offsets[name]
                f.seek(offset)  # 🔥 SEEK TO COLUMN ONLY

                comp_size = struct.unpack("<I", f.read(4))[0]
                compressed = f.read(comp_size)

                raw = zlib.decompress(compressed)
                result[name] = self._decode_column(raw, dtype, count)

        return result
