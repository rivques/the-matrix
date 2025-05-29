# the-matrix

This is a large (1ftx1ft) LED matrix display with a resolution of 120x120 monochrome pixels. My intended use for it is to act as an "ultra-clock," showing not just the time but also other useful information like weather, sports scores, maybe news, etc.

I've had the ultra-clock idea for a while, and I originally wanted to use flip dots for the display, but they turned out to be expensive and hard to find, so I switched to using LED matrices instead.

The full display is constructed of 9 display modules, each of which itself contains 25 8x8 LED matrices. Each module also contains positions for the shift registers and MOSFETs that make up the control circuitry.

The display is not without its quirks. Most of these stem from either the geometric realities of trying to fit everything onto the board or a software-compensatabel routing mistake that would take hours of work to fix in hardware. The biggest of these is that the current-limiting resistors aren't actually on the board but instead fly above the back of it. Also, the bottom and top row of matrices on each module are rotated 90 degrees, and every other module has pairs of rows and columns swapped (e.g. col1 connects to col2, col2->col1, col3->col4, etc.) This is something I can fix in software.

The display will probably be driven by a Pi Pico W or an ESP32, but especially if high framerates are not required it could be also driven by something less powerful. The driver connects to each row and column via the row control and column control pads.

One of the things I hope to learn from this board is where the limits actually lie when I try to drive things at high frequencies. I don't know how scared to be of things like ringing or EMI, and I'll probably find out.

The theoretical max framerate for this board is something like 4096fps, which would probably be implemented as 16fps with 255-tick BCM dimming, though this would require driving the clock line at something like 4MHz, and I have no idea if that'll be possible. If it's not, I can derate to something like 8fps with 7-tick dimming, which would be ~64fps or a much more manageable 60kHz clock frequency.

Here's a render of the back of the a single display module (the front is just a grid of matrices, which I don't have a 3D model for but I'm sure you can imagine). For more pictures, including the schematic and each internal layer, check out the [journal](https://github.com/rivques/the-matrix/blob/main/JOURNAL.md#may-29th).
![image](https://github.com/user-attachments/assets/c6b49828-dd3e-41d1-93e7-472a4d3e2d81)