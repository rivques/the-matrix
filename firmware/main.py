from machine import Pin
import utime

SLOWDOWN_CONST = 1_000_00

class Matrix:
    def __init__(self):
        self.rowdat_pins = [Pin(i, Pin.OUT) for i in range(1)]
        self.coldat_pin = Pin(15, Pin.OUT)
        self.latch_pin = Pin(16, Pin.OUT)
        self.latch_pin.value(0)
        self.clear_pin = Pin(17, Pin.OUT) # active low
        self.clear_pin.value(1)
        self.rowclk_pin = Pin(18, Pin.OUT)
        self.rowclk_pin.value(0)
        self.colclk_pin = Pin(19, Pin.OUT)
        self.colclk_pin.value(0)
        self.rowen_pin = Pin(20, Pin.OUT)
        self.rowen_pin.value(1) # disable output for now

        # clear registers
        self.clear_pin.value(0)
        utime.sleep_ms(2)
        self.clear_pin.value(1)

        # shift ones through the columns
        self.coldat_pin.value(1)
        for _ in range(len(self.rowdat_pins) * 8):
            self.colclk_pin.value(1)
            utime.sleep_us(10)
            self.colclk_pin.value(0)
            utime.sleep_us(10)
        self.latch_pin.value(1)
        utime.sleep_us(10)
        self.latch_pin.value(0)

    def display_frame(self, frame):
        try: 
            print("Displaying frame...")
            # the frame is a 2D list of bytes. each byte represents 8 pixels in a column.
            # to display a frame:
            # for each column:
            #  shift out the rows (8 pixels to a row pin)
            #  if it's the first column, shift a 0 onto the column data, otherwise, shift a 1
            #  latch the data

            # enable output
            self.rowen_pin.value(0)
            for col in range(len(frame)):
                print(f"Processing column {col}")
                # runs once per column
                for row in range(8):
                    # runs 8 times per column (once per row SR size)
                    for i, pin in enumerate(self.rowdat_pins):
                        # runs once per row per column
                        bit = (frame[col][i] & (1 << (row % 8))) != 0
                        print(f"  Row {row}, Pin {i}: {'ON' if bit else 'OFF'}")
                        if bit:
                            pin.value(1)
                        else:
                            pin.value(0)
                    utime.sleep_us(5*SLOWDOWN_CONST)
                    # shift out the row data
                    self.rowclk_pin.value(1)
                    utime.sleep_us(10*SLOWDOWN_CONST)
                    self.rowclk_pin.value(0)
                    utime.sleep_us(10*SLOWDOWN_CONST)
                # shift out the column data
                if col == 0:
                    self.coldat_pin.value(0)
                    print("  Setting coldat pin LOW for first column")
                else:
                    self.coldat_pin.value(1)
                    print("  Setting coldat pin HIGH")
                utime.sleep_us(5*SLOWDOWN_CONST)
                self.colclk_pin.value(1)
                utime.sleep_us(10*SLOWDOWN_CONST)
                self.colclk_pin.value(0)
                utime.sleep_us(10*SLOWDOWN_CONST)
                # latch the data
                self.latch_pin.value(1)
                utime.sleep_us(10*SLOWDOWN_CONST)
                self.latch_pin.value(0)
                print(f"  Latched column {col}")
            utime.sleep_us(235*SLOWDOWN_CONST)
            print("Frame displayed.")
        finally:
            # disable output
            self.rowen_pin.value(1)
            print("Output disabled.")

matrix = Matrix()
heart_frame = [
    [0b00110000],
    [0b01111000],
    [0b01111100],
    [0b00111110],
    [0b01111100],
    [0b01111000],
    [0b00110000],
    [0b00000000]
]

while True:
    matrix.display_frame(heart_frame)