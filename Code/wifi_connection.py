import network
import time
import sys


def scan_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning for Wi-Fi networks...")
    networks = wlan.scan()  # Scans for available networks
    
    available_networks = []  # Initialize the list to store SSIDs
    
    print("\nAvailable Networks:")
    for idx, net in enumerate(networks):  # Enumerate through the networks
        ssid = net[0].decode('utf-8')  # Decode the SSID from bytes to string
        print(f"{idx + 1}. {ssid}")
        available_networks.append(ssid)
    
    return available_networks


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print(f"\nConnecting to {ssid}...")
    
    # Wait for connection with timeout
    timeout = 10  # 10 seconds timeout
    while not wlan.isconnected() and timeout > 0:
        print("Connecting...", end="\r")
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print(f"\nConnected to {ssid}")
        print("Network config:", wlan.ifconfig())
    else:
        print(f"\nFailed to connect to {ssid}")
        wlan.disconnect()

def choose_wifi(networks):
    try:
        choice = int(input("\nEnter the number of the network you want to connect to: ")) - 1
        if 0 <= choice < len(networks):
            return networks[choice]
        else:
            print("Invalid choice!")
            sys.exit()
    except ValueError:
        print("Invalid input!")
        sys.exit()

def main():
    networks = scan_wifi()
    
    if len(networks) == 0:
        print("No Wi-Fi networks found!")
        return
    
    ssid = choose_wifi(networks)
    password = input(f"Enter password for {ssid}: ")
    
    connect_to_wifi(ssid, password)

if __name__ == "__main__":
    main()
