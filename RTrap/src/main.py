# src/main.py

import os
import sys
import time # Watcher loop ke liye
import argparse # Command line arguments parse karne ke liye

# Hamare custom modules aur config se import karein
from src.config.settings import get_settings
from src.generator.generator import DecoyGenerator
from src.watcher.watcher import DecoyWatcher

# Ensure data directory exists to save decoy list
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def save_decoy_list(decoy_paths, filepath):
    """
    Generated decoy file paths ko ek file mein save karta hai.
    """
    try:
        with open(filepath, 'w') as f:
            for path in decoy_paths:
                f.write(f"{path}\n")
        print(f"Decoy list saved to {filepath}")
    except Exception as e:
        print(f"Error saving decoy list to {filepath}: {e}")

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
                    if path and os.path.exists(path): # Only load if path is not empty and file exists
                         decoy_paths.append(path)
            print(f"Decoy list loaded from {filepath}. Found {len(decoy_paths)} existing decoy files.")
        else:
            print(f"Decoy list file not found at {filepath}. No decoys loaded.")
    except Exception as e:
        print(f"Error loading decoy list from {filepath}: {e}")
    return decoy_paths


def main():
    """
    RTrap application ka main function.
    Command line arguments ke through generator ya watcher run karta hai.
    """
    parser = argparse.ArgumentParser(description="RTrap: Ransomware Trapping and Containing System")
    parser.add_argument(
        '--mode',
        choices=['generate', 'watch'],
        required=True,
        help="Operation mode: 'generate' to create decoys, 'watch' to start monitoring."
    )
    parser.add_argument(
        '--directory',
        type=str,
        help=f"Directory to process. Defaults to setting: {get_settings()['general']['directory_to_monitor']}"
    )
    parser.add_argument(
        '--decoy_list',
        type=str,
        help=f"Path to the decoy list file for 'watch' mode. Defaults to setting: {get_settings()['general']['decoy_list_file']}"
    )


    args = parser.parse_args()

    # Settings load karein
    config = get_settings()
    print("Configuration loaded.")
    # print(config) # Optional: print config for debugging

    # Directory to monitor/generate decoys
    directory_to_process = args.directory if args.directory else config['general']['directory_to_monitor']
    if not directory_to_process or not os.path.isdir(directory_to_process):
        print(f"Error: Invalid or no directory specified for processing: {directory_to_process}")
        print("Please provide a valid directory using --directory or update DIRECTORY_TO_MONITOR in settings.py")
        sys.exit(1)


    if args.mode == 'generate':
        print("\n--- Running Decoy Generation Mode ---")
        # Decoy Generator initialize karein aur run karein
        # DecoyGenerator needs only generator settings, so config['generator'] is correct here
        decoy_generator = DecoyGenerator(config['generator'])
        created_decoys = decoy_generator.generate_decoys_for_directory(directory_to_process)

        if created_decoys:
            print(f"\nDecoy generation finished. Created {len(created_decoys)} decoy files.")
            # Generated decoy list ko save karein taki watcher use load kar sake
            decoy_list_file_path = args.decoy_list if args.decoy_list else config['general']['decoy_list_file']
            save_decoy_list(created_decoys, decoy_list_file_path)
        else:
            print("\nDecoy generation finished. No decoys were created.")

    elif args.mode == 'watch':
        print("\n--- Running Decoy Watcher Mode ---")
        # Decoy list load karein
        decoy_list_file_path = args.decoy_list if args.decoy_list else config['general']['decoy_list_file']
        decoy_paths_to_monitor = load_decoy_list(decoy_list_file_path)

        if not decoy_paths_to_monitor:
            print("No decoy files loaded for monitoring. Please run 'generate' mode first.")
            sys.exit(1)

        # Decoy Watcher initialize karein aur start karein
        # Poori config dictionary pass karein taaki Watcher ke components ko 'general' settings mil sakein
        decoy_watcher = DecoyWatcher(decoy_paths_to_monitor, config) # <-- Change is here!
        decoy_watcher.start()

        print("\nDecoy Watcher started. Monitoring active.")
        print(f"Monitoring directory: {directory_to_process}")
        print("Press Ctrl+C to stop the watcher.")

        # Watcher background thread mein chal raha hai, main thread ko alive rakhein
        try:
            while True:
                time.sleep(1) # Main thread kuch nahi kar raha, bas alive hai
        except KeyboardInterrupt:
            print("\nStopping Decoy Watcher...")
            decoy_watcher.stop()
            print("RTrap application finished.")


if __name__ == "__main__":
    main()
