#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  main.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

import gc
from   machine   import Pin
import time
import uasyncio  as asyncio

# Import your custom modules
import carousel
import font
import max7219
from   max7219   import MAX7219_INTENSITY_MIN, MAX7219_INTENSITY_MAX
import ir_remote  # Clean refactored asset file
from   ir_remote import IR_PIN_NUM
import sequencer
import state
from   tasks     import task_text_carousel
from   tasks     import task_audio
from   tasks     import task_iargb_leds
from   tasks     import task_sequencer
from   tasks     import task_web_ui

# --- Global System Version Configuration Flags ---
VERSION_MAJOR = 0x01  
VERSION_MINOR = 0x00  
VERSION_STRING = f" MESSAGING V{int(VERSION_MAJOR)}.{int(VERSION_MINOR):02d} "

# ----------------------------------------------------------
# 🚦 CORE EXECUTION MANAGER ENTRY POINT
# ----------------------------------------------------------
async def main():
    print(f"{VERSION_STRING.strip()} Multitasking Asynchronous Engine Initializing...")
    
    # Initialize hardware peripheral groups
    sequencer.init_sequencer()
    carousel.init_carousel()
    max7219.init_stick()
    # Apply your mid-scale brightness level right away
    max7219.set_brightness(state.state.matrix_brightness) # <-- Updated Line
    
#    # Apply your mid-scale brightness level right away
#    max7219.intensity(state.matrix_brightness)
    
    # 1. RUN ACTIVE BOOT SPLASH SCREEN + TAP SEQUENCER SELF TEST
    print("Rendering standalone boot splash + sequential tap verification...")
    max7219.print_string(0, VERSION_STRING)     
    sequencer.cycle_sequencer()    
    print("Hardware tap verification complete. All channels dark.")
    
    # 2. Bind the newly isolated remote module subsystem
    ir_remote.init_ir(IR_PIN_NUM, state)
    
    print("Scheduling cooperative concurrent tasks...")
    await asyncio.gather(
        task_sequencer(),
        task_audio(),
        task_iargb_leds(),
        task_text_carousel(),
        task_web_ui()
    )

if __name__ == "__main__":
    gc.collect()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped via REPL break signal.")
    except Exception as e:
        print(f"\nUnhandled Runtime Crash Error: {e}")
