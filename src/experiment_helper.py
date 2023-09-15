from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
import time
import pygame
import sys
import pprint

try:
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
    import RPi.GPIO as GPIO
except ImportError:
    RPI_MODE = False
    print("\n**** Running in non-RPi mode for testing only ****\n")


DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded example only


def initialise_directories():
    """
    Initialises the data and tone directories.

    Returns:
    - data_dir: The initialised data directory
    """
    data_dir = set_directory(DATA_DIR)
    return data_dir


# Define Servo objects for different types of feed. Can adjust the angles and times if needed
class Servo_pellets:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_pellets(self):
        self.servo.angle = 80
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)
        self.servo.angle = 0


class Servo_grain:
    def __init__(self, servo):
        self.servo = servo

    def dispense_feed_grain(self):
        self.servo.angle = 70
        print(f"Feed dispensed at: {datetime.now()}")
        time.sleep(0.5)
        self.servo.angle = 0


class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return GPIO.input(self.pin) == GPIO.LOW


def initialise_GPIO_buttons(RPi=RPI_MODE):
    if RPi:
        # Set up GPIO pins for buttons

        GPIO.setmode(GPIO.BCM)
        butpin_green = 6  # Green button
        butpin_blue = 7  # Blue button
        butpin_red = 12  # Red button

        # Set up GPIO pins for input with an internal pull-up resistor

        GPIO.setup(butpin_green, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(butpin_blue, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(butpin_red, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        green_button = Button(butpin_green)
        blue_button = Button(butpin_blue)
        red_button = Button(butpin_red)
        return GPIO, green_button, blue_button, red_button
    else:
        return None, None, None, None


# need a description of what this is?
def elapsed_seconds(start_time):
    delta_since_start = datetime.now() - start_time
    duration_since_start = delta_since_start.total_seconds()
    return duration_since_start


def listenForPause(red_button, logTouches, blue_button, touchSensor, trialPausedWav, trialRestartedWav):
    if red_button.is_pressed():
        pauseTime = datetime.now()
        # Process pause
        print(f"Process paused at: {datetime.now()}, Session paused")
        play_WAV(trialPausedWav, 1)
        while True:
            if red_button.is_pressed():
                print(f"Process resumed at: {datetime.now()}, Session resumed")
                play_WAV(trialRestartedWav, 1)
                return timedelta(0, elapsed_seconds(pauseTime))
    if logTouches:
        if blue_button.is_pressed():
            print(f"Manual touch recorded during sleep at: {datetime.now()}, Session under manual control")
            time.sleep(0.5)
        status = touchSensor.read()
        if status[1] > 0 or status[2] > 0 or status[3] > 0:
            print(f"Touch-pad status read during sleep at: {datetime.now()}")
            time.sleep(0.5)
    return timedelta(0, 0)


# need a description of what this is and what it does?
def pausable_sleep(duration_seconds, logTouches):
    start_time = datetime.now()
    elapsed = elapsed_seconds(start_time)
    while elapsed < duration_seconds:
        listenForPause(logTouches)
        elapsed = elapsed_seconds(start_time)
    return timedelta(0, elapsed)


# Function to play WAV file for a specified duration
def play_WAV(file_path, duration):
    sound = pygame.mixer.Sound(file_path)
    sound.play()
    pygame.time.delay(int(duration * 1000))
    time.sleep(duration)
    sound.stop()


def initialise_touch_sensor(sensitivity):
    """
    Initialises the touch sensor based on the given sensitivity level.

    Args:
        sensitivity (int): The sensitivity level of the touch sensor.

    Returns:
        PiicoDev_CAP1203: The initialised touch sensor object.
    """
    touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=sensitivity)
    return touch_sensor


def initialise_servo(servo_channel):
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


def initialise_sensors(sensitivity, servo_channel, RPi=RPI_MODE):
    """
    Initialises the sensors based on the given parameters.

    Args:
        sensitivity (int, optional): The sensitivity level of the touch sensor. Default is 4.
        RPi (bool, optional): A boolean flag indicating whether the code is running on a Raspberry Pi. Default is False.

    Returns:
        tuple: A tuple containing the initialised touch sensor and servo objects.

    Example:
        touch_sensor, servo = initialise_sensors(sensitivity=4, RPi=True)

    """
    if RPi:
        touch_sensor = initialise_touch_sensor(sensitivity)
        servo = initialise_servo(servo_channel)
        return touch_sensor, servo
    else:
        return None, None


def set_directory(dir_name):
    """
    Check if a directory with the given name exists.

    Args:
        dir_name (str or Path): The name or path of the directory to be checked.

    Raises:
        TypeError: If dir_name is not a string or a Path object.
        FileNotFoundError: If the directory doesn't exist.

    Example:
        set_directory('my_directory')
        In this example, the function is called with the directory name 'my_directory'.
        If the directory doesn't exist, a FileNotFoundError exception will be raised.
    """
    if not isinstance(dir_name, (str, Path)):
        raise TypeError("dir_name must be a string or a Path object.")
    if not Path(dir_name).exists():
        raise FileNotFoundError(f"The specified directory {dir_name} does not exist.")
    return Path(dir_name)


def create_output_filenames(subject_name, session_number, session_type):
    """
    Generate output filenames for an experiment log file and a data file.

    Args:
        subject_number (int): The number of the subject for which the filenames are being created.

    Returns:
        tuple: A tuple containing the log filename and the data filename, both based on the current date and time, and the subject number.

    Example:
        filenames = create_output_filenames(10)
        print(filenames)
        # Output: ('Experiment_2022-01-01T12:00:00_Subject_10.log', 'Experiment_2022-01-01T12:00:00_Subject_10.dat')
    """
    LOGFILE_PREFIX = "Experiment"
    file_name = f"{LOGFILE_PREFIX}_{datetime.now().isoformat()}_{subject_name}_{session_number}_{session_type}"
    return f"{file_name}.log", f"{file_name}.dat"


def log_event(
    event_name,
    data_dir,
    log_file,
    log_as_measurement=False,
    event_time=None,
    echo_to_console=True,
):
    """
    Log the event name and time to a file.

    Args:
        data_dir (str): The directory where the log/measurement file(s) will be stored.
        log_file (str): The name of the log file. The measurement file will have the same name, but with a .dat extension.
        event_name (str): The name/text of the event to be logged.
        log_as_measurement (bool, optional): If True, the event will also be logged as a measurement in a separate file. Default is False.
        event_time (str, optional): The timestamp of the event. If not provided, the current timestamp will be used.
        echo_to_console (bool, optional): If True, the log will be echoed to the console. Default is True.

    Returns:
        None

    Example:
        log_event("data", "log.txt", "Event 1")
        This example logs "Event 1" with the current timestamp to the file "log.txt" in the "data" directory.
    """

    if not Path(data_dir).exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    if event_time is None:
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(Path(data_dir) / log_file, "a") as flog:
        flog.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    if log_as_measurement:
        measurement_file = log_file.replace(".log", ".dat")
        with open(Path(data_dir) / measurement_file, "a") as f:
            f.write(f"{event_time}: {event_name}\n")
    return None


def log_trial_parameters(parameters, data_dir, log_file):
    pformatted = pprint.pformat(parameters)
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"PARAMETERS:\n{pformatted}\n")
    print(f"Logged - PARAMETERS:\n{pformatted}\n")
    return None


def set_subject_name(data_dir):
    subject_name = False
    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled and ready for the experiment\n")

    while not subject_name:
        subject_name_in = input("\nEnter subject name: ")
        subject_name, next_session_number, experiment_subjects_df = get_next_session_number(subject_name_in, data_dir)
    return subject_name, next_session_number, experiment_subjects_df


def get_next_session_number(subject_name, data_dir, subjects_file="experiment_subjects.xlsx"):
    if not (Path(data_dir) / subjects_file).exists():
        raise FileNotFoundError(f"Tracking file {Path(data_dir) / subjects_file} does not exist.")
    # Read in the tracking file
    experiment_subjects_df = pd.read_excel(Path(data_dir) / subjects_file)
    experiment_subjects_df["subject_name_clean"] = experiment_subjects_df["subject_name"].apply(
        lambda name: name.lower().replace(" ", "")
    )
    subject_names = [name.lower() for name in experiment_subjects_df["subject_name"].values.tolist()]
    # Amend to allow for subject names with spaces
    subject_names = [name.replace(" ", "") for name in subject_names]
    if subject_name.lower().replace(" ", "") not in subject_names:
        print(f"Subject {subject_name} not found in tracking file.\nSee {(Path(data_dir) / subjects_file).as_posix()}.")
        return False, 0
    next_session_number = (
        experiment_subjects_df[
            experiment_subjects_df["subject_name_clean"].str.contains(subject_name.lower().replace(" ", ""), case=False)
        ]["last_session_number"].values[0]
        + 1
    )
    experiment_subjects_df.loc[
        experiment_subjects_df["subject_name_clean"].str.contains(subject_name.lower().replace(" ", ""), case=False),
        "last_session_number",
    ] = next_session_number
    return subject_name, next_session_number, experiment_subjects_df


def update_subjects_xlsx(data_dir, experiment_subjects_df, subjects_file):
    experiment_subjects_df.drop(columns=["subject_name_clean"], inplace=True)
    experiment_subjects_df.to_excel(Path(data_dir) / subjects_file, index=False)
    return None


def choose_session_type():
    """
    Allows the user to select an session type from a predefined list.

    Returns:
        str: The selected session type.

    Example Usage:
        Choose session type:
        1 - RPE-A
        2 - RPE-H
        3 - RPE-E
        4 - RPE-R

        Enter session type: 2

        Output: "RPE-H"
    """
    session_types = ["RPE-A", "RPE-H", "RPE-E", "RPE-R"]
    session_choice = 0
    print("\nChoose session type:")
    for i, session_type in enumerate(session_types):
        print(f"{i+1} - {session_type}")
    while session_choice < 1 or session_choice > len(session_types):
        try:
            session_choice = int(input("\nEnter session type: "))
        except ValueError:
            session_choice = 0
    session_type = session_types[session_choice - 1]
    print()
    return session_type


def confirm_experiment_details(subject_name, session_number, session_type):
    """
    Confirms the experiment details with the user.

    Args:
        subject_name (str): The name of the subject.
        session_number (int): The session number.
        session_type (str): The type of experiment.

    Returns:
        True if the user confirms the experiment details are correct, False otherwise.
    """
    print(f"\nSubject name: {subject_name}")
    print(f"Session number: {session_number}")
    print(f"Experiment type: {session_type}")
    confirm = input("\nAre the details ok for this session (Y - continue / N - exit)?: ")
    if confirm == "" or confirm.lower()[0] == "y":
        return True
    else:
        return False


@dataclass
class Parameter:
    name: str
    val: float
    unit: str
    minimum_value: float
    maximum_value: float
    description: str


def parse_text_for_na(value):
    if pd.isna(value):
        return ""
    else:
        return value


def get_parameter(name, experiment_parameters_df):
    row = experiment_parameters_df.loc[experiment_parameters_df["name"] == name]
    if row.drop(columns=["name"]).isnull().values.all():
        return None
    return Parameter(
        name=name,
        val=row["value"].values[0],
        minimum_value=row["minimum_value"].values[0],
        maximum_value=row["maximum_value"].values[0],
        unit=parse_text_for_na(row["unit"].values[0]),
        description=parse_text_for_na(row["description"].values[0]),
    )


def load_validate_experiment_parameters(data_dir, parameters_xlsx="experiment_parameters.xlsx"):
    if not Path(data_dir / parameters_xlsx).exists():
        raise FileNotFoundError(f"{parameters_xlsx} does not exist")
    experiment_parameters_df = pd.read_excel(Path(data_dir / parameters_xlsx))
    par = {}
    for name in experiment_parameters_df["name"]:
        parameter = get_parameter(name, experiment_parameters_df)
        if parameter is not None:
            # check if parameter is numeric
            if isinstance(parameter.val, (int, float)):
                if parameter.val < parameter.minimum_value or parameter.val > parameter.maximum_value:
                    print(f"{parameter.name} is out of range: {parameter.val} {parameter.unit}")
                print(f"{parameter.name}: {parameter.val} {parameter.unit} - Validated")
            else:
                print(f"{parameter.name} is not numeric: {parameter.val}")
            par[name] = parameter.val
    return par


def setup_experiment(data_dir=DATA_DIR):
    pygame.mixer.init()  # Initialise the mixer module for playing WAV files
    data_dir = initialise_directories()
    p = load_validate_experiment_parameters(data_dir)
    touchSensor, servo = initialise_sensors(p["SENSITIVITY"], p["SERVO_CHANNEL"])
    subject_name, session_number, experiment_subjects_df = set_subject_name(data_dir)
    session_type = choose_session_type()
    if not confirm_experiment_details(subject_name, session_number, session_type):
        # TODO: Only write update to session number if confirmed
        sys.exit()
        # Update the tracking file with the next session number for the given subject (subject_name)
    update_subjects_xlsx(data_dir, experiment_subjects_df, subjects_file="experiment_subjects.xlsx")
    log_file, measurement_file = create_output_filenames(subject_name, session_number, session_type)
    log_trial_parameters(p, data_dir, log_file)
    log_event(f"Data directory: {data_dir}", data_dir, log_file)
    log_event(f"Log file: {log_file}", data_dir, log_file)
    log_event(f"Measurement file: {measurement_file}", data_dir, log_file)
    log_event(f"Subject {subject_name} - Session {session_number} started...", data_dir, log_file)
    return subject_name, session_number, session_type, p, touchSensor, servo, data_dir, log_file, measurement_file
