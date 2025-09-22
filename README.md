# libsim

[WebSim](https://websim.io) but for Python libraries — never see an ImportError again!

libsim brings the WebSim idea to Python imports: when you import a missing module under the libsim namespace, an LLM synthesizes the module code on demand based on how you use it in your code. 

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

## Example Output

```text
Generated tweet: Tinygrad, sleek and lean,
With minimal code, dreams convene.
From tensors to triumph, swift and true,
The ML revolution starts with you!
#tinygrad #python #mlmagic 🚀
[1, 2, 3, 4, 5, 6]
Sorted in 0.000010 seconds
[1, 2, 3, 4, 5, 6]
quick sort in 0.000010 seconds
[6, 5, 4, 3, 2, 1]
reverse quick sort in 0.000007 seconds
```

## How to Install

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
