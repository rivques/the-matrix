---
title: "The Matrix"
author: "rivques"
description: "A large LED matrix to display things like the time, weather, sports scores, etc."
created_at: "2025-05-27"
---
## total time thru end of May: 17 hours
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

![image](https://github.com/user-attachments/assets/cb18ec98-480b-40fe-80e5-c5641aa0dc52)

**total time spent: 2 hours**

# May 28th, part 2:
Start time: 2:45pm
I'm going to start routing the connectors. Hopefully I can stay on the interal layers, but I'm okay to use the outer ones sparingly.

[one hour later]

okay, one connector and some of the mosfets are routed. i've needed the outer layers 3 times so far - not as bad as I was expecting!

[another hour later]

ok, another connector and the rest of the mosfets' column connections are routed. next up: the row connectors.

...this is _really_ annoying routing.

...ok i've routed the left row connector. i'll do the right one later.

**total time spent: 2.5 hour**
# May 28th, part 3:
Start time: 8:30pm
ok time to do the last connector and then hopefully the last part won't be that bad.

[30 minutes later]

i've just realized that i set up the connectors wrong in the schematic, so row 1 would connect to row 2 and vice versa, row3<->row4, etc, same with columns. either i can give up the past 3 hours of work, or i can spend a similar amount of time fixing that in software. let me think for a second about that:
ok so the way this would manifest is just in the display, it wont cause any electrical issues fortunately. it'd just be that the middle row/column of matrices would have their column pairs swapped with each other. i wonder how i can efficiently represent that in software.

well i'm going to have to have a preprocessing step for every frame i want to display. and i'll leave it up to later me to figure out what the best way to swap the columns and rotate the displays is there, i'd rather spend 3 hours programming than 3 hours rerouting stuff i've already done once, and it'll hopefully take less than 3 hours to fix. it's unfortunate, but oh well.

anyways back to routing the last of the right connector, yipee!

[another 30 minutes later]

ok, all connectors complete! now the only thing left is just hooking up the shift registers, and i have almost all of the outer layers to make it happen. here's how it's looking now:

![image](https://github.com/user-attachments/assets/5eb50ffb-1bde-4139-b251-8824eeef83bf)

ok now i'm going to hook the mosfets up to the shift registers

[30 minutes later]
ok the mosfets are connected to the low-shift registers. now i need to connect the rows to the low-side shift registers, connect the shift register data lines to each other, and give power to everything.

[15 mins later]

all shift registers are connected to their matrices/mosfets. next: data lines.

[15 mins later]
ok the low-side data lines were pretty quick, because there's patterns between the chips. i've done the data lines on 1 high-side driver and they were super annoying - they're long and there's no patterns from chip to chip. i'm going to call it a night.

**total time spent: 2 hours**
**total time on May 28th: 6.5 hours**
# May 29th:
Start time: 9am
Time to finish up the data lines.

[45 minutes later]

That wasn't so bad. Now my only remaining unrouted nets are power and ground!

[30 minutes later]

ok, power and ground are routed, and I learned that fills don't need pre-existing traces in order to automatically connect to nets, so that saved me a lot of work. Time to run DRC and see how bad everything is.

...413+ errors. oh boy.

okay, so ~200 of those were because i'd input the JLC via size constraints (confused via diameter with annular width), so those went away. Most of the rest were because of me putting pads under the displays, which was by design. Then there were a few which were about short traces being unconnected, which I'm ignoring, and a bunch of silkscreen overlap, which I will now go fix.

WAIT I RAN THE SCHEMATIC PARITY CHECK AND SOMEWHERE ALONG THE WAY I FULLY DELETED A DISPLAY
ok time to trawl thru the git history and find when that happened

ok it was in the last commit so hopefully i can just put it back and things will be fine

yeah it turned out fine. i must have deleted it right before running drc. phew.

anyways time to go mess with silkscreens

[30 minutes later]

ok, I _think_ the board is complete! Here are some screenshots:
![image](https://github.com/user-attachments/assets/95647ebd-f127-4075-afd9-235a73a2d123)|![image](https://github.com/user-attachments/assets/defa0192-8b39-40a0-ad77-e2c8924c1cd8)|![image](https://github.com/user-attachments/assets/62e2b62d-9c90-4d13-956a-6170f5c1c6ed)
---|---|---
![image](https://github.com/user-attachments/assets/95b9d90a-ca58-4ee1-8662-008ed6dabccc)|![image](https://github.com/user-attachments/assets/8bcc3958-d47c-474d-92ad-c9f2e3ac8011)|![image](https://github.com/user-attachments/assets/6e4d1ab8-3fde-4e50-ab3e-6f93865b8149)
![image](https://github.com/user-attachments/assets/d31926eb-5e25-452a-9894-92f77d3c2094)|![image](https://github.com/user-attachments/assets/0f540712-941e-431a-b720-3c40be31190e)|![image](https://github.com/user-attachments/assets/c6b49828-dd3e-41d1-93e7-472a4d3e2d81)


going to export the gerbers and get a real price!

ok so it's $9 for the boards (with a coupon), plus $16 shipping. i can't believe how cheap JLC is.

and just going to do a revised bill of materials here:
(for some parts I'm getting spares since they'd be a pain to source if some turn out to be dead on arrival. if this can't be included in the grant i'll happily cover the spares myself)

Part|Quantity|Price/unit|Total price|# pins/unit|# pins total|Note|Link
---|---|---|---|---|---|---|---
788AS 8x8 LED Matrix|230|$0.35|$82.00|16|3600|not going to count on 0% DoA rate here|https://www.aliexpress.us/item/2251832771187101.html
74HC595 Shift Register|15|$0.22|$4.00|16|240|2x20 is cheaper than 3x5|https://www.aliexpress.us/item/3256807421796895.html
TPIC6B595 Shift Register|20|$0.50|$10|16|240|again, not counting on no DoA|https://www.aliexpress.us/item/3256806981485001.html
IRFU9024NPBF MOSFET|130|$0.40|$50.00|3|360||https://www.aliexpress.us/item/3256806868594722.html
220Ω Resistor|120|

wait

waiittttttt

i forgot the current-limiting resistors.

time to go back to routing hell (:

ok wait can i get away without them  
so the mosfets will source up to like 1.5A/col  
and the tpic6b595s will sink 150mA/row  
and the max current per led is 20mA  
yeahhhhh  

ok next idea: can i avoid putting the resistors on the board using the third dimension  
like can i directly solder one leg to the drain pin of the tpic, and then solder the other leg to the pad where that drain pin is meant to go  
the datasheet says the legs extend 1/8th inch below the body,
so... maybe?
uhh let me try this with a different DIP part


ok after experimenting a bit i dont think that's feasible. but maybe i could solder a resistor to the chip, then solder the other leg to somewhere else where the net is connected (i.e. onto one of the matrix legs).  
looking at the pcb, the farthest distance that would be is 50mm, and my resistor is 60mm long. so that should work! it'll be really, really ugly, but it should work.

ok crisis mostly averted. i'm going to go add silkscreen to where i experct resistors to be and then i'll finish the bom.

ok silkscreen added and board reexported. that was annoying, and it'll be more annoying in the future, but i don't think i could reasonably add the resistors to the board without spending at least another 5 hours routing.

anyways, BOM:

Part|Quantity|Price/unit|Total price|# pins/unit|# pins total|Note|Link
---|---|---|---|---|---|---|---
788AS 8x8 LED Matrix|230|$0.35|$82.00|16|3600|not going to count on 0% DoA rate here|https://www.aliexpress.us/item/2251832771187101.html
74HC595 Shift Register|15|$0.22|$4.00|16|240|2x20 is cheaper than 3x5|https://www.aliexpress.us/item/3256807421796895.html
TPIC6B595 Shift Register|20|$0.50|$10|16|240|again, not counting on no DoA|https://www.aliexpress.us/item/3256806981485001.html
IRFU9024NPBF MOSFET|125|$0.40|$40.00|3|360||https://www.aliexpress.us/item/3256808251284284.html
220Ω Resistor|120|$0.02|$2.80|2|240|2x100 is cheaper than 12x10|https://www.aliexpress.us/item/2251832766343175.html
2x20 right-angle header female|2|$2.00|$4.00|40|80||https://www.aliexpress.us/item/3256805899201197.html
2x20 right-angle header male|2|$2.50|$5.00|40|80||https://www.aliexpress.us/item/3256804718416281.html
5V 3A Power Supply|1|$4.00|$4.00|2|2||https://www.aliexpress.us/item/3256805577151044.html
Matrix PCB|10|$2.5|$25.00|0|0|i'll buy this separately from the grant so i can combine it with another order|JLCPCB
Total|||$173||4850|total w/o PCB: $148 :tada:

i think this is almost ready to ship!  
**total time spent: 3.5 hours**

# June 26th:
Start time: 4pm

OK some of the parts have started to arrive. I'm realizing I'm going to need to make a tool to hold the displays in the right place while I solder them, so I'm going to grab the 3D model and throw it in Onshape and see what I can do.

ok, i've got the model in Onshape (and I added a model of the matrix module itself), and I've started to sketch out a magazine page. The holder will have to wait for tomorrow.

**total time spent: 1 hour**
# June 27th:
Start time: 11:15am

just nearly finished the magazine page. it took a while but i'm not used to figma. one weird thing i ended up doing was to get a render of the board with a transparent background, I rendered it in KiCad, then remove the background with remove.bg, but that only gave a low-quality version, so I pulled it into GIMP, and used the transparency as a mask on the high-quality render.

**total time spent: 1 hour**

# June 30th:
Start time: 4pm

All my parts arrived!

I 3D printed some little feet that I can use while soldering to hold the board at the correct height. 

I'm going to start by soldering the bare minimum support components for a single display (DS1) and go from there. That includes, in order:

- U1
- U6
- Q1-Q8
- DS1
- R1-R8

Hmm, by not doing the whole board at once I'll make it much more annoying to solder the rest of the backside components. I think it's worth it to be able to test the first display, though. 

As a side note, the order for an entire module will be:
- U1-U5
- U6-U10 (with outputs cut)
- J1-J6 as needed
- Q1-Q40
- DS1-DS25
- R1-R40

[45 mins later]
aaa i forgot to cut the outputs on U6, so i've had to cut the physical traces, which is luckily possible but is still a pain.

[45 mins later]
i'm almost there! i've just got 3 jumper resistors left, which are, predictably, the most annoying part. i don't look forward to doing 115 more of them.

**total time spent: 1.5 hours**

# June 30th, part 2:
Start time: 9:45pm

time to solder the last 3 resistors, then i'll write some test code

[30 mins later]  
resistors soldered! behold (but not too closely):  
![image](https://github.com/user-attachments/assets/02790142-4bb1-41dc-9155-b947c5dda2f9)

ok tomorrow we wire it up and start testing!  
**total time spent: 30 mins**  
**total time on June 30th: 2 hours**  

# July 1st:
Start time: 12:30pm

time to start on code. i'll start with full software driving, not PIO, while i test things at low FPS.

[an hour later]

i've wired everything up and written some test code and... it's not working. it seems like i'm doing something wrong with at least the low-side shift register, because when i short one of its outputs to ground i do get leds turning on. the voltages on its output pins are either 5 volts (which is reasonable for open-drain state) or 3 volts (which is not reasonable, especially if that's it trying to sink current). it's not unlikely that i broke the chip while soldering, but i'm hoping it's not that. i'm going to write a super simple test program and try to isolate the problem.

[45 mins later]  
so there's also something wrong with the high-side. i'm focusing on that one first - it seems to be totally unresponsive to my commands.  
i found it - i just miswired the column control header. hopefully that fixes many of the problems.
and also it looks like i've partially miswired the row control header as well.

[15 mins later]  
ok, rewiring complete, and it looks like that helped a lot, but not all the way. going to keep messing with the test program.

[15 mins later]  
ok i think i've isolated the issue to the low side. (column 3 has a bad solder joint too, but that's not the main issue). for some reason, the shift register just isn't listening to me. i'm going to take a break, but I think the next step is to triple-check the pinout and then the datasheet if that doesn't work.

**total time spent: 2.25 hours**

# July 1st, part 2:
Start time: 6pm

no apparent wiring issue. time to check the datasheet.  
i see a problem! in the schematic, I mixed up RCK and SRCK (labeling them as ROWCLK and ROWLATCH instead of the other way around). Let me try swapping them back in my wiring...  
progress! now one row of LEDs lights up!  
AND IT ALMOST FULLY LIGHTS WHEN I RUN THE RIGHT TEST CODE!

the one remaining issue is that COL3 isn't illuminating. I'm going to reflow the solder joints really quick and see if that helps.  
it didn't fix it. Time to play more of everyone's favorite game "where's the voltage?"  
...actually, i just reflowed the wrong joint. Reflowing the correct joint fixed it!

ok, time to test some other stuff. First up: PWMing the ROWEN pin for global brightness control.  
...yep, works perfectly.

briefly, here's the current list of the various ways in which this is janky:
- need to use 3D resistor technology to connect the low side shift registers
- need to use display height jigs + solder from top to fit around the expansion ports
- row latch and clock pins are the wrong way around on the schematic

next: try to drive it in PIO, and hopefully fix some of the flickering i'm seeing which I assume is from micropython's garbage collection or similar.

... no luck on the first attempt at PIO, but there's so many things that could be wrong. I'm going to pare it down to a minimal example and build it back up.

... ok i worked out a bunch of bugs. now the only thing left is something weird with the ring size parameter on the DMA. maybe i need to align the buffer to memory or smth? anyways its a problem for later. one thing that helped a lot was putting LEDs on most of the outputs so I could see what I was trying to do. then it was just a matter of tweaking the various parameters of the PIO stuff (set_init ordering, transfer size, byte swapping, etc.) until it worked.

**total time spent: 2.5 hours**

# July 1st, part 3:
Start time: 10:30pm

Against my better judgment I'm going to keep working on this tonight. I have some ideas for how to fix the ring size issue.

[30 mins later]  
IT WORKS! like, fully works! the trick was to just have an interrupt run whenver the DMA write was done that immediately restarted it. I ran into some weirdness where the board refused to enumerate on USB once I uploaded the file, but a flash_nuke.uf2 fixed that. Now to see how far I can push the PIO frequency...  
looks like 2MHz has some slight ghosting - like the rows stay on for a little while the next column is written, but 1MHz is fine. Working backwards, that equates to:
```numbat
let pio_clk = 1MHz
let col_rate = pio_clk/52
let full_bw_rate = col_rate/120
    = 160 fps
```
That's... a little lower than I hoped. It means I might not be able to get any greyscale values without getting flickering. But there's definetly room for optimization, I bet if I adjust the timings in the PIO program I can figure out which delay is critical to eliminating ghosting and which I can speed up. Now, though, I think the next step is to solder up another matrix module and try to get two working together. This is looking really promising!

**total time spent: 30 mins**
**total time on July 1st: 5.25 hours**

# July 2nd
Start time: 3:30 pm

OK with yesterday's success I'm going to solder the rest of the high-side components to expand to a 8x40 display.

[1 hour later]

that was 32 transistors, 4 shift registers, and 4 displays in ~1 hour, or a little under 4 joints per minute. That's a bit slow, but hopefully working in bigger batches will help.

Now, i'm going to adjust the code to account for the 32 new columns, which should be pretty trivial

[1.25 hours later]
...it was not pretty trivial. there were a few solder joints i needed to reflow, but then micropython started being weird - like claiming the pio was running, then not actually running it except for the 0.1secs when i pressed ctrl+c, and disconnecting from the repl fixed the issue.

[15 mins later]

i spent some time trying to make a function to draw a framebuf on the screen, but i had a bad approach. i'll try again later.

**total time spent: 2.5 hours**

# July 9th:
Start time: 1pm

The goal for today is to get one full module working. So I need to solder:
- U7-U10 (with outputs cut)
- J5 and J6
- DS10-DS25
- R9-R40

[4 hours later]

soldering complete! again, the resistors were incredibly annoying. I do think it won't be _that_ bad to solder the non-row-control modules.

Going to update the code to use a 40x40 display, and see how it works.

[1 hour later]

updated the code, and it mostly works! there's a few display joints that need reflowing, some of which will be a massive pain to reach, but by and large it works! next: figuring out what transform each display needs to be in the right place. 

[another hour later]

got all the pins reflowed! there's some glitchiness with some pixels flickering, not sure why that is yet. my next step is probably to try and optimize the framebuf->pio data step - right now it takes 1700ms(!) and if i can get that to like <50ms then I can do some animations.

here's what it looks like now:  
![image](https://github.com/user-attachments/assets/aad71cca-ffee-4487-9617-ec89d40b00de)


**total time spent: 6 hours**
