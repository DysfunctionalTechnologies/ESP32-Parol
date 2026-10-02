#----------------------------------------------------------#
# Project: ESP32-Parol
# Module:  state.py
# Author:  Timothy S. Carlson
#----------------------------------------------------------#

#----------------------------------------------------------#
# System Imports
#----------------------------------------------------------#
#----------------------------------------------------------#

#----------------------------------------------------------#
# Project Imports
#----------------------------------------------------------#
# Absolutely NO imports are allowed in this file!
#from max7219 import MAX7219_INTENSITY_MIN # Remove this dependency, use a raw integer instead
#----------------------------------------------------------#

class SystemState:
    def __init__(self):
        self.POWER_ON = True
        self.reset_carousel = False
        self.matrix_brightness = 0  # Raw int default (removes max7219 file dependency)

# Single global instance shared across the entire system
state = SystemState()

#----------------------------------------------------------#
if __name__ == "__main__":
#----------------------------------------------------------#
    print("This module cannot be run directly.")
    print("Please run main.py")
#----------------------------------------------------------#
    