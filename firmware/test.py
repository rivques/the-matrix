from machine import Pin, PWM
import utime
import rp2

SLOWDOWN_CONST = 1

# out_init is for 15xrowdat+coldat, set_init is latch, clear, rowclk, colclk
@rp2.asm_pio(out_init=[rp2.PIO.OUT_LOW] * 16, set_init=[rp2.PIO.OUT_LOW, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW], autopull=True, fifo_join=rp2.PIO.JOIN_TX)
def pio_disp_routine():
    # this function shifts out a single column. It's expecting data to be constantly fed to it via DMA.
    # It consumes 16-bit words (though the FIFO is filled in 32-bit mode), where the first 15 bits are row data and the last bit is column data.
    # A single full column (120 pixels) is 16 bytes of data.

    # Shift 8 times out to the row data pins, pulsing the row clock each time.
    out(pins, 16).delay(1)
    set(pins, 0b1100).delay(1) # just the first time, pulse the column clock
    set(pins, 0b0000).delay(1) # once

pio = rp2.StateMachine(0, pio_disp_routine, out_base=Pin(0), set_base=Pin(16), freq=10_000)
pio.active(1)

try:
    while True:
        utime.sleep(1)
except:
    pio.active(0)
    print("PIO deactivated.")
    raise