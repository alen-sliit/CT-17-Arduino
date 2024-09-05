from time import sleep_ms, ticks_ms 
from machine import I2C, Pin 
from i2c_lcd import I2cLcd 

AddressOfLcd = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
# connect scl to GPIO 22, sda to GPIO 21
lcd = I2cLcd(i2c, AddressOfLcd, 2, 16)

def testLcd(num):
    lcd.move_to(0,0)
    lcd.putstr('Micropython')
    lcd.move_to(0,1)
    lcd.putstr("Praveen Malik " + str(num))

while True:
    for i in range(100):
        testLcd(i)
        sleep_ms(500)
        
lcd.blink_cursor_on()
lcd.blink_cursor_off()
lcd.show_cursor()
lcd.display_on()
lcd.backlight_on()
