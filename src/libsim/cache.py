import shutil
from .config import config
from pathlib import Path

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
        files: A dictionary where keys are file paths (relative to the project root,
               e.g., 'libsim/foo/bar.py') and values are the Python code to save.
    """
    if not config.use_cache:
        return

    for file_path, code in files.items():
        path_obj = Path(file_path)

        # The llm will return paths like 'libsim/foo/bar.py'. We need to handle this.
        # We expect the first part to be 'libsim'
        if not path_obj.parts or path_obj.parts[0] != 'libsim':
            print(f"[libsim] Warning: cannot handle cache path {file_path}")
            continue

        relative_path = Path(*path_obj.parts[1:])
        full_path = config.cache_dir / relative_path

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            full_path.write_text(code)
            # Ensure __init__.py exists in all parent dirs up to the cache root.
            p = full_path.parent
            while p.is_relative_to(config.cache_dir) and p != config.cache_dir:
                (p / "__init__.py").touch(exist_ok=True)
                p = p.parent

        except IOError as e:
            print(f"[libsim] Error writing to cache file {full_path}: {e}")