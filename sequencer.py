#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  sequencer.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
import uasyncio as asyncio
import time
from   machine import Pin, idle
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
import state
#----------------------------------------------------------#

# --- 12-Channel Body & Ring Transistor Taps (Shifted for GPIO 1 Audio) ---
BODY_PINS = [2, 3, 8, 9, 10, 11, 12]  # Shifted to start at 2 to clear Audio on Pin 1
RING_PINS = [13, 14, 15, 16, 17]      # Perfectly continuous safe block

body_taps = []
ring_taps = []

#----------------------------------------------------------#
def init_sequencer():
#----------------------------------------------------------#
    global body_taps, ring_taps
    try:
        body_taps = [Pin(p, Pin.OUT, value=0) for p in BODY_PINS]
        ring_taps = [Pin(p, Pin.OUT, value=0) for p in RING_PINS]
        print(f"Initialized {len(body_taps)} Body and {len(ring_taps)} Ring transistor taps.")
    except ValueError as e:
        print(f"Low-level Hardware Initialization Failure: {e}")
#----------------------------------------------------------#

#----------------------------------------------------------#
def cycle_sequencer():
#----------------------------------------------------------#
    all_taps = body_taps + ring_taps
    for current_tap in all_taps:
        current_tap.value(1)
        time.sleep_ms(400)
        current_tap.value(0)
#----------------------------------------------------------#
        
#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#
