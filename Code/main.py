import time
# import requests as requests
# import json as json
# import sys
# import network

# from mail_alert import AlertMail
from machine import Pin
from hardware import LCD, STEPMOTOR, DoorControl, Alarm, RealTimeClock

# Lists to store pending and monitoring medicines
pendingMedicine = {}
monitoringMedicine = {}

button_enable = False
button_clicked = False
door_control = None 

# Initialize hardware components
lcd = LCD()
stepper = STEPMOTOR()
door_control = DoorControl()  
alarm = Alarm()  
rtc = RealTimeClock()
# def fetch_data_from_server():
#     try:
#         response = requests.get("http://localhost:3000/espGet")
#         if response.status_code == 200:
#             data = json.loads(response.text)
#             print("received data from server = ", data)
#             return data
#         else:
#             print("Error fetching data, status code:", response.status_code)
#             return {}
#     except Exception as e:
#         print("Error:", e)
#         return {}


# Function to create dummy data
def fetch_dummy_data():
    data = {
        "1": {"medicineStatus": "pending", "medicineTime": "17:30"},
        "2": {"medicineStatus": "pending", "medicineTime": "17:32"},
        "3": {"medicineStatus": "missed", "medicineTime": "23:40"}
    }
    print("Using dummy data:", data)
    return data

# Setup button
def setup_button_interrupt(pin_number, door_control_instance):
    global door_control
    door_control = door_control_instance  # Set the DoorControl instance
    medi_sw = Pin(pin_number, Pin.IN, Pin.PULL_UP)
    medi_sw.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

def button_pressed(pin):
    global button_enable, button_clicked, door_control
    if button_enable and door_control:
        print("Button pressed.")
        button_clicked = True
        print("opening door....")
        #door_control.open_door()
        time.sleep(10)
        #door_control.close_door()
        print("closing door....")
        button_enable = False

setup_button_interrupt(18, door_control)

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
    alarm.start_buzzer()

# Clears screen
def clear_display():
    lcd.clear()

# Set the desired date and time
rtc.set_time(17, 30, 0)
rtc.set_date(3, 25, 9, 2024)

def display_time_and_date():
    current_time = rtc.get_formatted_time()
    current_date = rtc.get_date()
    
    lcd.clear()
    lcd.dispStr(f"Time:{current_time}\n")  
    lcd.dispStr(f"Date:{current_date}")  
    time.sleep(0.5)

def check_pending_medicines():
    global pendingMedicine, monitoringMedicine
    found_medicine = False
    while not found_medicine:
        display_time_and_date()  
        current_time = rtc.get_formatted_time()
        
        for medi, medi_time in list(pendingMedicine.items()):
            if medi_time == current_time:
                lcd.clear()
                stepper.attach()
                stepper.rotate(int(medi), 'cw')
                stepper.detach()
                # Move to monitoring list
                monitoringMedicine[medi] = pendingMedicine[medi]  
                pendingMedicine.pop(medi)  
                start_alarm(medi)  
                found_medicine = True
                return medi
        time.sleep(1)  

# Function to monitor taken or missed medicines
def monitor_medicines():
    global monitoringMedicine, button_enable, button_clicked
    elapsed_time = 0

    while monitoringMedicine:
        medi = list(monitoringMedicine.keys())[0]
        print(f"Time to take medicine {medi}. Waiting for button press...")
        button_enable = True
        button_clicked = False

        # Wait for button press or timeout
        while elapsed_time <= 100 and not button_clicked:
            print("Waiting for button press or timeout...")
            time.sleep(5)
            elapsed_time += 50

        if button_clicked:
            clear_display()
            lcd.dispStr("Medicine taken")
            send_status_to_server(medi, "taken")
            print(f"Medicine {medi} taken.")
            stepper.attach()
            stepper.rotate(int(medi), 'ccw')
            stepper.detach()
        else:
            print(f"Medicine {medi} missed.")
            send_status_to_server(medi, "missed")
            stepper.attach()
            stepper.rotate(int(medi), 'ccw')
            stepper.detach()

        monitoringMedicine.pop(medi)
        clear_display()

# Simulate sending medicine status back to the server
def send_status_to_server(medicine, status):
    print(f"Sending Medicine {medicine} status '{status}' to server.")


# # Function to send medicine status back to the server
# def send_status_to_server(medicine, status):
#     try:
#         data = {
#             medicine: status
#         }
#         response = requests.post("http://localhost:3000/espPost", json=data)
#         if response.status_code == 200:
#             print("Status sent successfully:", status)
#         else:
#             print("Failed to send status:", response.status_code)
#     except Exception as e:
#         print("Error:", e)


# # Notify user about missed medicine (add custom notification logic here)
# def notify_missed_medicine(medicine):
#     alert_mail.send_alert(medicine)

# Main loop
def main_loop():
    alarm.stop_buzzer()
    
    while True:
        medicines = fetch_dummy_data()
        process_medicines(medicines)

        while pendingMedicine or monitoringMedicine:
            if pendingMedicine:
                check_pending_medicines()
            if monitoringMedicine:
                monitor_medicines()
            time.sleep(20)

main_loop()
