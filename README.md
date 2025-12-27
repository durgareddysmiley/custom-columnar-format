# Custom Columnar File Format


## Project Purpose

This project implements a simplified custom columnar file format to understand how modern analytical storage formats like Apache Parquet and ORC work internally. The goal is to store tabular data efficiently, enable compression, and support fast selective column reads for analytics workloads.


## File Format Idea

The custom file format stores data in a columnar layout instead of a row-based layout like CSV. Each column is written as a separate contiguous block in the file and compressed using the zlib compression algorithm. A binary header stores metadata such as schema information, number of rows, and byte offsets for each column, allowing the reader to directly seek to required columns.


## Selective Column Read

The reader supports selective column reads (column pruning). By using column offsets stored in the file header, the reader can directly seek to and decompress only the required columns without scanning the entire file. This significantly improves performance for analytical queries.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/durgareddysmiley/custom-columnar-format
    cd custom-columnar-format
    ```

2.  **Install dependencies** (required for running tests):
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The project can be used via the unified tool `ccf.py` or the specific conversion scripts.

### 1. Unified Tool (`ccf.py`)
```bash
# Pack
python ccf.py pack sample.csv output.ccf

# Inspect
python ccf.py inspect output.ccf

# Unpack
python ccf.py unpack output.ccf result.csv --columns name,score
```

### 2. Specific Scripts (Requirement Compliant)
If you prefer identifying tools by their specific function:

**Convert CSV to Custom Format**:
```bash
python csv_to_custom.py sample.csv output.ccf
```

**Convert Custom Format to CSV**:
```bash
python custom_to_csv.py output.ccf result.csv --columns name,score
```
