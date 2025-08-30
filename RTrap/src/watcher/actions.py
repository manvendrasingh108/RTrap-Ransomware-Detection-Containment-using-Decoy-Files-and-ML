# src/watcher/actions.py

import os
import psutil # Process management ke liye
import time # Delay ke liye
import subprocess # System commands run karne ke liye
import sys # OS type check karne ke liye
import platform # Platform check karne ke liye (aapke code se add kiya gaya)

def kill_process_by_pid(pid):
    """
    Diye gaye Process ID (PID) wale process ko kill karta hai.
    """
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        print(f"Attempting to kill process: {process_name} (PID: {pid})")
        process.kill()
        print(f"Process {process_name} (PID: {pid}) killed successfully.")
        return True
    except psutil.NoSuchProcess:
        print(f"Error: No process found with PID {pid}.")
        return False
    except psutil.AccessDenied:
        print(f"Error: Permission denied to kill process with PID {pid}. Might need administrator privileges.")
        return False
    except Exception as e:
        print(f"Error killing process with PID {pid}: {e}")
        return False

def kill_processes_by_pids(pids):
    """
    Diye gaye Process IDs (PIDs) ki list wale processes ko kill karta hai.
    """
    if not pids:
        print("No PIDs provided to kill.")
        return 0

    killed_count = 0
    print(f"Attempting to kill processes with PIDs: {pids}")
    for pid in pids:
        if kill_process_by_pid(pid):
            killed_count += 1
    print(f"Finished attempting to kill processes. Killed {killed_count} out of {len(pids)}.")
    return killed_count


def kill_process_by_name(process_name):
    """
    Diye gaye naam wale saare processes ko kill karta hai.
    Warning: Yeh careful reh kar use karein, system processes bhi kill ho sakte hain.
    Ransomware ke specific process name ka pata hone par zyada useful.
    """
    killed_count = 0
    print(f"Attempting to kill all processes with name: {process_name}")
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                print(f"Found process {process_name} (PID: {proc.info['pid']}). Killing...")
                proc.kill()
                print(f"Process {process_name} (PID: {proc.info['pid']}) killed.")
                killed_count += 1
            except psutil.NoSuchProcess:
                pass # Process already died
            except psutil.AccessDenied:
                print(f"Error: Permission denied to kill process {process_name} (PID: {proc.info['pid']}).")
            except Exception as e:
                print(f"Error killing process {process_name} (PID: {proc.info['pid']}): {e}")
    print(f"Finished attempting to kill processes with name {process_name}. Killed {killed_count}.")
    return killed_count > 0


def disconnect_network():
    """
    Operating system ke hisaab se network connectivity disconnect karta hai.
    Aapke diye gaye code logic ko use kiya gaya hai.
    Note: Yeh implementation OS-dependent hai aur ho sakta hai ki administrator privileges ki zaroorat pade.
    """
    print("🌐 Trying to disconnect network...")
    os_type = platform.system() # Use platform.system() as in your code

    try:
        if os_type == "Windows":
            # Aapke diye gaye logic ko use kar rahe hain - common interfaces try karna
            interfaces = ["Wi-Fi", "WLAN", "Ethernet"]
            for interface in interfaces:
                try:
                    print(f"Attempting to disable Windows interface: {interface}")
                    # Added shell=True and suppressed output as in your code
                    subprocess.run(
                        ["netsh", "interface", "set", "interface", interface, "disable"],
                        check=True,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"🔌 Interface '{interface}' disabled.")
                    return True # Agar koi ek interface disable ho jaye toh success
                except subprocess.CalledProcessError as e:
                    # print(f"Failed to disable interface '{interface}': {e}") # Optional detailed error
                    continue # Try the next interface if one fails
            print("⚠️ Failed to disable any known Windows network interface.")
            return False # Agar koi bhi interface disable na ho paya

        elif os_type == "Linux":
            # Aapke diye gaye Linux command ko use kar rahe hain
            # Note: nmcli har Linux distro mein nahi ho sakta aur sudo ki zaroorat pad sakti hai
            print("Using Linux command (nmcli)...")
            try:
                subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
                print("🔌 Linux Wi-Fi turned off using nmcli.")
                return True
            except FileNotFoundError:
                 print("Error: 'nmcli' command not found. Make sure it's installed and in your PATH.")
                 return False
            except subprocess.CalledProcessError as e:
                 print(f"Error executing nmcli command: {e}. Might need sudo.")
                 return False


        elif os_type == "Darwin": # macOS
            print("Network disconnection for macOS is not implemented in this basic example.")
            print("You might need to use 'networksetup -setairportpower off' or similar commands.")
            return False # Not implemented for macOS


        else:
            print(f"Network disconnection not implemented for OS type: {os_type}")
            return False # Not implemented for this OS

    except Exception as e:
        print(f"An unexpected error occurred during network disconnection: {e}")
        return False


# Example Usage (Testing)
if __name__ == "__main__":
    print("Testing Actions Module...")

    # --- Test Kill Process by PID ---
    # Iske liye koi test process chalana padega (jaise notepad.exe)
    # Aur phir uska PID nikal kar test karna hoga.
    # Yeh test automatic nahi hai, manual karna padega.
    print("\n--- Testing Kill Process by PID (Manual) ---")
    # Example (Uncomment and modify to test):
    # try:
    #     # Find PID of a running process (e.g., notepad.exe)
    #     target_pid = None
    #     for proc in psutil.process_iter(['pid', 'name']):
    #         if proc.info['name'].lower() == 'notepad.exe': # Case-insensitive match
    #             target_pid = proc.info['pid']
    #             print(f"Found notepad.exe with PID: {target_pid}")
    #             break
    #
    #     if target_pid:
    #         print(f"Please open notepad.exe manually to test killing PID {target_pid}.")
    #         time.sleep(5) # Give time to open
    #         success = kill_processes_by_pids([target_pid])
    #         if success:
    #             print(f"Successfully killed process with PID {target_pid}.")
    #         else:
    #             print(f"Failed to kill process with PID {target_pid}.")
    #     else:
    #          print("notepad.exe not found running. Cannot test kill by PID.")
    #
    # except Exception as e:
    #      print(f"Error during manual PID kill test: {e}")


    # --- Test Kill Process by Name ---
    print("\n--- Testing Kill Process by Name (Manual) ---")
    # Example (Uncomment and modify to test):
    # process_name_to_kill = "notepad.exe" # Change this to a process you want to test killing
    # print(f"Please open {process_name_to_kill} manually to test killing by name.")
    # time.sleep(5) # Give time to open
    # success = kill_process_by_name(process_name_to_kill)
    # if success:
    #     print(f"Successfully killed {process_name_to_kill} by name.")
    # else:
    #     print(f"Failed to kill {process_name_to_kill} by name.")


    # --- Test Disconnect Network ---
    print("\n--- Testing Disconnect Network (Use with caution!) ---")
    # Disconnect action potentially disrupts your internet connection.
    # Uncomment the line below to test.
    # print("Attempting to disconnect network in 5 seconds...")
    # time.sleep(5)
    # disconnect_success = disconnect_network()
    # if disconnect_success:
    #     print("Network disconnection routine executed.")
    # else:
    #     print("Network disconnection routine failed.")
    # print("Remember to reconnect manually if needed!")

