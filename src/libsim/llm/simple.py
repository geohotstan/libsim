
import litellm
import json
from ..config import config

def invoke_llm(source_code, module_names):
    """
    Calls the LLM to generate Python code for a list of module names.
    """
    if not source_code:
        raise ImportError("Could not find the source code of the calling module.")

    prompt = f"""
You are an expert Python programmer acting as a code generator.
Your task is to write the Python code for a set of modules based on a user's script.

The user's code, which triggered this generation, is:
---
{source_code}
---

Based on the user's code, you must generate the Python code for the following modules:
- {(', '.join(module_names))}

**Instructions:**
1.  Analyze the user's code to determine what functions, classes, and variables are required for each module.
2.  Your output MUST be a single JSON object.
3.  The keys of the JSON object must be the relative file paths for the code to be generated (e.g., `wow/sort.py`, `generate_tweet/__init__.py`).
4.  The values must be the Python code for each file.
5.  Define all necessary objects. If the user's code is `from libsim.hello import world` and then `world.greet()`, you must generate a `world` object with a `greet()` method in the `hello/__init__.py` or `hello.py` file.
6.  **ABSOLUTELY DO NOT** use `import sys` or refer to `sys.modules`.
7.  **ABSOLUTELY DO NOT** import any external python library that is not in the standard python library.
8.  Ensure that you do not define global variables that have the same name as function parameters.

**Generated JSON for modules:**
"""

    try:
        response = litellm.completion(
            model=config.llm_model,
            messages=[{"content": prompt, "role": "user"}],
            response_format={"type": "json_object"}
        )
        generated_text = response.choices[0].message.content.strip()

        if config.debug >= 1:
            print(generated_text)

        parsed_json = json.loads(generated_text)
        if not isinstance(parsed_json, dict):
            raise ImportError("LLM response was not a valid JSON object.")

        return parsed_json

    except Exception as e:
        print(f"Error calling LLM for modules {module_names}: {e}")
        raise ImportError(f"LLM API call failed for modules {module_names}.")
