# Custom Columnar Format (CCF) – Specification

## Overview

This document defines the custom binary columnar file format (CCF).
The format is designed to store tabular data in a column-oriented layout
to enable efficient analytical queries and selective column reads.

## File Layout

The CCF file is a **binary file** with little-endian byte order.

The logical layout is:

1.  **Header** (Fixed size)
2.  **Schema Definition** (Variable size)
3.  **Column Metadata Table** (Fixed-size entries per column)
4.  **Column Data Blocks** (Compressed blobs)

---

## 1. Header Structure

The header appears at the beginning of the file.

| Field | Size | Type | Value / Description |
| :--- | :--- | :--- | :--- |
| Magic Number | 4 bytes | Bytes | `CCF1` (0x43 0x43 0x46 0x31) |
| Version | 1 byte | UInt8 | Format version (Currently 1) |
| Column Count | 4 bytes | UInt32 | Total number of columns |
| Row Count | 8 bytes | UInt64 | Total number of rows |

---

## 2. Schema Metadata

Immediately following the header is the schema definition, which describes the name and type of each column.
The schema entries appear in the order of the columns.

For each column:

| Field | Size | Type | Description |
| :--- | :--- | :--- | :--- |
| Name Length | 2 bytes | UInt16 | Length of the column name in bytes |
| Name | Variable | Bytes | UTF-8 encoded column name |
| Data Type | 1 byte | UInt8 | `1`=Int, `2`=Float, `3`=String |

---

## 3. Column Metadata Table

After the schema, there is a reserved table containing location information for each column's data block. This allows O(1) seeking to any column.

For each column (in order):

| Field | Size | Type | Description |
| :--- | :--- | :--- | :--- |
| Offset | 8 bytes | UInt64 | Absolute byte offset to the start of the data block |
| Compressed Size | 8 bytes | UInt64 | Size of the compressed data block in bytes |
| Uncompressed Size | 8 bytes | UInt64 | Size of the uncompressed data in bytes |

Total size of this table = `Column Count * 24 bytes`.

---

## 4. Column Data Blocks

The actual data for each column is stored as a contiguous, compressed block.

-   **Compression**: Each block is compressed using **zlib**.
-   **Storage**: The reader seeks to `Offset` and reads `Compressed Size` bytes.

### Uncompressed Data Layout

Once decompressed, the data is laid out according to its type:

#### Integer (Type 1)
-   Sequence of 32-bit signed integers (Little Endian).
-   Size = `Row Count * 4` bytes.

#### Float (Type 2)
-   Sequence of 64-bit IEEE 754 floating-point numbers (Little Endian).
-   Size = `Row Count * 8` bytes.

#### String (Type 3)
-   **Offsets Section**: Sequence of `Row Count` 32-bit unsigned integers. Each integer represents the cumulative end offset of a string in the blob.
-   **Blob Section**: Concatenated UTF-8 bytes of all strings.

**Example String Decoding**:
To read the i-th string:
-   Read `Offset[i]` (End of current string).
-   Read `Offset[i-1]` (Start of current string, or 0 if i=0).
-   Slice `Blob[Start:End]`.

---

## Constants

-   **Magic**: `b'CCF1'`
-   **Version**: `1`
-   **Type Int**: `1`
-   **Type Float**: `2`
-   **Type String**: `3`
