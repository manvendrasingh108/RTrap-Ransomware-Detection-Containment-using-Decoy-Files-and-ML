
# src/config/settings.py

import os

# --- General Settings ---
# Project ka root directory
# Corrected BASE_DIR calculation: Go up three directories from the location of settings.py (src/config/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directory jahan generated decoy file paths ki list save/load hogi
# Watcher ko pata hona chahiye kaun si files decoys hain.
DECOY_LIST_FILE = os.path.join(BASE_DIR, "data", "decoy_list.txt")

# Directory jahan aap files monitor karna chahte hain aur decoys plant karna chahte hain
# Is directory ko careful reh kar choose karein, ransomware is par attack kar sakta hai.
# Testing ke liye ek dedicated test directory use karna achha hai.
# !!! Updated path according to your request !!!
DIRECTORY_TO_MONITOR = r"C:\Users\MANVENDRA SINGH\Downloads\Test"
# Using a raw string (r"...") is recommended for Windows paths to avoid issues with backslashes.


# --- Generator Settings ---
GENERATOR_SETTINGS = {
    'pca_n_components': 0.99, # PCA mein kitna variance retain karna hai (0.0 se 1.0 ke beech float)
    'ap_damping': 0.5,        # Affinity Propagation damping parameter
    'ap_max_iter': 200,       # Affinity Propagation max iterations
    'ap_convergence_iter': 15,# Affinity Propagation convergence iterations
    'ap_preference': None,    # Affinity Propagation preference parameter (None matlab auto)
    'decoy_marker': "RTrap_Decoy", # String to add to decoy filenames
    'recursive_generation': False # Generator subdirectories mein files include karega ya nahi
}

# --- Watcher Settings ---
WATCHER_SETTINGS = {
    'watcher_debounce_interval': 1, # File events ke beech minimum time interval (seconds)
    'recursive_monitoring': False, # Watcher subdirectories ko monitor karega ya nahi (GENERATOR_SETTINGS se sync mein rakhein)

    # --- Action Settings ---
    'enable_actions': True, # Kya detection hone par defensive actions leni hain?
    'disconnect_network_on_detection': True, # Kya network disconnect karna hai detection par?

    # Process killing settings
    # Agar aap specific ransomware process name jaante hain toh yahaan likh sakte hain
    # Warning: Careful reh kar use karein!
    'process_to_kill_name': None, # Example: 'notepad.exe' for testing, or None

    # Process identification heuristic settings
    # Scan processes created in last X seconds
    'process_scan_timeframe': 10,  # <-- Value set for testing
    # List of process names to consider suspicious
    # Added names for testing the Python simulation script
    'suspicious_process_names': ['python.exe', 'simulate_ransomware.py'], # <-- Value set for testing

    # Delay after triggering actions before resetting the trigger flag (in seconds)
    'action_reset_delay': 5,

    # Note: Agar aapko process ID kill karna hai toh uske liye logic event handler mein add karna padega
    # jo process identify kar sake. Yeh complex hai (jaisa humne abhi attempt kiya hai heuristic se).
}


def get_settings():
    """
    Saari configuration settings ko ek dictionary mein return karta hai.
    Future mein aap yahaan se settings ek file se load kar sakte hain.
    """
    settings = {
        'general': {
            'base_dir': BASE_DIR,
            'decoy_list_file': DECOY_LIST_FILE,
            'directory_to_monitor': DIRECTORY_TO_MONITOR
        },
        'generator': GENERATOR_SETTINGS,
        'watcher': WATCHER_SETTINGS
    }
    return settings

# Example of how you might load settings from a JSON file later:
# import json
# def load_settings_from_json(filepath):
#     try:
#         with open(filepath, 'r') as f:
#             settings_data = json.load(f)
#         return settings_data
#     except FileNotFoundError:
#         print(f"Error: Settings file not found at {filepath}")
#         return None
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from {filepath}")
#         return None

# Example usage in another module:
# from .config.settings import get_settings
# config = get_settings()
# monitor_dir = config['general']['directory_to_monitor']
# pca_components = config['generator']['pca_n_components']

