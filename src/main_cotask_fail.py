"""!
This script implements tasks for initializing hardware components, finding hotspots using a camera, and 
controlling a motor using PID control. This was intended to be all done using Cotask. Unfortunately, the program
was never able to fully function, but the intent was there.
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


def task_init():
    """!
    Task to initialize hardware components such as encoder, motor, servo, and camera.
    """
    # Initialize encoder, motor, servo, and camera
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    servo1 = servo_trigger.ServoDriver('PB6', 4, 1)
    
    i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
    cam = image_to_encoder.MLX_Cam(i2c_bus)
    
    # Start flywheel and reset encoder
    Flywheel.start_flywheel()
    utime.sleep_ms(2000)
    enc.zero()
    
    while True:
        yield  # Yield to allow other tasks to run

# Task function for finding the hotspot
def task_find_hotspot():
    """!
    Task to find the hotspot using the camera.
    """
    # Initialize encoder, motor, servo, and camera
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    servo1 = servo_trigger.ServoDriver('PB6', 4, 1)
    
    i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
    cam = image_to_encoder.MLX_Cam(i2c_bus)
    
    while True:
        try:
            iterations = 0
            
            # Finding the hotspot with the use of image_to_encoder
            while iterations < 1:
                image = cam.get_image()
                hot_spot = cam.find_hotSpot(image)
                iterations += 1
            
            setpoint = cam.hotspot_to_encoder_position(hot_spot[0], 32)

            print("Hottest spot coordinates:", hot_spot)
            encoder_position = cam.hotspot_to_encoder(hot_spot[0])
            print("Encoder Position:", encoder_position)  
        
        except ValueError as e:
            print('ValueError:', e)
        
        except Exception as e:
            print('Exception:', str(e))

        yield  # Yield to allow other tasks to run

# Task function for PID control
def task_pid_control():
    """!
    Task to control the motor using PID control.
    """
    # Initialize encoder, motor, servo, and camera
    enc = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)
    moe = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    servo1 = servo_trigger.ServoDriver('PB6', 4, 1)
    
    i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
    cam = image_to_encoder.MLX_Cam(i2c_bus)
    
    while True:
        try:       
            Kp = 0.17
            Ki = 0.01
            Kd = 0
            
            # Step response
            while enc.read() + 5 < setpoint or enc.read() - 5 > setpoint:
                current_position = enc.read()
                output = close.run(current_position)
                moe.set_duty_cycle(output)
                utime.sleep_ms(10)
            
            moe.set_duty_cycle(0)
            servo1.set_pos(250)
            utime.sleep_ms(3000)
            Flywheel.stop_flywheel()
            servo1.set_pos(0)
            utime.sleep_ms(1000)
           
            Kp = 0.17
            Ki = 0.1
            Kd = 0
            
            while enc.read() + 3 < setpoint or enc.read() - 3 > setpoint:
                current_position = enc.read()
                output = close.run(current_position)
                moe.set_duty_cycle(output)
                utime.sleep_ms(10)
                
            moe.set_duty_cycle(0)
        
        except ValueError as e:
            print('ValueError:', e)
        
        except Exception as e:
            print('Exception:', str(e))

        yield  # Yield to allow other tasks to run

# Main function to create tasks and start the scheduler
def main():
    """!
    Main function to initialize tasks and start the scheduler.
    """
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create the tasks
    task1 = cotask.Task(task_init, name="Task_Init", priority=1, period=100,
                        profile=True, trace=False)
    task2 = cotask.Task(task_find_hotspot, name="Task_Find_Hotspot", priority=2, period=70,
                        profile=True, trace=False)
    task3 = cotask.Task(task_pid_control, name="Task_PID_Control", priority=3, period=180,
                        profile=True, trace=False)
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)

    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    print('\n' + str(cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')

# Call the main function to start the application
if __name__ == "__main__":
    main()
