"""
This script demonstrates cooperative multitasking using Cotask on a microcontroller. 
Tasks 1 and 2 perform closed-loop control of motors based on encoder feedback. 
The script also utilizes shared variables and a queue for inter-task communication.

Authors: Conor Schott, Fermin Moreno, Berent Baysal
"""

import gc  # Importing garbage collector for memory management
import utime  # Importing utime for microsecond-level timing
import pyb  # Importing pyb for board-specific functionality
import cotask  # Importing cotask for cooperative multitasking
import task_share  # Importing task_share for shared variables among tasks
import encoder_reader  # Importing custom module for reading encoder values
import motor_control  # Importing custom module for motor control
import closed_loop  # Importing custom module for closed-loop control

#---------------------------------------------------------------------------------

def task1_fun():
    """!
    Task function for Task 1.
    Implements closed-loop control of a motor based on encoder feedback.
    """
    encoder1 = encoder_reader.Encoder(8, pyb.Pin.board.PC6, pyb.Pin.board.PC7)  # Encoder for Task 1
    motor1 = motor_control.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)  # Motor driver for Task 1
    close1 = closed_loop.ClosedLoopController(0.03, 50000)  # Closed-loop controller for Task 1
    encoder1.zero()  # Zeroing the encoder

    graph_printed = False  # Flag to indicate whether graph has been printed for current trial

    while True:
        iterations1 = 0
        while iterations1 <= 150:
            current_position1 = encoder1.read()  # Reading current encoder position
            output1 = close1.run(current_position1)  # Running closed-loop control
            motor1.set_duty_cycle(output1)  # Setting motor duty cycle
            iterations1 += 1
            yield 0

        if not graph_printed:
            close1.print_results()  # Printing results if graph hasn't been printed yet
            graph_printed = True  # Set flag to True after printing graph once

        motor1.set_duty_cycle(0)  # Stopping the motor

# Function for Task 2 with similar functionality as Task 1
def task2_fun():
    """!
    Task function for Task 2.
    Implements closed-loop control of another motor based on encoder feedback.
    """
    encoder2 = encoder_reader.Encoder(4, pyb.Pin.board.PB6, pyb.Pin.board.PB7)  # Encoder for Task 2
    motor2 = motor_control.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)  # Motor driver for Task 2
    close2 = closed_loop.ClosedLoopController(0.03, 50000)  # Closed-loop controller for Task 2
    encoder2.zero()  # Zeroing the encoder

    graph_printed = False  # Flag to indicate whether graph has been printed for current trial

    while True:
        iterations2 = 0
        while iterations2 <= 150:
            current_position2 = encoder2.read()
            output2 = close2.run(current_position2)
            motor2.set_duty_cycle(output2)
            iterations2 += 1
            yield 0

        if not graph_printed:
            close2.print_results()
            graph_printed = True  # Set flag to True after printing graph once

        motor2.set_duty_cycle(0)

#----------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")
    
    # Creating shared variables and queue
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False, name="Queue 0")

    # Creating tasks and adding them to task list
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=45,
                        profile=True, trace=False)
    task2 = cotask.Task(task2_fun, name="Task_2", priority=1, period=45,
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

