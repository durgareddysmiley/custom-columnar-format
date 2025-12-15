# Custom Columnar Format (CCF) – Specification


## Overview

This document defines a custom columnar file format called CCF.
The format is designed to store tabular data in a column-oriented way
instead of the traditional row-based CSV format.

The main goal is to improve column-wise access and understanding of
how columnar storage works.


## File Layout

The CCF file is a text-based file.

The file is divided into the following sections in order:

1. Header
2. Schema
3. Column Data

Each section appears exactly once and in the same order.


## Header Structure

The header appears at the beginning of the file and contains
basic information about the file.

The header includes:
- Magic string to identify the file format
- Version number of the format

Format:
CCF|<version>

Example:
CCF|1


## Schema Format

The schema defines metadata for each column.

For every column, the following information is stored:
- Column name
- Data type
- Number of values in the column

Each column schema is stored on a separate line.

Format:
<column_name>|<data_type>|<value_count>

Example:
id|int|3
name|string|3
age|int|3


## Supported Data Types

The following data types are supported in version 1:

- int    : Integer values
- float  : Floating-point values
- string : Text values

All values are stored in text form.


## Column Data Storage

After the schema section, column data is stored.

Data is written column by column, not row by row.

For each column:
- All values of the column are written
- One value per line
- Values appear in the same order as in the original CSV

Columns are separated by a blank line.


## Compression Method

No compression is applied in version 1 of the format.

All values are stored as plain text.


## Endianness

Endianness is not applicable because the format is text-based.


## Complete Example

CSV Input:
id,name,age
1,Alice,20
2,Bob,21
3,Carol,22
CCF Output:
CCF|1

id|int|3
name|string|3
age|int|3

1
2
3

Alice
Bob
Carol

20
21
22
