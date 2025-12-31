import struct
import zlib
from typing import List, Any
from constants import MAGIC, VERSION, TYPE_INT, TYPE_FLOAT, TYPE_STRING
from exceptions import CCFError

def infer_type(value: str) -> int:
    """
    Infer the data type of a single string value.
    
    Args:
        value: The string value to inspect.
        
    Returns:
        One of TYPE_INT, TYPE_FLOAT, or TYPE_STRING.
    """
    try:
        int(value)
        return TYPE_INT
    except ValueError:
        pass

    try:
        float(value)
        return TYPE_FLOAT
    except ValueError:
        pass

    return TYPE_STRING


def resolve_column_type(values: List[str]) -> int:
    """
    Resolve the type for a whole column based on its values.
    
    Logic:
    - If any value is a string that cannot be parsed as number, the whole column is STRING.
    - If any value is a float (and no strings), the whole column is FLOAT.
    - Otherwise, if all are integers, the column is INT.
    
    Args:
        values: List of string values for the column.
        
    Returns:
        The resolved type ID for the column.
    """
    current_type = TYPE_INT
    for v in values:
        t = infer_type(v)
        if t == TYPE_STRING:
            return TYPE_STRING
        if t == TYPE_FLOAT and current_type == TYPE_INT:
            current_type = TYPE_FLOAT
    return current_type


class CCFWriter:
    """
    Writer class for the Custom Columnar Format (CCF).
    Handles serialization of tabular data into a compressed, columnar binary format.
    """
    def __init__(self, output_file: str):
        self.output_file = output_file

    def write(self, headers: List[str], rows: List[List[str]]) -> None:
        """
        Writes data to the CCF file.
        
        Args:
            headers: List of column names.
            rows: List of rows, where each row is a list of string values (as read from CSV).
            
        Raises:
            IOError: If file writing fails.
        """
        if not rows:
             # Handle empty case: create a dummy file with no rows
             ncols = len(headers)
             nrows = 0
             cols = [[] for _ in headers]
             col_types = [TYPE_STRING for _ in headers] # default
        else:
            ncols = len(headers)
            nrows = len(rows)

            # Transpose to columns
            cols = list(zip(*rows))
            
            # Infer types
            col_types = []
            for col in cols:
                col_types.append(resolve_column_type(col))

        with open(self.output_file, 'wb') as f:
            # 1. Header
            f.write(MAGIC)
            f.write(struct.pack('<B', VERSION))
            f.write(struct.pack('<I', ncols))
            f.write(struct.pack('<Q', nrows))

            # 2. Schema
            for name, dtype in zip(headers, col_types):
                name_bytes = name.encode('utf-8')
                f.write(struct.pack('<H', len(name_bytes)))
                f.write(name_bytes)
                f.write(struct.pack('<B', dtype))

            # 3. Reserve space for Column Metadata Table
            # Each entry: Offset (8), CompressedSize (8), UncompressedSize (8) = 24 bytes
            meta_start_pos = f.tell()
            for _ in range(ncols):
                f.write(struct.pack('<QQQ', 0, 0, 0))

            # 4. Data Blocks
            col_meta_info = []

            for i, (col_data, dtype) in enumerate(zip(cols, col_types)):
                start_offset = f.tell()
                
                raw_bytes = b''
                if dtype == TYPE_INT:
                    for v in col_data:
                        try:
                            val = int(v)
                        except ValueError:
                            val = 0
                        raw_bytes += struct.pack('<i', val)
                elif dtype == TYPE_FLOAT:
                    for v in col_data:
                        try:
                            val = float(v)
                        except ValueError:
                            val = 0.0
                        raw_bytes += struct.pack('<d', val)
                else: # TYPE_STRING
                    # Format: Use the offset approach
                    # [offset1, offset2, ... offsetN] [string_data_blob]
                    offsets = []
                    blob = b''
                    curr_blob_offset = 0
                    for v in col_data:
                        b = v.encode('utf-8')
                        curr_blob_offset += len(b)
                        offsets.append(curr_blob_offset)
                        blob += b
                    
                    for o in offsets:
                        raw_bytes += struct.pack('<I', o)
                    raw_bytes += blob

                compressed = zlib.compress(raw_bytes)
                f.write(compressed)

                col_meta_info.append((start_offset, len(compressed), len(raw_bytes)))

            # 5. Fill Metadata Table
            f.seek(meta_start_pos)
            for offset, csize, usize in col_meta_info:
                f.write(struct.pack('<QQQ', offset, csize, usize))
