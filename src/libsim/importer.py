import importlib.abc
import importlib.util
import inspect
import re
from types import ModuleType

from .llm import invoke_llm
from .config import config
from . import cache

def get_caller_source_code():
    """
    Walks the stack to find the source code of the module that
    initiated the import call.
    """
    # We are looking for the first frame that is NOT part of libsim or importlib
    for frame_info in inspect.stack():
        module = inspect.getmodule(frame_info.frame)
        if module:
            module_name = module.__name__
            if not module_name.startswith('libsim') and not module_name.startswith('importlib'):
                # We found the caller frame.
                try:
                    with open(frame_info.filename, 'r') as f:
                        return f.read()
                except (FileNotFoundError, TypeError):
                    # Fallback for special cases like interactive sessions
                    return None
    return None

def get_caller_libsim_imports(source_code):
    if source_code is None:
        return []
    # Find all imports from libsim
    # e.g., from libsim.foo.bar import baz
    imports = re.findall(r'from\s+(libsim(?:\.\w+)+)\s+import', source_code)
    # Find all direct imports of libsim modules
    # e.g., import libsim.foo.bar
    imports += re.findall(r'import\s+(libsim(?:\.\w+)+)', source_code)

    # Find imports like: from libsim import foo, bar as b, or from libsim import (foo, bar)
    simple_froms = re.findall(r'from\s+libsim\s+import\s+([^\n]+)', source_code)
    for group in simple_froms:
        parts = group.split(',')
        for part in parts:
            name = part.strip().split()[0].strip('()')
            if name:
                imports.append(f'libsim.{name}')

    return imports


class CallableModule(ModuleType):
    def __call__(self, *args, **kwargs):
        # This makes the module instance itself callable.
        # We look for a special attribute `_callable_func` which holds the
        # actual function to be called.
        if hasattr(self, "_callable_func"):
            return self._callable_func(*args, **kwargs)
        raise TypeError(f"'{self.__name__}' module object is not directly callable. Did you forget to define a main function?")


class LibSimLoader(importlib.abc.Loader):
    """
    The custom loader. Its job is to execute the dynamically generated code.
    It now handles both cache hits (loading from a file) and cache misses (generating with an LLM).
    """
    def __init__(self, fullname):
        self.fullname = fullname

    def create_module(self, spec):
        # We return our custom module type here.
        return CallableModule(spec.name)

    def exec_module(self, module):
        """
        This is the core of the magic!
        """
        try:
            fullname = module.__name__
            parts = fullname.split('.')[1:]
            if not parts: return

            # Since everything is a package, the module's code is in __init__.py
            # and its submodules are in the directory.
            package_dir_in_cache = config.cache_dir.joinpath(*parts)
            module.__path__ = [str(package_dir_in_cache)]

            caller_source = get_caller_source_code()
            libsim_imports = get_caller_libsim_imports(caller_source)
            if fullname not in libsim_imports and not any(i.startswith(fullname + '.') for i in libsim_imports):
                return

            # Always invoke LLM to check/update/generate code
            if config.debug >= 1:
                print(f"[libsim] Generating {fullname} with LLM.")

            cache.remove_module_from_cache(fullname)
            updated_files = invoke_llm(caller_source, fullname)

            files_to_cache = {f"libsim/{f}": code for f, code in updated_files.items()}
            cache.save_code_to_cache(files_to_cache)

            # The primary code for the module is in __init__.py
            for file_name, file_content in updated_files.items():
                exec(file_content, module.__dict__)

                function_name = fullname.split('.')[-1]
                main_func = module.__dict__.get(function_name)

                if callable(main_func):
                    module._callable_func = main_func


        except SyntaxError as e:
            print(f"LLM-generated code for {module.__name__} has a syntax error: {e}")
            raise ImportError(f"Failed to import {module.__name__} due to a syntax error in generated code.") from e
        except Exception as e:
            print(f"Failed to dynamically create module {module.__name__}: {e}")
            raise


class LibSimFinder(importlib.abc.MetaPathFinder):
    """
    The custom finder. Its job is to tell Python we can handle
    any import that starts with 'libsim.'.
    All libsim modules are treated as packages.
    """
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('libsim'):
            return None

        # Exclude libsim.config from our loader, it should always be loaded from its file.
        if fullname == 'libsim.config':
            return None

        # Since our loader handles both cached and generated modules, we always
        # return our custom loader for any 'libsim' import.
        return importlib.util.spec_from_loader(
            fullname,
            LibSimLoader(fullname),
            is_package=True
        )

