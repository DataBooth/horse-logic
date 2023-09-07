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

from experiment_helper import create_output_filenames, set_directory, log_event

tones = {
    "start": "Start_tone_600.wav",
    "correct": "Correct_tone_1000.wav",
    "end": "End_tone_1200.wav",
}

N_SUBJECT = 20  # Needs to be set to the actual number of subjects (or larger)
N_TRIAL = 10  # Needs to be set to the actual number of trials

# CH: Do we need the following quantities or similar?
MAX_TIME_TRIAL_SECONDS = 2 * 60.0
MAX_N_OBSERVATION = 30

N_TOUCH = 3
SENSITIVITY = 5
SENSITIVITY_MIN = 1  # CH: Check the min and max allowed values (good way to check you using a valid value)
SENSITIVITY_MAX = 6
TOUCH_PAD_DELAY = 0.1

SERVO_CHANNEL = 1
SERVO_OPEN = 180  # Open servo 180 degrees
SERVO_CLOSE = 0  # Close servo
SERVO_DELAY = 0.7
SERVO_DELAY_AFTER_FEED = 3
FEED_DISPENSE = 20

# Specify the paths for the data directory and the tones directory.

DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded example only
TONE_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/src/tones"  # CH: example only


def initialise_touch_sensor(sensitivity):
    """
    Initialises the touch sensor based on the given sensitivity level.

    Args:
        sensitivity (int): The sensitivity level of the touch sensor.

    Returns:
        PiicoDev_CAP1203: The initialised touch sensor object.
    """
    if sensitivity < SENSITIVITY_MIN or sensitivity > SENSITIVITY_MAX:
        raise ValueError(f"Invalid sensitivity level. Sensitivity must be between {SENSITIVITY_MIN} and {SENSITIVITY_MAX}.")

    touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=sensitivity)
    return touch_sensor


def initialise_servo(servo_channel=SERVO_CHANNEL):
    """
    Initialises a servo motor.

    Args:
        servo_channel (int, optional): The channel number of the servo motor. Default is SERVO_CHANNEL.

    Returns:
        PiicoDev_Servo: The initialised servo motor object.
    """
    servo_driver = PiicoDev_Servo_Driver()
    servo = PiicoDev_Servo(servo_driver, servo_channel)
    return servo


def initialise_sensors(sensitivity=4, Rpi=False):
    """
    Initialises the sensors based on the given parameters.

    Args:
        sensitivity (int, optional): The sensitivity level of the touch sensor. Default is 4.
        Rpi (bool, optional): A boolean flag indicating whether the code is running on a Raspberry Pi. Default is False.

    Returns:
        tuple: A tuple containing the initialised touch sensor and servo objects.

    Example:
        touch_sensor, servo = initialise_sensors(sensitivity=4, Rpi=True)

    """
    if Rpi:
        touch_sensor = initialise_touch_sensor(sensitivity)
        servo = initialise_servo(SERVO_CHANNEL)
        return touch_sensor, servo
    else:
        return None, None


def play_wav_file(tone_name, duration_sec, tone_dir):
    """
    Play a WAV file with a specified tone name, duration, and tone directory.

    Args:
        tone_name (str): The name of the tone to be played. See the `tones` dictionary for the available tones.
        duration_sec (float): The duration of the tone in seconds.
        tone_dir (str): The directory where the WAV files are located.

    Raises:
        FileNotFoundError: If the specified tone directory does not exist.

    Returns:
        None. The function does not return any value.
    """
    if not Path(tone_dir).exists():
        # print error and exit
        raise FileNotFoundError(f"The specified tone directory {tone_dir} does not exist.")
    sound = pygame.mixer.Sound(f"{tone_dir}/{tones[tone_name]}")
    sound.play()
    time.sleep(duration_sec)  # wait for the specified duration (s)
    sound.stop()


