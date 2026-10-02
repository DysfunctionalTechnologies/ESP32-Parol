#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  ir_remote.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
from machine import Pin
#----------------------------------------------------------#

#----------------------------------------------------------#
# Library Imports
#----------------------------------------------------------#
from ir_rx.nec import NEC_16\
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
import max7219
import state
#----------------------------------------------------------#

#----------------------------------------------------------#
# --- Hardware Allocation Setup ---
#----------------------------------------------------------#
IR_PIN_NUM = 18
#----------------------------------------------------------#

#----------------------------------------------------------#
# Ubiquitous Chinesium IR Remote
# 24 key, coin cell battery
#----------------------------------------------------------#
CHINESIUM_REMOTE   = 0xEF00
IR_BRIGHTNESS_UP   = 0x00
IR_BRIGHTNESS_DOWN = 0x01
IR_POWER_OFF       = 0x02
IR_POWER_ON        = 0x03
IR_MUSIC_OFF       = 0x04
IR_MUSIC_ON        = 0x05
IR_IGNORE_06       = 0x06
IR_IGNORE_07       = 0x07
IR_IGNORE_08       = 0x08
IR_IGNORE_09       = 0x09
IR_IGNORE_0A       = 0x0A
IR_IGNORE_0B       = 0x0B
IR_IGNORE_0C       = 0x0C
IR_IGNORE_0D       = 0x0D
IR_IGNORE_0E       = 0x0E
IR_IGNORE_0F       = 0x0F
IR_IGNORE_10       = 0x10
IR_IGNORE_11       = 0x11
IR_IGNORE_12       = 0x12
IR_IGNORE_13       = 0x13
IR_IGNORE_14       = 0x14
IR_IGNORE_15       = 0x15
IR_IGNORE_16       = 0x16
IR_IGNORE_17       = 0x17
#----------------------------------------------------------#

#----------------------------------------------------------#
# Global reference to keep the low-level listener from
# being garbage collected
#----------------------------------------------------------#
_receiver = None
_state_ref = None
#----------------------------------------------------------#

#----------------------------------------------------------#
def init_ir(pin_num, system_state):
#----------------------------------------------------------#
    # Binds the hardware pin to the NEC listener and links
    # the shared global application state.
    #------------------------------------------------------#
    global _receiver, _state_ref
    _state_ref = system_state
    
    ir_pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
    _receiver = NEC_16(ir_pin, _ir_callback)
    print("Infrared Remote Engine bound and listening...")
#----------------------------------------------------------#

#----------------------------------------------------------#
def _ir_callback(data, addr, ctrl):
#----------------------------------------------------------#
    # Asynchronous hardware intercept callback for 24-key
    # remote codes.
    #------------------------------------------------------#
    global _state_ref
    if data < 0 or _state_ref is None: 
        return  # Filter out noise and repeat bursts
        
    print(f"IR Intercepted -> Addr: 0x{addr:04X} | Key: 0x{data:02X}")
    
    # Restrict processing strictly to your verified 24-key remote master address
    if addr == CHINESIUM_REMOTE:
        
        #--------------------------------------------------#
        # Row 1, Button 1: Brightness UP -> 0x00
        #--------------------------------------------------#
        if data == IR_BRIGHTNESS_UP:
            if _state_ref.POWER_ON and _state_ref.matrix_brightness < 15:
                _state_ref.matrix_brightness += 1
                max7219.set_brightness(_state_ref.matrix_brightness) # <-- Updated Line
                print(f"Brightness Increased: {_state_ref.matrix_brightness}/15")
        #--------------------------------------------------#

        #--------------------------------------------------#
        # Row 1, Button 2: Brightness DOWN -> 0x01
        #--------------------------------------------------#
        elif data == IR_BRIGHTNESS_DOWN:
            if _state_ref.POWER_ON and _state_ref.matrix_brightness > 0:
                _state_ref.matrix_brightness -= 1
                max7219.set_brightness(_state_ref.matrix_brightness) # <-- Updated Line
                print(f"Brightness Decreased: {_state_ref.matrix_brightness}/15")
        #--------------------------------------------------#
 
        #--------------------------------------------------#
        # --- POWER TOGGLE CONTROLS ---
        #--------------------------------------------------#
        # Row 1, Button 3: Power OFF -> 0x02
        #--------------------------------------------------#
        elif data == IR_POWER_OFF:
            print("SYSTEM SHUTDOWN TRIGGERED VIA IR")
            _state_ref.POWER_ON = False
            _handle_power_state_change()
        #--------------------------------------------------#
            
        #--------------------------------------------------#
        # Row 1, Button 4: Power ON -> 0x03
        #--------------------------------------------------#
        elif data == IR_POWER_ON:
            print("SYSTEM POWER ON TRIGGERED VIA IR")
            _state_ref.POWER_ON = True
            _state_ref.reset_carousel = True
            _handle_power_state_change()
        #--------------------------------------------------#
#----------------------------------------------------------#

#----------------------------------------------------------#
def _handle_power_state_change():
#----------------------------------------------------------#
    # Manages low-level display driver states instantly
    # when power toggles.
    #------------------------------------------------------#
    global _state_ref
    if not _state_ref.POWER_ON:
        print("Blanking STICK completely to enter low-power sleep...")
        max7219.clear_stick()
        # Turn off all transistor loops globally if your main taps are instantiated
        try:
            import main
            for tap in (main.body_taps + main.ring_taps):
                tap.value(0)
        except:
            pass
#----------------------------------------------------------#

#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#

