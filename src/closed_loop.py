"""
@brief Implements a closed-loop controller for motor control.

@details
This module contains the implementation of a closed-loop controller for motor control. It includes functions for setting the setpoint, adjusting the proportional and integral gains, and running the control loop.

@author
Author: Conor Schott, Fermin Moreno, Berent Baysal

@date
Date: 3/14/2024

@version
Version: [Version Number]
!"""

import utime
import pyb
import encoder_reader
import motor_control

class ClosedLoopController:
    """
    Class representing a closed-loop controller for motor control.
    !"""

    def __init__(self, Kp, Ki, setpoint):
        """
        Initialize the closed-loop controller.

        @param Kp: The proportional gain.
        @type Kp: float
        @param Ki: The integral gain.
        @type Ki: float
        @param setpoint: The desired setpoint.
        @type setpoint: float
        !"""
        self.Kp = Kp
        self.Ki = Ki
        self.setpoint = setpoint
        self.measured_output = 0
        self.integral = 0
        self.time_buffer = []
        self.position_buffer = []
        self.start_time = None
        
    def run(self, measured_output):
        """
        Run the control loop.

        @param measured_output: The measured output.
        @type measured_output: float
        @return: The actuation signal.
        @rtype: float
        !"""
        if self.start_time is None:
            self.start_time = utime.ticks_ms()

        self.measured_output = measured_output
        error = self.setpoint - self.measured_output
        self.integral += error
        actuation_signal = self.Kp * error + self.Ki * self.integral

        if len(self.time_buffer) < 200:
            current_time = (utime.ticks_ms() - self.start_time) // 10
            self.time_buffer.append(current_time)
            self.position_buffer.append(self.measured_output)

        return actuation_signal

    def set_setpoint(self, setpoint):
        """
        Set the setpoint.

        @param setpoint: The desired setpoint.
        @type setpoint: float
        !"""
        self.setpoint = setpoint
        self.integral = 0  # Reset the integral term when the setpoint changes

    def set_Kp(self, Kp):
        """
        Set the proportional gain.

        @param Kp: The proportional gain.
        @type Kp: float
        !"""
        self.Kp = Kp

    def set_Ki(self, Ki):
        """
        Set the integral gain.

        @param Ki: The integral gain.
        @type Ki: float
        !"""
        self.Ki = Ki
        
if __name__ == '__main__':
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)

    close = ClosedLoopController(Kp=.00003, Ki=0.0003, setpoint=0)

    target_setpoint = 50000
    close.set_setpoint(target_setpoint)

    # Main control loop
    while True:
        current_position = enc.read()
        output = close.run(current_position)
        moe.set_duty_cycle(output)
        print(current_position)
        utime.sleep_ms(10)
