import sys
import importlib.abc
import importlib.util
from types import ModuleType
import os
import inspect
import litellm

# Set the model and API key. Using an environment variable for the key is best practice.
# LLM_MODEL = "openrouter/mistralai/mistral-7b-instruct:free"
# LLM_MODEL = "openrouter/z-ai/glm-4.5-air:free"
LLM_MODEL = "openrouter/deepseek/deepseek-chat-v3.1:free"

def get_caller_source_code():
    """
    Walks the stack to find the source code of the module that
    initiated the import call.
    """
    # We are looking for the first frame that is NOT part of importsim or importlib
    for frame_info in inspect.stack():
        module = inspect.getmodule(frame_info.frame)
        if module:
            module_name = module.__name__
            if not module_name.startswith('importsim') and not module_name.startswith('importlib'):
                # We found the caller frame.
                try:
                    with open(frame_info.filename, 'r') as f:
                        return f.read()
                except (FileNotFoundError, TypeError):
                    # Fallback for special cases like interactive sessions
                    return None
    return None


def invoke_llm(source_code, module_name):
    """
    Calls the LLM to generate Python code for the specified module name
    based on the provided source code context.
    """
    if not source_code:
        raise ImportError("Could not find the source code of the calling module.")

    prompt = f"""
You are an expert Python programmer acting as a code generator.
Your task is to write the Python code that will form the body of a new module. This code will be executed using `exec(your_code, module_namespace)`.

The user's code, which triggered this generation, is:
---
{source_code}
---

Based on the user's code, you must generate the Python code for the module named `{module_name}`.

**Instructions:**
1.  Analyze the user's code to determine what functions, classes, and variables are required.
2.  Define these objects directly. For example, if the user's code is `from importsim.hello import world` and then `world.greet()`, you (when generating the `importsim.hello` module) MUST generate a `world` object instance that has a `greet()` method. A class definition alone is not enough.
3.  **ABSOLUTELY DO NOT** use `import sys` or refer to `sys.modules`. The `exec` environment handles this. Your code should only contain the definitions of the required objects.
3.  **ABSOLUTELY DO NOT** import any external python library that is not in the standard python library.
4.  Your output MUST be a single, clean block of Python code, suitable for `exec`. Start the code with ```python and end it with ```. Do not include any other text or explanations.
5.  **IMPORTANT**: Ensure that you do not define global variables that have the same name as function parameters. This will cause a `SyntaxError`.

**Generated Python Code for the body of {module_name}:**
"""

    try:
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[{"content": prompt, "role": "user"}],
        )
        generated_text = response.choices[0].message.content.strip()
        #print("LLM generated text:")
        #print(generated_text)

        # This parsing logic is deliberately strict. We require the LLM to return
        # a single, clean python code block, as instructed in the prompt. This avoids
        # trying to clean up messy or conversational responses.
        start_tag = "```python"
        end_tag = "```"

        start_index = generated_text.find(start_tag)
        if start_index != -1:
            end_index = generated_text.find(end_tag, start_index + len(start_tag))
            if end_index != -1:
                generated_code = generated_text[start_index + len(start_tag):end_index].strip()
            else:
                # Fallback if the end tag is missing
                generated_code = generated_text[start_index + len(start_tag):].strip()
        else:
            # If no ```python block is found, we cannot safely proceed.
            raise ImportError(f"LLM response for {module_name} did not contain a valid ```python code block.")

        if not generated_code:
            raise ImportError(f"LLM failed to generate code for module {module_name}.")

        return generated_code

    except Exception as e:
        print(f"Error calling LLM for module {module_name}: {e}")
        raise ImportError(f"LLM API call failed for module {module_name}.")


def generate_code(module_name):
    """
    Dynamically generates Python code for a given module name using an LLM.
    """
    #print("module_name", module_name)
    caller_source = get_caller_source_code()
    generated_code = invoke_llm(caller_source, module_name)
    return generated_code


class CallableModule(ModuleType):
    def __call__(self, *args, **kwargs):
        # This makes the module instance itself callable.
        # We look for a special attribute `_callable_func` which holds the
        # actual function to be called.
        if hasattr(self, "_callable_func"):
            return self._callable_func(*args, **kwargs)
        raise TypeError(f"'{self.__name__}' module object is not directly callable. Did you forget to define a main function?")


class ImportSimLoader(importlib.abc.Loader):
    """
    The custom loader. Its job is to execute the dynamically generated code.
    """
    def __init__(self, fullname):
        self.fullname = fullname

    def create_module(self, spec):
        # We return our custom module type here.
        return CallableModule(spec.name)

    def exec_module(self, module):
        """
        This is the core of the magic!
        This method is called to "execute" the module's code.
        """
        try:
            code = generate_code(module.__name__)
            #print(code)
            exec(code, module.__dict__)

            # After executing the code, we need to find the function that
            # the user intended to call. We'll assume the function name
            # matches the last part of the import path.
            function_name = module.__name__.split('.')[-1]
            main_func = module.__dict__.get(function_name)

            if callable(main_func):
                module._callable_func = main_func
            else:
                # If the intended function isn't found or isn't callable,
                # we leave the _callable_func attribute unset. The __call__
                # method in CallableModule will then raise a TypeError.
                pass

            module.__path__ = []
        except SyntaxError as e:
            print(f"LLM-generated code for {module.__name__} has a syntax error: {e}")
            raise ImportError(f"Failed to import {module.__name__} due to a syntax error in generated code.") from e
        except Exception as e:
            print(f"Failed to dynamically create module {module.__name__}: {e}")
            raise


class ImportSimFinder(importlib.abc.MetaPathFinder):
    """
    The custom finder. Its job is to tell Python we can handle
    any import that starts with 'importsim.'.
    """
    def find_spec(self, fullname, path, target=None):
        #print("fullname", fullname)
        if fullname.startswith('importsim'):
            return importlib.util.spec_from_loader(
                fullname,
                ImportSimLoader(fullname),
                is_package=True
            )
        return None