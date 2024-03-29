# ME 405 Term Project, Group 14

# Introduction: 

### Goal: 

The final turret design will be used to compete in 1v1 battles (called dueling) with other groups to determine who can hit their target first over the span of 5 rounds. 

### Customer: 

ME 405 Instructor (Dr. Ridgely)


### Brief Overview: 

Our turret design for the ME 405 term project features a dynamic combination of a lazy susan mechanism for horizontal panning and an adjustable firing angle mechanism, complemented by integrated flywheels to assist in launching projectiles. This setup enables autonomous target acquisition, aiming, and firing control on a Nerf™ or similar projectile launcher within the specified dimensional constraints. With safety considerations and adherence to project guidelines in mind, our turret system aims to achieve precise and efficient performance in dueling scenarios. 

### Functionality:

Our final product was able to locate its target using the IR camera, rotate the turret to target using the encoder motors, and shoot the target using the servo trigger and flywheels within the span of approximately 5.25 seconds. 

# Hardware Design: 

NOTE: All CAD is in this folder: https://github.com/fmoren05/Term-Project/tree/main/cad


### KEY COMPONENTS

Microcontroller: STM32L476RG Nucelo (From Lab, Quantity: 1)

Motor Drivers: Lab Encoder Motors (Used For Panning Axis, Quantity: 1)

Servo Drivers: S51 Servo (Used As Trigger, Quantity: 1)

DC Motors: Gikfun 1.5V-6V EK1450 (Used As Flywheels, Quantity: 2)

Lazy Susan: (Used For Panning Axis, Quantity: 1)

Nerf Fortnite Maganize: (Used To Hold Nerf Bullets, Quantity: 1)

Gears+Housing: (Used 3D Printed Parts from ENDER 3)

MLX Thermal Camera: (Used To Find Target, Quantity: 1)

![image](https://github.com/fmoren05/Term-Project/assets/132640536/ce465a27-afd6-463f-9f4d-bb921be6ea81)

Figure 1: General CAD overview of system. Note that there is a horizontal panning axis and flywheel components. 

![servo](https://github.com/fmoren05/Term-Project/assets/156385954/ded17ace-ae5a-4ab5-a130-a17aa628b9eb)

Figure 2: Firing sequence schematic of system. Note that the servo trigger will push the nerf bullet into the flywheels.

# Software Design:

Our software was written using Micropython via Thonny. The software consisted of files pertaining to motor control, PID control, MLX to encoder processing, servo triggering, flywheel activation, and cotasking via main. There are multiple main files for our project to demonstrate our progress throughout. Our first main did not implement cotasking, whereas our cotasking main did. Our final attempt at improving our working cotasking main failed cotasking due to running into unforseen debugging issues by the time of dueling. The regular main without cotasking and the cotasking main both work. As a result, we have all three mains available for the user to look at in case they want to recreate our turret.

Software Link: https://fmoren05.github.io/Term-Project/

# Electronic Design: 

Our electronic design is displayed below along with depictions of the special circuitry used. Special circuitry included a 12V to 6V voltage regulator as well as a low side MOSFET switch. The panning axis motor used was the one provided for the lab, so it was connected as instructed. We decided to use the B channel pins for the encoder, so we used PC1 for the EN_B, PA0 for IN1_B, and PA1 for IN2_B. The motor voltage wires were also hooked up to the positive and negative B terminals on the motor driver. The motor driver itself was powered by the voltage supply set to 12V with a current limit of 0.5A. The MLX camera was powered by the 3v3 supply and it utilized the SDA and SCL pins on the shoe. Our servo motor utilized the 6V output from the voltage regulator, and it was connected to Pin B6 ont the microconroller. The MOSFET switch utilized Pin C0, and it would regualte between high and low in order to allow for the passing of current to the flywheel motors. Our E-stop for the system was a two input switch, capable of cutting off the 12V supply to the sytem as well as the voltage supply to the flywheel motors.

![image](https://github.com/fmoren05/Term-Project/assets/156385954/c50f1105-7ef4-47a1-808b-d7fd96c1f143)

Figure 3: Overall Circuit Diagram of System.

![image](https://github.com/fmoren05/Term-Project/assets/156385954/2e7ecd68-8abd-45ad-a0a7-47c0372085f3)


Figure 4: Low-side MOSFET switch used for flywheel motors diagram. 

![image](https://github.com/fmoren05/Term-Project/assets/156385954/1772b2a8-6f60-4d94-9b0b-320cfb8660c2)

Figure 5: 12V to 6V voltage regulator used for servo trigger motor diagram. Circuit image of MOSFET switch

![image](https://github.com/fmoren05/Term-Project/assets/156385950/1119cf7a-1b49-49d4-b11a-c1ffc9c627db)


Figure 6: Circuit image of MOSFET switch

![image](https://github.com/fmoren05/Term-Project/assets/156385950/abb3c800-195e-4659-8604-1710b4cc8944)


Figure 7: Circuit image of voltage regulator

# State Diagrams of System

The state diagrams below illustrate what is going on with our main_cotasking.py file. Figure 6 shows the sequence of states that the firing sequence task undergoes as it runs simultaneously with the
flywheel motor task depicted in Figure 7.

![Firing_Secuence_State_Diagram](https://github.com/fmoren05/Term-Project/assets/156385950/790e4b55-d850-4f88-a7ff-82202f48e91a)


Figure 6: Firing sequence state diagram.


![Flywheel_Motors_State_Diagram drawio](https://github.com/fmoren05/Term-Project/assets/156385950/4ea4958a-5ad5-4e95-94c0-718d582fd607)

Figure 7: Flywheel motor state diagram.

# Discussion of Results:

The system was extensively tested using various test scenarios to evaluate its performance and reliability. Testing involved validating closed-loop motor control under different conditions, such as a moving versus nonmoving target. Furthermore, different movement orientations were considered, such as hands out, facing sideways, and squatting. As a result, we ended up determining the best encoder position based on moving the individual across the table and then plotting the results. From there, we created a position calculation based on where the user was relative to the table, which corresponded to an encoder count range for our panning axis motor. As a result, our system was robust for its environment if the user’s height isn’t below or above our fixed turret height. When recording our tests, it was determined that our turret hit the target about 85% of the time. 


![image](https://github.com/fmoren05/Term-Project/assets/156385950/10583b70-88eb-4af6-abf7-cfdb28595a79)


Figure 8: Final system design.


# Lessons Learned & Recommendations:

Several key insights were gained during the turret battle session. We didn’t account for groups to rub their hands together and wave them out right after the 5 second timer was done. As a result, our camera tried to lock on to a target that was too high for our turret to hit despite our panning axis accurately positioning itself to fire the hands. Furthermore, it seemed that some groups would drastically change their position right after they 5 second stop condition which would mess with our hotspot detection code as our program was calibrated to start reading data right after the 5 seconds and then fire. If the person drastically changed orientation right after 5 seconds, our camera may only detect its previous movement during the firing sequence. As a result, if you are planning on creating a turret system, we would recommend having a vertical and horizontal panning axis as well as using a better gear system (such as a utilizing concave flywheel that will grab onto the nerf bullet better and helical gears for the panning axis to allow for better meshing). 

# Additonal Links:
### CAD: https://github.com/fmoren05/Term-Project/tree/main/cad

### DOXYGEN: https://fmoren05.github.io/Term-Project/

### SRC: https://github.com/fmoren05/Term-Project/tree/main/src





