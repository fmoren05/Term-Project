"""!
@brief This script demonstrates cooperative multitasking using Cotask on a microcontroller.
Tasks 1 and 2 perform closed-loop control of motors based on encoder feedback.
The script also utilizes shared variables and a queue for inter-task communication.

@file main.py
@author Conor Schott, Fermin Moreno, Berent Baysal
"""
import utime
import pyb
import encoder_reader
import motor_control
import PID_Closed_Loop
import image_to_encoder
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
import servo_trigger
import Flywheel




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
cam = image_to_encoder.MLX_Cam(i2c_bus)
#Actual important stuff is below this line-----------------------------------------


Flywheel.start_flywheel()
utime.sleep_ms(2000)
enc.zero()
while True:
    try:       
        
        Kp = 0.17
        Ki = 0.01
        Kd = 0
        iterations = 0
        #finding the hotspot with the use of image_to_encoder---------
        while iterations < 1:
            image = cam.get_image()
            #cam.ascii_art(image)
            hot_spot = cam.find_hotSpot(image)
            #utime.sleep_ms(1) ########
            iterations+=1
        
        #Flywheel.run_flywheel()
        setpoint = cam.hotspot_to_encoder_position(hot_spot[0], 32)
        #setpoint = -25652
        print(setpoint)
        
        #------------------------------------------------------


        print("Hottest spot coordinates:", hot_spot)
        encoder_position = cam.hotspot_to_encoder(hot_spot[0])
        print("Encoder Position:", encoder_position)  
        
        
        close = PID_Closed_Loop.ClosedLoopController(Kp, Ki, Kd, setpoint)
        iterations = 0
        
        
        #Step response-----------------------------------------
        
        while enc.read()+5 < setpoint or enc.read()-5 > setpoint:
            current_position = enc.read()
            output = close.run(current_position)
            moe.set_duty_cycle(output)
            #print(current_position)
            utime.sleep_ms(10)
            
        moe.set_duty_cycle(0)
        servo1.set_pos(250)
        utime.sleep_ms(3000)
        Flywheel.stop_flywheel()
        servo1.set_pos(0)
        utime.sleep_ms(1000)
        
        #moe.set_duty_cycle(0)
        #utime.sleep_ms(2000)
       
        Kp = 0.17
        Ki = 0.1
        Kd = 0
        setpoint = 0
        close = PID_Closed_Loop.ClosedLoopController(Kp, Ki, Kd, setpoint)
        
        while enc.read()+3 < setpoint or enc.read()-3 > setpoint:
            current_position = enc.read()
            output = close.run(current_position)
            moe.set_duty_cycle(output)
            #print(current_position)
            utime.sleep_ms(10)   
        moe.set_duty_cycle(0)
        break
        
#EXCEPT BLOCKS--------------------------------------------------------    
        
    except ValueError as e:
        print('ValueError:', e)
        
    except Exception as e:
        print('Exception:', str(e))  # Convert integer 'e' to string explicitly
        # Additional exception handling or logging can be added here
       
