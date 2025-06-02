# setup.py for pyWannier90 (fallback for older pip versions)
# Note: Modern installations should use pyproject.toml with scikit-build-core

import sys
from pathlib import Path

# For modern pip (>=10.0), this file should not be needed
# as pyproject.toml will be used instead
if sys.version_info >= (3, 8):
    try:
        # Try to use the modern build backend
        from scikit_build_core import build
        print("Using modern scikit-build-core backend")
    except ImportError:
        print("Warning: scikit-build-core not available, falling back to setuptools")
        print("Consider upgrading pip and using: pip install -e .")

# Fallback setup.py for compatibility
from setuptools import setup

if __name__ == "__main__":
    # This setup.py is mainly for development and compatibility
    # The actual build configuration is in pyproject.toml
    setup(
        name="pyWannier90",
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
    )
