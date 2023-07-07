# Key package information for hardware components

## pigpio - PI General Purpose Input Outputs (GPIO)

# https://github.com/joan2937/pigpio
# http://abyz.me.uk/rpi/pigpio/python.html
# http://abyz.me.uk/rpi/pigpio/examples.html#Python%20code

## PiicoDev® Capacitive Touch Sensor CAP1203

# https://github.com/CoreElectronics/CE-PiicoDev-Capacitive-Touch-Sensor-CAP1203
# https://core-electronics.com.au/guides/piicodev-capacitive-touch-sensor-cap1203-raspberry-pi-guide/
# https://raw.githubusercontent.com/CoreElectronics/CE-PiicoDev-CAP1203-MicroPython-Module/main/PiicoDev_CAP1203.py

## PiicoDev® Buzzer

# https://core-electronics.com.au/piicodev-buzzer-module.html
# https://github.com/CoreElectronics/CE-PiicoDev-Buzzer-MicroPython-Module

## PiicoDev® Unified library

# https://github.com/CoreElectronics/CE-PiicoDev-Unified
# https://github.com/CoreElectronics/CE-PiicoDev-PyPI


# ---------------------------------------------------------------------------- #

import os
import sys
import time

import pigpio
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_Unified import sleep_ms


# Define key hardware parameters
START_CMD_PI_GPIO_PROCESS = "sudo pigpiod"
TOUCH_SENSITIVITY_LEVEL = 3
SERVO_PIN = 18  # GPIO pin for the servo
SERVO_MIN = 500  # Minimum pulse width for the servo
SERVO_MAX = 2500  # Maximum pulse width for the servo

# Define experiment parameters
N_TRIAL = 5  # Change this number as required for the number of trials

# Start the pigpio daemon
os.system(START_CMD_PI_GPIO_PROCESS)
# TODO: Does this work without specifying an admin password?

# Initialise the sensors
buzzer = PiicoDev_Buzzer()
touchSensor = PiicoDev_CAP1203(touchmode="single", sensitivity=TOUCH_SENSITIVITY_LEVEL)

# Initialise touch sensor variables
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Connect to the local Raspberry Pi GPIO
rpi = pigpio.pi()


# create a servo object
servo = rpi.set_servo_pulsewidth(SERVO_PIN, 0)
# TODO: Note that the servo variable is not used subsequently

# Main loop
try:
    while touch_count < N_TRIAL:
        # Play start tone
        buzzer.tone(1000, 2000)  # Start the start tone
        time.sleep(2)  # Delay for 2 seconds
        buzzer.noTone()  # Stop the start tone

        while True:
            # Check if sensor is touched
            if is_touch_active:
                status = touchSensor.read()
                print(f"Touch Pad Status: {str(status[1])}  {str(status[2])}  {str(status[3])}")
                # TODO: What is in status[0]?
                sleep_ms(100)

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    # Make the buzzer sound for a maximum of 2 seconds
                    buzzer.tone(800, 2000)  # Start the buzzer tone
                    time.sleep(3)  # Delay for 3 seconds

                    # Control the servo motor
                    rpi.set_servo_pulsewidth(SERVO_PIN, SERVO_MAX)  # Move servo to 90 degree position
                    time.sleep(1)  # Delay for 1 second for operation of servo
                    rpi.set_servo_pulsewidth(SERVO_PIN, SERVO_MIN)  # Move servo position back to start

                    start_time = time.time()
                    sleep_ms(5000)  # delay for dispense and consumption of feed- adjust after prototyping with horses

                    touch_count += 1
                    last_touch_time = time.time()

                    if touch_count == N_TRIAL:
                        # Make a different sound after N_TRIAL registered touches
                        buzzer.tone(1200, 500)  # Start the different buzzer tone
                        time.sleep(0.5)
                        buzzer.noTone()  # Stop the different buzzer tone
                        touch_count = 0  # Reset touch count after the session ends

                        # Terminate the script
                        sys.exit()

                    break

except KeyboardInterrupt:
    buzzer.noTone()  # Stop the buzzer if program is interrupted
    rpi.set_servo_pulsewidth(SERVO_PIN, 0)  # Move the servo to the stop position
    rpi.stop()  # Release the servo motor control  #TODO: Check that this is intended and not servo variable?


# TODO: Maybe you want to stop the pigpiod process at the end of each experiment? (security-wise)
