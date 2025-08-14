# the-matrix

This is a large (theoretically 1ftx1ft) LED matrix display with a resolution of up to 120x120 monochrome pixels. My intended use for it is to act as an "ultra-clock," showing not just the time but also other useful information like weather, sports scores, maybe news, etc. However, it should be said that this is designed to be a generic module, and not destined for any specific project - this should be something I can pull off my shelf, send the correct control signals to, and get a display from.

I've had the ultra-clock idea for a while, and I originally wanted to use flip dots for the display, but they turned out to be expensive and hard to find, so I switched to using LED matrices instead.

The full display is constructed of 9 display modules, each of which itself contains 25 8x8 LED matrices. Each module also contains positions for the shift registers and MOSFETs that make up the control circuitry.

However, I have not yet built the full display - scaling up from 1 to 9 modules turned out to be _much_ harder than expected. I have 4 modules fully built, plus harnesses and a control board - I just haven't been able to make them play nice, despite spending more than 20 hours on scaling and troubleshooting. I still hope to realize the full vision at some point, but I'm pretty burnt out on this for the short term.

The display is not without its quirks. Most of these stem from either the geometric realities of trying to fit everything onto the board or a software-compensatable routing mistake that would take hours of work to fix in hardware. The biggest of these is that the current-limiting resistors aren't actually on the board but instead fly above the back of it. Also, the bottom and top row of matrices on each module are rotated 90 degrees, and every other module has pairs of rows and columns swapped (e.g. col1 connects to col2, col2->col1, col3->col4, etc.) This is something I can fix in software.

The display will probably be driven by a Pi Pico W or an ESP32, but especially if high framerates are not required it could be also driven by something less powerful. The driver connects to each row and column via the row control and column control pads.

One of the things I hope to learn from this board is where the limits actually lie when I try to drive things at high frequencies. I don't know how scared to be of things like ringing or EMI, and I'll probably find out.

The theoretical max framerate for this board is something like 4096fps, which would probably be implemented as 16fps with 255-tick BCM dimming, though this would require driving the clock line at something like 4MHz, and I have no idea if that'll be possible. If it's not, I can derate to something like 8fps with 7-tick dimming, which would be ~64fps or a much more manageable 60kHz clock frequency.

Here's a render of the back of the a single display module (the front is just a grid of matrices, which I don't have a 3D model for but I'm sure you can imagine). For more pictures, including the schematic and each internal layer, check out the [journal](https://github.com/rivques/the-matrix/blob/main/JOURNAL.md#may-29th).
![image](https://github.com/user-attachments/assets/c6b49828-dd3e-41d1-93e7-472a4d3e2d81)

BOM (for some parts I'm getting spares since they'd be a pain to source if some turn out to be dead on arrival. if this can't be included in the grant i'll happily cover the spares myself):

Part|Quantity|Price/unit|Total price|# pins/unit|# pins total|Note|Link
---|---|---|---|---|---|---|---
788AS 8x8 LED Matrix|230|$0.35|$82.00|16|3600|not going to count on 0% DoA rate here|https://www.aliexpress.us/item/2251832771187101.html
74HC595 Shift Register|15|$0.22|$4.00|16|240|2x20 is cheaper than 3x5|https://www.aliexpress.us/item/3256807421796895.html
TPIC6B595 Shift Register|20|$0.50|$10|16|240|again, not counting on no DoA|https://www.aliexpress.us/item/3256806981485001.html
IRFU9024NPBF MOSFET|125|$0.40|$40.00|3|360||https://www.aliexpress.us/item/3256808251284284.html
220Ω Resistor|120|$0.02|$2.80|2|240|2x100 is cheaper than 12x10|https://www.aliexpress.us/item/2251832766343175.html
2x20 right-angle header female|12|$2.00|$4.00|40|80||https://www.aliexpress.us/item/3256805899201197.html
2x20 right-angle header male|12|$2.50|$5.00|40|80||https://www.aliexpress.us/item/3256804718416281.html
5V 3A Power Supply|1|$4.00|$4.00|2|2||https://www.aliexpress.us/item/3256805577151044.html
Matrix PCB|10|$2.5|$25.00|0|0|i'll buy this separately from the grant so i can combine it with another order|JLCPCB
Total|||$173||4850|total w/o PCB: $148 :tada:

Schematic:
![image](https://github.com/user-attachments/assets/da3e68c8-1c97-4b34-9f4b-f0a703996c76)