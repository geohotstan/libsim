import shutil
from .config import config

def remove_module_from_cache(module_name: str):
    """
    Removes a module's cache directory.
    """
    if not config.use_cache:
        return

    parts = module_name.split('.')[1:]
    if not parts: return

    package_dir_in_cache = config.cache_dir.joinpath(*parts)
    if package_dir_in_cache.exists():
        shutil.rmtree(package_dir_in_cache)

def save_code_to_cache(files: dict[str, str]):
    """
    Saves multiple code files to the file-based cache.

    Args:
        files: A dictionary where keys are file paths (relative to the cache root,
               e.g., 'foo/bar.py') and values are the Python code to save.
    """
    if not config.use_cache:
        return

    for file_path, code in files.items():
        full_path = config.cache_dir / file_path

        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            full_path.write_text(code)
        except IOError as e:
            print(f"[libsim] Error writing to cache file {full_path}: {e}")