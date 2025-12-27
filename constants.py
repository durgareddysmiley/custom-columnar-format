# Custom Columnar Format (CCF) Constants

MAGIC = b'CCF1'
VERSION = 1

# Data Types
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_STRING = 3

# String representation for debugging/schema display
TYPE_MAP = {
    TYPE_INT: "int",
    TYPE_FLOAT: "float",
    TYPE_STRING: "string"
}
