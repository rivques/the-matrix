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
IRLZ44N MOSFET|120|$0.20|$25.00|3|360|https://www.aliexpress.us/item/3256807774117402.html
220Ω Resistor|120|$0.02|$2.80|2|240|https://www.aliexpress.us/item/2251832766343175.html
5V 3A Power Supply|1|$4.00|$4.00|2|2|https://www.aliexpress.us/item/3256805577151044.html
Matrix PCB|10|$2.20|$22.00|0|0|JLCPCB
Control PCB|5|$2.80|$14.00|0|0|JLCPCB
Total|||$160||4700|

Okay, $160 isn't terrible. What I'm more concerned about is 4700 joints, that'll take a while. Rounding up to 5000 for the connectors and stuff, if I can do 40 joints per minute (optimistic), that'll take:
```numbat
unit joints
5000 joints / (40 joints/minute)
    = 125 minutes
```
...that's not as bad as I thought. It'll probably end up being twice that, but I was afraid it'd be something like 40 hours. This project seems feasible!