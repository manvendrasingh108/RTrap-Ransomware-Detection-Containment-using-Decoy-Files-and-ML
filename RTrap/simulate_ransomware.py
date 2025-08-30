# simulate_ransomware.py (RTrap project ke root folder mein banayein)

import os
import time
import random

# Decoy list file ka path (yeh project root ke data folder mein hai)
DECOY_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "decoy_list.txt")

def load_decoy_list(filepath):
    """
    Decoy file paths ko ek file se load karta hai.
    """
    decoy_paths = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    path = line.strip()
                    if path and os.path.exists(path):
                         decoy_paths.append(path)
            print(f"Loaded {len(decoy_paths)} decoy paths from {filepath}")
        else:
            print(f"Decoy list file not found at {filepath}. Cannot simulate.")
    except Exception as e:
        print(f"Error loading decoy list from {filepath}: {e}")
    return decoy_paths

def simulate_modification(file_path):
    """
    Ek file ko simulate karta hai modify karna (bas usmein kuch data append karta hai).
    """
    try:
        # File ko 'append' mode mein open karein
        with open(file_path, 'a') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            random_data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(10, 50)))
            content_to_add = f"\n# SIMULATED_RANSOMWARE_ACTIVITY: {timestamp} - {random_data}"
            f.write(content_to_add)
        print(f"Simulated modification on: {file_path}")
    except Exception as e:
        print(f"Error simulating modification on {file_path}: {e}")

def run_simulation():
    """
    Simulation process chalata hai.
    """
    decoy_paths = load_decoy_list(DECOY_LIST_FILE)

    if not decoy_paths:
        print("No decoy files to simulate modification on. Generate decoys first.")
        return

    print("\n--- Starting Ransomware Simulation ---")
    print("This script will modify decoy files to trigger the watcher.")
    print("Press Ctrl+C to stop the simulation.")

    try:
        while True:
            # Har decoy file ko random delay ke baad modify karein
            for decoy_path in decoy_paths:
                simulate_modification(decoy_path)
                # Simulate ransomware working on files with some delay
                time.sleep(random.uniform(0.5, 2.0)) # Random delay between modifications

            # Sab files modify hone ke baad thoda wait karein
            time.sleep(5) # Wait before starting the loop again, if needed

    except KeyboardInterrupt:
        print("\n--- Ransomware Simulation Stopped By User ---")
    except Exception as e:
        print(f"An error occurred during simulation: {e}")


if __name__ == "__main__":
    run_simulation()

