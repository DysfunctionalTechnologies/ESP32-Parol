#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  max7219.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
import time
from   machine import Pin, idle
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
import font
import state
#----------------------------------------------------------#

#----------------------------------------------------------#
# 1. Hardware Pin Configurations
#----------------------------------------------------------#
DIN = Pin(4, Pin.OUT)
CLK = Pin(6, Pin.OUT)
CS  = Pin(7, Pin.OUT)
#----------------------------------------------------------#


#----------------------------------------------------------#
# 2. Layout & Scaling Configurations
#----------------------------------------------------------#
NUM_MODULES             = 17     # Scales dynamically if modules change
LEFT_TO_RIGHT           = True   # True = Input on Left (Mod 0). False = Input on Right.
#----------------------------------------------------------#

#----------------------------------------------------------#
# MAX7219 Commands
#----------------------------------------------------------#
MAX7219_NOP             = 0x00
    #------------------------------------------------------#
MAX7219_DIGIT_0         = 0x01
MAX7219_DIGIT_1         = 0x02
MAX7219_DIGIT_2         = 0x03
MAX7219_DIGIT_3         = 0x04
MAX7219_DIGIT_4         = 0x05
MAX7219_DIGIT_6         = 0x07
MAX7219_DIGIT_7         = 0x08
    #------------------------------------------------------#
MAX7219_DECODE          = 0x09
MAX7219_DECODE_OFF      = 0x00
MAX7219_DECODE_ON       = 0xFF
    #------------------------------------------------------#
MAX7219_INTENSITY       = 0x0A
MAX7219_INTENSITY_0     = 0x00
MAX7219_INTENSITY_MIN   = MAX7219_INTENSITY_0
MAX7219_INTENSITY_1     = 0x01
MAX7219_INTENSITY_2     = 0x02
MAX7219_INTENSITY_3     = 0x03
MAX7219_INTENSITY_4     = 0x04
MAX7219_INTENSITY_5     = 0x05
MAX7219_INTENSITY_6     = 0x06
MAX7219_INTENSITY_7     = 0x07
MAX7219_INTENSITY_MID   = MAX7219_INTENSITY_7
MAX7219_INTENSITY_8     = 0x08
MAX7219_INTENSITY_9     = 0x09
MAX7219_INTENSITY_A     = 0x0A
MAX7219_INTENSITY_B     = 0x0B
MAX7219_INTENSITY_C     = 0x0C
MAX7219_INTENSITY_D     = 0x0D
MAX7219_INTENSITY_E     = 0x0E
MAX7219_INTENSITY_F     = 0x0F
MAX7219_INTENSITY_MAX   = MAX7219_INTENSITY_F
    #------------------------------------------------------#
MAX7219_SCANLIMIT       = 0x0B
MAX7219_SCANLIMIT_MIN   = 0x00
MAX7219_SCANLIMIT_MAX   = 0x07
    #------------------------------------------------------#
MAX7219_SHUTDOWN        = 0x0C
MAX7219_SHUTDOWN_ON     = 0x00
MAX7219_SHUTDOWN_OFF    = 0x01
    #------------------------------------------------------#
MAX7219_DISPLAYTEST     = 0x0F
MAX7219_DISPLAYTEST_OFF = 0x00
MAX7219_DISPLAYTEST_ON  = 0x01
    #------------------------------------------------------#
    # System Parameters
    #------------------------------------------------------#
MAX7219_DIGITS          = NUM_MODULES
MAX7219_LINES           = 8
MAX7219_DATA            = MAX7219_DIGITS * MAX7219_LINES
#----------------------------------------------------------#

# Ensure clean idle states
CS.value(1)
CLK.value(0)

# --- Persistent RAM Frame Buffer  ---
# Structure: A dictionary mapping logical rows (1 to 8) to a list of bytes.
# Each entry in the list holds the byte state for that specific module index.
# Initializes completely blank (all bits 0)
_frame_buffer = {row: [0x00] * NUM_MODULES for row in range(1, 9)}

# --- Text Engine Layout State ---
_current_mod = 0       # Tracks active module cursor position (0 to NUM_MODULES-1)

def init_stick():
    print(f"Initializing {NUM_MODULES}-module STICK with geometry corrections...")
    send_all_same(MAX7219_DISPLAYTEST, MAX7219_DISPLAYTEST_OFF) # Display Test Off
    send_all_same(MAX7219_SCANLIMIT,   MAX7219_SCANLIMIT_MAX)   # Scan Limit: Active all 8 rows
    send_all_same(MAX7219_DECODE,      MAX7219_DECODE_OFF)      # Decode Mode: Direct pixel control
    send_all_same(MAX7219_INTENSITY,   MAX7219_INTENSITY_MIN)   # Intensity: Low brightness
    send_all_same(MAX7219_SHUTDOWN,    MAX7219_SHUTDOWN_OFF)    # Shutdown: Normal Operation
    send_all_same(MAX7219_INTENSITY,   MAX7219_INTENSITY_MAX)   # Intensity: Low brightness
    clear_stick()

def send_all_same(reg, data):
    """Broadcasts a raw configuration command to all modules."""
    CS.value(0)
    for _ in range(NUM_MODULES):
        shift_out(reg)
        shift_out(data)
    CS.value(1)

def shift_out(byte_value):
    """Bit-bangs a single byte with clock pulses."""
    for bit in range(8):
        DIN.value((byte_value >> (7 - bit)) & 0x01)
        CLK.value(1)
        CLK.value(0)

