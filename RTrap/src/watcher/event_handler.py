# src/watcher/event_handler.py

import os
import time # Logging timestamp ke liye aur delay ke liye
import threading # Actions ko non-blocking banane ke liye threading use kar sakte hain
import psutil # Process info nikalne ke liye
# Actions module se functions import karein
from watchdog.events import FileSystemEventHandler
from .actions import kill_processes_by_pids, kill_process_by_name, disconnect_network
# Settings se BASE_DIR access karne ke liye settings module import karna pad sakta hai
# Ya phir config_settings dictionary mein base_dir ko pass kiya gaya hai jo hum use kar rahe hain.
# Hum config_settings se hi base_dir lenge jo watcher.py se aa raha hai.


class DecoyFileHandler(FileSystemEventHandler):
    def __init__(self, decoy_file_paths, config_settings=None):
        """
        Decoy File System Event Handler ko initialize karta hai.
        decoy_file_paths: Ek set ya list jismein saare decoy files ke paths hain jinhein monitor karna hai.
        config_settings: Configuration se mili hui settings (actions, etc., aur general settings like base_dir).
        """
        self.decoy_file_paths = set(decoy_file_paths) # Quick lookup ke liye set use karein
        self.config = config_settings if config_settings is not None else {}
        self.is_action_triggered = threading.Event() # Flag to indicate if action is already triggered
        # Multiple events same time par hone se bachne ke liye (debounce/throttle)
        self.last_event_time = 0
        self.debounce_interval = self.config.get('watcher_debounce_interval', 1) # Seconds

        # Heuristic settings for process identification
        self.process_scan_timeframe = self.config.get('process_scan_timeframe', 10) # Scan processes created in last X seconds
        self.suspicious_process_names = set(self.config.get('suspicious_process_names', [])) # List of names to look for

        # Log file path define karein
        # Base directory ko config se len (jo watcher.py se pass ho raha hai)
        base_dir = self.config.get('general', {}).get('base_dir')
        if base_dir:
             self.log_file_path = os.path.join(base_dir, "data", "rtrap_log.txt")
             # Ensure data directory exists before trying to log
             os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
             print(f"Incident log file path: {self.log_file_path}")
        else:
             # Fallback if base_dir is not available in config (shouldn't happen with main.py)
             self.log_file_path = "rtrap_log.txt"
             print(f"Warning: Base directory not found in config. Log file might be created in current directory: {self.log_file_path}")


        print(f"DecoyFileHandler initialized. Monitoring {len(self.decoy_file_paths)} decoy files.")


    def log_incident(self, file_path, potential_pids=None, process_name_attempt=None):
        """
        Ransomware detection incident ko log karta hai file mein.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"[{timestamp}] ALERT: Ransomware activity detected on {file_path}"

        if potential_pids:
            log_entry += f" - Potential attacker PIDs: {potential_pids}"
        elif process_name_attempt:
             log_entry += f" - Configured process name attempt: {process_name_attempt}"

        log_entry += "\n"

        try:
            with open(self.log_file_path, "a") as log_file:
                log_file.write(log_entry)
            print(f"📝 Logged incident to {self.log_file_path}")
        except Exception as e:
            print(f"Error writing to log file {self.log_file_path}: {e}")


    def on_modified(self, event):
        """
        Jab koi file modify hoti hai toh yeh method call hota hai.
        """
        # Directory modification events ko ignore karein
        if event.is_directory:
            return

        # Decoy file modify hui ya nahi check karein
        if event.src_path in self.decoy_file_paths:
            current_time = time.time()
            # Debounce logic: Agar pichhla event debounce_interval ke andar hua tha toh ignore karein
            if current_time - self.last_event_time < self.debounce_interval:
                 # print(f"Event on {event.src_path} debounced.")
                 return

            print(f"\n!!! Decoy file modified: {event.src_path} !!!")
            self.last_event_time = current_time

            # --- Process Identification Attempt (Heuristic) ---
            # Isko action trigger hone se pehle identify kar rahe hain taki log mein aa sake
            potential_pids_to_kill = self.identify_potential_attacker_pids(current_time)
            print(f"Identified potential attacker PIDs: {potential_pids_to_kill}")
            # -------------------------------------------------

            # --- Log The Incident ---
            # Logging ko actions se pehle kar rahe hain taaki detection turant log ho jaye
            self.log_incident(
                event.src_path,
                potential_pids=potential_pids_to_kill,
                process_name_attempt=self.config.get('process_to_kill_name', None) # Log configured name if any
                )
            # ------------------------


            # Action trigger karein agar abhi tak koi action trigger nahi hua hai
            if not self.is_action_triggered.is_set():
                 self.is_action_triggered.set() # Flag set kar dein
                 print("Triggering defensive actions...")

                 # Actions ko ek naye thread mein run kar sakte hain
                 # taki watcher ki main loop block na ho
                 # potential_pids_to_kill ko actions thread ko pass karein
                 action_thread = threading.Thread(target=self.trigger_actions, args=(event.src_path, potential_pids_to_kill,))
                 action_thread.start()
            else:
                 print("Action already triggered, ignoring subsequent events for now.")


    # Aap on_created, on_deleted, on_moved methods ko bhi implement kar sakte hain
    # agar aap un events par bhi action lena chahte hain.

    def identify_potential_attacker_pids(self, event_time):
        """
        Heuristic tarike se potentially attacker processes ki PIDs identify karta hai.
        Ab yeh recent processes mein se unhein dhoondhta hai jinka naam suspicious list mein ho.
        event_time: Jis waqt event trigger hua.
        """
        potential_pids = []
        print(f"Scanning processes created in the last {self.process_scan_timeframe} seconds for suspicious names...")
        # Fetch process info in one go for efficiency if possible
        try:
            all_processes = psutil.process_iter(['pid', 'name', 'create_time'])
        except psutil.AccessDenied:
            print("Warning: Access denied to list processes. Cannot perform process identification heuristic.")
            return [] # Cannot proceed without process list
        except Exception as e:
            print(f"Error listing processes: {e}")
            return []


        for proc in all_processes:
            try:
                process_info = proc.info
                process_pid = process_info.get('pid')
                process_name = process_info.get('name')
                process_create_time = process_info.get('create_time') # Use .get()

                # Ensure we have necessary info
                if process_pid is None or process_name is None or process_create_time is None:
                    # print(f"Skipping process due to missing info: {process_info}") # Optional debug
                    continue


                # Heuristic: Process created recently AND name is in suspicious list
                is_recent = (event_time - process_create_time) <= self.process_scan_timeframe
                is_suspicious_name = self.suspicious_process_names and process_name.lower() in self.suspicious_process_names

                if is_recent and is_suspicious_name:
                    print(f" - Found suspicious recent process: {process_name} (PID: {process_pid}, Created: {time.ctime(process_create_time)})")
                    potential_pids.append(process_pid)
                    # Continue scan, maybe more suspicious processes exist

                # Note: Aur bhi advanced heuristics yahaan add ki ja sakti hain

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Ignore processes that might have exited or we don't have access to
                pass
            except Exception as e:
                print(f"Error scanning process: {e}")


        # Remove duplicate PIDs if any
        potential_pids = list(set(potential_pids))

        # Optional: Remove current process PID from the list if we don't want to kill self (careful!)
        current_process_pid = os.getpid()
        if current_process_pid in potential_pids:
             # print(f"Removing current process PID ({current_process_pid}) from potential targets.")
             potential_pids.remove(current_process_pid)


        return potential_pids


    def trigger_actions(self, triggered_file_path, potential_pids_to_kill):
        """
        Defensive actions execute karta hai.
        triggered_file_path: Jis decoy file par event hua.
        potential_pids_to_kill: List of PIDs to attempt to kill.
        """
        print(f"Actions triggered due to event on: {triggered_file_path}")

        # Check if actions are enabled in config
        if not self.config.get('enable_actions', True):
            print("Defensive actions are disabled in configuration.")
            # Optional: Reset trigger flag here if actions are fully disabled
            # self.is_action_triggered.clear()
            return

        # --- Action 1: Identify and Kill the process (using identified PIDs) ---
        # Use the PIDs identified by the heuristic
        if potential_pids_to_kill:
            print("Attempting to kill potential attacker processes by PID...")
            kill_processes_by_pids(potential_pids_to_kill)
            # Note: This requires the Watcher to be run with administrator privileges.
        elif self.config.get('process_to_kill_name', None):
             # Fallback to killing by configured name if no specific PIDs identified by heuristic
             configured_name = self.config.get('process_to_kill_name')
             print(f"No potential PIDs identified by heuristic, attempting to kill by configured name: {configured_name}")
             kill_process_by_name(configured_name)
        else:
            print("No potential PIDs identified by heuristic and no process name configured to kill.")


        # --- Action 2: Disconnect Network ---
        if self.config.get('disconnect_network_on_detection', True): # Config से control karein
            print("Attempting to disconnect network...")
            disconnect_network()
        else:
            print("Network disconnection is disabled in configuration.")

        print("Defensive actions finished.")

        # Action complete hone ke baad flag reset karein
        # Agar aap chahte hain ki action phir se trigger ho agar aur events aayein.
        # Thoda delay de sakte hain reset se pehle agar system ko stabilize hone ka time dena ho.
        time.sleep(self.config.get('action_reset_delay', 5)) # Default 5 seconds delay before resetting trigger
        self.is_action_triggered.clear() # Flag reset karein

# Example Usage (This will be used in file_monitor.py or watcher.py)
if __name__ == "__main__":
    print("Testing DecoyFileHandler (Requires manual file modification)...")
    print("Note: Process identification heuristic is basic and for demonstration.")

    # Dummy directory aur files setup (same as previous tests)
    dummy_dir = "test_directory_handler_log"
    os.makedirs(dummy_dir, exist_ok=True)

    # Dummy files
    non_decoy_file = os.path.join(dummy_dir, "normal_file.txt")
    decoy_file_1 = os.path.join(dummy_dir, "MY_SECRET_decoy.doc")
    decoy_file_2 = os.path.join(dummy_dir, "photos_decoy.jpg")

    with open(non_decoy_file, "w") as f:
        f.write("This is a normal file.")
    with open(decoy_file_1, "w") as f:
        f.write("This is decoy file 1.")
    with open(decoy_file_2, "w") as f:
        f.write("This is decoy file 2.")

    # Decoy file paths ki list
    decoy_paths_to_monitor = [decoy_file_1, decoy_file_2]

    # DecoyFileHandler ka instance banayein
    # Configuration settings pass karein (example: process name to kill)
    watcher_config = {
        'enable_actions': True, # Actions enabled
        'process_to_kill_name': None, # No specific name kill by default
        'disconnect_network_on_detection': False, # Testing ke liye False
        'watcher_debounce_interval': 0.5, # 0.5 seconds debounce
        'process_scan_timeframe': 10, # Scan processes created in last 10 seconds
        # Suspicious names include python.exe for testing simulation script
        'suspicious_process_names': ['python.exe', 'simulate_ransomware.py'],
        'action_reset_delay': 5, # 5 seconds delay after actions before resetting trigger
        # general settings needed for log file path
        'general': {
            'base_dir': os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        }
    }

    # Ensure dummy data directory for log exists if using BASE_DIR
    base_for_log_test = watcher_config['general']['base_dir']
    if base_for_log_test:
        os.makedirs(os.path.join(base_for_log_test, "data"), exist_ok=True)


    event_handler = DecoyFileHandler(decoy_paths_to_monitor, config_settings=watcher_config)

    # Ab Watchdog Observer setup karna padega is handler ko use karne ke liye.
    # Yeh code file_monitor.py mein jayega.
    # Filhaal, aap manually in files ko modify karke output dekh sakte hain.
    print(f"\nPlease modify '{decoy_file_1}' or '{decoy_file_2}' to trigger the handler.")
    print(f"Modify '{non_decoy_file}' to see no action.")
    print("Press Ctrl+C to exit.")

    # To make the handler react, we need a watcher loop, which is in file_monitor.py
    # This test block alone won't run the handler methods automatically on file change.
    # It only demonstrates creating the handler instance.

    # Clean up dummy directory and potentially log file
    # import shutil
    # shutil.rmtree(dummy_dir)
    # print(f"\nCleaned up {dummy_dir}")
    # # Optional: Clean up log file after testing
    # log_file_path_for_test = os.path.join(watcher_config['general']['base_dir'], "data", "rtrap_log.txt")
    # if os.path.exists(log_file_path_for_test):
    #      os.remove(log_file_path_for_test)
    #      print(f"Cleaned up log file: {log_file_path_for_test}")
