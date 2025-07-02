from machine import Pin, PWM, freq
import utime
import rp2

#freq(25_000_000)  # Set the CPU frequency to 18 MHz for better timing control
SLOWDOWN_CONST = 1
NUM_COLS = 40

# out_init is for 15xrowdat+coldat, set_init is latch, clear, rowclk, colclk
@rp2.asm_pio(out_init=[rp2.PIO.OUT_LOW] * 16, set_init=[rp2.PIO.OUT_LOW, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW], autopull=True, pull_thresh=16, fifo_join=rp2.PIO.JOIN_TX)
def pio_disp_routine():
    # this function shifts out a single column. It's expecting data to be constantly fed to it via DMA.
    # It consumes 16-bit words (though the FIFO is filled in 32-bit mode), where the first 15 bits are row data and the last bit is column data.
    # A single full column (120 pixels) is 16 bytes of data.

    # Shift 8 times out to the row data pins, pulsing the row clock each time.
    out(pins, 16).delay(1)
    set(pins, 0b1110).delay(1) # just the first time, pulse the column clock
    set(pins, 0b0010).delay(1) # once
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # twice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # thrice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # quadrice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # quintice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # sextice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # septice
    out(pins, 16).delay(1)
    set(pins, 0b0110).delay(1)
    set(pins, 0b0010).delay(1) # octice

    # latch the data
    set(pins, 0b0011).delay(1) # latch pin high
    set(pins, 0b0010).delay(1) # latch pin low

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
        self.rowen_pin = PWM(Pin(20, Pin.OUT), freq=10_000_000, duty_u16=0)
        self.rowen_pin.duty_u16(65535) # disable output for now
        self.brightness = 0.5

        # clear registers
        self.clear_pin.value(0)
        utime.sleep_ms(2)
        self.clear_pin.value(1)

        # shift ones through the columns
        self.coldat_pin.value(1)
        for _ in range(NUM_COLS):
            self.colclk_pin.value(1)
            utime.sleep_us(10)
            self.colclk_pin.value(0)
            utime.sleep_us(10)
        self.latch_pin.value(1)
        utime.sleep_us(10)
        self.latch_pin.value(0)

    def display_frame(self, frame):
        try: 
            # print("Displaying frame...")
            # the frame is a 2D list of bytes. each byte represents 8 pixels in a column.
            # to display a frame:
            # for each column:
            #  shift out the rows (8 pixels to a row pin)
            #  if it's the first column, shift a 0 onto the column data, otherwise, shift a 1
            #  latch the data

            # enable output
            self.rowen_pin.duty_u16(int((1-self.brightness) * 65535))
            self.brightness += 0.01
            if self.brightness > 0.7:
                self.brightness = 0.0

            for col in range(len(frame)):
                # print(f"Processing column {col}")
                # runs once per column
                for row in range(8):
                    # runs 8 times per column (once per row SR size)
                    for i, pin in enumerate(self.rowdat_pins):
                        # runs once per row per column
                        bit = (frame[col][i] & (1 << (row % 8))) != 0
                        # print(f"  Row {row}, Pin {i}: {'ON' if bit else 'OFF'}")
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
                    # print("  Setting coldat pin LOW for first column")
                else:
                    self.coldat_pin.value(1)
                    # print("  Setting coldat pin HIGH")
                utime.sleep_us(5*SLOWDOWN_CONST)
                self.colclk_pin.value(1)
                utime.sleep_us(10*SLOWDOWN_CONST)
                self.colclk_pin.value(0)
                utime.sleep_us(10*SLOWDOWN_CONST)
                # latch the data
                self.latch_pin.value(1)
                utime.sleep_us(10*SLOWDOWN_CONST)
                self.latch_pin.value(0)
                # print(f"  Latched column {col}")
            utime.sleep_us(235*SLOWDOWN_CONST)
            # print("Frame displayed.")
        finally:
            # disable output
            self.rowen_pin.duty_u16(65535)
            # print("Output disabled.")
    
    def display_pio(self, frame, pio_freq):
        # configure the PIO to display the given frame.
        # As a first step, convert the frame to the format PIO is expecting.
        # The frame is given as a 2D list of bytes, where each top-level list is a column and each byte is 8 pixels in that column.
        # The PIO expects 8 16-bit words per column, where each the LS 15 bits in row i are data for row % 8 == i in that column, and the MS bit is 1 at the first word in the column.\

        pio_data = []
        for col in range(len(frame)):
            # runs once per column
            words = [1 << 15] * 8 # 8 words per column
            if col == 0:
                words[0] = 0 # first column has a 0 in the MS bit of the first word

            for word_num in range(len(words)):
                # runs 8 times per column, once per PIO input word
                for row_reg in range(15):
                    # runs once per row shift register
                    if row_reg < 1:
                        bit = (frame[col][row_reg] & (1 << word_num)) != 0
                    else:
                        bit = 0 # we only have 1 row SR for now
                    # put the bit in the correct position in the word    
                    words[word_num] |= (bit << row_reg)
            
            # put each byte of each word in the PIO data array, little-endian
            print(f"Words for column {col}:")
            for word in words:
                print(f"  {word:016b}", end=' ')
                pio_data.append(word & 0xFF)
                pio_data.append((word >> 8) & 0xFF)
            print()
        
        raw_data = bytearray(pio_data)
        print(f"Raw PIO data: {raw_data.hex()}")
        self.pio = rp2.StateMachine(0, pio_disp_routine, out_base=self.rowdat_pins[0], set_base=self.latch_pin, freq=pio_freq)
        self.dma = rp2.DMA()
        config = self.dma.pack_ctrl(
            inc_write=False, # don't increment the write addr, we're writing to the peripheral
            # ring_size=8, # 16 bytes per column, 8 columns (TODO: increment 3 when more columns are added)
            # ring_sel=False, # increment the read address
            treq_sel=0, # dreq on the TX FIFO of the first PIO state machine
            size=1, # 16-bit transfers
            bswap=False, # no byte swapping
            irq_quiet=False, # irq on completion
        )
        self.dma.config(read=raw_data, write=self.pio, ctrl=config, count=8*NUM_COLS, trigger=False)
        self.dma.irq(lambda _: self.dma.config(read=raw_data, write=self.pio, ctrl=config, count=8*NUM_COLS, trigger=True), hard=True)
        self.pio.active(1)
        self.dma.active(1)
        

