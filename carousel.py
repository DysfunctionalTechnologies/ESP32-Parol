#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  carousel.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
import os
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
from   font  import SPECIAL_SNOWFLAKE, SPECIAL_BELL
import state
import max7219
#----------------------------------------------------------#

#----------------------------------------------------------#
# --- Layout Metrics ---
#----------------------------------------------------------#
NUM_SLOTS   = 14
SLOT_SIZE   = 18  # 1 Control Byte + 17 Text Bytes
FILE_NAME   = "carousel.dat"
TEMP_FILE   = "carousel.tmp"
#----------------------------------------------------------#

#----------------------------------------------------------#
# --- In-Memory Active Carousel Buffer (Initialized blank) ---
#----------------------------------------------------------#
_carousel_ram = bytearray([0x00] * (NUM_SLOTS * SLOT_SIZE))
#----------------------------------------------------------#

#----------------------------------------------------------#
def init_carousel():
#----------------------------------------------------------#
    # Loads the messaging array from flash storage or
    # builds a fresh factory bank.
    #------------------------------------------------------#
    global _carousel_ram
    print("Loading message carousel from storage...")
    
    try:
        # Check if the non-volatile data file exists on the chip
        if FILE_NAME in os.listdir():
            with open(FILE_NAME, "rb") as f:
                f.readinto(_carousel_ram)
            print("Carousel data successfully restored from flash.")
        else:
            print("No existing carousel file found. Formatting default bank...")
            _load_factory_defaults()
    except Exception as e:
        print("Storage reading error encountered:", e)
        _load_factory_defaults()

#----------------------------------------------------------#
def _load_factory_defaults():
#----------------------------------------------------------#
    # Populates crisp default strings if storage is blank
    # or corrupted.
    #------------------------------------------------------#
    clear_all_slots()
    # Slot 0: Enabled (Bit 7=1), Static Dwell 3s, Msg: " MERRY CHRISTMAS "
    set_slot(0, True, 0, 3, chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+
                            chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+
                            chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE)+
                            chr(SPECIAL_SNOWFLAKE)+chr(SPECIAL_SNOWFLAKE))
    # Slot 1: Enabled (Bit 7=1), Static Dwell 3s, Msg: " MERRY CHRISTMAS "
    set_slot(1, True, 0, 3, chr(SPECIAL_SNOWFLAKE)+"MERRY CHRISTMAS"+chr(SPECIAL_BELL))
    # Slot 2: Enabled (Bit 7=1), Static Dwell 3s, Msg: " HAPPY NEW YEAR! "
    set_slot(2, True, 0, 3, " HAPPY NEW YEAR! ")
    # Slot 3: Enabled (Bit 7=1), Static Dwell 3s, Msg: "   WELCOME TO    "
    set_slot(3, True, 0, 3, "   WELCOME TO    ")
    # Slot 4: Enabled (Bit 7=1), Static Dwell 3s, Msg: "  DYSFUNCTIONAL  "
    set_slot(4, True, 0, 3, "  DYSFUNCTIONAL  ")
    # Slot 5: Enabled (Bit 7=1), Static Dwell 3s, Msg: "  TECHNOLOGIES   "
    set_slot(5, True, 0, 3, "  TECHNOLOGIES   ")
    # Slot 6: Enabled (Bit 7=1), Static Dwell 3s, Msg: "   PHILIPPINES   "
    set_slot(6, True, 0, 3, "   PHILIPPINES   ")
    # Slot 7: Enabled (Bit 7=1), Static Dwell 3s, Msg: "GOD BLESS AMERICA"
    set_slot(7, True, 0, 3, "GOD BLESS AMERICA")
    save_carousel_to_flash()
#----------------------------------------------------------#
    
#----------------------------------------------------------#
def clear_all_slots():
#----------------------------------------------------------#
    # Wipes the RAM buffer clean with spaces and zeroed flags.
    #------------------------------------------------------#
    global _carousel_ram
    for slot in range(NUM_SLOTS):
        offset = slot * SLOT_SIZE
        _carousel_ram[offset] = 0x00  # Disabled, zero flags, zero dwell
        for i in range(17):
            _carousel_ram[offset + 1 + i] = 0x20  # Fill payload with ASCII spaces

#----------------------------------------------------------#
def set_slot(slot, enabled, scroll_mode, dwell, text_str):
#----------------------------------------------------------#
    # Packs a message layout chunk tightly into a specific
    # 18-byte RAM slot.
    #------------------------------------------------------#
    if not (0 <= slot < NUM_SLOTS): return
    offset = slot * SLOT_SIZE
    
    # Pack Control Byte 0 (Bit 7: Enable, Bits 4-6: Scroll, Bits 0-3: Dwell)
    control_byte = 0x00
    if enabled: control_byte |= 0x80                 
    control_byte |= (int(scroll_mode) & 0x07) << 4   
    control_byte |= (int(dwell) & 0x0F)              
    _carousel_ram[offset] = control_byte
    
    # Pad or truncate string strictly to 17 bytes to fit our module size layout
    padded_str = (text_str + " " * 17)[:17]
    for i in range(17):
        _carousel_ram[offset + 1 + i] = ord(padded_str[i])
#----------------------------------------------------------#

#----------------------------------------------------------#
def get_slot(slot):
#----------------------------------------------------------#
    # Unpacks an 18-byte slot chunk and returns a
    # human-readable dictionary block.
    #------------------------------------------------------#
    if not (0 <= slot < NUM_SLOTS): return None
    offset = slot * SLOT_SIZE
    
    control_byte = _carousel_ram[offset]
    enabled = bool(control_byte & 0x80)
    scroll_mode = (control_byte >> 4) & 0x07
    dwell = control_byte & 0x0F
    
    chars = []
    for i in range(17):
        chars.append(chr(_carousel_ram[offset + 1 + i]))
    text_str = "".join(chars)
    
    return {
        "enabled": enabled,
        "scroll_mode": scroll_mode,
        "dwell": dwell,
        "text": text_str
    }
#----------------------------------------------------------#

#----------------------------------------------------------#
def save_carousel_to_flash():
#----------------------------------------------------------#
    # Executes a power-fail safe atomic transaction to
    # write RAM to SPI flash.
    #------------------------------------------------------#
    print("Committing carousel updates to non-volatile flash securely...")
    try:
        # Write to staging file first
        with open(TEMP_FILE, "wb") as f:
            f.write(_carousel_ram)
        # Atomic file pointer swap at the file system level
        os.rename(TEMP_FILE, FILE_NAME)
        print("Secure flash synchronization complete.")
        return True
    except Exception as e:
        print("CRITICAL CRASH: Flash commit save interrupted:", e)
        return False
#----------------------------------------------------------#
    
#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#