def clear_stick():
    """Wipes the local memory frame buffer and updates the display panels."""
    global _frame_buffer
    print("Completely blanking the entire STICK...")
    # Clear out local memory states
    for row in range(1, 9):
        _frame_buffer[row] = [0x00] * NUM_MODULES
    # Push cleared memory out to the physical chips
    flush()
    set_cursor(0)

def flush():
    """Pushes the current RAM frame buffer states down to the physical cascade line."""
    for row in range(1, 9):
        send_row_data(row, _frame_buffer[row])

def send_row_data(logical_row, module_data_list):
    """
    Sends data for a logical row (1=Top, 8=Bottom) across all modules.
    Inverts and flips bits to match physical board geometry layouts.
    """
    # Fix row inversion: Logical Row 1 (Top) maps to physical MAX7219 row register 8
    physical_reg = 9 - logical_row
    
    CS.value(0)
    
    # Cascade data down the chain (from last module down to module 0)
    for m in range(NUM_MODULES - 1, -1, -1):
        shift_out(physical_reg)
        
        # Fix column inversion: Reverse bits for this specific module
        corrected_data = reverse_bits(module_data_list[m])
        shift_out(corrected_data)
        
    CS.value(1)
    
def reverse_bits(b):
    """Reverses the bit order of a byte (e.g., 0b10000000 becomes 0b00000001)."""
    # This corrects the Right-to-Left local column mirroring inside each module
    b = ((b & 0xF0) >> 4) | ((b & 0x0F) << 4)
    b = ((b & 0xCC) >> 2) | ((b & 0x33) << 2)
    b = ((b & 0xAA) >> 1) | ((b & 0x55) << 1)
    return b

def set_cursor(p):
    """
    Sets the active cursor to a specific character module position (0 to NUM_MODULES-1).
    If the parameter is invalid or off the end of the stick, resets position to 0.
    """
    global _current_mod
    if 0 <= p < NUM_MODULES:
        _current_mod = p
    else:
        _current_mod = 0  # Safety fallback to the beginning of the stick

def print_char(char_code):
    """
    Renders an 8x8 font bitmap row-by-row directly into the RAM frame buffer 
    at the currently targeted module slot position, then auto-advances the cursor.
    This function operates strictly in RAM and does NOT trigger a hardware flush.
    """
    global _current_mod, _frame_buffer
    
    # 1. Fetch character bitmap array, falling back to Space (all 0s) if missing
    bitmap = font.FONT_MAP.get(char_code, font.FONT_MAP[0x20])
    
    # 2. Determine target physical module index based on orientation configuration
    if LEFT_TO_RIGHT:
        target_module = _current_mod
    else:
        target_module = (NUM_MODULES - 1) - _current_mod

    # 3. Write font data directly into the row matrix for that module channel
    for row_idx in range(8):
        logical_row = row_idx + 1
        row_byte = bitmap[row_idx]
        _frame_buffer[logical_row][target_module] = row_byte

    # 4. Advance layout cursor, wrapping back to 0 if the scaling limit is met
    _current_mod += 1
    if _current_mod >= NUM_MODULES:
        _current_mod = 0

def print_string(*args):
    """
    Prints a text string across the STICK modules.
    
    Usage:
        print_string("TEXT")         - Prints at the current cursor position.
        print_string(0, "TEXT")      - Sets cursor to 0, then prints text.
        print_string(12, "TEXT")     - Sets cursor to 12, then prints text (wraps around).
    """
    # 1. Parse dynamic arguments
    if len(args) == 2:
        position = args[0]
        text_str = args[1]
        set_cursor(position) # Explicitly shift cursor first
    elif len(args) == 1:
        text_str = args[0]   # Keep current cursor position
    else:
        return # Safety gate for empty or invalid calls

    # 2. Iterate through and push characters to the RAM buffer
    for char in text_str:
        print_char(ord(char))
        
    # 3. HIGH-LEVEL APPLICATION TAIL FLUSH:
    # Now that the entire string has been completely written to memory,
    # issue exactly ONE hardware write to update the physical display.
    flush()
    
def stick_diagnostic():
    """Runs structural diagnostic verification routine patterns."""
    while True:
        print("Scanning rows (Top to Bottom)...")
        for row in range(1, 9):
            send_row_data(row, [0xFF] * NUM_MODULES)
            time.sleep(0.25)
            send_row_data(row, [0x00] * NUM_MODULES)
        
        time.sleep(0.25)
        clear_stick()
        
        print("Walking columns (Smoothly from Left to Right)...")
        frame = [0x00] * NUM_MODULES
        for m in range(NUM_MODULES):
            for bit in range(8):
                frame[m] = (0x80 >> bit)
                for row in range(1, 9):
                    send_row_data(row, frame)
                time.sleep(0.25)
                frame[m] = 0x00
        clear_stick()
        time.sleep(0.25)

def set_brightness(level):
    """
    Exposes a top-level function to adjust the matrix cascade brightness.
    Accepts an intensity value from 0 (dimmest) to 15 (brightest).
    """
    # Enforce safe hardware boundary restrictions (0x00 to 0x0F)
    if level < 0: level = 0
    if level > 15: level = 15
    
    # Send configuration command 0x0A directly down the cascade line
    send_all_same(0x0A, level)

#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#
