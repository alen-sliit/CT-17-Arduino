import requests as requests
import json as json
import datetime
# import machine
import time
# from machine import Pin, Timer

# Lists to store pending and monitoring medicines
pendingMedicine = {}
monitoringMedicine = {}
button_clicked = False

# Pin setup for the button and motor (adjust according to your hardware)
# button = Pin(14, Pin.IN, Pin.PULL_UP)  # Assume button connected to GPIO 14
# motor = Pin(15, Pin.OUT)  # Assume motor connected to GPIO 15

def fetch_data_from_server():
    try:
        response = requests.get("http://localhost:3000/espGet")
        if response.status_code == 200:
            data = json.loads(response.text)
            print("received data from server = ", data)
            return data
        else:
            print("Error fetching data, status code:", response.status_code)
            return {}
    except Exception as e:
        print("Error:", e)
        return {}

# Add pending medicines to the pendingMedicine list 
def process_medicines(medicines):
    global pendingMedicine
    for medi in list(medicines.keys()):
        if (medicines[medi]["medicineStatus"] == "pending"):
            pendingMedicine[medi] = medicines[medi]["medicineTime"] #{"1":"22:37"}
    print("pending medicine = ", pendingMedicine)

# Alarm function to sound the alert
def start_alarm(medicine):
    print("ALARM! Time to take your medicine ", medicine)
    # You can add buzzer or LED code here for actual hardware alert

# check if it's time for any pending medicine
def check_pending_medicines():
    global pendingMedicine, monitoringMedicine
    current_time = datetime.datetime.now().strftime("%H:%M")

    for medi in list(pendingMedicine.keys()):  
        medicine_time = pendingMedicine[medi]
        print("current time ", current_time, " equals medicine time ", medicine_time)
        if current_time == medicine_time:
            start_alarm(medi)
            monitoringMedicine[medi] = pendingMedicine[medi]
            
    print("Monitoring medicine = ", monitoringMedicine)

# Function to monitor taken or missed medicines
def monitor_medicines():
    global monitoringMedicine
    current_time_min = int(datetime.datetime.now().strftime("%M"))

    for medi in list(monitoringMedicine.keys()):  #{"1":"22:37"}        
        medi_minutes = int(monitoringMedicine[medi].split(":")[1])
        time_diff = (current_time_min - medi_minutes)  # Time difference in minutes

        if time_diff < 0:
            time_diff += 60 

        if button_clicked:  # Button pressed 
            rotate_motor()
            send_status_to_server(medi, "taken")
            monitoringMedicine.pop(medi)
            pendingMedicine.pop(medi)

        elif time_diff >= 2:  # Medicine missed after 10 minutes
            notify_missed_medicine(medi)
            send_status_to_server(medi, "missed")
            monitoringMedicine.pop(medi)
            pendingMedicine.pop(medi)
        print("time diif: ",time_diff)

# Function to rotate the motor
def rotate_motor():
    # motor.on()  # Rotate motor to dispense medicine
    # time.sleep(2)  # Delay for motor to run
    # motor.off()
    print("motor rotating")

# Function to send medicine status back to the server
def send_status_to_server(medicine, status):
    try:
        data = {
            medicine: status
        }
        response = requests.post("http://localhost:3000/espPost", json=data)
        if response.status_code == 200:
            print("Status sent successfully:", status)
        else:
            print("Failed to send status:", response.status_code)
    except Exception as e:
        print("Error:", e)

# Notify user about missed medicine (add custom notification logic here)
def notify_missed_medicine(medicine):
    print("You missed your medicine:", medicine)

# Main loop
def main_loop():
    while True:
        medicines = fetch_data_from_server() #{"1":{"medicineStatus":"pending","medicineTime":"22:37"}}
        process_medicines(medicines)
        # checking if the medicine is already been added to monitoring list
        for (key,value) in medicines.items():
            if key not in monitoringMedicine: 
                check_pending_medicines()
            elif monitoringMedicine[key] != value:
                check_pending_medicines()
        monitor_medicines()
        time.sleep(20)  # Run every 20 seconds

# Start the loop
main_loop()
