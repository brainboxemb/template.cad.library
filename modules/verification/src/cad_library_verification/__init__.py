"""Consumer-specific CAD verification checks."""

def _require_equal(expected, actual, *, label):
    from cad_verification import require_equal

    return require_equal(expected, actual, label=label)


def verify_body_count(*, expected: int, actual: int):
    """Delegate an explicit body-count expectation to the verification library."""
    return _require_equal(expected, actual, label="body count")
