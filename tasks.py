#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  tasks.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
import uasyncio as asyncio
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
import state
import sequencer
from   sequencer import body_taps, ring_taps
import carousel
import max7219
import audio
import iargb

#----------------------------------------------------------#

#----------------------------------------------------------#
# --- CENTRALIZED OPERATIONAL SYSTEM STATE ENGINE ---
#----------------------------------------------------------#
# ASYNC SUBSYSTEM TASK STUBS
#----------------------------------------------------------#

#----------------------------------------------------------#
async def task_audio():
#----------------------------------------------------------#
    # Manages background music note timing structures
    # without blocking
    #------------------------------------------------------#
    while True:
        await asyncio.sleep_ms(10)  
#----------------------------------------------------------#

#----------------------------------------------------------#
async def task_iargb_leds():
#----------------------------------------------------------#
    """Spits data streams down to the Addressable smart color pixels."""
    while True:
        await asyncio.sleep_ms(30)  
#----------------------------------------------------------#

#----------------------------------------------------------#
async def task_sequencer():
#----------------------------------------------------------#
    """Drives the 7 Body Taps and 5 Ring Taps chasing patterns."""
    print("Transistor chase sequencer active.")
    step = 0
    
    try:
        while True:
            if state.state.POWER_ON:
                # If this task is inside tasks.py, it needs 'sequencer.body_taps'
                # Let's see if it throws a NameError here:
                for i, tap in enumerate(sequencer.body_taps):
                    tap.value(1 if i == (step % len(sequencer.body_taps)) else 0)
                for i, tap in enumerate(sequencer.ring_taps):
                    tap.value(1 if i == ((step // 2) % len(sequencer.ring_taps)) else 0)
                step += 1
                await asyncio.sleep_ms(100)
            else:
                # Cleanly turn off all high-current paths immediately when powered off
                for tap in sequencer.body_taps:
                    tap.value(0)
                for tap in sequencer.ring_taps:
                    tap.value(0)
                await asyncio.sleep_ms(200)  
    except Exception as e:
        # This will catch and print any silent NameError or AttributeError in Thonny!
        print(f"\n[SEQUENCER CRASH] Task halted because: {e}\n")
#----------------------------------------------------------#
        
#----------------------------------------------------------#
async def task_text_carousel():
#----------------------------------------------------------#
    # Cycles through your 14 saved messages using their
    # individual dwell times
    #------------------------------------------------------#
    current_slot = 0
    print("Carousel Text Rotation Engine initialized (Slots 0-13 available).")

    while True:
        if state.state.POWER_ON:
            if state.state.reset_carousel:
                current_slot = 0
                state.state.reset_carousel = False
                
            cfg = carousel.get_slot(current_slot)
            
            if cfg and cfg["enabled"]:
                print(f"Slot {current_slot} Active -> Dwell: {cfg['dwell']}s | Msg: '{cfg['text']}'")
                max7219.set_cursor(0)
                max7219.print_string(cfg["text"])
                
                seconds_counted = 0
                while seconds_counted < cfg["dwell"] and state.state.POWER_ON:
                    if state.state.reset_carousel:
                        break
                    await asyncio.sleep(1) 
                    seconds_counted += 1
                    
                if state.state.reset_carousel:
                    continue
            
            current_slot = (current_slot + 1) % 14
        else:
            # FIX: Actively clear the physical display hardware buffer when power is disabled
            max7219.set_cursor(0)
            max7219.print_string(" " * 17) # Print 17 spaces to instantly force-blank all 17 modules
            
            # Alternatively, if your max7219 module has a clear/flush command, use it here:
            # max7219.clear() 
            
            await asyncio.sleep_ms(200)
#----------------------------------------------------------#

#----------------------------------------------------------#
async def task_web_ui():
#----------------------------------------------------------#
    # Handles parsing browser connection requests on the
    # local server port.
    #------------------------------------------------------#
    while True:
        await asyncio.sleep_ms(100)
#----------------------------------------------------------#

#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#