def initialise_experiment(subject_number, initial_delay=10):
    """
    Initialises the experiment by creating directories, generating output filenames, and logging important information.

    Args:
        subject_number (int): The number of the subject for which the experiment is being initialised.
        initial_delay (int, optional): The initial delay in seconds before the experiment starts. Default is 10 seconds.

    Returns:
        tuple: A tuple containing the following elements:
            - data_dir (str): The path to the data directory.
            - tone_dir (str): The path to the tone directory.
            - log_file (str): The name of the log file.
            - measurement_file (str): The name of the measurement file.
            - initial_delay (int): The initial delay in seconds before the experiment starts.
    """
    data_dir = set_directory(DATA_DIR)
    tone_dir = set_directory(TONE_DIR)
    log_file, measurement_file = create_output_filenames(subject_number)
    log_event(data_dir, log_file, f"Data directory: {data_dir}")
    log_event(data_dir, log_file, f"Log file: {log_file}")
    log_event(data_dir, log_file, f"Measurement file: {measurement_file}")
    return data_dir, tone_dir, log_file, measurement_file, initial_delay


# CH: Do we also want to allow/record the Session number (for each subject)?
def set_subject_number(N_SUBJECT, N_TRIAL):
    """
    Prompts the user to enter a subject number between 1 and N_SUBJECT.

    Args:
        N_SUBJECT (int): The maximum number of subjects.
        N_TRIAL (int): The number of trials.

    Returns:
        int: The selected subject number within the valid range.

    Example Usage:
        N_SUBJECT = 10
        N_TRIAL = 5
        subject_number = set_subject_number(N_SUBJECT, N_TRIAL)
        print(f"Selected subject number: {subject_number}")

    """
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

pygame.mixer.init()  # Initialise the mixer module for playing WAV files
touch_sensor, servo = initialise_sensors(sensitivity=SENSITIVITY, Rpi=RPI_MODE)
subject_number = set_subject_number(N_SUBJECT, N_TRIAL)
data_dir, tone_dir, log_file, measurement_file, initial_delay = initialise_experiment(subject_number)

log_event(data_dir, log_file, "Session started...")

# Initialise key tracking variables

sequence_count = 0
touch_count = 0
last_touch_time = time.time()
is_touch_active = True

# Example of logging a measurement quantity

log_event(
    data_dir,
    log_file,
    f"Last touch time: {last_touch_time}",
    log_as_measurement=True,
    echo_to_console=False,
)

log_event(
    data_dir,
    log_file,
    f"Waiting for {initial_delay} seconds before starting the first sequence...",
)

# Wait for button press to start the experiment

# TODO: Check if button is pressed - something like this:
# while not button.is_pressed():
#    pass


time.sleep(initial_delay)  # Add the initial delay

# Main loop

try:
    sequence_number = 1  # Initialise the sequence number
    is_button_pressed = False

    while touch_count < N_TOUCH and not is_button_pressed:  # Adjust the number of touches as needed
        # Print the current sequence number
        log_event(data_dir, log_file, f"Current sequence: {sequence_number}")
        play_wav_file("start", duration_sec=2, tone_dir=tone_dir)
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
                    play_wav_file("correct", duration_sec=2, tone_dir=tone_dir)
                    time.sleep(SERVO_DELAY)

                    # Control the servo motor
                    servo.angle = SERVO_OPEN
                    log_event(data_dir, log_file, "Feed dispensed")
                    time.sleep(SERVO_DELAY_AFTER_FEED)  # Delay operation of servo
                    servo.angle = SERVO_CLOSE

                    start_time = time.time()
                    time.sleep(FEED_DISPENSE)

                    touch_count += 1
                    last_touch_time = time.time()

                    log_event(
                        data_dir,
                        log_file,
                        f"{last_touch_time}",
                        log_as_measurement=True,
                        echo_to_console=False,
                    )

                    # TODO: Check if button is pressed - something like this:
                    # is_button_pressed = button.is_pressed()

                    if (
                        touch_count == N_TRIAL
                    ):  # CH: Change this number as required for the number of trials ## CHECK THIS number? Should this be N_TOUCH?
                        # Make a different sound after n registered touches
                        play_wav_file("end", duration_sec=3, tone_dir=tone_dir)
                        touch_count = 0  # CH: Reset touch count after the session ends -- probs not needed - reset each time at start of loop
                        log_event(data_dir, log_file, "Session ended")
                        sys.exit()  # Terminate the script
                    break

        sequence_number += 1  # Increment the sequence number ## CHECK: Get sequence/trial language consistent

except KeyboardInterrupt:
    log_event(data_dir, log_file, "Keyboard interrupt - exiting...")
    if RPI_MODE:
        servo.release()
