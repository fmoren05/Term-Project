"""
@file Flywheel.py
@brief Implements functions for controlling a flywheel.

@details
This module contains functions to start and stop a flywheel motor by controlling a pin on a Pyboard.

@author
Author: Conor Schott, Fermin Moreno, Berent Baysal

@date
Date: 3/14/2024


@version
Version: 1.0
!"""

import pyb

def start_flywheel():
    """
    Start the flywheel motor.
    !"""
    # Initialize the pin for controlling the flywheel
    pinC0 = pyb.Pin(pyb.Pin.board.PC0, pyb.Pin.OUT_PP)

    # Turn on the flywheel
    pinC0.value(1)

def stop_flywheel():
    """
    Stop the flywheel motor.
    !"""
    # Initialize the pin for controlling the flywheel
    pinC0 = pyb.Pin(pyb.Pin.board.PC0, pyb.Pin.OUT_PP)
    
    # Turn off the flywheel
    pinC0.value(0)
