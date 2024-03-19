# Term Project
Introduction: 

Our turret design for the ME 405 term project features a dynamic combination of a lazy susan mechanism for horizontal panning and an adjustable firing angle mechanism, complemented by integrated flywheels to assist in launching projectiles. This setup enables autonomous target acquisition, aiming, and firing control on a Nerf™ or similar projectile launcher within the specified dimensional constraints. With safety considerations and adherence to project guidelines in mind, our turret system aims to achieve precise and efficient performance in dueling scenarios. As a result, this final turret design will be used to compete in 1v1 battles with other groups to determine who can hit their target first over the span of 5 rounds. 

# Hardware Design: 

KEY COMPONENTS

Microcontroller: STM32L476RG Nucelo (From Lab, Quantity: 1)

Motor Drivers: Lab Encoder Motors (Used For Panning Axis, Quantity: 1)

Servo Drivers: S51 Servo (Used As Trigger, Quantity: 1)

DC Motors: Gikfun 1.5V-6V EK1450 (Used As Flywheels, Quantity: 2)

Lazy Susan: (Used For Panning Axis, Quantity: 1)

Nerf Fortnite Maganize: (Used To Hold Nerf Bullets, Quantity: 1)

Gears+Housing: (Used 3D Printed Parts from ENDER 3)


Sensors: May include additional sensors for environment monitoring or feedback, depending on the application requirements.
Peripheral Devices: Interfaces with peripheral devices such as cameras, temperature sensors, or other actuators for expanded functionality.

![image](https://github.com/fmoren05/Term-Project/assets/132640536/ce465a27-afd6-463f-9f4d-bb921be6ea81)
Figure 1: General CAD overview of system. Note that there is a horizontal panning axis and flywheel components. 

![servo](https://github.com/fmoren05/Term-Project/assets/156385954/ded17ace-ae5a-4ab5-a130-a17aa628b9eb)
Figure 2: Firing sequence schematic of system. Note that the servo trigger will push the nerf bullet into the flywheels.

# Software Design:


