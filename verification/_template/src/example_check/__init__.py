"""Illustrative consumer-specific verification module."""
from cad_verification import require_equal

def verify_body_count(*, expected: int, actual: int):
    """Verify an explicitly supplied expectation against measured evidence."""
    return require_equal(expected, actual, label="body count")