matrix = Matrix()
frame = [
    # heart
    [0b00110000],
    [0b01111000],
    [0b01111100],
    [0b00111110],
    [0b01111100],
    [0b01111000],
    [0b00110000],
    [0b00000000],
    # smiley
    [0b01111110],
    [0b11001011],
    [0b11111101],
    [0b11111101],
    [0b11111101],
    [0b11111101],
    [0b11001011],
    [0b01111110],
    # inverted heart
    [0b11001111],
    [0b10000111],
    [0b10000011],
    [0b11000001],
    [0b10000011],
    [0b10000111],
    [0b11001111],
    [0b11111111],
    # 1px checkerboard
    [0b10101010],
    [0b01010101],
    [0b10101010],
    [0b01010101],
    [0b10101010],
    [0b01010101],
    [0b10101010],
    [0b01010101],
    # 2px checkerboard
    [0b11001100],
    [0b11001100],
    [0b00110011],
    [0b00110011],
    [0b11001100],
    [0b11001100],
    [0b00110011],
    [0b00110011],  
]
matrix.rowen_pin.duty_u16(32000)

pio_freq = 400_000  # PIO frequency
matrix.display_pio(frame, pio_freq)
try:
    while True:
        utime.sleep_ms(500)
        print(f"{matrix.pio.tx_fifo()} bytes on the TX FIFO")
        print(f"State machine active: {matrix.pio.active()}")
        print(f"DMA active: {matrix.dma.active()}")
        print(f"Processor frequency: {freq()} Hz")
        print(f"PIO frequency: {pio_freq} Hz")

except:
    matrix.dma.active(0)
    matrix.pio.active(0)
    matrix.dma.close()
    matrix.rowen_pin.duty_u16(65535)  # disable output
    print("DMA and PIO deactivated.")
    raise