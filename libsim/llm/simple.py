import litellm

# Set the model and API key. Using an environment variable for the key is best practice.
# LLM_MODEL = "openrouter/mistralai/mistral-7b-instruct:free"
LLM_MODEL = "openrouter/z-ai/glm-4.5-air:free"
# LLM_MODEL = "openrouter/deepseek/deepseek-chat-v3.1:free"


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
2.  Define these objects directly. For example, if the user's code is `from libsim.hello import world` and then `world.greet()`, you (when generating the `vibelib.hello` module) MUST generate a `world` object instance that has a `greet()` method. A class definition alone is not enough.
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
