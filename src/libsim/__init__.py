import sys

# --- Public API ---
from .config import config

# --- Initialization ---

from .importer import LibSimFinder

def _initialize():
    """
    Initializes the libsim environment.
    """
    # Create the cache directory if it doesn't exist
    config.cache_dir.mkdir(parents=True, exist_ok=True)

    # Add the cache directory to Python's path, so it can find cached modules.
    # We add it at the beginning to ensure it's checked first.
    sys.path.insert(0, str(config.cache_dir))

    # When this package is imported, we immediately install our custom
    # import finder into Python's import machinery.
    # This is the entry point that makes all the magic happen.
    sys.meta_path.insert(0, LibSimFinder())

_initialize()
