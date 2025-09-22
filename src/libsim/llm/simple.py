import litellm
import json
from ..config import config

def invoke_llm(source_code, module_names):
    """
    Calls the LLM to generate Python code for a list of module names.
    """
    if not source_code:
        raise ImportError("Could not find the source code of the calling module.")

    prompt = f"""You are a Python code generator.
Based on the user's code below, generate the code for the requested Python modules.

User's code:
---
{source_code}
---
Please ignore `from libsim import config` and any usage of `config` in the user's code.

Generate the code for these modules: {(', '.join(module_names))}

- Do not import any external libraries.

Your response must be a single JSON object where keys are file paths and values are the corresponding Python code.
Make sure the file paths match the corresponding module names so that the import statements in the user's code will work correctly.
The file paths you choose must result in a valid Python module structure that will satisfy the imports in the user's code. For example, for a module `foo`, you can generate either a file `foo.py` or a package `foo/__init__.py`, or a complex package with multiple files.
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
        raise ImportError(f"LLM API call failed for modules {module_names}.") from e