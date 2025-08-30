# src/watcher/file_monitor.py
import os # !!! Yeh line add ki gayi hai !!!
import time
from watchdog.observers import Observer
from .event_handler import DecoyFileHandler # Humne jo custom handler banaya

class FileMonitor:
    def __init__(self, decoy_file_paths, config_settings=None):
        """
        FileMonitor (Watchdog Observer) ko initialize karta hai.
        decoy_file_paths: List of paths of decoy files.
        config_settings: Watcher ke liye configuration settings.
        """
        self.decoy_file_paths = decoy_file_paths
        self.config = config_settings if config_settings is not None else {}
        self.observer = Observer()
        self.event_handler = DecoyFileHandler(decoy_file_paths, config_settings)
        self.is_monitoring = False

        # Kis directories ko monitor karna hai?
        # Humein un directories ko monitor karna hai jahan hamare decoy files hain.
        # Duplicate directories se bachne ke liye set use karein.
        self.directories_to_monitor = set()
        for file_path in self.decoy_file_paths:
            directory = os.path.dirname(file_path)
            self.directories_to_monitor.add(directory)

        if not self.directories_to_monitor:
            print("Warning: No directories found for monitoring based on decoy file paths.")


    def start_monitoring(self):
        """
        File system monitoring start karta hai.
        """
        if not self.directories_to_monitor:
            print("Cannot start monitoring: No directories to watch.")
            return

        if self.is_monitoring:
            print("Monitoring is already running.")
            return

        print("Starting file system monitoring...")

        try:
            # Har directory ke liye handler schedule karein
            # recursive=False rakh rahe hain agar hum sirf decoy files ke exact parent directories monitor kar rahe hain.
            # Agar aapko subdirectories bhi monitor karne hain jahan decoys ho sakte hain toh True karein.
            # RTrap paper mein deceptive files "across the directory" plant karne ki baat hai,
            # toh recursive monitoring shayad zaroori ho sakti hai agar decoys subfolders mein bhi hain.
            recursive_monitoring = self.config.get('watcher_recursive_monitoring', False)

            for directory in self.directories_to_monitor:
                 if os.path.isdir(directory):
                     self.observer.schedule(self.event_handler, directory, recursive=recursive_monitoring)
                     print(f"Scheduled monitoring for directory: {directory} (Recursive: {recursive_monitoring})")
                 else:
                     print(f"Warning: Directory not found for monitoring: {directory}")


            self.observer.start() # Observer thread start karein
            self.is_monitoring = True
            print("File system monitoring started.")

            # Observer loop ko alive rakhne ke liye infinite loop ya join() use karein
            # join() main thread ko tab tak block karega jab tak observer stop nahi ho jata.
            # Background monitoring ke liye aap join() ko avoid kar sakte hain
            # aur main application mein ek loop ya signal handling mechanism bana sakte hain
            # observer.join()

        except Exception as e:
            print(f"Error starting file monitoring: {e}")
            self.is_monitoring = False


    def stop_monitoring(self):
        """
        File system monitoring stop karta hai.
        """
        if not self.is_monitoring:
            print("Monitoring is not running.")
            return

        print("Stopping file system monitoring...")
        try:
            self.observer.stop() # Observer ko stop karne ka signal dein
            self.observer.join() # Observer thread ko finish hone ka wait karein
            self.is_monitoring = False
            print("File system monitoring stopped.")
        except Exception as e:
            print(f"Error stopping file monitoring: {e}")


# Example Usage (This will be used in watcher.py)
if __name__ == "__main__":
    print("Testing FileMonitor (Requires manual file modification)...")

    # Dummy directory aur files setup (same as handler test)
    dummy_dir = "test_directory_monitor"
    os.makedirs(dummy_dir, exist_ok=True)

    decoy_file_1 = os.path.join(dummy_dir, "SECRET_decoy_A.txt")
    decoy_file_2 = os.path.join(dummy_dir, "private_decoy_B.doc")

    with open(decoy_file_1, "w") as f:
        f.write("Decoy A content.")
    with open(decoy_file_2, "w") as f:
        f.write("Decoy B content.")

    decoy_paths_to_monitor = [decoy_file_1, decoy_file_2]

    # FileMonitor instance banayein
    monitor_config = {
         'watcher_debounce_interval': 0.5,
         'disconnect_network_on_detection': False, # Testing ke liye False
         'process_to_kill_name': None # Testing ke liye None
    }
    file_monitor = FileMonitor(decoy_paths_to_monitor, config_settings=monitor_config)

    # Monitoring start karein
    file_monitor.start_monitoring()

    print(f"\nMonitoring directory: {dummy_dir}")
    print(f"Please modify '{decoy_file_1}' or '{decoy_file_2}' to trigger events.")
    print("Press Ctrl+C to stop monitoring.")

    # Monitoring loop ko alive rakhne ke liye
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        file_monitor.stop_monitoring()
        print("Monitoring stopped by user.")

    # Clean up dummy directory
    # import shutil
    # shutil.rmtree(dummy_dir)
    # print(f"\nCleaned up {dummy_dir}")