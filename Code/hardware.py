from machine import I2C, Pin, PWM

from i2c_lcd import I2cLcd
import time

# LCD Class
class LCD:
    def __init__(self):
        AddressOfLcd = 0x27
        i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
        self.lcd = I2cLcd(i2c, AddressOfLcd, 2, 16)

    def dispStr(self, prompt):
        self.lcd.putstr(prompt)

    def clear(self):
        self.lcd.clear()


# Servo Motor Class
class ServoMotor:
    def __init__(self):
        servo_pin = 15  # PWM-capable pin
        frequency = 50  # Standard frequency for servos is 50Hz
        self.pwm = PWM(Pin(servo_pin), freq=frequency)

    def set_servo_angle(self, angle):
        duty = int(40 + (angle / 180.0) * 75)
        self.pwm.duty(duty)



class GORILLACELL_STEPMOTOR:
    def __init__(self):
        IN1 = Pin(13, Pin.OUT)
        IN2 = Pin(12, Pin.OUT)
        IN3 = Pin(14, Pin.OUT)
        IN4 = Pin(27, Pin.OUT)

# Define the step sequence for half-stepping
half_step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

# Function to set the motor coil states
def set_step(self,w1, w2, w3, w4):
    IN1.value(w1)
    IN2.value(w2)
    IN3.value(w3)
    IN4.value(w4)

# Function to rotate the motor
def step_motor(self,steps, delay=2):
    for _ in range(steps):
        for step in half_step_sequence:
            set_step(step[0], step[1], step[2], step[3])
            time.sleep_ms(delay)

# Main loop to control motor
try:
    while True:
        step_motor(512)  # Rotate 512 steps (one full rotation)
        time.sleep(2)
        step_motor(-512)  # Rotate 512 steps in the opposite direction
        time.sleep(2)

except KeyboardInterrupt:
    # Turn off all coils when the script is stopped
    set_step(0, 0, 0, 0)
    print("Motor stopped")

# Alarm Class
class Alarm:
    def __init__(self):
        self.buzzer = PWM(Pin(5))

    def start_buzzer(self):
        for _ in range(10):
            self.buzzer.freq(1000)
            self.buzzer.duty(512)
            time.sleep(0.2)
            self.buzzer.duty(0)
            time.sleep(0.2)
        print("Buzzer finished alarm sequence.")

    def stop_buzzer(self):
        self.buzzer.duty(0)
        print("Alarm stopped.")


# Door Control Class
class DoorControl:
    def __init__(self):
        self.servo_motor = ServoMotor()

    def open_door(self):
        self.servo_motor.set_servo_angle(180)
        print("Door opened.")

    def close_door(self):
        self.servo_motor.set_servo_angle(90)
        print("Door closed.")

# Custom RTC Class for DS1307
class RealTimeClock:
    DS1307_I2C_ADDR = 0x68

    def __init__(self):
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

    def bcd_to_dec(self, bcd):
        return (bcd // 16) * 10 + (bcd % 16)

    def dec_to_bcd(self, dec):
        return (dec // 10) * 16 + (dec % 10)

    def get_time_in_utc(self):
        # Read time data from DS1307
        data = self.i2c.readfrom_mem(self.DS1307_I2C_ADDR, 0x00, 7)

        # Convert BCD to decimal
        second = self.bcd_to_dec(data[0] & 0x7F)  # Mask to ignore clock halt bit
        minute = self.bcd_to_dec(data[1])
        hour = self.bcd_to_dec(data[2] & 0x3F)  # 24-hour format

        return hour, minute, second

    def get_formatted_time(self):
        hour, minute, _ = self.get_time_in_utc()
        return f"{hour:02}:{minute:02}"  # 24-hour time format

    def get_date(self):
        data = self.i2c.readfrom_mem(self.DS1307_I2C_ADDR, 0x00, 7)

        year = self.bcd_to_dec(data[6]) + 2000
        month = self.bcd_to_dec(data[5])
        day = self.bcd_to_dec(data[4])

        return f"{year}-{month:02}-{day:02}"  # Format YYYY-MM-DD
    def set_time(self, hour, minute, second):
        # Convert time to BCD and write to DS1307
        data = bytearray(3)
        data[0] = self.dec_to_bcd(second)
        data[1] = self.dec_to_bcd(minute)
        data[2] = self.dec_to_bcd(hour)  # 24-hour format
        self.i2c.writeto_mem(self.DS1307_I2C_ADDR, 0x00, data)

    def set_date(self, year, month, day):
        # Convert date to BCD and write to DS1307
        data = bytearray(4)
        data[0] = self.dec_to_bcd(day)
        data[1] = self.dec_to_bcd(month)
        data[2] = self.dec_to_bcd(year - 2000)  # Store only the last two digits of the year
        self.i2c.writeto_mem(self.DS1307_I2C_ADDR, 0x04, data)
