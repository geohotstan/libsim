from pathlib import Path

class _Config:
    """
    Central configuration for the libsim library.
    """
    def __init__(self):
        self.use_cache = True
        self.cache_dir = Path.home() / '.libsim'
        self.llm_model = "openrouter/x-ai/grok-4-fast:free"
        self.debug = 0  # 0=none, 1=basic, 2=verbose

# Singleton instance of the config
config = _Config()
