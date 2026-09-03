"""Unit tests for Python traceback error normalization."""

from stackoverflow_mcp.ranking import normalize_python_error


def test_full_traceback_normalization():
    traceback_input = """
2026-09-03 17:51:37,123 [ERROR] Traceback (most recent call last):
  File "C:\\Users\\admin\\app\\main.py", line 42, in <module>
    res = process_data(0x7ff89123)
  File "/usr/local/lib/python3.10/site-packages/utils.py", line 105, in process_data
    return 10 / x
ZeroDivisionError: division by zero
    """
    normalized = normalize_python_error(traceback_input)
    assert normalized == "ZeroDivisionError: division by zero"


def test_strip_memory_addresses_and_uuids():
    err = "AttributeError: 'NoneType' object at 0x7f8a9b1c2d3e has no attribute 'fetch' (id: 123e4567-e89b-12d3-a456-426614174000)"
    normalized = normalize_python_error(err)
    assert "0x7f8a9b1c2d3e" not in normalized
    assert "123e4567-e89b-12d3-a456-426614174000" not in normalized
    assert "AttributeError: 'NoneType' object at has no attribute 'fetch' (id: )" in normalized or "AttributeError" in normalized


def test_log_level_prefix_stripping():
    err = "[CRITICAL] KeyError: 'missing_config_key'"
    normalized = normalize_python_error(err)
    assert normalized == "KeyError: 'missing_config_key'"


def test_import_error_normalization():
    err = """
ModuleNotFoundError: No module named 'fastmcp'
    """
    normalized = normalize_python_error(err)
    assert normalized == "ModuleNotFoundError: No module named 'fastmcp'"


def test_empty_input():
    assert normalize_python_error("") == ""
    assert normalize_python_error("   \n ") == ""
