"""
@file encoder_reader.py
@brief Implements an encoder reader using Pyboard's Timer and Pin modules.

@details
This module contains the Encoder class, which implements an encoder reader using Pyboard's Timer and Pin modules.

@author
Authors: Conor Schott, Fermin Moreno, Berent Baysal

@date
Date: 16th February 2024

!"""

from pyb import Timer, Pin
import time

class Encoder:
    """
    Class representing an encoder reader.
    !"""

    def __init__(self, timer, enc_pin_A, enc_pin_B):
        """
        Initialize the encoder reader.

        @param timer: Timer for encoder counting.
        @type timer: int
        @param enc_pin_A: Encoder channel A pin.
        @type enc_pin_A: pyb.Pin
        @param enc_pin_B: Encoder channel B pin.
        @type enc_pin_B: pyb.Pin
        !"""
        self.timer = Timer(timer, prescaler=0, period=0xFFFF)
        self.enc_chA = self.timer.channel(1, Timer.ENC_AB, pin=enc_pin_A)
        self.enc_chB = self.timer.channel(2, Timer.ENC_AB, pin=enc_pin_B)
        self.cur_value = 0
        self.prev_value = self.timer.counter()
        
    def read(self):
        """
        Read the encoder values.

        @return: Tuple containing the current encoder count, delta, and channel A and B values.
        @rtype: int
        !"""
        delta = self.timer.counter() - self.prev_value
        if delta > 32767:
            delta -= 65536
        elif delta < -32768:
            delta += 65535
        self.prev_value = self.timer.counter()
        self.cur_value += delta  
        return self.cur_value

    def zero(self):
        """
        Set the count to zero at the current position for both encoders.
        !"""
        self.cur_value = 0

if __name__ == '__main__':
    encoder1 = Encoder(4, Pin.board.PB6, Pin.board.PB7)
    encoder2 = Encoder(8, Pin.board.PC6, Pin.board.PC7)
    
    while True:
        encoder2_value = encoder2.read()
        print()
        print("Encoder 2 Value:", encoder2_value)
        time.sleep(.10)
        print()
