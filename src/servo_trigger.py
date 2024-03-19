"""
Servo Driver Class

This script defines a class `ServoDriver` for controlling servo motors using MicroPython on a Pyboard. The class allows setting the position of the servo motor using PWM signals.

The `ServoDriver` class initializes the servo driver with the specified pin, timer, and timer channel. It provides a method `set_pos` to set the position of the servo motor by specifying the angle.

The script also includes a test code block to demonstrate the usage of the `ServoDriver` class.

@author
Author: Conor Schott, Fermin Moreno, Berent Baysal

Date: 3/14/2024
!"""

import micropython
import time
import pyb



class ServoDriver:
    def __init__ (self, servo_pin, timer, timer_channel ):
        """
        Initializes the ServoDriver object.

        Args:
            servo_pin (str): The pin connected to the servo motor.
            timer (int): The timer number to use for PWM.
            timer_channel (int): The channel of the timer to use for PWM.
        !"""
        servo_pin = getattr(pyb.Pin.board, servo_pin) # Get the pin value for the pin stored in servo_pin
        
        # Initialize the pin as an output pin
        self.servo_pin=pyb.Pin(servo_pin, pyb.Pin.OUT_PP, value=0)
        
        # Start the timer and set its frequency and prescaler
        t = pyb.Timer(timer, freq= 5000) 
        t.prescaler(80)  # Set prescaler to get clock frequency to 1 MHz, not 80
        
        # Start PWM on the timer channel for the pin
        self.timer_channel=t.channel(timer_channel, pyb.Timer.PWM, pin=self.servo_pin) 

    def set_pos(self, angle):
        """
        Sets the position of the servo motor.

        Args:
            angle (int): The desired angle of the servo motor.
        !"""
        # Convert angle in degrees to the PWM needed for the servo controller
        PWM_angle = (angle / 180) * 2000 + 500   # 500 microseconds is 0 degrees, 2500 is 180 degrees
        PWM_angle = int(PWM_angle)
        
        # Set the pulse width of the timer channel
        self.timer_channel.pulse_width(PWM_angle)

if __name__ == "__main__":  
    # Test code to demonstrate usage of the ServoDriver class
    servo1 = ServoDriver('PB6', 4, 1)
    servo1.set_pos(250)  # Set servo position to 250 degrees
    time.sleep(3)
    servo1.set_pos(0)    # Set servo position to 0 degrees
    time.sleep(3)
