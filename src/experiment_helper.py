import pprint
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import pygame

try:
    import RPi.GPIO as GPIO
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
except ImportError:
    RPI_MODE = False
    print("\n**** Running in non-RPi mode for testing only ****\n")


DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # CH: Hard-coded example only


def initialise_data_dir():
    """
    Initialises the data directory.

    This function initialises the data directory by calling the `set_directory` function
    with the `DATA_DIR` variable as the argument.

    Returns:
        str: The path to the data directory.
    """
    data_dir = set_directory(DATA_DIR)
    return data_dir


# Define Servo objects for different types of feed. Can adjust the angles and times if needed
class Servo_pellets:
    """
    A class that controls a servo motor to dispense feed pellets.

    Attributes:
        servo (object): The servo object used for controlling the servo motor.
    """

    def __init__(self, servo):
        """
        Initialises a Servo_pellets object.

        Args:
            servo (object): The servo object used for controlling the servo motor.
        """
        self.servo = servo

    def dispense_feed_pellets(self):
        """
        Controls the servo motor to dispense feed pellets.

        This method sets the servo angle to 80 degrees to dispense the pellets,
        and then sets it back to 0 degrees to stop the dispensing.
        """
        self.servo.angle = 80
        # print(f"Feed dispensed at: {datetime.now()}") - logging this in the main code
        time.sleep(0.5)
        self.servo.angle = 0


class Servo_grain:
    """
    A class that controls a servo motor to dispense feed grain.

    Args:
        servo: The servo object used for controlling the servo motor.

    Example Usage:
        servo = Servo()
        grain_dispenser = Servo_grain(servo)
        grain_dispenser.dispense_feed_grain()
    """

    def __init__(self, servo):
        """
        Initialises the Servo_grain object with a servo object.

        Args:
            servo: The servo object used for controlling the servo motor.
        """
        self.servo = servo

    def dispense_feed_grain(self):
        """
        Controls the servo motor to dispense feed grain.

        The servo angle is set to 70 degrees to dispense the grain,
        and then set back to 0 degrees to stop the dispensing.
        """
        self.servo.angle = 70
        # print(f"Feed dispensed at: {datetime.now()}") - logging this in the main code
        time.sleep(0.5)
        self.servo.angle = 0


class Button:
    """
    A class representing a button connected to a Raspberry Pi GPIO pin.

    Attributes:
        pin (int): The GPIO pin number to which the button is connected.

    Methods:
        __init__(self, pin):
            Initialises a Button object with the specified GPIO pin. Sets up the GPIO pin as an input with a pull-up resistor.

        is_pressed(self):
            Returns True if the button is pressed (GPIO pin is low), otherwise returns False.
    """

    def __init__(self, pin):
        """
        Initialises a Button object with the specified GPIO pin. Sets up the GPIO pin as an input with a pull-up resistor.

        Args:
            pin (int): The GPIO pin number to which the button is connected.
        """
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        """
        Returns True if the button is pressed (GPIO pin is low), otherwise returns False.
        """
        return GPIO.input(self.pin) == GPIO.LOW


def initialise_GPIO_buttons(RPi=RPI_MODE):
    """
    Initialises GPIO pins for buttons on a Raspberry Pi.

    Args:
        RPi (bool, optional): A boolean indicating whether the code is running on a Raspberry Pi or not.
                              Default is RPI_MODE which is set to False if the RPi.GPIO module is not imported.

    Returns:
        tuple: A tuple containing the GPIO object and instances of the Button class for each button if the code is running on a Raspberry Pi.
               If the code is not running on a Raspberry Pi, it returns None for all the variables.
    """

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
    """
    Calculate the duration in seconds between the current time and a given start time.

    Args:
        start_time (datetime): A datetime object representing the start time.

    Returns:
        float: The duration in seconds between the current time and the start_time.
    """
    delta_since_start = datetime.now() - start_time
    duration_since_start = delta_since_start.total_seconds()
    return duration_since_start


