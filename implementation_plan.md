Implementation Plan - Refactor Custom Columnar Format
The goal is to address the user feedback by professionalizing the codebase, ensuring a single unified interface, robust error handling, and proper dependency management. Although the codebase currently features 
writer.py
 and 
reader.py
 which are cleaner than the feedback implies, we will consolidate the ad-hoc CLI scripts into a single tool and add formal testing.

User Review Required
NOTE

The current codebase appears to have already addressed some of the feedback (e.g., 
SPEC.md
 matches the binary format, 
constants.py
 exists). This plan focuses on "Senior-Level" improvements: unifying the CLI, adding formal tests, and ensuring robustness.

Proposed Changes
1. Unified CLI (ccf.py) [NEW]
Replace 
csv_to_custom.py
 and 
custom_to_csv.py
 with a single entry point ccf.py using argparse.

Subcommands:
pack: CSV -> CCF
unpack: CCF -> CSV (with column selection)
inspect: View metadata/schema (new feature, helpful for debugging)
2. Core Library Improvements
reader.py
 & 
writer.py
:
Add custom exceptions (e.g., CCFError, SchemaMismatchError).
Improve docstrings and type hints.
Ensure robust file closing (already using context managers, but verify exception paths).
3. Cleanup
Delete: 
csv_to_custom.py
, 
custom_to_csv.py
 (replaced by ccf.py).
4. Dependencies
requirements.txt
: Add pytest (for testing).
5. Testing
test_ccf.py [NEW]: Convert 
verify.py
 into a proper unittest or pytest suite.
Test int, float, string types.
Test selective reading.
Test edge cases (empty files, nulls).
6. Documentation
SPEC.md
: Minor polish to ensure it perfectly matches the implementation.
Verification Plan
Automated Tests
Run the newly created test suite:

python -m pytest test_ccf.py
(Or python -m unittest test_ccf.py if we stick to stdlib, but pytest is preferred for output).

Manual Verification
Test the new CLI:

# Pack
python ccf.py pack sample.csv output.ccf
# Inspect
python ccf.py inspect output.ccf
# Unpack
python ccf.py unpack output.ccf result.csv --columns name,score