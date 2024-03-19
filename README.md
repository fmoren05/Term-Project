# Term Project

# Introduction: 

Goal: 

The final turret design will be used to compete in 1v1 battles (called dueling) with other groups to determine who can hit their target first over the span of 5 rounds. 

Customer: 

ME 405 Instructor (Dr. Ridgely)


Brief Overview: 

Our turret design for the ME 405 term project features a dynamic combination of a lazy susan mechanism for horizontal panning and an adjustable firing angle mechanism, complemented by integrated flywheels to assist in launching projectiles. This setup enables autonomous target acquisition, aiming, and firing control on a Nerf™ or similar projectile launcher within the specified dimensional constraints. With safety considerations and adherence to project guidelines in mind, our turret system aims to achieve precise and efficient performance in dueling scenarios. 

# Hardware Design: 

NOTE: All CAD is in this folder: https://github.com/fmoren05/Term-Project/tree/main/cad


KEY COMPONENTS

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
![image](https://github.com/fmoren05/Term-Project/assets/156385954/47345f5e-ff6a-48bf-90e8-84db1d92e567)


Figure 3: Low-side mosfet switch used for flywheel motors. 

![image](https://github.com/fmoren05/Term-Project/assets/156385954/1772b2a8-6f60-4d94-9b0b-320cfb8660c2)


Figure 4: 12V to 6V voltage regulator used for servo trigger motor. 

# State Diagrams of System

Figure 5: Firing sequence state diagram.

Figure 6: Flywheel motor state diagram.

# Discussion of Results:

The system was extensively tested using various test scenarios to evaluate its performance and reliability. Testing involved validating closed-loop motor control under different conditions, such as a moving versus nonmoving target. Furthermore, different movement orientations were considered, such as hands out, facing sideways, and squatting. As a result, we ended up determining the best encoder position based on moving the individual across the table and then plotting the results. From there, we created a position calculation based on where the user was relative to the table, which corresponded to an encoder count range for our panning axis motor. As a result, our system was robust for its environment if the user’s height isn’t below or above our fixed turret height. When recording our tests, it was determined that our turret hit the target about 85% of the time. 

# Lessons Learned & Recommendations:

Several key insights were gained during the turret battle session. We didn’t account for groups to rub their hands together and wave them out right after the 5 second timer was done. As a result, our camera tried to lock on to a target that was too high for our turret to hit despite our panning axis accurately positioning itself to fire the hands. Furthermore, it seemed that some groups would drastically change their position right after they 5 second stop condition which would mess with our hotspot detection code as our program was calibrated to start reading data right after the 5 seconds and then fire. If the person drastically changed orientation right after 5 seconds, our camera may only detect its previous movement during the firing sequence. As a result, if you are planning on creating a turret system, we would recommend having a vertical and horizontal panning axis as well as using a better gear system (such as a utilizing concave flywheel that will grab onto the nerf bullet better and helical gears for the panning axis to allow for better meshing). 

# Additonal Links:
CAD: https://github.com/fmoren05/Term-Project/tree/main/cad

DOXYGEN: https://github.com/fmoren05/Term-Project/tree/main/docs

SRC: https://github.com/fmoren05/Term-Project/tree/main/src





