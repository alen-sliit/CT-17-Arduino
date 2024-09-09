import requests as requests
import json as json
import datetime
import time
import sys
import network

from lcd import LCD
from stepper_motor import GORILLACELL_STEPMOTOR
from mail_alert import AlertMail
from servo_motor import ServoMotor
from machine import Pin

# Lists to store pending and monitoring medicines
pendingMedicine = {}
monitoringMedicine = {}
button_enable = False
button_clicked = False

lcd = LCD()
stepper = GORILLACELL_STEPMOTOR()
alert_mail = AlertMail()
servo_motor = ServoMotor()
medi_sw = Pin(0, Pin.IN)


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
        if medicines[medi]["medicineStatus"] == "pending":
            pendingMedicine[medi] = medicines[medi]["medicineTime"]  # {"1":"22:37"}
    print("pending medicine = ", pendingMedicine)


# Alarm function to sound the alert
def start_alarm(medicine):
    lcd.disp_text(f"Take medicine {medicine}")


def open_door():
    global button_clicked
    if button_enable:
        servo_motor.set_servo_angle(180)
        button_clicked = True


def mag_sensor(medi):
    # add a loop to check if medi cap is taken
    close_door()


def close_door():
    servo_motor.set_servo_angle(0)


medi_sw.irq(handler=open_door, trigger=Pin.IRQ_FALLING)


# check if it's time for any pending medicine
def check_pending_medicines():
    global pendingMedicine, monitoringMedicine
    current_time = datetime.datetime.now().strftime("%H:%M")

    for medi in list(pendingMedicine.keys()):
        medicine_time = pendingMedicine[medi]
        print("current time ", current_time, " equals medicine time ", medicine_time)
        if current_time == medicine_time:
            stepper.rotate(int(medi) * 45, 'cw')
            start_alarm(medi)
            monitoringMedicine[medi] = pendingMedicine[medi]

    print("Monitoring medicine = ", monitoringMedicine)


# Function to monitor taken or missed medicines
def monitor_medicines():
    global monitoringMedicine
    current_time_min = int(datetime.datetime.now().strftime("%M"))

    for medi in list(monitoringMedicine.keys()):  # {"1":"22:37"}
        medi_minutes = int(monitoringMedicine[medi].split(":")[1])
        time_diff = (current_time_min - medi_minutes)  # Time difference in minutes

        if time_diff < 0:
            time_diff += 60

        global button_enable
        button_enable = True

        if button_clicked:  # Button pressed
            mag_sensor(medi)
            send_status_to_server(medi, "taken")
            monitoringMedicine.pop(medi)
            pendingMedicine.pop(medi)
            button_clicked = False

        elif time_diff >= 10:  # Medicine missed after 10 minutes
            notify_missed_medicine(medi)
            send_status_to_server(medi, "missed")
            monitoringMedicine.pop(medi)
            pendingMedicine.pop(medi)
        print("time difference: ", time_diff)


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
    alert_mail.send_alert(medicine)


# Main loop
def main_loop():
    while True:
        medicines = fetch_data_from_server()  #{"1":{"medicineStatus":"pending","medicineTime":"22:37"}}
        process_medicines(medicines)
        # checking if the medicine is already been added to monitoring list
        for (key, value) in medicines.items():
            if key not in monitoringMedicine:
                check_pending_medicines()
            elif monitoringMedicine[key] != value:
                check_pending_medicines()
        monitor_medicines()
        time.sleep(20)  # Run every 20 seconds


# Start the loop
main_loop()
