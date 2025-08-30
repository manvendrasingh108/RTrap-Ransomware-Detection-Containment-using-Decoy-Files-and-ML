# src/watcher/watcher.py

from .file_monitor import FileMonitor
# Agar zaroorat pade toh config ya utils se bhi import kar sakte hain
# from ..config import settings # Example agar config use karna ho

class DecoyWatcher:
    def __init__(self, decoy_file_paths, config_settings=None):
        """
        DecoyWatcher (Watcher Module Orchestrator) ko initialize karta hai.
        decoy_file_paths: List of paths of decoy files to monitor.
                           Yeh list DecoyGenerator se milegi.
        config_settings: Watcher ke liye configuration settings.
        """
        if config_settings is None:
            config_settings = {} # Agar None hai toh empty dict use karein

        self.decoy_file_paths = decoy_file_paths
        self.config = config_settings
        self.file_monitor = FileMonitor(self.decoy_file_paths, self.config)
        self.is_running = False

        if not self.decoy_file_paths:
            print("Warning: DecoyWatcher initialized with no decoy file paths to monitor.")


    def start(self):
        """
        Decoy monitoring start karta hai.
        """
        if self.is_running:
            print("DecoyWatcher is already running.")
            return

        print("Starting DecoyWatcher...")
        try:
            self.file_monitor.start_monitoring()
            self.is_running = True
            print("DecoyWatcher started. Monitoring is active.")
            # Note: file_monitor.start_monitoring() starts the observer in a new thread.
            # The main thread (where start() was called) will continue.
            # You might need a mechanism in your main application to keep the script alive
            # while the watcher thread runs in the background.
            # The file_monitor.join() call inside start_monitoring would block,
            # but we designed start_monitoring not to block main thread by default.

        except Exception as e:
            print(f"Error starting DecoyWatcher: {e}")
            self.is_running = False

    def stop(self):
        """
        Decoy monitoring stop karta hai.
        """
        if not self.is_running:
            print("DecoyWatcher is not running.")
            return

        print("Stopping DecoyWatcher...")
        try:
            self.file_monitor.stop_monitoring()
            self.is_running = False
            print("DecoyWatcher stopped.")
        except Exception as e:
            print(f"Error stopping DecoyWatcher: {e}")

    # Aap yahaan DecoyWatcher ke state ko save/load karne ke methods bhi add kar sakte hain,
    # agar zaroorat pade (though watcher state is less complex than generator model states).


# Example Usage (in main.py or another orchestration script)
# from src.watcher.watcher import DecoyWatcher
# from src.config.settings import get_settings # Assuming settings module exists and has get_settings

# # Example: Get decoy paths from somewhere (e.g., a file where generator saved them)
# # or pass the list directly if generator just ran.
# generated_decoy_paths = ["path/to/decoy1", "path/to/decoy2"] # Replace with actual list

# config = get_settings() # Load configuration for watcher

# decoy_watcher = DecoyWatcher(generated_decoy_paths, config)

# decoy_watcher.start()

# # Keep the main application alive while the watcher runs in the background
# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     decoy_watcher.stop()
#     print("Application shut down by user.")