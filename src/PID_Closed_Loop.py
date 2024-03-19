"""!
@file PID_Closed_Loop
@brief Implements a ClosedLoopController class for controlling a system using closed-loop feedback.

@details
This script defines a ClosedLoopController class, which implements a closed-loop feedback controller 
for controlling a system. It utilizes proportional-integral-derivative (PID) control with adjustable 
constants (Kp, Ki, Kd). The controller calculates the actuation signal based on the measured output 
and the desired setpoint.

@author
Authors: Conor Schott, Fermin Moreno, Berent Baysal

@date
Date: 3/14/2024

@dependencies
Dependencies:
- utime
- pyb
- encoder_reader
- motor_control
"""

import utime
import pyb
import encoder_reader
import motor_control

class ClosedLoopController:
    """!
    Implements a ClosedLoopController class for controlling a system using closed-loop feedback.
    """

    def __init__(self, Kp, Ki, Kd, setpoint):
        """!
        Initializes the ClosedLoopController object with the provided parameters.
        @param Kp: Proportional gain constant
        @param Ki: Integral gain constant
        @param Kd: Derivative gain constant
        @param setpoint: Desired setpoint for the system
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.measured_output = 0
        self.integral = 0
        self.prev_error = 0
        self.time_buffer = []
        self.position_buffer = []
        self.start_time = None
        self.current_time = 0
        self.previous_time = 0
        self.delta_time = 0
        
    def run(self, measured_output):
        """!
        Runs the closed-loop control algorithm to calculate the actuation signal.
        @param measured_output: Measured output from the system
        @return: Actuation signal calculated by the controller
        """
        if self.start_time is None:
            self.start_time = utime.ticks_ms()
            
        self.delta_time = self.current_time - self.previous_time
        self.previous_time = self.current_time
        self.measured_output = measured_output
        error = self.setpoint - self.measured_output
        self.integral += error * self.current_time
        if self.delta_time == 0:
            derivative = 0
        else:
            derivative = (error - self.prev_error) / self.delta_time
        
        actuation_signal = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        if len(self.time_buffer) < 200:
            self.current_time = (utime.ticks_ms() - self.start_time) // 1000
            self.time_buffer.append(self.current_time)
            self.position_buffer.append(self.measured_output)

        self.prev_error = error

        return actuation_signal

    def set_setpoint(self, setpoint):
        """!
        Sets the desired setpoint for the system.
        @param setpoint: Desired setpoint for the system
        """
        self.setpoint = setpoint
        self.integral = 0
        self.prev_error = 0

    def set_Kp(self, Kp):
        """!
        Sets the proportional gain constant (Kp).
        @param Kp: Proportional gain constant
        """
        self.Kp = Kp

    def set_Ki(self, Ki):
        """!
        Sets the integral gain constant (Ki).
        @param Ki: Integral gain constant
        """
        self.Ki = Ki

    def set_Kd(self, Kd):
        """!
        Sets the derivative gain constant (Kd).
        @param Kd: Derivative gain constant
        """
        self.Kd = Kd

if __name__ == '__main__':
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)

    close = ClosedLoopController(Kp=0.17, Ki=0.01, Kd=0, setpoint=0)

    target_setpoint = -26690
    close.set_setpoint(target_setpoint)

    while True:
        current_position = enc.read()
        output = close.run(current_position)
        moe.set_duty_cycle(output)
        print(current_position)
        utime.sleep_ms(10)
