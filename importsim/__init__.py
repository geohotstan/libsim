import sys
from .importer import ImportSimFinder

# When this package is imported, add our custom finder to the meta_path.
# We check to make sure it's not already there to avoid duplicates.
if not any(isinstance(finder, ImportSimFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, ImportSimFinder())

print("importsim custom importer has been initialized.")
