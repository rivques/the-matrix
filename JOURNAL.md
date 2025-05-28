---
title: "The Matrix"
author: "rivques"
description: "A large LED matrix to display things like the time, weather, sports scores, etc."
created_at: "2025-05-27"
---
# May 27th:
Ok so this is something I've wanted to make for a while: a kind of "super-clock" that shows not just the time but also other relevant information. Initially I wanted to use flip-dot displays, but those are expensive and hard to find, so I'm pivoting to an LED matrix. I want to put a bunch of [these cheap 8x8 displays](https://www.aliexpress.us/item/2251832771187101.html) together, right now I'm thinking 30x30cm, which is 15x15=225 displays or 120x120=1440 pixels. The raw cost of those displays would be ~$80. I'm trying to figure out driver ICs. Ideally I'd like to solder everything myself, with no tiny SMD parts. One option is a bunch (30-450) of 74HC595s, depending on how many displays I want to be able to control at once. Let's take a second to do the math of how many LEDs/second I need to update to get, say, 10fps:
```numbat
let target = 10 fps
unit leds
let num_leds = 15*15*64leds
let leds_per_second = num_leds/frame*target
    = 144_000 leds/s
```
Okay. So say I go with the minimum of 30 74HC595s, and I update one column of the screen at a time. At 3V3 the max clock frequency is something like 25MHz, so let's see if 1MHz is enough:
```numbat
let clock_freq = 1 MHz
let columns_per_second = clock_freq/120
    = 8333 columns/s
let frames_per_second = columns_per_second/120
    ~70 fps
```
That's actually very good! And if I can actually hit 10MHz then I could get 700fps which might even be enough to do some PWM (BCM?) dimming, and that's assuming I have all the shift registers daisy-chained together and am not driving them in paralell. And another reason why that's great is that it makes my current needs low, if I'm only lighting a max of 120 leds at a time. So that would put my current needs at:
```numbat
let leds_per_column = 120 leds
let current_per_led = 12mA/led
let current_per_column = leds_per_column*current_per_led
    = 1.44 A
```
And since I'm only using one column at a time, that power is very manageable! I'll probably need to put a transistor on each column and row, because the 74HC595s can only source 6mA per pin, and I'd like to hit more like 12 or 14. So I'll need 240 transistors and 120 resistors, which won't be fun to solder, but shouldn't be too bad.

...

okay, i've done some more research, and it looks like it might make sense to switch to something like the TPIC6B595 for the low side, since it can sink enough current without needing a transistor. 

And then to fit it within the JLC PCB size I'll make a bunch of smaller boards that hook together with like right-angle duponts.

OK so here's what the major components are looking like right now:
Part|Quantity|Price/unit|Total price|# pins/unit|# pins total|Link
---|---|---|---|---|---|---
788AS 8x8 LED Matrix|225|$0.35|$80.00|16|3600|https://www.aliexpress.us/item/2251832771187101.html
74HC595 Shift Register|15|$0.22|$4.00|16|240|https://www.aliexpress.us/item/3256807421796895.html
TPIC6B595 Shift Register|15|$0.50|$7.50|16|240|https://www.aliexpress.us/item/3256806981485001.html
IRF9520 MOSFET|120|$0.40|$48.00|3|360|https://www.aliexpress.us/item/3256806868594722.html
220Ω Resistor|120|$0.02|$2.80|2|240|https://www.aliexpress.us/item/2251832766343175.html
5V 3A Power Supply|1|$4.00|$4.00|2|2|https://www.aliexpress.us/item/3256805577151044.html
Matrix PCB|10|$2.20|$22.00|0|0|JLCPCB
Total|||$164||4700|

Okay, $164 isn't terrible. What I'm more concerned about is 4700 joints, that'll take a while. Rounding up to 5000 for the connectors and stuff, if I can do 40 joints per minute (optimistic), that'll take:
```numbat
unit joints
5000 joints / (40 joints/minute)
    = 125 minutes
```
...that's not as bad as I thought. It'll probably end up being twice that, but I was afraid it'd be something like 40 hours. This project seems feasible!

**total time spent (estimate): 2.5 hours**: 

# May 27th, part 2:
OK i'm going to sit down and try to work out a schematic. I also realized that I needed to switch to a P-channel MOSFET for the high side, which I changed in the BOM.

[much later]

ok so there's a schematic now. i decided im not going to have a separate PCB for the control board, i'll just do that on perfboard. (again, bom has been updated). so now the plan is to make 9 (well, 10, because of JLC order sizing) boards to _almost_ the schematic. each board will be populated with its 25 displays and the 4 40 pin connectors, and then one board in each row/column will have that row/colum's driving circuitry. Then the board with driving circuitry will be connected to the control board, which will have a pi pico w on it. next up: routing this monstrosity. i'll have to make sure i don't make impossible sandwhiches, but other than that it shouldn't be difficult, just tedious.

## screenshots
![image](https://github.com/user-attachments/assets/da3e68c8-1c97-4b34-9f4b-f0a703996c76)
## close-up on one matrix and drivers
![image](https://github.com/user-attachments/assets/6af99db9-f6dd-43ef-a9e7-f797d15006f3)

**total time spent (estimate): 3 hours**

# May 27th, part 3:
start time: 11pm

ok i'm going to start on the pcb layout. I'm not ghoing to try to do routing tonight, but i do want to at least get the rough positions of things figured out.

ok, i'm about 30 mins in, and its becoming clear that i have to rotate the top and bottom rows of displays 90 degrees so i can fit the row connectors in. this will cause some headaches when doing the firmware, but i don't think i have a choice. this is what it's looking like now:

![image](https://github.com/user-attachments/assets/264028eb-a2ef-4b61-ad5d-3660abba76a9)

ok now for the (hopefully easier!) task of shoving all the ics and mosfets under the displays.

...and i'm realizing that there's no way to do this without 4 layers. fortunately it's not that much mroe expensive.

30 more minutes later, these mosfets are just way too big. i'm going to switch to the [IRFU9024NPBF](https://www.aliexpress.us/item/2251832086805199.htm), which is actually cheaper than my original option, and it's in the smaller TO-251 package.

...it's been another 30 minutes, and i've gotten everything placed, thanks to the smaller mosfets. here's what it's looking like:

![image](https://github.com/user-attachments/assets/ac2b804d-06ce-40c6-a030-e04c9fffb564)

and that may not look terrible, but keep in mind that almost every empty pad is going to have an led matrix in it from the other side, and that's not even considering the traces between the near-1000 pads on this board. if this is possible, it's possible by the slimmest of margins.

**total time spent: 1.5 hours**
**total time on May 27th: 7 hours**
# May 28th:
Start time: 9am
Okay I'm starting to route the rows to each other. I'm changing the footprint of the mOSTFETS slightly to allow a trace to fit between their pads.
[one hour later]
so i've gotten the middle rows and the rght column and a half routed. it's difficult but not impossible. the top and bottom rows are going to be a massive pain since they're rotated.
[another hour later]
Ok, i have all of the matrices routed, using just the internal layers. I haven't routed the connectors or drivers yet, but hopefully the outer layers are enough room for that. here's what it looks like now:



** total time spent: 2 hours**