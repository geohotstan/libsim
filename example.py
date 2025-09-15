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
