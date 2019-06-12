# conftest.py

"""
if hasattr(sys, "_called_from_test"):
    # called from within a test run
    ...
else:
    # called "normally"
    ...
"""


def pytest_configure(config):
    import sys

    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys

    del sys._called_from_test
