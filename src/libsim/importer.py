
import importlib.abc
import importlib.util
import inspect
import re
from types import ModuleType
from pathlib import Path

from .llm import invoke_llm
from .config import config
from . import cache

def get_caller_source_code():
    """
    Walks the stack to find the source code of the module that
    initiated the import call.
    """
    for frame_info in inspect.stack():
        module = inspect.getmodule(frame_info.frame)
        if module:
            module_name = module.__name__
            if not module_name.startswith('libsim') and not module_name.startswith('importlib'):
                try:
                    with open(frame_info.filename, 'r') as f:
                        return f.read()
                except (FileNotFoundError, TypeError):
                    return None
    return None

def get_caller_libsim_imports(source_code):
    if source_code is None:
        return []
    imports = re.findall(r'from\s+(libsim(?:\.\w+)+)\s+import', source_code)
    imports += re.findall(r'import\s+(libsim(?:\.\w+)+)', source_code)
    simple_froms = re.findall(r'from\s+libsim\s+import\s+([^\n]+)', source_code)
    for group in simple_froms:
        parts = group.split(',')
        for part in parts:
            name = part.strip().split()[0].strip('()')
            if name:
                imports.append(f'libsim.{name}')
    return [imp for imp in imports if imp != 'libsim.config']

class CallableModule(ModuleType):
    def __call__(self, *args, **kwargs):
        if hasattr(self, "_callable_func"):
            return self._callable_func(*args, **kwargs)
        raise TypeError(f"'{self.__name__}' module object is not directly callable.")

class LibSimLoader(importlib.abc.Loader):
    def __init__(self, fullname, generated_code):
        self.fullname = fullname
        self.generated_code = generated_code if generated_code else {}

    def create_module(self, spec):
        return CallableModule(spec.name)

    def exec_module(self, module):
        fullname = module.__name__
        parts = fullname.split('.')[1:]

        path_as_module = Path(*parts).with_suffix('.py')
        path_as_package = Path(*parts) / '__init__.py'

        code_to_exec = self.generated_code.get(str(path_as_package)) or self.generated_code.get(str(path_as_module))

        package_dir_in_cache = config.cache_dir.joinpath(*parts)
        module.__path__ = [str(package_dir_in_cache)]

        if code_to_exec:
            try:
                exec(code_to_exec, module.__dict__)
                function_name = fullname.split('.')[-1]
                main_func = module.__dict__.get(function_name)
                if callable(main_func):
                    module._callable_func = main_func
            except Exception as e:
                print(f"Error executing generated code for {fullname}: {e}")
                raise ImportError from e

class LibSimImporter(importlib.abc.MetaPathFinder):
    def __init__(self):
        self._generated_code = None
        self._is_generating = False

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('libsim') or fullname == 'libsim.config':
            return None

        if self._generated_code is None and not self._is_generating:
            self._is_generating = True

            caller_source = get_caller_source_code()
            libsim_imports = get_caller_libsim_imports(caller_source)

            if not libsim_imports:
                self._is_generating = False
                return None

            if config.debug >= 1:
                print(f"[libsim] Found imports: {libsim_imports}")
                print(f"[libsim] Generating code for all modules in a single LLM call.")

            try:
                self._generated_code = invoke_llm(caller_source, list(set(libsim_imports)))

                processed_code = {}
                for path, code in self._generated_code.items():
                    if path.startswith('libsim/'):
                        processed_code[path[len('libsim/'):]] = code
                    else:
                        processed_code[path] = code
                self._generated_code = processed_code

                cache.save_code_to_cache(self._generated_code)

            except Exception as e:
                print(f"Failed to generate code: {e}")
                self._is_generating = False
                return None

        return importlib.util.spec_from_loader(
            fullname,
            LibSimLoader(fullname, self._generated_code),
            is_package=True
        )
