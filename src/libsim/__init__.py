
import sys
from .importer import LibSimImporter
from .config import config

# Install the importer when the package is imported.
if not any(isinstance(finder, LibSimImporter) for finder in sys.meta_path):
    sys.meta_path.insert(0, LibSimImporter())
