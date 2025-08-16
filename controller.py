import sys

from config import OPENAPI_STUB_DIR

sys.path.append(OPENAPI_STUB_DIR)


def test_api(var):
    """Return a variable in the form of a JSON."""
    return {"Variable": var}
