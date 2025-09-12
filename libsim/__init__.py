import sys
from .importer import LibSimFinder

# When this package is imported, we immediately install our custom
# import finder into Python's import machinery.
# This is the entry point that makes all the magic happen.
sys.meta_path.insert(0, LibSimFinder())