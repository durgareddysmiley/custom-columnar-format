class CCFError(Exception):
    """Base exception for Custom Columnar Format errors."""
    pass

class CCFMagicError(CCFError):
    """Raised when file magic bytes do not match."""
    pass

class CCFVersionError(CCFError):
    """Raised when file version is unsupported."""
    pass

class CCFColumnError(CCFError):
    """Raised when a requested column is not found."""
    pass

class CCFSchemaError(CCFError):
    """Raised when there is an issue with the schema."""
    pass
