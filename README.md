# libsim

A Python library simulator that dynamically generates modules on import using a Large Language Model (LLM).

## What is this?

`libsim` is an experimental Python library that intercepts import statements for any module under the `libsim` namespace. Instead of loading code from a file, it uses an LLM to generate the module's code on-the-fly based on how you use it in your code.

For example, if you write:

```python
from libsim.my_module import my_function

result = my_function("hello")
```

`libsim` will see that you're trying to import `my_function` from `libsim.my_module`. It will then ask an LLM to generate the Python code for a function called `my_function` inside a module called `my_module`, making its best guess about what that function should do based on the context of your code.

## How it Works

The magic happens through a custom import hook that is installed when you import the `libsim` package.

1.  **MetaPathFinder:** A custom `LibSimFinder` is inserted into `sys.meta_path`. This finder is responsible for handling any import that starts with `libsim.`.
2.  **Custom Loader:** When an import like `from libsim.foo import bar` is found, the `LibSimFinder` tells Python to use our `LibSimLoader`.
3.  **Code Generation:** The `LibSimLoader` inspects the source code of the file that made the import request. It sends this source code to an LLM (via `litellm`) with a prompt asking it to generate the required module (`libsim.foo` in this case).
4.  **Dynamic Execution:** The LLM-generated Python code is then executed using `exec()`, creating the new module and its contents in memory.
5.  **Module Caching:** Python's import system caches the newly created module in `sys.modules`, so subsequent imports of the same module will use the cached version without calling the LLM again.

## Example Usage

The `example.py` file demonstrates how to use `libsim`:

```python
import time
from libsim import generate_tweet
from libsim.wow import sort

tweet: str = generate_tweet(subject="tinygrad", style="a short poem", viral=True)
print(f"Generated tweet: {tweet}")

st = time.time()
print(sort([5,3,6,2,1,4]))
print(f"Sorted in {time.time() - st:.6f} seconds")

st = time.time()
print(sort([5,3,6,2,1,4], method="quick sort"))
print(f"quick sort in {time.time() - st:.6f} seconds")

st = time.time()
print(sort([5,3,6,2,1,4], method="quick sort", reverse=True))
print(f"reverse quick sort in {time.time() - st:.6f} seconds")
```

In this example, the modules `libsim.generate_tweet` and `libsim.wow.sort` do not exist as physical files. They are generated and imported at runtime by the LLM based on their usage in this script.

## How to Run

1.  **Install dependencies:**
    ```bash
    uv sync
    ```

2.  **Set up your LLM:**
    The project uses `litellm` to connect to various LLM providers. You need to configure the model you want to use. By default, it's set to use a free model on OpenRouter. You may need to set an API key as an environment variable depending on the service you choose.

    Edit `libsim/llm/simple.py` to change the `LLM_MODEL`.

3.  **Run the example:**
    ```bash
    python example.py
    ```

## Configuration

-   **LLM Model:** You can change the LLM model by editing the `LLM_MODEL` variable in `libsim/llm/simple.py`.
-   **Prompt:** The prompt sent to the LLM can be modified in `libsim/llm/simple.py`.
