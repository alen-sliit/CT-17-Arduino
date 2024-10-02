import time
import urequests  
import ujson  
import network
# from mail_alert import AlertMail
from machine import Pin
from hardware import LCD, SG90Servo, DoorControl, Alarm, RealTimeClock, IR

# Lists to store pending and monitoring medicines
pendingMedicine = {}
monitoringMedicine = {}

ipaddress = "192.168.167.228"

def getTime():
    try:
        # Send GET request to the server
        response = urequests.get("http://worldtimeapi.org/api/timezone/Asia/Colombo")
        if response.status_code == 200:
            api_response = ujson.loads(response.text)
            datetime_str = api_response['datetime']

            # The datetime format is "YYYY-MM-DDTHH:MM:SS.SSSSSS±HH:MM"
            hours = int(datetime_str[11:13])   # Slice out the hours part
            minutes = int(datetime_str[14:16])  # Slice out the minutes part
            seconds = int(datetime_str[17:19])
            
            # Extract year, month, and day using string slicing
            # The datetime format is "YYYY-MM-DDTHH:MM:SS.SSSSSS±HH:MM"
            year = int(datetime_str[0:4])   # Slice out the year part
            month = int(datetime_str[5:7])  # Slice out the month part
            day = int(datetime_str[8:10])   # Slice out the day part
            
            rtc.set_time(hours,minutes,seconds)
            rtc.set_date(year, month, day)
        else:
            print("Error fetching data, status code:", response.status_code)
            
    except Exception as e:
        print("Error:", e)

def connectWifi():
    # Initialize Wi-Fi in station mode
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    ssid = "realme C53"
    password = "12345678"
    # Connect to the selected network
    print(f"Connecting to {ssid}...")
    sta_if.connect(ssid, password)

    # Check connection status
    if sta_if.isconnected():
        lcd.dispStr("\nConnected!")
        lcd.dispStr(f"Network config: {sta_if.ifconfig()}", )
    else:
        lcd.dispStr("\nFailed to connect. Please check your password and try again.")
    time.sleep(5)
    lcd.clear()
    
def fetch_data_from_server():
    try:
        # Send GET request to the server
        response = urequests.get(f"http://{ipaddress}:3000/espGet")
        if response.status_code == 200:
            # Parse JSON response
            data = ujson.loads(response.text)
            print("received data from server =", data)
            return data
        else:
            # Handle non-200 status codes
            print("Error fetching data, status code:", response.status_code)
            return {}
    except Exception as e:
        # Handle any exceptions (e.g., network error)
        print("Error:", e)
        return {}

# Setup button
def setup_button_interrupt(pin_number):
    medi_sw = Pin(pin_number, Pin.IN, Pin.PULL_UP)
    medi_sw.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

def button_pressed(pin):
    global button_enable, button_clicked
    button_clicked = True
    if button_enable:
        print("Button pressed.")
        bottle_taken = False
        time_elapsed = 0
        button_enable = False

        door_control.open_door() 
        
        while time_elapsed <= 30:
            if ir_sensor.is_bottle_removed():
                print(f"Pill bottle {medi} removed. Waiting for it to be put back.")
                print(f"Pill bottle {medi} put back. Door closing.")
                time.sleep(15)
                door_control.close_door()
                break
  
            time.sleep(1)  # Sleep for 1 second between checks
            time_elapsed += 1
             
        
        # If no bottle was taken after 30 seconds, or it was put back, close the door
        if not bottle_taken:
            print("No pill bottle taken after 30 seconds. Door closing.")
            door_control.close_door()


# Add pending medicines to the pendingMedicine list
def process_medicines(medicines):
    global pendingMedicine
    for medi in list(medicines.keys()):
        if medicines[medi]["medicineStatus"] == "pending":
            pendingMedicine[medi] = medicines[medi]["medicineTime"]
    print("Pending medicine:", pendingMedicine)

# function to sound the alarm
def start_alarm(medicine):
    lcd.dispStr(f"Take medicine {medicine}")
    # alarm.start_buzzer()

# Set the desired date and time
def display_time_and_date():
    current_time = rtc.get_formatted_time()
    current_date = rtc.get_date()
    
    lcd.clear()
    lcd.dispStr(f"Time:{current_time}      ")  
    lcd.dispStr(f"Date:{current_date}")  
    time.sleep(0.5)

def check_pending_medicines():
    global pendingMedicine, monitoringMedicine
    
    display_time_and_date()   
    current_time = rtc.get_formatted_time()
        
    for medi, medi_time in list(pendingMedicine.items()):
        if medi_time == current_time:
            lcd.clear()
            stepper.attach()
            stepper.rotate(int(medi))
            stepper.detach()
            # Move to monitoring list
            monitoringMedicine[medi] = pendingMedicine[medi]  
            pendingMedicine.pop(medi)  
            start_alarm(medi)   

# Function to monitor taken or missed medicines
def monitor_medicines():
    global monitoringMedicine, button_enable, button_clicked
    elapsed_time = 0

    while monitoringMedicine:
        medi = list(monitoringMedicine.keys())[0]
        print(f"Time to take medicine {medi}. Waiting for button press...")
        button_enable = True

        # Wait for button press or timeout
        while elapsed_time <= 100:
            print("Waiting for button press or timeout...")
            time.sleep(5)
            elapsed_time += 50
        
        lcd.clear()
        
        if button_clicked:
            lcd.dispStr("Medicine taken")
            send_status_to_server(medi, "taken")
            print(f"Medicine {medi} taken.")
        else:
            print(f"Medicine {medi} missed.")
            send_status_to_server(medi, "missed")
        stepper.attach()
        stepper.rotate(8 - int(medi))
        stepper.detach()

        monitoringMedicine.pop(medi)
        lcd.clear()

def send_status_to_server(medicine, status):
    print(f"Sending Medicine {medicine} status '{status}' to server.")
    
    try:
        data = {
           medicine: status
        }
        json_data = ujson.dumps(data)  # Convert to JSON string
        response = urequests.post(f"http://{ipaddress}:3000/espPost", data=json_data, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            print("Status sent successfully:", status)
        else:
            print("Failed to send status:", response.status_code)
        
        response.close()  # Always close the response to free memory
    except Exception as e:
        print("Error:", e)


# Notify user about missed medicine (add custom notification logic here)
def notify_missed_medicine(medicine):
    alert_mail.send_alert(medicine)

# Initialize hardware components
lcd = LCD()
# stepper = STEPMOTOR()
door_control = DoorControl()  
alarm = Alarm()  
rtc = RealTimeClock()
setup_button_interrupt(18)
ir_sensor = IR(4)

button_clicked = False

connectWifi()
getTime()

# Main loop
def main_loop():
    while True:
        medicines = fetch_data_from_server()
        process_medicines(medicines)

        if pendingMedicine:
            check_pending_medicines()
        if monitoringMedicine:
            monitor_medicines()
        time.sleep(20)

main_loop()



