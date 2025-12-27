# Walkthrough

This document explains the end-to-end flow of the Custom Columnar Format (CCF).

## Steps
1. CSV is converted to CCF using csv_to_custom.py
2. Data is written using CCFWriter
3. Metadata table enables O(1) column access
4. Reader reconstructs CSV using custom_to_csv.py

Verification has been completed successfully.
