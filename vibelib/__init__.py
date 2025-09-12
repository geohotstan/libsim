import sys
from .importer import VibeLibFinder

# When this package is imported, add our custom finder to the meta_path.
# We check to make sure it's not already there to avoid duplicates.
if not any(isinstance(finder, VibeLibFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, VibeLibFinder())

print("vibelib custom importer has been initialized.")
