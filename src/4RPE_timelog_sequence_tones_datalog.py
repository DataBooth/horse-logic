import time
import sys
import pygame
from datetime import datetime

try:
    # from PiicoDev_Buzzer import PiicoDev_Buzzer
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
    from PiicoDev_Unified import sleep_ms
except ImportError:
    RPI_MODE = False

from experiment_helper import create_output_filenames, set_data_dir, log_event

tones = {
    "start": "/home/horselogic/Documents/test audio project_data/Start tone _600.wav",
    "correct": "/home/horselogic/Documents/test audio project_data/Correct tone_1000.wav",
    "end": "/home/horselogic/Documents/test audio project_data/End tone_1200.wav",
}

N_SUBJECT = 20  # Needs to be set to the actual number of subjects (or larger)
N_TRIAL = 10  # Needs to be set to the actual number of trials


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


def play_wav_file(file_path, duration):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

    # wait for the specified duration (s)
    time.sleep(duration)

    # silence the tone
    sound.stop()

    # pygame.mixer.music.load(file_path) #OLD-worked
    # pygame.mixer.music.play() OLD-worked

    # wait for the music to finish playing OLD worked
    # while pygame.mixer.music.get_busy():
    # time.sleep(0.1)


def initialise_experiment(subject_number, initial_delay=10):
    data_dir = set_data_dir()
    log_file, measurement_file = create_output_filenames(subject_number)

    log_event(data_dir, log_file, f"Data directory is: {data_dir}")
    log_event(data_dir, log_file, f"Log file is: {log_file}")
    log_event(data_dir, log_file, f"Measurement file is: {measurement_file}")

    # Print session started at date/time
    log_event(data_dir, log_file, f"Session started at: {datetime.now()}")
    return data_dir, log_file, measurement_file, initial_delay


### Start of experiment

touch_sensor, servo = initialise_sensors(Rpi=RPI_MODE)

if not RPI_MODE:
    print("Running in non-Rpi mode for testing only")


# Initialise key tracking variables
subject_number = 0
sequence_count = 0  # Initialise the sequence count
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

## TODO: Need to allow setting the subject number - interactive?

print("\nStarting experiment:")
print("\n  Press Ctrl-C to exit the experiment\n")
print("  Ensure the subject is settled in the stall:")
print(f"   - Commencing the experiment with {N_TRIAL} trials...")

while subject_number < 1 or subject_number > N_SUBJECT:
    try:
        subject_number = int(input(f"\nEnter subject number (between 1 and {N_SUBJECT}): "))
    except ValueError:
        subject_number = 0

data_dir, log_file, measurement_file, initial_delay = initialise_experiment(subject_number=1)

# Initial delay before the first sequence (in seconds)
initial_delay = initial_delay

log_event(data_dir, log_file, f"Waiting for {initial_delay} seconds before starting the first sequence...")
time.sleep(initial_delay)  # Add the initial delay

# Main loop

try:
    sequence_number = 1  # Initialize the sequence number

    while touch_count < 3:  # Adjust the number of touches as needed
        # Print the current sequence number
        print(f"Current sequence: {sequence_number}")

        # Play start tone buzzer
        # buzz.tone(1000, 2000)  # Start the start tone
        # time.sleep(2)  # Delay for 2 seconds
        # buzz.noTone()  # Stop the start tone
        # start_time = datetime.now()

        # play start tone mp3
        play_wav_file(tone_paths[0], 2)
        # time.sleep(2) # play tone for 2s
        print(f"Start tone played at: {datetime.now()}")

        while True:
            # Check if sensor is touched
            if is_touch_active:
                status = touch_sensor.read()

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    print(f"Touch-pad status read at: {datetime.now()}")
                    sleep_ms(100)

                if status[1] > 0 or status[2] > 0 or status[3] > 0:
                    # Make the buzzer sound for a maximum of 2 seconds
                    # buzz.tone(800, 2000)  # Start the buzzer tone
                    play_wav_file(tone_paths[1], 2)  # play correct tone for 2 s
                    # time.sleep(2) # play correct tone for 2s
                    time.sleep(3)  # Delay operation of servo for 3 seconds

                    # Control the servo motor
                    servo.angle = 180  # Open servo 180 degrees
                    print(f"Feed dispensed at: {datetime.now()}")
                    time.sleep(0.7)  # Delay for 1 second for operation of servo
                    servo.angle = 0  # Close servo

                    start_time = time.time()
                    sleep_ms(20000)  # Delay for feed dispense and consumption

                    touch_count += 1
                    last_touch_time = time.time()

                    if touch_count == 10:  # Change this number as required for the number of trials
                        # Make a different sound after n registered touches
                        # buzz.tone(1200, 500)  # Start the different buzzer tone
                        # time.sleep(0.5)
                        # buzz.noTone()  # Stop the different buzzer tone
                        play_wav_file(tone_paths[2], 3)  # play end of session tone for 3 s
                        # time.sleep(3) #play end of session tone for 3s)
                        touch_count = 0  # Reset touch count after the session ends
                        print(f"Session ended at: {datetime.now()}")
                        # Terminate the script
                        sys.exit()

                    break

        sequence_number += 1  # Increment the sequence number

except KeyboardInterrupt:
    # buzz.noTone()  # Stop the buzzer if the program is interrupted
    servo.release()  # Release the servo motor
