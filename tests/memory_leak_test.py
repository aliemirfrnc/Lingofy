import os
import psutil
import time
import gc
from fastapi.testclient import TestClient
from backend.main import app
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

def get_process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)  # in MB

def run_memory_test(total_requests=100000):
    client = TestClient(app)
    
    print(f"Starting Memory Leak Test with {total_requests} requests...")
    initial_mem = get_process_memory()
    print(f"Initial Memory: {initial_mem:.2f} MB")
    
    # We will test an endpoint that touches the database to see if DB leaks memory
    # We use a dummy login endpoint (it will fail with 400/401 but still trigger logic)
    payload = {"email": "test@test.com", "password": "wrongpassword"}
    
    mem_readings = []
    
    start_time = time.time()
    for i in range(1, total_requests + 1):
        res = client.get("/lyrics?track=dummy&artist=dummy")
        
        if i % 10000 == 0:
            current_mem = get_process_memory()
            mem_readings.append(current_mem)
            elapsed = time.time() - start_time
            rps = i / elapsed
            print(f"Processed {i} requests | Memory: {current_mem:.2f} MB | {rps:.2f} RPS")
            
    # Force Garbage Collection
    gc.collect()
    final_mem = get_process_memory()
    print(f"Final Memory after GC: {final_mem:.2f} MB")
    
    mem_diff = final_mem - initial_mem
    print(f"Memory Difference: {mem_diff:.2f} MB")
    
    # Analyze if it stabilized
    # If the last 3 readings are very close to each other, it stabilized.
    if len(mem_readings) >= 3:
        last_3 = mem_readings[-3:]
        variance = max(last_3) - min(last_3)
        if variance < 5.0:  # Less than 5MB variance in the last 30,000 requests
            print("Status: \u2705 RAM Stabilized (No Leak Detected)")
        else:
            print(f"Status: \u274c Potential Leak. Variance in last 30k reqs: {variance:.2f} MB")
    
    # Log the result to a file for evidence
    with open("memory_leak_report.txt", "w") as f:
        f.write(f"Initial Memory: {initial_mem:.2f} MB\n")
        f.write(f"Final Memory (post-GC): {final_mem:.2f} MB\n")
        f.write(f"Difference: {mem_diff:.2f} MB\n")
        for idx, mem in enumerate(mem_readings):
            f.write(f"After {(idx+1)*10000} requests: {mem:.2f} MB\n")

if __name__ == "__main__":
    run_memory_test(20000)
