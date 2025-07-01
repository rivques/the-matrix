from machine import Pin
import utime

rowdat_pins = [Pin(i, Pin.OUT) for i in range(1)]
coldat_pin = Pin(15, Pin.OUT)
latch_pin = Pin(16, Pin.OUT)
latch_pin.value(0)
clear_pin = Pin(17, Pin.OUT) # active low
clear_pin.value(1)
rowclk_pin = Pin(18, Pin.OUT)
rowclk_pin.value(0)
colclk_pin = Pin(19, Pin.OUT)
colclk_pin.value(0)
rowen_pin = Pin(20, Pin.OUT)
rowen_pin.value(0) # enable output for now

# clear registers
clear_pin.value(0)
utime.sleep_ms(2)
clear_pin.value(1)

# put a 1 in columns 0 and 1
coldat_pin.value(1)
utime.sleep_us(100)
colclk_pin.value(1)
utime.sleep_us(100)
colclk_pin.value(0)
utime.sleep_us(100)
colclk_pin.value(1)
utime.sleep_us(100)
colclk_pin.value(0)
utime.sleep_us(100)
latch_pin.value(1)
utime.sleep_us(100)
latch_pin.value(0)

# parade a 1 across the rows
while True:
    rowdat_pins[0].value(1)
    utime.sleep_us(100)
    rowclk_pin.value(1)
    utime.sleep_us(100)
    rowclk_pin.value(0)
    utime.sleep_us(100)
    rowdat_pins[0].value(0)
    utime.sleep_us(100)
    latch_pin.value(1)
    utime.sleep_us(100)
    latch_pin.value(0)
    for i in range(7):
        # # run a 1 across the columns
        # coldat_pin.value(0)
        # utime.sleep_us(100)
        # colclk_pin.value(1)
        # utime.sleep_us(100)
        # colclk_pin.value(0)
        # utime.sleep_us(100)
        # latch_pin.value(1)
        # utime.sleep_us(100)
        # latch_pin.value(0)
        # coldat_pin.value(1)
        # for j in range(7):
        #     print(f"Row {i}, Column {j+1}")
        #     colclk_pin.value(1)
        #     utime.sleep_us(100)
        #     colclk_pin.value(0)
        #     utime.sleep_us(100)
        #     latch_pin.value(1)
        #     utime.sleep_us(100)
        #     latch_pin.value(0)
        #     utime.sleep_ms(500)
        rowclk_pin.value(1)
        utime.sleep_us(100)
        rowclk_pin.value(0)
        utime.sleep_ms(500)
        print(f"Row {i+1} shifted out")
    


# shift ones through the columns
coldat_pin.value(1)
utime.sleep_us(100)
for _ in range(len(rowdat_pins) * 8):
    colclk_pin.value(1)
    utime.sleep_us(100)
    colclk_pin.value(0)
    utime.sleep_us(100)
latch_pin.value(1)
utime.sleep_us(100)
latch_pin.value(0)

print("Initialized. Current state should be ROWEN high, ones on all 74HC595 outputs, so all row/col should be tristated from both sides.")
print("Check that this is true:")
utime.sleep(2)

print("Setting columns to 0, should drive all cols HIGH. low side should still be tristated.")
coldat_pin.value(0)
for _ in range(len(rowdat_pins) * 8):
    colclk_pin.value(1)
    utime.sleep_us(10)
    colclk_pin.value(0)
    utime.sleep_us(10)
latch_pin.value(1)
utime.sleep_us(10)
latch_pin.value(0)
print("Confirm HIGH on columns:")
while True:
    pass