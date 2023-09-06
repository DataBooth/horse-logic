import time
import sys
import pygame
from datetime import datetime
from pathlib import Path

try:
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
except ImportError:
    RPI_MODE = False
    print("\n**** Running in non-RPi mode for testing only ****\n")

from experiment_helper import create_output_filenames, set_data_dir, log_event

tones = {
    "start": "Start_tone_600.wav",
    "correct": "Correct_tone_1000.wav",
    "end": "End_tone_1200.wav",
}

N_SUBJECT = 20  # Needs to be set to the actual number of subjects (or larger)
N_TRIAL = 10  # Needs to be set to the actual number of trials
N_TOUCH = 3
SENSITIVITY = 5
TOUCH_PAD_DELAY = 0.1
SERVO_DELAY = 0.7
SERVO_DELAY_AFTER_FEED = 3
FEED_DISPENSE = 20

TONES_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/src/tones"  # CH: example only

if not Path(TONES_DIR).exists():
    print(f"\nTones directory not found: {TONES_DIR}\n")
    raise FileExistsError


def initialise_sensors(sensitivity=4, Rpi=False):
    if Rpi:
        # Initialise the sensors
        # buzz = PiicoDev_Buzzer()
        touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=sensitivity)

        # Initialise the servo driver
        servo_driver = PiicoDev_Servo_Driver()

        # Initialise the servo
        servo = PiicoDev_Servo(servo_driver, 1)  # Replace '1' with the appropriate channel for the servo

        # servo = PiicoDev_Servo(servo_driver, 1, min_us=600, max_us=2400, degrees=270)
        return touch_sensor, servo
    else:
        return None, None


def play_wav_file(tone_name, duration_sec, tone_dir=TONES_DIR):
    if not Path(tone_dir).exists():
        # print error and exit
        raise FileNotFoundError
    pygame.mixer.init()
    sound = pygame.mixer.Sound(f"{tone_dir}/{tones[tone_name]}")
    sound.play()
    time.sleep(duration_sec)  # wait for the specified duration (s)
    sound.stop()


def initialise_experiment(subject_number, initial_delay=10):
    data_dir = set_data_dir()
    log_file, measurement_file = create_output_filenames(subject_number)
    log_event(data_dir, log_file, f"Data directory: {data_dir}")
    log_event(data_dir, log_file, f"Log file: {log_file}")
    log_event(data_dir, log_file, f"Measurement file: {measurement_file}")
    return data_dir, log_file, measurement_file, initial_delay


def set_subject_number(N_SUBJECT, N_TRIAL):
    subject_number = 0

    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled in the stall:")
    print(f"   - Commencing the experiment with {N_TRIAL} trials...")

    while subject_number < 1 or subject_number > N_SUBJECT:
        try:
            subject_number = int(input(f"\nEnter subject number (between 1 and {N_SUBJECT}): "))
        except ValueError:
            subject_number = 0
    return subject_number


#### Start of experiment ####

touch_sensor, servo = initialise_sensors(sensitivity=SENSITIVITY, Rpi=RPI_MODE)
subject_number = set_subject_number(N_SUBJECT, N_TRIAL)
data_dir, log_file, measurement_file, initial_delay = initialise_experiment(subject_number)

log_event(data_dir, log_file, "Session started...")

# Initialise key tracking variables

sequence_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Example of logging a measurement quantity

log_event(data_dir, log_file, f"Last touch time: {last_touch_time}", log_as_measurement=True, echo_to_console=False)
log_event(data_dir, log_file, f"Waiting for {initial_delay} seconds before starting the first sequence...")
time.sleep(initial_delay)  # Add the initial delay

# Main loop

try:
    sequence_number = 1  # Initialize the sequence number

    while touch_count < N_TOUCH:  # Adjust the number of touches as needed
        # Print the current sequence number
        log_event(data_dir, log_file, f"Current sequence: {sequence_number}")
        play_wav_file("start", duration_sec=2)
        log_event(data_dir, log_file, "Start tone played")

        while True:
            if not RPI_MODE:
                print("\n**** Exiting non-RPi mode (testing only) ****\n")
                sys.exit()

            # Check if sensor is touched
            if is_touch_active:
                status = touch_sensor.read()

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    log_event(data_dir, log_file, "Touch-pad status read")
                    time.sleep(TOUCH_PAD_DELAY)
                    play_wav_file("correct", duration_sec=2)
                    time.sleep(SERVO_DELAY)

                    # Control the servo motor
                    servo.angle = 180  # Open servo 180 degrees
                    log_event(data_dir, log_file, "Feed dispensed")
                    time.sleep(SERVO_DELAY_AFTER_FEED)  # Delay operation of servo
                    servo.angle = 0  # Close servo

                    start_time = time.time()
                    time.sleep(FEED_DISPENSE)

                    touch_count += 1
                    last_touch_time = time.time()

                    log_event(data_dir, log_file, f"{last_touch_time}", log_as_measurement=True, echo_to_console=False)

                    if touch_count == N_TRIAL:  # Change this number as required for the number of trials ## CHECK THIS number?
                        # Make a different sound after n registered touches
                        play_wav_file("end", duration_sec=3)
                        touch_count = 0  # Reset touch count after the session ends - ## CHECK: Probs not needed
                        log_event(data_dir, log_file, "Session ended")
                        sys.exit()  # Terminate the script
                    break

        sequence_number += 1  # Increment the sequence number ## CHECK: Get sequence/trial language consistent

except KeyboardInterrupt:
    log_event(data_dir, log_file, "Keyboard interrupt - exiting...")
    if RPI_MODE:
        servo.release()  # Release the servo motor