# Function to play WAV file for a specified duration
def play_WAV(file_path, duration):
    """
    Play a WAV audio file for a specified duration.

    Args:
        file_path (str): The path to the WAV audio file.
        duration (float): The duration in seconds for which the audio should be played.

    Returns:
        None

    Example:
        play_WAV('audio.wav', 2)
        This code will play the 'audio.wav' file for 2 seconds.
    """
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
        servo_channel (int, optional): The channel number of the servo motor.

    Returns:
        PiicoDev_Servo: The initialised servo motor object.
    """
    servo_driver = PiicoDev_Servo_Driver()
    servo = PiicoDev_Servo(servo_driver, servo_channel)
    return servo


def initialise_sensors(sensitivity, servo_channel, RPi=RPI_MODE):
    """
    Initialise the touch sensor and servo motor based on the given sensitivity and servo channel.

    Args:
        sensitivity (int): The sensitivity level of the touch sensor.
        servo_channel (int): The channel number of the servo motor.
        RPi (bool, optional): Indicates if the code is running on a Raspberry Pi. Defaults to RPI_MODE.

    Returns:
        tuple: A tuple containing the initialised touch sensor and servo motor objects.
               If not running on a Raspberry Pi, returns (None, None).
    """
    if RPi:
        touch_sensor = initialise_touch_sensor(sensitivity)
        servo = initialise_servo(servo_channel)
        return touch_sensor, servo
    else:
        return None, None


def set_directory(dir_name):
    """
    Check if the input directory exists and return a Path object representing the directory.

    Args:
        dir_name (str or Path): The name or path of the directory to be checked.

    Returns:
        Path: The Path object representing the input directory.

    Raises:
        TypeError: If dir_name is not a string or a Path object.
        FileNotFoundError: If the specified directory does not exist.
    """
    if not isinstance(dir_name, (str, Path)):
        raise TypeError("dir_name must be a string or a Path object.")
    if not Path(dir_name).exists():
        raise FileNotFoundError(f"The specified directory {dir_name} does not exist.")
    return Path(dir_name)


def create_output_filenames(subject_name, session_number, session_type):
    """
    Generate the names for the log file and measurement file based on the subject name, session number, and session type.

    Args:
        subject_name (str): The name of the subject.
        session_number (int): The number of the session.
        session_type (str): The type of the session.

    Returns:
        tuple: A tuple containing the name of the log file and the name of the measurement file.

    Example:
        subject_name = "John"
        session_number = 1
        session_type = "preliminary"
        log_file, measurement_file = create_output_filenames(subject_name, session_number, session_type)
        print(log_file)  # Output: Experiment_2022-01-01T12:00:00_John_1_preliminary.log
        print(measurement_file)  # Output: Experiment_2022-01-01T12:00:00_John_1_preliminary.dat
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
        return False, 0, 0
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
    confirm = input("\nAre the details ok for this session (Y (or return) - continue / N - exit)?: ")
    if confirm == "" or confirm.lower()[0] == "y":
        return True
    else:
        return False


@dataclass
class Parameter:
    """
    A class representing a specific parameter used in an experiment.

    Attributes:
        name (str): The name of the parameter.
        val (float): The value of the parameter.
        unit (str): The unit of measurement for the parameter.
        minimum_value (float): The minimum allowed value for the parameter.
        maximum_value (float): The maximum allowed value for the parameter.
        description (str): A description of the parameter.
    """
    name: str
    val: float
    unit: str
    minimum_value: float
    maximum_value: float
    description: str


def parse_text_for_na(value):
    """
    Check if a value is a missing value (NaN) and return the value or an empty string.

    Parameters:
    value (any): The value to be checked for NaN.

    Returns:
    str: The original value if it is not NaN.
         An empty string if the value is NaN.
    """

    if pd.isna(value):
        return ""
    else:
        return value


def get_parameter(name, experiment_parameters_df):
    """
    Retrieves a specific parameter from a DataFrame containing experiment parameters.

    Args:
        name (str): The name of the parameter to retrieve.
        experiment_parameters_df (DataFrame): The DataFrame containing the experiment parameters.

    Returns:
        Parameter: The parameter with the specified name, or None if the parameter does not exist in the DataFrame.
    """
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
    """
    Load and validate experiment parameters from an Excel file.

    Args:
        data_dir (str): The directory where the experiment data is stored.
        parameters_xlsx (str, optional): The name of the Excel file containing the experiment parameters.
            Defaults to "experiment_parameters.xlsx".

    Raises:
        FileNotFoundError: If the experiment parameters Excel file does not exist in the specified data directory.

    Returns:
        dict: A dictionary containing the validated parameter values.
    """

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
    """
    Initialises the necessary components and parameters for an experiment.

    Args:
        data_dir (str, optional): The directory where the experiment data will be stored.

    Returns:
        tuple: A tuple containing the subject name, session number, session type, experiment parameters, touch sensor object, servo motor object, data directory, log file name, and measurement file name.

    Example:
        subject_name, session_number, session_type, p, touchSensor, servo, data_dir, log_file, measurement_file = setup_experiment()

    """
    pygame.mixer.init()  # Initialise the mixer module for playing WAV files
    data_dir = initialise_data_dir()
    p = load_validate_experiment_parameters(data_dir)
    touchSensor, servo = initialise_sensors(p["SENSITIVITY"], p["SERVO_CHANNEL"])
    subject_name, session_number, experiment_subjects_df = set_subject_name(data_dir)
    session_type = choose_session_type()
    if not confirm_experiment_details(subject_name, session_number, session_type):
        print("\nExiting - user terminated session...\n")
        sys.exit()
    update_subjects_xlsx(data_dir, experiment_subjects_df, subjects_file="experiment_subjects.xlsx")
    log_file, measurement_file = create_output_filenames(subject_name, session_number, session_type)
    log_trial_parameters(p, data_dir, log_file)
    comment = input("\nEnter any comments for this session: ")
    log_event(f"Comment: {comment}", data_dir, log_file)
    log_event(f"Data directory: {data_dir}", data_dir, log_file)
    log_event(f"Log file: {log_file}", data_dir, log_file)
    log_event(f"Measurement file: {measurement_file}", data_dir, log_file)
    log_event(f"Subject {subject_name} - Session {session_number} started...", data_dir, log_file)
    return subject_name, session_number, session_type, p, touchSensor, servo, data_dir, log_file, measurement_file
