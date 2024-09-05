from machine import Pin, PWM
import time

servo_pin = 15  # PWM-capable pin
frequency = 50  # Standard frequency for servos is 50Hz
pwm = PWM(Pin(servo_pin), freq=frequency)

def set_servo_angle(angle):
    # Convert the angle to the duty cycle (between 40 and 115 for 0 to 180 degrees)
    duty = int(40 + (angle / 180.0) * 75)
    pwm.duty(duty)
    