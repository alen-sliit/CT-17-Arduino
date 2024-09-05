from machine import Pin

led = Pin(2, Pin.OUT)
sw = Pin(0, Pin.IN)

def toggleLight(pin):
    led.value(not led.value())

sw.irq(handler=toggleLight, trigger=Pin.IRQ_FALLING)
