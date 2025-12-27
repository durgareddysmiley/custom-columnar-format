import struct
import zlib
from constants import MAGIC, VERSION, TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_MAP
from exceptions import CCFMagicError, CCFVersionError, CCFColumnError, CCFError

class CCFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.header = {}
        self.schema = [] # List of (name, dtype)
        self.col_meta = {} # name -> (offset, csize, usize)
        self.nrows = 0

        try:
            self._load_metadata()
        except (IOError, OSError) as e:
            raise CCFError(f"Failed to open or read file '{file_path}': {e}") from e

    def _load_metadata(self):
        with open(self.file_path, 'rb') as f:
            magic = f.read(4)
            if magic != MAGIC:
                raise CCFMagicError(f"Invalid file format: Magic bytes mismatch. Expected {MAGIC}, got {magic}")
            
            version = struct.unpack('<B', f.read(1))[0]
            if version != VERSION:
                raise CCFVersionError(f"Unsupported version: {version}. Expected {VERSION}.")
            
            self.header['version'] = version
            ncols = struct.unpack('<I', f.read(4))[0]
            self.nrows = struct.unpack('<Q', f.read(8))[0]
            self.header['ncols'] = ncols
            self.header['nrows'] = self.nrows

            # Read Schema
            for _ in range(ncols):
                l_bytes = f.read(2)
                if not l_bytes:
                     raise CCFError("Unexpected EOF while reading schema.")
                l = struct.unpack('<H', l_bytes)[0]
                name_bytes = f.read(l)
                if len(name_bytes) != l:
                     raise CCFError("Unexpected EOF while reading column name.")
                name = name_bytes.decode('utf-8')
                dtype = struct.unpack('<B', f.read(1))[0]
                self.schema.append((name, dtype))

            # Read Metadata Table
            # It follows strictly after schema
            for name, dtype in self.schema:
                meta_bytes = f.read(24)
                if len(meta_bytes) != 24:
                    raise CCFError("Unexpected EOF while reading column metadata.")
                offset, csize, usize = struct.unpack('<QQQ', meta_bytes)
                self.col_meta[name] = (offset, csize, usize, dtype)

    def read_columns(self, columns=None):
        """
        Reads specified columns.
        columns: list of names. If None, reads all.
        Returns: dict {col_name: [values]}
        """
        if columns is None:
            columns = [name for name, _ in self.schema]
        
        result = {}
        
        # Validate columns first
        for name in columns:
            if name not in self.col_meta:
                raise CCFColumnError(f"Column '{name}' not found in file. Available: {list(self.col_meta.keys())}")
        
        try:
            with open(self.file_path, 'rb') as f:
                for name in columns:
                    offset, csize, usize, dtype = self.col_meta[name]
                    
                    # Seek and Read
                    f.seek(offset)
                    compressed_data = f.read(csize)
                    if len(compressed_data) != csize:
                        raise CCFError(f"Incomplete data read for column '{name}'.")
                        
                    try:
                        raw_data = zlib.decompress(compressed_data)
                    except zlib.error as e:
                        raise CCFError(f"Decompression failed for column '{name}': {e}")
                    
                    if len(raw_data) != usize:
                         # Warn or error if size mismatch?
                         # For strict correctness, let's warn but proceed, or raise. 
                         # Let's verify strictly.
                         if len(raw_data) != usize:
                             raise CCFError(f"Size mismatch for column '{name}': expected {usize}, got {len(raw_data)}")

                    # Parse
                    result[name] = self._parse_column(raw_data, dtype, self.nrows)
        except (IOError, OSError) as e:
            raise CCFError(f"IO Error reading file: {e}") from e
        
        return result

    def _parse_column(self, raw_bytes, dtype, userid_nrows):
        values = []
        if dtype == TYPE_INT:
            expected_size = userid_nrows * 4
            if len(raw_bytes) < expected_size:
                 raise CCFError(f"Insufficient data for INT column. Expected {expected_size}, got {len(raw_bytes)}")
            # 4 bytes per int
            for i in range(userid_nrows):
                val = struct.unpack_from('<i', raw_bytes, i * 4)[0]
                values.append(val)
        
        elif dtype == TYPE_FLOAT:
            expected_size = userid_nrows * 8
            if len(raw_bytes) < expected_size:
                 raise CCFError(f"Insufficient data for FLOAT column. Expected {expected_size}, got {len(raw_bytes)}")
            # 8 bytes per double
            for i in range(userid_nrows):
                val = struct.unpack_from('<d', raw_bytes, i * 8)[0]
                values.append(val)
        
        elif dtype == TYPE_STRING:
            # [offset1 (4), offset2 (4)...] [blob]
            # Offsets count = nrows
            offsets_size = userid_nrows * 4
            if len(raw_bytes) < offsets_size:
                 raise CCFError(f"Insufficient data for STRING column offsets. Expected at least {offsets_size}, got {len(raw_bytes)}")
                 
            offsets = []
            pos = 0
            for _ in range(userid_nrows):
                o = struct.unpack_from('<I', raw_bytes, pos)[0]
                offsets.append(o)
                pos += 4
            
            blob_start_in_raw = pos
            blob = raw_bytes[blob_start_in_raw:]
            
            # Basic Bounds Check on offsets?
            # Max offset should be <= len(blob)
            if offsets and offsets[-1] > len(blob):
                 raise CCFError(f"String offset out of bounds. Max offset {offsets[-1]}, blob size {len(blob)}")
            
            start = 0
            for end in offsets:
                if end < start:
                     # safeguard
                     end = start
                s_bytes = blob[start:end]
                values.append(s_bytes.decode('utf-8'))
                start = end
        
        return values
