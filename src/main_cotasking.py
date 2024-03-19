"""!
@file main_cotasking.py

@brief This script demonstrates cooperative multitasking using Cotask on a microcontroller.
Task 1 performs closed-loop control of the panning axis brushed DC motor based on camera feedback.
The camera outputs a hotspot coordinate which is then translated to encoder counts and used as the setpoint 
for our PID controller. Upon reaching the desired setpoint, the task then calls for the servo motor trigger to activate,
placing a Nerf bullet into the path of the flywheels. 

Task 2 controls the low-side MOSFET switch that is responsible for sending current to our flywheel motors.


@author Conor Schott, Fermin Moreno, Berent Baysal
"""

import gc  # Importing garbage collector for memory management
import pyb  # Importing pyb for board-specific functionality
import utime  # Importing utime for microsecond-level timing
import cotask  # Importing cotask for cooperative multitasking
import task_share
import motor_control
import encoder_reader
import PID_Closed_Loop
import image_to_encoder
import servo_trigger
import Flywheel
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
#---------------------------------------------------------------------------------

def firing_sequence_fun():
    """!
    Task function for Firing Sequence.
    Implements closed-loop control of a motor based on camera feedback.
    """
    # ENCODER AND MOTOR SETUP----------------------------------------------------------
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    servo1 = servo_trigger.ServoDriver('PB6',4,1)

    # CAMERA SETUP---------------------------------------------------------------------

    try:
        from pyb import info
    except ImportError:
        i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
    else:
        i2c_bus = I2C(1)

    i2c_address = 0x33
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    cam = Progress1.MLX_Cam(i2c_bus)
    # Actual important stuff is below this line-----------------------------------------

    
    utime.sleep_ms(2000)
    enc.zero()
    while True:
        try:
            Kp = 0.17
            Ki = 0.01
            Kd = 0
            iterations = 0
            # Finding the hotspot with the use of progress1---------
            while iterations < 1:
                image = cam.get_image()
                # cam.ascii_art(image)
                hot_spot = cam.find_hotSpot(image)
                # utime.sleep_ms(1) ########
                iterations += 1

            setpoint = cam.hotspot_to_encoder_position(hot_spot[0], 32)
            print(setpoint)

            print("Hottest spot coordinates:", hot_spot)
            encoder_position = cam.hotspot_to_encoder(hot_spot[0])
            print("Encoder Position:", encoder_position)

            close = PID_Closed_Loop.ClosedLoopController(Kp, Ki, Kd, setpoint)
            iterations = 0

            # Step response-----------------------------------------
            while enc.read() + 5 < setpoint or enc.read() - 5 > setpoint:
                current_position = enc.read()
                output = close.run(current_position)
                moe.set_duty_cycle(output)
                # print(current_position)
                utime.sleep_ms(10)

            moe.set_duty_cycle(0)
            servo1.set_pos(250)
            utime.sleep_ms(500)
            servo1.set_pos(0)
            utime.sleep_ms(500)

            Kp = 0.17
            Ki = 0.1
            Kd = 0
            setpoint = 0
            close = PID_Closed_Loop.ClosedLoopController(Kp, Ki, Kd, setpoint)

            while enc.read() + 3 < setpoint or enc.read() - 3 > setpoint:
                current_position = enc.read()
                output = close.run(current_position)
                moe.set_duty_cycle(output)
                # print(current_position) #used for testing
                utime.sleep_ms(10)
            moe.set_duty_cycle(0)
            break

        # EXCEPTION BLOCKS--------------------------------------------------------
        except ValueError as e:
            print('ValueError:', e)
        except Exception as e:
            print('Exception:', str(e))  # Convert integer 'e' to string explicitly
            # Additional exception handling or logging can be added here

# Function for Flywheel Motors with similar functionality as Firing Sequence
def flywheel_motors_fun():
    """!
    Task function for Flywheel Motors.
    Activates the low-side MOSFET switch for a set time limit.
    """
    
    while True:
        Flywheel.start_flywheel()
        utime.sleep_ms(10000)
        Flywheel.stop_flywheel()
        break

#----------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Creating shared variables and queue
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False, name="Queue 0")

    # Creating tasks and adding them to task list
    task1 = cotask.Task(firing_sequence_fun, name="Firing_Sequence", priority=1, period=45,
                        profile=True, trace=False)
    task2 = cotask.Task(flywheel_motors_fun, name="Flywheel_Motors", priority=1, period=45,
                        profile=True, trace=False)
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    gc.collect()  # Running garbage collection for memory management

    while True:
        try:
            cotask.task_list.pri_sched()  # Priority scheduling for tasks
        except KeyboardInterrupt:
            break

    # Printing diagnostics after interruption
    print('\n' + str(cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')
