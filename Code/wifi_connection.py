import network
import socket
import time

# Create Access Point
def create_access_point():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32-Config', password='12345678')
    while not ap.active():
        pass
    print('Access Point Created:', ap.ifconfig())

# Handle incoming requests and serve a simple HTML form
def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    if 'GET / ' in request:
        response = """<!DOCTYPE html>
        <html>
        <head>
            <title>ESP32 WiFi Config</title>
        </head>
        <body>
            <h1>Enter WiFi Credentials</h1>
            <form action="/" method="post">
                SSID: <input type="text" name="ssid"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """
        client_socket.send("HTTP/1.1 200 OK\r\n")
        client_socket.send("Content-Type: text/html\r\n")
        client_socket.send("Connection: close\r\n\r\n")
        client_socket.sendall(response)
    elif 'POST / ' in request:
        body_start = request.find('\r\n\r\n') + 4
        body = request[body_start:]
        ssid, password = extract_credentials(body)
        client_socket.send("HTTP/1.1 200 OK\r\n")
        client_socket.send("Content-Type: text/html\r\n")
        client_socket.send("Connection: close\r\n\r\n")
        client_socket.sendall("<h1>Credentials Received!</h1>")

        client_socket.close()
        return ssid, password

    client_socket.close()
    return None, None

# Extract SSID and password from POST body
def extract_credentials(body):
    params = body.split('&')
    ssid = params[0].split('=')[1]
    password = params[1].split('=')[1]
    return ssid, password

# Connect to the provided WiFi credentials
def connect_to_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    # Wait until connected
    for _ in range(10):
        if station.isconnected():
            print('Connected to WiFi:', station.ifconfig())
            return True
        time.sleep(1)

    print('Connection failed!')
    return False

def run_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    ssid, password = None, None

    while ssid is None or password is None:
        client_socket, addr = s.accept()
        ssid, password = handle_client(client_socket)

    return ssid, password

# Main program
create_access_point()

# Start the web server
ssid, password = run_server()

# Once credentials are received, try to connect to the WiFi network
if ssid and password:
    if connect_to_wifi(ssid, password):
        print('Connected successfully!')
    else:
        print('Failed to connect. Restart to try again.')
        create_access_point()