import platform
import subprocess
import time
import socket
from datetime import datetime

def check_port(host, port, timeout=3):
    """
    Checks if a specific port is open on a host.
    Returns True if open, False otherwise.
    """
    try:
        # Create a new socket object
        # AF_INET for IPv4, SOCK_STREAM for TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout) # Set a timeout for the connection attempt
            # Try to connect to the host on the specified port
            s.connect((host, port))
        return True # Connection successful
    except (socket.timeout, socket.error):
        return False # Connection failed
		
def simple_monitor():
    """
    Monitors a host by sending a single ping request every few seconds.
    """
    # Get the target host from the user
    host_to_check = input("Enter the hostname or IP address to monitor: ")
    
    # Get the monitoring interval from the user
    try:
        delay = int(input("Enter the monitoring interval in seconds (e.g., 5): "))
    except ValueError:
        print("Invalid input. Using default 5 seconds.")
        delay = 5

    print(f"\n--- Starting monitor for {host_to_check} ---")
    print(f"--- Press Ctrl+C to stop ---")

    # Determine the correct ping command based on the OS
    # -n 1 for Windows, -c 1 for Linux/macOS
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host_to_check]

    try:
        while True:
            # Execute the ping command, hiding its output
            # A return code of 0 means the ping was successful
            response = subprocess.run(
                command, 
                stdout=subprocess.DEVNULL, # Hides the command's output
                stderr=subprocess.DEVNULL  # Hides any errors
            )

            # Get the current time for the log message
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if response.returncode == 0:
                print(f"[{current_time}] {host_to_check} is UP")
            else:
                print(f"[{current_time}] {host_to_check} is DOWN")
            
            # Wait for the specified interval before the next check
            time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n--- Monitor stopped by user ---")
    except Exception as e:
        print(f"An error occurred: {e}")

def advanced_monitor():
    """
    Monitors a host by pinging it and then checking specified TCP ports.
    """
    # Get user input
    host_to_check = input("Enter the hostname or IP address to monitor: ")
    ports_str = input("Enter ports to check, separated by commas (e.g., 80,443,22): ")
    
    try:
        ports_to_check = [int(p.strip()) for p in ports_str.split(',')]
    except ValueError:
        print("Invalid port list. Please enter numbers separated by commas.")
        return
        
    try:
        delay = int(input("Enter the monitoring interval in seconds (e.g., 10): "))
    except ValueError:
        print("Invalid input. Using default 10 seconds.")
        delay = 10

    print(f"\n--- Starting advanced monitor for {host_to_check} on ports {ports_to_check} ---")
    print(f"--- Press Ctrl+C to stop ---")

    # Ping command setup
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    ping_command = ['ping', param, '1', host_to_check]

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. First, check if the host is reachable via ping
            ping_response = subprocess.run(
                ping_command, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )

            if ping_response.returncode == 0:
                print(f"[{current_time}] Host {host_to_check} is UP.")
                # 2. If host is up, check the specified ports
                for port in ports_to_check:
                    if check_port(host_to_check, port):
                        print(f"  - Port {port} is OPEN")
                    else:
                        print(f"  - Port {port} is CLOSED")
            else:
                print(f"[{current_time}] Host {host_to_check} is DOWN.")
            
            print("-" * 30) # Separator for clarity
            time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n--- Monitor stopped by user ---")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the advanced monitor
if __name__ == "__main__":
    # Choose which monitor to run. Let's make it easy to switch.
    choice = input("Choose monitor type (1 for Simple, 2 for Advanced): ")
    if choice == '1':
        simple_monitor()
    elif choice == '2':
        advanced_monitor()
    else:
        print("Invalid choice. Running Simple Monitor by default.")
        simple_monitor()