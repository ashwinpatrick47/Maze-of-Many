import time
import subprocess

def run_with_config(config_file):
    t0 = time.perf_counter()
    subprocess.run(["python3", "maze_runner.py", config_file], check=True)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000  # ms

# Example run
ms = run_with_config("config.json")
print("Elapsed:", round(ms, 3), "ms")
