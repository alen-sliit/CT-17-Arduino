from machine import I2C, Pin
from i2c_lcd import I2cLcd 


class LCD:
    def __init__(self):
        address_of_lcd = 0x27
        i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
        # connect scl to GPIO 22, sda to GPIO 21
        self.lcd = I2cLcd(i2c, address_of_lcd, 2, 16)

    def disp_text(self, prompt1, prompt2, num):
        self.lcd.move_to(0, 0)
        self.lcd.putstr(prompt1)
        self.lcd.move_to(0, 1)
        self.lcd.putstr(prompt2 + " " + str(num))


        
# lcd.blink_cursor_on()
# lcd.blink_cursor_off()
# lcd.show_cursor()
# lcd.display_on()
# lcd.backlight_on()
